#!/usr/bin/env python3
"""Ferramenta determinística de aprovação do copy-squad (ADR-001: D1 a D4, D8, D21, E1, E2 e E8).

Somente biblioteca padrão. Subcomandos:

    hash         <approval-request.json>
    content-hash <arquivo.json>
    verify --request R --decision D [--for-execution] [--payload ARQUIVO]
           (o ARQUIVO é o payload.json da rodada, E8)
    sample <asset_id> [--rate 0.20]
    decide --request R --decision approved|approved_with_edits|rejected
           --reviewer ID --confirm <12 primeiros hex do hash> [--comments TEXTO]

`--now` e `--config` (verify e decide) só são aceitos com a variável de ambiente
COPY_SQUAD_TEST_MODE=1; fora disso o script recusa (exit 2). No uso real o relógio é
o do sistema e a lista de aprovadores é a do config.yaml do squad.

`decide` é de uso exclusivo do humano (no Claude Code, com o prefixo `!`). Nenhum
agente deve executá-lo. A proveniência é procedimental, não criptográfica (D4); o hook opcional
scripts/guard_approval_decision.py (E8) impede o Claude de rodá-lo.

Com `jsonschema` instalado, o `verify` também valida o pedido e a decisão contra os
schemas do squad (contracts/); sem ele, essas duas checagens não existem.

O arquivo config.yaml é localizado pela posição deste script (pasta acima de
scripts/), nunca por caminho absoluto.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SQUAD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = SQUAD_ROOT / "config.yaml"
RECORDED_VIA_VALUES = ("human-cli", "human-chat-confirmed")
DECISIONS = ("approved", "approved_with_edits", "rejected")
DECISION_TTL_HOURS = 72
EXPIRY_TOLERANCE_SECONDS = 60
CONFIRM_LEN = 12
TEST_MODE_ENV = "COPY_SQUAD_TEST_MODE"
EXECUTION_OPERATIONS = ("publish", "send", "run_ads", "update_page")
BOUND_FIELDS = ("gate", "operation", "destination", "channel")
CONTRACTS_DIR = SQUAD_ROOT / "contracts"

# Mapeamento de meta.status da decisão (E2).
_META_STATUS = {
    "approved": "approved",
    "rejected": "rejected",
    "approved_with_edits": "needs_approval",
}


# --------------------------------------------------------------------- hash (D1)

def canonical_payload_bytes(payload) -> bytes:
    """JSON canônico: chaves ordenadas, sem espaços, UTF-8 sem escape ASCII."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def payload_sha256(payload) -> str:
    return hashlib.sha256(canonical_payload_bytes(payload)).hexdigest()


def content_sha256(document) -> str:
    """content_sha256 (E1): mesmo método do D1, aplicado ao documento JSON inteiro."""
    return payload_sha256(document)


def request_payload_hash(request: dict) -> str:
    if not isinstance(request, dict) or "payload" not in request:
        raise ValueError("approval-request sem o campo payload")
    return payload_sha256(request["payload"])


# ------------------------------------------------------------------- utilidades

