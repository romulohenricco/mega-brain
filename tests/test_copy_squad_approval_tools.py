"""Testes de squads/copy-squad/scripts/approval_tools.py (ADR-001: D1 a D4, D8, D21, E1 e E2).

Suíte rápida: tudo roda em pastas temporárias pequenas (um approval-request e um config.yaml);
nada copia o repositório. O relógio e o config só entram pelo modo de teste.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SQUAD = REPO / "squads" / "copy-squad"
TOOLS_PATH = SQUAD / "scripts" / "approval_tools.py"
VALIDATOR_PATH = SQUAD / "scripts" / "validate_copy_squad.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tools = _load("approval_tools", TOOLS_PATH)

# Vetor conhecido: payload com acento, hash do JSON canônico UTF-8 sem escape ASCII.
VECTOR_PAYLOAD = {"n": 1, "headline": "Ação rápida"}
VECTOR_CANONICAL = '{"headline":"Ação rápida","n":1}'
VECTOR_SHA256 = "8d15a25ecd7f0b53c4cefb5b285b1038b20e19b8a4a3d75ff2ca8e53eb50d375"
VECTOR_SHA256_ASCII_ESCAPED = "9fea7de1ff3b74195da0a7b8d8bd7a6c3744f2507f5553201b3507d8cd7ce1c5"

NOW = "2026-11-10T12:00:00+00:00"
REVIEWER = "ana-revisora"
BASE_REQUEST = json.loads((SQUAD / "fixtures" / "approval-request.valid.json").read_text(encoding="utf-8"))
BUSINESS = BASE_REQUEST["meta"]["business"]
CONFIG_TEXT = "human_gates:\n  owner: approval-owner\n  approvers:\n    default: []\n    " + BUSINESS + ": [" + REVIEWER + "]\n"


@pytest.fixture(autouse=True)
def test_mode(monkeypatch):
    """--now e --config só funcionam em modo de teste (E1)."""
    monkeypatch.setenv(tools.TEST_MODE_ENV, "1")


@pytest.fixture
def workspace(tmp_path):
    """Pasta com config.yaml de teste e um approval-request G4/publish com hash correto."""
    (tmp_path / "config.yaml").write_text(CONFIG_TEXT, encoding="utf-8", newline="\n")
    request = copy.deepcopy(BASE_REQUEST)
    request["payload_sha256"] = tools.request_payload_hash(request)
    folder = tmp_path / "06-approval" / request["asset_id"] / "g4-r1"
    folder.mkdir(parents=True)
    req_path = folder / "approval-request.json"
    _write(req_path, request)
    return {"root": tmp_path, "config": tmp_path / "config.yaml", "request": request, "req_path": req_path}


def _write(path: Path, doc) -> None:
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _decide(ws, decision="approved", reviewer=REVIEWER, confirm=None, now=NOW, comments="Aprovado após leitura integral."):
    confirm = confirm if confirm is not None else ws["request"]["payload_sha256"][:12]
    argv = ["decide", "--request", str(ws["req_path"]), "--decision", decision,
            "--reviewer", reviewer, "--confirm", confirm,
            "--now", now, "--config", str(ws["config"])]
    if comments is not None:
        argv += ["--comments", comments]
    return tools.main(argv)


def _verify(ws, decision_path, now=NOW, capsys=None, extra=(), auto_payload=True):
    extra = list(extra)
    if auto_payload and "--for-execution" in extra and "--payload" not in extra:
        # E8: o preflight sempre recebe o payload.json da rodada (= approval-request.payload)
        request = json.loads(Path(ws["req_path"]).read_text(encoding="utf-8"))
        payload_file = Path(ws["req_path"]).parent / "payload.json"
        payload_file.write_text(json.dumps(request["payload"], ensure_ascii=False, sort_keys=True,
                                           separators=(",", ":")), encoding="utf-8", newline="\n")
        extra += ["--payload", str(payload_file)]
    code = tools.main(["verify", "--request", str(ws["req_path"]), "--decision", str(decision_path),
                       "--now", now, "--config", str(ws["config"]), *extra])
    out = json.loads(capsys.readouterr().out) if capsys else None
    return code, out


def _failed(out):
    return [c["name"] for c in out["checks"] if not c["ok"]]


def _decision_file(ws, capsys, decision="approved", **overrides):
    """Grava a decisão pelo decide e aplica sobrescritas (chaves com ponto entram em meta ou bound_to)."""
    assert _decide(ws, decision=decision) == 0
    capsys.readouterr()
    path = ws["req_path"].parent / "approval-decision.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key, value in overrides.items():
        target, name = doc, key
        for prefix in ("meta.", "bound_to."):
            if key.startswith(prefix):
                target, name = doc[prefix[:-1]], key[len(prefix):]
        if value is None:
            target.pop(name, None)
        else:
            target[name] = value
    _write(path, doc)
    return path


# ------------------------------------------------------------------------ hash

def test_hash_known_vector_with_accent():
    assert tools.canonical_payload_bytes(VECTOR_PAYLOAD).decode("utf-8") == VECTOR_CANONICAL
    assert tools.payload_sha256(VECTOR_PAYLOAD) == VECTOR_SHA256
    assert hashlib.sha256(VECTOR_CANONICAL.encode("utf-8")).hexdigest() == VECTOR_SHA256
    # escapar o acento em ASCII muda o hash: ensure_ascii=False é parte do método D1
    assert VECTOR_SHA256 != VECTOR_SHA256_ASCII_ESCAPED


def test_hash_ignores_key_order_and_covers_only_payload(workspace):
    reordered = {"headline": "Ação rápida", "n": 1}
    assert tools.payload_sha256(reordered) == tools.payload_sha256(VECTOR_PAYLOAD)
    request = copy.deepcopy(workspace["request"])
    before = tools.request_payload_hash(request)
    request["destination"] = "outro destino"
    request["operation"] = "send"
    request["channel"] = "email"
    assert tools.request_payload_hash(request) == before


def test_hash_cli_prints_hash(workspace, capsys):
    assert tools.main(["hash", str(workspace["req_path"])]) == 0
    assert capsys.readouterr().out.strip() == workspace["request"]["payload_sha256"]


def test_validator_hash_matches_tool_hash():
    validator = _load("validate_copy_squad_for_hash", VALIDATOR_PATH)
    assert validator.canonical_payload_sha256(VECTOR_PAYLOAD) == VECTOR_SHA256 == tools.payload_sha256(VECTOR_PAYLOAD)


# ---------------------------------------------------------------- content-hash (E1)

def test_content_hash_is_canonical_hash_of_the_whole_file(workspace, tmp_path, capsys):
    doc = tmp_path / "doc.json"
    # ordem de chaves e espaços diferentes do canônico: o hash tem de ignorá-los
    doc.write_text('{\n  "n": 1,\n  "headline": "Ação rápida"\n}\n', encoding="utf-8")
    assert tools.main(["content-hash", str(doc)]) == 0
    assert capsys.readouterr().out.strip() == VECTOR_SHA256
    assert tools.content_sha256(VECTOR_PAYLOAD) == VECTOR_SHA256
    # sobre o approval-request inteiro difere do hash do payload
    assert tools.main(["content-hash", str(workspace["req_path"])]) == 0
    whole = capsys.readouterr().out.strip()
    assert whole == tools.payload_sha256(workspace["request"]) != workspace["request"]["payload_sha256"]


def test_content_hash_missing_file_fails_cleanly(tmp_path, capsys):
    assert tools.main(["content-hash", str(tmp_path / "nao-existe.json")]) == 1
    assert "erro" in capsys.readouterr().err


# ---------------------------------------------------------------------- sample

def test_sample_is_deterministic_and_matches_formula(capsys):
    expected = int(hashlib.sha256(b"cvc-lp-mentoria").hexdigest()[:8], 16) / 0xFFFFFFFF
    assert abs(expected - 0.6431086053240831) < 1e-12
    assert tools.sample("cvc-lp-mentoria", 0.64) is False
    assert tools.sample("cvc-lp-mentoria", 0.65) is True
    assert tools.sample("cvc-lp-mentoria") == tools.sample("cvc-lp-mentoria")
    assert tools.main(["sample", "cvc-lp-mentoria", "--rate", "0.65"]) == 0
    assert capsys.readouterr().out.strip() == "true"
    assert tools.main(["sample", "cvc-lp-mentoria"]) == 0
    assert capsys.readouterr().out.strip() == "false"


def test_sample_rate_extremes():
    ids = [f"asset-{i}" for i in range(50)]
    assert not any(tools.sample(a, 0.0) for a in ids)
    assert all(tools.sample(a, 1.01) for a in ids)


# ---------------------------------------------------------------------- decide

def test_decide_writes_valid_decision_with_bound_to(workspace, capsys):
    assert _decide(workspace) == 0
    written = Path(capsys.readouterr().out.strip())
    assert written == workspace["req_path"].resolve().parent / "approval-decision.json"
    doc = json.loads(written.read_text(encoding="utf-8"))
    request = workspace["request"]
    assert doc["human_attested"] is True
    assert doc["recorded_via"] == "human-cli"
    assert doc["meta"]["produced_by"] == "approval-owner"
    assert doc["meta"]["artifact_type"] == "approval-decision"
    assert "model" not in doc["meta"] and "prompt_version" not in doc["meta"]
    assert doc["payload_sha256"] == tools.request_payload_hash(request)
    assert doc["decided_at"] == "2026-11-10T12:00:00+00:00"
    assert doc["expires_at"] == "2026-11-13T12:00:00+00:00"
    assert doc["approval_request_id"] == request["meta"]["artifact_id"]
    assert doc["meta"]["artifact_id"] == "apd-" + request["meta"]["artifact_id"].split("-", 1)[1]
    # E1: bound_to copiado do pedido
    assert doc["bound_to"] == {k: request[k] for k in ("gate", "operation", "destination", "channel")}
    # o arquivo gravado cumpre o contrato
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((SQUAD / "contracts" / "approval-decision.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(doc)


@pytest.mark.parametrize("decision,status", [
    ("approved", "approved"),
    ("rejected", "rejected"),
    ("approved_with_edits", "needs_approval"),
])
def test_decide_maps_meta_status(workspace, capsys, decision, status):
    assert _decide(workspace, decision=decision) == 0
    doc = json.loads(Path(capsys.readouterr().out.strip()).read_text(encoding="utf-8"))
    assert doc["decision"] == decision and doc["meta"]["status"] == status
    assert tools._META_STATUS[decision] == status


def test_decide_requires_matching_confirm(workspace, capsys):
    assert _decide(workspace, confirm="000000000000") == 1
    assert not (workspace["req_path"].parent / "approval-decision.json").exists()
    assert "--confirm" in capsys.readouterr().err


def test_decide_refuses_unlisted_reviewer_and_overwrite(workspace):
    assert _decide(workspace, reviewer="desconhecido") == 1
    assert _decide(workspace) == 0
    assert _decide(workspace) == 1  # decisão é imutável: nova rodada, não sobrescrita


def test_decide_rejects_unknown_decision_value(workspace):
    with pytest.raises(SystemExit):
        _decide(workspace, decision="maybe")


# ---------------------------------------------------------------------- verify

def test_verify_ok_for_approved_within_window(workspace, capsys):
    assert _decide(workspace) == 0
    capsys.readouterr()
    code, out = _verify(workspace, workspace["req_path"].parent / "approval-decision.json", capsys=capsys)
    assert code == 0 and out["ok"] is True
    assert all(c["ok"] for c in out["checks"])
    names = {c["name"] for c in out["checks"]}
    assert {"bound_to_igual_ao_pedido", "decidido_antes_de_agora", "janela_de_72h", "meta_status_coerente"} <= names


@pytest.mark.parametrize(
    "overrides,failed",
    [
        ({"payload_sha256": "0" * 64}, "hash_decision_igual_recalculado"),
        ({"decision": "approved_with_edits", "meta.status": "needs_approval"}, "decision_approved"),
        ({"decision": "rejected", "meta.status": "rejected"}, "decision_approved"),
        ({"human_attested": False}, "human_attested"),
        ({"human_attested": None}, "human_attested"),
        ({"recorded_via": "agent"}, "recorded_via_valido"),
        ({"recorded_via": None}, "recorded_via_valido"),
        ({"reviewer": "outra-pessoa"}, "reviewer_em_approvers"),
        ({"meta.produced_by": "copy-publisher"}, "produced_by_approval_owner"),
        ({"meta.model": "sonnet"}, "sem_model_ou_prompt_version"),
        ({"meta.prompt_version": "1.0.0"}, "sem_model_ou_prompt_version"),
        ({"approval_request_id": "apr-outro"}, "decision_refere_a_este_request"),
        ({"expires_at": "2026-11-10T11:00:00+00:00"}, "dentro_da_validade"),
        # E1: decisão amarrada ao pedido
        ({"bound_to": None}, "bound_to_igual_ao_pedido"),
        ({"bound_to.destination": "outro destino"}, "bound_to_igual_ao_pedido"),
        ({"bound_to.operation": "run_ads"}, "bound_to_igual_ao_pedido"),
        ({"bound_to.channel": "email"}, "bound_to_igual_ao_pedido"),
        ({"bound_to.gate": "G1"}, "bound_to_igual_ao_pedido"),
        ({"bound_to.channel": None}, "bound_to_igual_ao_pedido"),
        ({"bound_to.extra": "x"}, "bound_to_igual_ao_pedido"),
        # E2: validade e proveniência
        ({"decided_at": "2026-11-10T12:00:01+00:00", "expires_at": "2026-11-13T12:00:01+00:00"}, "decidido_antes_de_agora"),
        ({"expires_at": "2026-11-14T12:00:00+00:00"}, "janela_de_72h"),
        ({"expires_at": "2026-11-13T12:01:01+00:00"}, "janela_de_72h"),
        ({"expires_at": "2026-11-13T11:58:59+00:00"}, "janela_de_72h"),
        ({"expires_at": None}, "dentro_da_validade"),
        ({"decided_at": "ontem"}, "decidido_antes_de_agora"),
        ({"recorded_via": "human-chat-confirmed", "comments": None}, "comments_com_citacao_do_humano"),
        ({"recorded_via": "human-chat-confirmed", "comments": "   "}, "comments_com_citacao_do_humano"),
        ({"meta.status": "needs_approval"}, "meta_status_coerente"),
        ({"meta.status": None}, "meta_status_coerente"),
    ],
)
def test_verify_fails_for_each_violation(workspace, capsys, overrides, failed):
    path = _decision_file(workspace, capsys, **overrides)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and out["ok"] is False
    assert failed in _failed(out)


def test_verify_expiry_tolerance_is_sixty_seconds(workspace, capsys):
    path = _decision_file(workspace, capsys, expires_at="2026-11-13T12:00:30+00:00")
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 0 and out["ok"] is True


def test_verify_accepts_human_chat_confirmed_with_literal_quote(workspace, capsys):
    path = _decision_file(workspace, capsys, recorded_via="human-chat-confirmed",
                          comments='Mensagem do humano: "pode publicar a versão aprovada".')
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 0 and out["ok"] is True


def test_verify_fails_when_payload_changed_after_request(workspace, capsys):
    path = _decision_file(workspace, capsys)
    request = json.loads(workspace["req_path"].read_text(encoding="utf-8"))
    request["payload"]["headline"] = "Texto alterado depois da aprovação"
    _write(workspace["req_path"], request)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1
    assert "hash_request_igual_recalculado" in _failed(out) and "hash_decision_igual_recalculado" in _failed(out)


def test_verify_fails_when_request_gate_or_destination_changed_after_decision(workspace, capsys):
    path = _decision_file(workspace, capsys)
    request = json.loads(workspace["req_path"].read_text(encoding="utf-8"))
    request["destination"] = "outro destino, não aprovado"
    request["operation"] = "run_ads"
    _write(workspace["req_path"], request)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and _failed(out) == ["bound_to_igual_ao_pedido"]


def test_verify_expired_after_window(workspace, capsys):
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, now="2026-11-13T12:00:01+00:00", capsys=capsys)
    assert code == 1
    assert "dentro_da_validade" in _failed(out)
    # no instante exato do vencimento a janela já fechou; um segundo antes ainda vale
    code, out = _verify(workspace, path, now="2026-11-13T11:59:59+00:00", capsys=capsys)
    assert code == 0 and out["ok"] is True


def test_verify_missing_file_is_failure_not_crash(workspace, capsys):
    code, out = _verify(workspace, workspace["root"] / "nao-existe.json", capsys=capsys)
    assert code == 1 and out["ok"] is False


def test_verify_with_empty_approvers_blocks(workspace, capsys):
    path = _decision_file(workspace, capsys)
    workspace["config"].write_text("human_gates:\n  approvers:\n    default: []\n", encoding="utf-8")
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1
    assert "reviewer_em_approvers" in _failed(out)


# --------------------------------------------------- verify --for-execution (E1)

def test_for_execution_passes_for_g4_external_operation(workspace, capsys):
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 0 and out["ok"] is True
    assert {"execucao_gate_g4", "execucao_operation_externa", "execucao_risco_nao_low"} <= {c["name"] for c in out["checks"]}


@pytest.mark.parametrize("operation", list(tools.EXECUTION_OPERATIONS))
def test_for_execution_accepts_every_external_operation(workspace, capsys, operation):
    request = copy.deepcopy(workspace["request"])
    request["operation"] = operation
    _write(workspace["req_path"], request)
    workspace["request"] = request
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 0 and out["ok"] is True


@pytest.mark.parametrize("changes,failed", [
    ({"gate": "G1"}, "execucao_gate_g4"),
    ({"gate": "G3"}, "execucao_gate_g4"),
    ({"gate": "SAMPLING"}, "execucao_gate_g4"),
    ({"operation": "approve_brief"}, "execucao_operation_externa"),
    ({"operation": "internal_use"}, "execucao_operation_externa"),
    ({"risk_level": "low"}, "execucao_risco_nao_low"),
])
def test_for_execution_rejects_non_external_requests(workspace, capsys, changes, failed):
    request = copy.deepcopy(workspace["request"])
    request.update(changes)
    _write(workspace["req_path"], request)
    workspace["request"] = request
    path = _decision_file(workspace, capsys)
    # sem --for-execution a decisão amarrada ao pedido continua válida ...
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 0 and out["ok"] is True
    # ... e com --for-execution (preflight) o pedido que não é de execução externa é barrado
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 1 and failed in _failed(out)


def test_for_execution_with_payload_compares_content_hash(workspace, capsys):
    path = _decision_file(workspace, capsys)
    payload_file = workspace["root"] / "payload.json"
    _write(payload_file, workspace["request"]["payload"])
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution", "--payload", str(payload_file)])
    assert code == 0 and out["ok"] is True
    assert "hash_do_conteudo_a_executar" in {c["name"] for c in out["checks"]}

    changed = copy.deepcopy(workspace["request"]["payload"])
    changed["headline"] = changed["headline"] + " (editado depois da aprovação)"
    _write(payload_file, changed)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution", "--payload", str(payload_file)])
    assert code == 1 and _failed(out) == ["hash_do_conteudo_a_executar"]


def test_for_execution_without_payload_fails(workspace, capsys):
    """E8: preflight sem --payload não confere o conteúdo a executar, então reprova."""
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"], auto_payload=False)
    assert code == 1 and "execucao_payload_informado" in _failed(out)


def test_payload_file_missing_is_failure_not_crash(workspace, capsys):
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--payload", str(workspace["root"] / "nao-existe.json")])
    assert code == 1 and out["ok"] is False


# ------------------------------------------------ business, campanha e schema (E8)

def _overwrite_decision(path, **overrides):
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key, value in overrides.items():
        target, name = (doc["meta"], key[len("meta."):]) if key.startswith("meta.") else (doc, key)
        if value is None:
            target.pop(name, None)
        else:
            target[name] = value
    _write(path, doc)
    return path


def test_approvers_come_from_the_request_business_not_from_the_decision(workspace, capsys):
    """Quem escreve a decisão não escolhe a lista de aprovadores: vale o business do pedido."""
    path = _decision_file(workspace, capsys)
    workspace["config"].write_text(
        "human_gates:\n  approvers:\n    default: [" + REVIEWER + "]\n    " + BUSINESS + ": [somente-o-dono]\n",
        encoding="utf-8", newline="\n")
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and "reviewer_em_approvers" in _failed(out)
    for business in ("outro-negocio", None):
        _overwrite_decision(path, **{"meta.business": business})
        code, out = _verify(workspace, path, capsys=capsys)
        assert code == 1
        assert "reviewer_em_approvers" in _failed(out), "o default da decisão adulterada não pode valer"
        assert "decision_business_igual_ao_pedido" in _failed(out)


@pytest.mark.parametrize("overrides,failed", [
    ({"meta.business": "outro-negocio"}, "decision_business_igual_ao_pedido"),
    ({"meta.business": None}, "decision_business_igual_ao_pedido"),
    ({"meta.campaign_id": "camp-outra"}, "decision_campaign_igual_ao_pedido"),
    ({"meta.campaign_id": None}, "decision_campaign_igual_ao_pedido"),
    ({"meta.artifact_type": "approval-request"}, "decision_artifact_type"),
    ({"meta.artifact_type": None}, "decision_artifact_type"),
])
def test_decision_meta_must_match_the_request(workspace, capsys, overrides, failed):
    path = _decision_file(workspace, capsys, **overrides)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and failed in _failed(out)


def test_request_artifact_type_is_checked(workspace, capsys):
    path = _decision_file(workspace, capsys)
    request = json.loads(workspace["req_path"].read_text(encoding="utf-8"))
    request["meta"]["artifact_type"] = "approval-decision"
    _write(workspace["req_path"], request)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and "request_artifact_type" in _failed(out)


def _rewrite_pair(ws, path, req_changes=None, bound_changes=None):
    """Altera pedido e decisão juntos (None remove a chave), como faria quem forja os dois lados."""
    request = json.loads(ws["req_path"].read_text(encoding="utf-8"))
    decision = json.loads(path.read_text(encoding="utf-8"))
    for key, value in (req_changes or {}).items():
        if value is None:
            request.pop(key, None)
        else:
            request[key] = value
    for key, value in (bound_changes or {}).items():
        if value is None:
            decision["bound_to"].pop(key, None)
        else:
            decision["bound_to"][key] = value
    _write(ws["req_path"], request)
    _write(path, decision)


@pytest.mark.parametrize("field,value", [("destination", ""), ("destination", "   "), ("destination", None),
                                          ("channel", ""), ("channel", None)])
def test_for_execution_rejects_empty_destination_or_channel_even_when_both_sides_match(workspace, capsys, field, value):
    path = _decision_file(workspace, capsys)
    _rewrite_pair(workspace, path, req_changes={field: value}, bound_changes={field: value})
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 1
    failed = _failed(out)
    assert "execucao_destination_channel_preenchidos" in failed
    assert "execucao_bound_to_completo" in failed


@pytest.mark.parametrize("key", ["gate", "operation", "destination", "channel"])
def test_for_execution_rejects_bound_to_missing_a_key(workspace, capsys, key):
    path = _decision_file(workspace, capsys)
    _rewrite_pair(workspace, path, bound_changes={key: None})
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 1
    assert "execucao_bound_to_completo" in _failed(out) and "bound_to_igual_ao_pedido" in _failed(out)


def test_for_execution_bound_to_values_must_be_non_empty_strings(workspace, capsys):
    path = _decision_file(workspace, capsys)
    _rewrite_pair(workspace, path, bound_changes={"channel": 7})
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    assert code == 1 and "execucao_bound_to_completo" in _failed(out)


def test_schema_validation_covers_request_and_decision(workspace, capsys):
    pytest.importorskip("jsonschema")
    path = _decision_file(workspace, capsys)
    code, out = _verify(workspace, path, capsys=capsys)
    names = {c["name"] for c in out["checks"]}
    assert code == 0 and {"request_valido_no_schema", "decision_valido_no_schema"} <= names
    _overwrite_decision(path, reviewer=42, campo_inventado=True)
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and "decision_valido_no_schema" in _failed(out)
    detail = next(c["detail"] for c in out["checks"] if c["name"] == "decision_valido_no_schema")
    assert "reviewer" in detail


def test_empty_destination_fails_request_schema_without_for_execution(workspace, capsys):
    pytest.importorskip("jsonschema")
    path = _decision_file(workspace, capsys)
    _rewrite_pair(workspace, path, req_changes={"destination": ""}, bound_changes={"destination": ""})
    code, out = _verify(workspace, path, capsys=capsys)
    assert code == 1 and "request_valido_no_schema" in _failed(out)


def test_schema_validation_is_skipped_without_jsonschema(workspace, capsys, monkeypatch):
    path = _decision_file(workspace, capsys)
    monkeypatch.setitem(sys.modules, "jsonschema", None)
    code, out = _verify(workspace, path, capsys=capsys, extra=["--for-execution"])
    names = {c["name"] for c in out["checks"]}
    assert code == 0 and out["ok"] is True
    assert not ({"request_valido_no_schema", "decision_valido_no_schema"} & names)


def test_request_schema_requires_non_empty_destination():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((SQUAD / "contracts" / "approval-request.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["destination"]["minLength"] == 1
    request = copy.deepcopy(BASE_REQUEST)
    request["destination"] = ""
    assert list(jsonschema.Draft202012Validator(schema).iter_errors(request))


def test_round_folder_flow_with_payload_json_beside_the_request(workspace, capsys):
    """E8: o payload.json da rodada (= request.payload) é o que o preflight compara e a execução usa."""
    path = _decision_file(workspace, capsys)
    payload_file = workspace["req_path"].parent / "payload.json"
    payload_file.write_text(json.dumps(workspace["request"]["payload"], ensure_ascii=False, sort_keys=True,
                                       separators=(",", ":")), encoding="utf-8", newline="\n")
    extra = ["--for-execution", "--payload", str(payload_file)]
    code, out = _verify(workspace, path, capsys=capsys, extra=extra)
    assert code == 0 and out["ok"] is True
    tampered = json.loads(payload_file.read_text(encoding="utf-8"))
    tampered["headline"] += " (alterado depois)"
    payload_file.write_text(json.dumps(tampered, ensure_ascii=False), encoding="utf-8", newline="\n")
    code, out = _verify(workspace, path, capsys=capsys, extra=extra)
    assert code == 1 and _failed(out) == ["hash_do_conteudo_a_executar"]


# ---------------------------------------------- modo de teste para --now e --config (E1)

def test_now_and_config_are_refused_outside_test_mode(workspace, monkeypatch, capsys):
    path = _decision_file(workspace, capsys)
    monkeypatch.delenv(tools.TEST_MODE_ENV)
    base = ["verify", "--request", str(workspace["req_path"]), "--decision", str(path)]
    assert tools.main(base + ["--now", NOW]) == 2
    assert tools.main(base + ["--config", str(workspace["config"])]) == 2
    assert tools.main(base + ["--now", NOW, "--config", str(workspace["config"])]) == 2
    err = capsys.readouterr().err
    assert tools.TEST_MODE_ENV in err
    # valor diferente de "1" também recusa
    monkeypatch.setenv(tools.TEST_MODE_ENV, "0")
    assert tools.main(base + ["--now", NOW]) == 2
    monkeypatch.setenv(tools.TEST_MODE_ENV, "true")
    assert tools.main(base + ["--now", NOW]) == 2


def test_decide_refuses_now_and_config_outside_test_mode(workspace, monkeypatch):
    monkeypatch.delenv(tools.TEST_MODE_ENV)
    assert _decide(workspace) == 2
    assert not (workspace["req_path"].parent / "approval-decision.json").exists()


def test_verify_without_flags_runs_outside_test_mode(workspace, monkeypatch, capsys):
    path = _decision_file(workspace, capsys)
    monkeypatch.delenv(tools.TEST_MODE_ENV)
    code = tools.main(["verify", "--request", str(workspace["req_path"]), "--decision", str(path)])
    out = json.loads(capsys.readouterr().out)
    # roda com o relógio e o config.yaml reais do squad: não é recusa (exit 2); a decisão de teste não passa
    assert code == 1 and out["ok"] is False
    assert "reviewer_em_approvers" in _failed(out)


def test_cli_process_refuses_now_without_test_mode(workspace):
    env = {k: v for k, v in os.environ.items() if k != tools.TEST_MODE_ENV}
    proc = subprocess.run(
        [sys.executable, "-I", str(TOOLS_PATH), "verify", "--request", str(workspace["req_path"]),
         "--decision", str(workspace["req_path"]), "--now", NOW],
        capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
    assert proc.returncode == 2
    assert tools.TEST_MODE_ENV in proc.stderr


def test_cli_process_hash_matches_function(workspace):
    env = {k: v for k, v in os.environ.items() if k != tools.TEST_MODE_ENV}
    proc = subprocess.run([sys.executable, "-I", str(TOOLS_PATH), "hash", str(workspace["req_path"])],
                          capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
    assert proc.returncode == 0
    assert proc.stdout.strip() == workspace["request"]["payload_sha256"]


# ------------------------------------------------------------------ utilidades

def test_parse_iso_handles_z_offset_and_naive():
    assert tools.parse_iso("2026-11-10T12:00:00Z") == tools.parse_iso("2026-11-10T09:00:00-03:00")
    assert tools.parse_iso("2026-11-10T12:00:00").utcoffset() == timedelta(0)


def test_minimal_approvers_parser_matches_yaml_reader():
    parsed = tools._minimal_approvers(CONFIG_TEXT)
    assert parsed == {"default": [], BUSINESS: [REVIEWER]}


def test_real_config_is_found_by_script_position():
    assert tools.DEFAULT_CONFIG == SQUAD / "config.yaml"
    assert isinstance(tools.load_approvers(tools.DEFAULT_CONFIG), dict)


def test_fixture_pair_matches_the_tool_hash():
    request = json.loads((SQUAD / "fixtures" / "approval-request.valid.json").read_text(encoding="utf-8"))
    decision = json.loads((SQUAD / "fixtures" / "approval-decision.valid.json").read_text(encoding="utf-8"))
    assert request["payload_sha256"] == decision["payload_sha256"] == tools.request_payload_hash(request)


def test_tool_source_has_no_machine_paths():
    validator = _load("validate_copy_squad_for_scan", VALIDATOR_PATH)
    assert validator.find_forbidden(TOOLS_PATH.read_text(encoding="utf-8")) == []
    assert validator.find_forbidden(Path(__file__).read_text(encoding="utf-8")) == []