def load_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_iso(value: str) -> datetime:
    """Interpreta data-hora ISO 8601; sem fuso é tratada como UTC."""
    text = str(value).strip()
    if text[-1:] in ("Z", "z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def load_approvers(config_path: Path) -> dict:
    """Lê human_gates.approvers do config.yaml (PyYAML se houver; senão leitor mínimo)."""
    text = Path(config_path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        cfg = yaml.safe_load(text) or {}
        approvers = ((cfg.get("human_gates") or {}).get("approvers")) or {}
        return {str(k): [str(x) for x in (v or [])] for k, v in approvers.items()} if isinstance(approvers, dict) else {}
    return _minimal_approvers(text)


def _minimal_approvers(text: str) -> dict:
    out: dict = {}
    lines = text.splitlines()
    in_block = False
    base_indent = 0
    for line in lines:
        if not in_block:
            m = re.match(r"^(\s*)approvers:\s*$", line)
            if m:
                in_block = True
                base_indent = len(m.group(1))
            continue
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent:
            break
        m = re.match(r"^\s*([^:#\s][^:]*):\s*\[(.*?)\]", line)
        if m:
            items = [x.strip().strip("'\"") for x in m.group(2).split(",") if x.strip()]
            out[m.group(1).strip().strip("'\"")] = items
    return out


def approvers_for(approvers: dict, business: str | None) -> list:
    if business and business in approvers:
        return list(approvers[business])
    return list(approvers.get("default") or [])


# ----------------------------------------------------------------------- verify

def _non_empty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def schema_problems(instance, schema_name: str, contracts_dir: Path = CONTRACTS_DIR):
    """Valida `instance` contra contracts/<schema_name>.schema.json.

    Retorna None quando o jsonschema ou o schema não estão disponíveis (checagem opcional);
    senão a lista (possivelmente vazia) de problemas em texto.
    """
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return None
    path = Path(contracts_dir) / f"{schema_name}.schema.json"
    if not path.is_file():
        return None
    schema = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(instance), key=lambda e: list(map(str, e.absolute_path))):
        loc = "/".join(str(x) for x in err.absolute_path) or "(raiz)"
        out.append(f"{loc}: {err.message[:120]}")
    return out


def verify(request: dict, decision: dict, approvers: dict, now: datetime,
           for_execution: bool = False, payload=None, contracts_dir: Path = CONTRACTS_DIR) -> dict:
    """Preflight (D8, E1, E2, E8). `payload` é o payload.json da rodada, a executar (opcional)."""
    checks: list = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    try:
        recalculated = request_payload_hash(request)
    except ValueError as exc:
        add("payload_presente", False, str(exc))
        return {"ok": False, "checks": checks}
    req_hash = request.get("payload_sha256")
    dec_hash = decision.get("payload_sha256")
    add("hash_request_igual_recalculado", req_hash == recalculated,
        f"request={req_hash} recalculado={recalculated}")
    add("hash_decision_igual_recalculado", dec_hash == recalculated,
        f"decision={dec_hash} recalculado={recalculated}")
    if payload is not None:
        to_run = payload_sha256(payload)
        add("hash_do_conteudo_a_executar", to_run == req_hash,
            f"conteudo={to_run} request={req_hash}")
    rmeta = request.get("meta") if isinstance(request.get("meta"), dict) else {}
    dmeta = decision.get("meta") if isinstance(decision.get("meta"), dict) else {}
    req_id = rmeta.get("artifact_id")
    add("request_artifact_type", rmeta.get("artifact_type") == "approval-request",
        f"request.meta.artifact_type={rmeta.get('artifact_type')}")
    add("decision_artifact_type", dmeta.get("artifact_type") == "approval-decision",
        f"decision.meta.artifact_type={dmeta.get('artifact_type')}")
    add("decision_business_igual_ao_pedido",
        _non_empty_str(rmeta.get("business")) and dmeta.get("business") == rmeta.get("business"),
        f"decision.meta.business={dmeta.get('business')!r} request.meta.business={rmeta.get('business')!r}")
    add("decision_campaign_igual_ao_pedido",
        _non_empty_str(rmeta.get("campaign_id")) and dmeta.get("campaign_id") == rmeta.get("campaign_id"),
        f"decision.meta.campaign_id={dmeta.get('campaign_id')!r} request.meta.campaign_id={rmeta.get('campaign_id')!r}")
    for label, doc, schema_name in (("request", request, "approval-request"), ("decision", decision, "approval-decision")):
        problems = schema_problems(doc, schema_name, contracts_dir)
        if problems is not None:
            add(f"{label}_valido_no_schema", not problems,
                "; ".join(problems[:5]) or f"{label} valida contra contracts/{schema_name}.schema.json")
    add("decision_refere_a_este_request", decision.get("approval_request_id") == req_id,
        f"approval_request_id={decision.get('approval_request_id')} artifact_id={req_id}")
    add("decision_approved", decision.get("decision") == "approved",
        f"decision={decision.get('decision')} (approved_with_edits nunca autoriza execução)")

    bound = decision.get("bound_to")
    if isinstance(bound, dict):
        diffs = [f"{k}: decision={bound.get(k)!r} request={request.get(k)!r}"
                 for k in BOUND_FIELDS if k not in bound or bound.get(k) != request.get(k)]
        extra = sorted(set(bound) - set(BOUND_FIELDS))
        if extra:
            diffs.append(f"campos extras em bound_to: {extra}")
        add("bound_to_igual_ao_pedido", not diffs,
            "; ".join(diffs) or "gate, operation, destination e channel iguais ao pedido")
    else:
        add("bound_to_igual_ao_pedido", False, "decision sem o objeto bound_to")

    if for_execution:
        add("execucao_gate_g4", request.get("gate") == "G4", f"gate={request.get('gate')}")
        add("execucao_operation_externa", request.get("operation") in EXECUTION_OPERATIONS,
            f"operation={request.get('operation')} permitido={list(EXECUTION_OPERATIONS)}")
        add("execucao_risco_nao_low", request.get("risk_level") not in (None, "low"),
            f"risk_level={request.get('risk_level')}")
        add("execucao_destination_channel_preenchidos",
            _non_empty_str(request.get("destination")) and _non_empty_str(request.get("channel")),
            "destination e channel do pedido devem ser strings não vazias")
        add("execucao_payload_informado", payload is not None,
            "preflight exige --payload com o payload.json da rodada (E8): sem ele não se confere o que será executado")
        bound_now = decision.get("bound_to")
        add("execucao_bound_to_completo",
            isinstance(bound_now, dict) and all(_non_empty_str(bound_now.get(k)) for k in BOUND_FIELDS),
            "as quatro chaves de bound_to (gate, operation, destination, channel) devem ser strings não vazias")

    decided = expires = None
    try:
        decided = parse_iso(decision.get("decided_at"))
        add("decidido_antes_de_agora", decided <= now,
            f"decided_at={decided.isoformat()} agora={now.isoformat()}")
    except (TypeError, ValueError, IndexError):
        add("decidido_antes_de_agora", False, "decided_at ausente ou inválido")
    try:
        expires = parse_iso(decision.get("expires_at"))
        add("dentro_da_validade", now < expires, f"agora={now.isoformat()} expires_at={expires.isoformat()}")
    except (TypeError, ValueError, IndexError):
        add("dentro_da_validade", False, "expires_at ausente ou inválido")
    if decided is not None and expires is not None:
        delta = abs((expires - (decided + timedelta(hours=DECISION_TTL_HOURS))).total_seconds())
        add("janela_de_72h", delta <= EXPIRY_TOLERANCE_SECONDS,
            f"expires_at - decided_at = {(expires - decided).total_seconds() / 3600:.4f} h "
            f"(esperado {DECISION_TTL_HOURS} h, tolerância {EXPIRY_TOLERANCE_SECONDS} s)")
    else:
        add("janela_de_72h", False, "decided_at ou expires_at inválido")

    add("human_attested", decision.get("human_attested") is True, f"human_attested={decision.get('human_attested')}")
    add("recorded_via_valido", decision.get("recorded_via") in RECORDED_VIA_VALUES,
        f"recorded_via={decision.get('recorded_via')}")
    if decision.get("recorded_via") == "human-chat-confirmed":
        add("comments_com_citacao_do_humano", bool(str(decision.get("comments") or "").strip()),
            "human-chat-confirmed exige comments com a mensagem literal do humano")
    meta = dmeta
    add("produced_by_approval_owner", meta.get("produced_by") == "approval-owner",
        f"produced_by={meta.get('produced_by')}")
    add("sem_model_ou_prompt_version", "model" not in meta and "prompt_version" not in meta,
        "decisão humana não pode trazer meta.model nem meta.prompt_version")
    expected_status = _META_STATUS.get(decision.get("decision"))
    add("meta_status_coerente", expected_status is not None and meta.get("status") == expected_status,
        f"meta.status={meta.get('status')} esperado={expected_status}")
    # E8: os aprovadores são os do negócio do PEDIDO, nunca os declarados pela própria decisão.
    allowed = approvers_for(approvers, rmeta.get("business"))
    add("reviewer_em_approvers", decision.get("reviewer") in allowed,
        f"reviewer={decision.get('reviewer')} business_do_pedido={rmeta.get('business')!r} "
        f"aprovadores_configurados={len(allowed)}")
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


# ----------------------------------------------------------------------- sample

def sample(asset_id: str, rate: float = 0.20) -> bool:
    digest = hashlib.sha256(asset_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF < rate


# ----------------------------------------------------------------------- decide

def build_decision(request: dict, decision: str, reviewer: str, comments: str | None, now: datetime) -> dict:
    rmeta = request.get("meta") or {}
    req_id = str(rmeta.get("artifact_id", ""))
    suffix = req_id.split("-", 1)[1] if "-" in req_id else req_id
    meta = {
        "schema_version": "1.0.0",
        "artifact_id": f"apd-{suffix}",
        "artifact_type": "approval-decision",
        "business": rmeta.get("business"),
        "produced_by": "approval-owner",
        "produced_at": now.isoformat(),
        "version": 1,
        "status": _META_STATUS[decision],
    }
    if rmeta.get("campaign_id"):
        meta["campaign_id"] = rmeta["campaign_id"]
    if request.get("risk_level"):
        meta["risk_level"] = request["risk_level"]
    doc = {
        "meta": meta,
        "human_attested": True,
        "recorded_via": "human-cli",
        "approval_request_id": req_id,
        "decision": decision,
        "reviewer": reviewer,
        "decided_at": now.isoformat(),
        "payload_sha256": request_payload_hash(request),
        "bound_to": {k: request.get(k) for k in BOUND_FIELDS},
    }
    if comments:
        doc["comments"] = comments
    doc["expires_at"] = (now + timedelta(hours=DECISION_TTL_HOURS)).isoformat()
    return doc


# -------------------------------------------------------------------------- CLI

def _out(text: str) -> None:
    sys.stdout.write(text + "\n")


def _config_path(args) -> Path:
    return Path(args.config) if args.config else DEFAULT_CONFIG


def cmd_hash(args) -> int:
    _out(request_payload_hash(load_json(args.request)))
    return 0


def cmd_content_hash(args) -> int:
    _out(content_sha256(load_json(args.file)))
    return 0


def cmd_verify(args) -> int:
    try:
        request = load_json(args.request)
        decision = load_json(args.decision)
        payload = load_json(args.payload) if args.payload else None
        approvers = load_approvers(_config_path(args))
        now = parse_iso(args.now) if args.now else utc_now()
    except (OSError, ValueError) as exc:
        _out(json.dumps({"ok": False, "checks": [{"name": "leitura_dos_arquivos", "ok": False, "detail": str(exc)}]},
                        ensure_ascii=False, indent=2))
        return 1
    result = verify(request, decision, approvers, now, for_execution=args.for_execution, payload=payload)
    _out(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def cmd_sample(args) -> int:
    _out("true" if sample(args.asset_id, args.rate) else "false")
    return 0


def cmd_decide(args) -> int:
    request_path = Path(args.request)
    request = load_json(request_path)
    expected = request_payload_hash(request)[:CONFIRM_LEN]
    if args.confirm.lower() != expected:
        sys.stderr.write(f"--confirm não confere com os {CONFIRM_LEN} primeiros hex do hash recalculado ({expected}).\n")
        return 1
    meta = request.get("meta") or {}
    allowed = approvers_for(load_approvers(_config_path(args)), meta.get("business"))
    if args.reviewer not in allowed:
        sys.stderr.write("reviewer ausente em human_gates.approvers do config.yaml; decisão não gravada.\n")
        return 1
    target = request_path.resolve().parent / "approval-decision.json"
    if target.exists():
        sys.stderr.write("approval-decision.json já existe nesta pasta; decisões são imutáveis. Abra nova rodada.\n")
        return 1
    now = parse_iso(args.now) if args.now else utc_now()
    doc = build_decision(request, args.decision, args.reviewer, args.comments, now)
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    _out(str(target))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ferramentas determinísticas de aprovação do copy-squad.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("hash", help="payload_sha256 do approval-request (método D1)")
    p.add_argument("request")
    p.set_defaults(func=cmd_hash)

    p = sub.add_parser("content-hash", help="content_sha256: sha256 do JSON canônico do arquivo inteiro (E1)")
    p.add_argument("file")
    p.set_defaults(func=cmd_content_hash)

    p = sub.add_parser("verify", help="preflight de execução (D8, E1, E2): JSON {ok, checks[]}, exit 0/1")
    p.add_argument("--request", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--for-execution", action="store_true", dest="for_execution",
                   help="exige gate G4, operation de execução externa (publish, send, run_ads, update_page) e risco acima de low")
    p.add_argument("--payload", help="payload.json da rodada (E8), igual a approval-request.payload; o hash D1 dele deve ser igual ao payload_sha256 do pedido")
    p.add_argument("--now", help=f"somente com {TEST_MODE_ENV}=1: data-hora ISO 8601 (padrão: agora, UTC)")
    p.add_argument("--config", help=f"somente com {TEST_MODE_ENV}=1: config.yaml (padrão: o do squad deste script)")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("sample", help="amostragem determinística: true ou false")
    p.add_argument("asset_id")
    p.add_argument("--rate", type=float, default=0.20)
    p.set_defaults(func=cmd_sample)

    p = sub.add_parser("decide", help="USO EXCLUSIVO DO HUMANO: grava approval-decision.json ao lado do request")
    p.add_argument("--request", required=True)
    p.add_argument("--decision", required=True, choices=DECISIONS)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--confirm", required=True, help="12 primeiros hex do hash do payload")
    p.add_argument("--comments")
    p.add_argument("--now", help=f"somente com {TEST_MODE_ENV}=1: data-hora ISO 8601 (padrão: agora, UTC)")
    p.add_argument("--config", help=f"somente com {TEST_MODE_ENV}=1: config.yaml (padrão: o do squad deste script)")
    p.set_defaults(func=cmd_decide)
    return parser


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if (getattr(args, "now", None) or getattr(args, "config", None)) and os.environ.get(TEST_MODE_ENV) != "1":
        sys.stderr.write(f"--now e --config só são aceitos com {TEST_MODE_ENV}=1 (modo de teste); "
                         "no uso real o relógio e o config.yaml são os do sistema e do squad.\n")
        return 2
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"erro: {exc}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
