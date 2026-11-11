#!/usr/bin/env python3
"""Validador determinístico do copy-squad.

Verifica estrutura, config, agentes, tasks, workflows, contratos, skills,
wrappers e independência/portabilidade, sem rede e sem LLM.

Uso:
    python squads/copy-squad/scripts/validate_copy_squad.py [--json] [--repo RAIZ]

Dependências (scripts/requirements.txt): Python 3, PyYAML e jsonschema (>= 4.18).
A ausência do jsonschema é ERROR (a validação de contratos e fixtures é
obrigatória); use --allow-missing-jsonschema apenas para um diagnóstico parcial,
que vira WARN.

O validador também se varre: linhas com o comentário de marcação
"# forbidden-pattern-def" são as únicas ignoradas na busca de padrões proibidos.

Exit code: 0 sem ERROR (WARN não reprova); 1 com pelo menos um ERROR.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import functools
import hashlib
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.stderr.write("PyYAML é obrigatório para este validador.\n")
    raise SystemExit(2)

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    jsonschema = None
    Draft202012Validator = None

SQUAD_NAME = "copy-squad"
IGNORE_MARKER = "# forbidden-pattern-def"
DECISION_FIXTURE_PAIRS = [
    ("fixtures/approval-request.valid.json", "fixtures/approval-decision.valid.json"),
    ("templates/json/approval-request.example.json", "templates/json/approval-decision.example.json"),
]
BASH_AGENTS = {"copy-chief", "copy-publisher", "cro-analyst", "knowledge-curator"}
WEB_AGENTS = {"research-analyst", "compliance-checker"}

REQUIRED_DIRS = [
    "agents", "tasks", "workflows", "templates", "checklists", "data",
    "contracts", "fixtures", "knowledge", "docs", "scripts",
]
REQUIRED_FILES = ["config.yaml", "context.yaml", "README.md", "agent-registry.yaml"]
WORKSPACE_LEVELS = {"none", "read_only", "controlled_runtime_consumer", "workspace_first"}
TASK_KEYS = [
    "task", "responsavel", "execution_type", "atomic_layer",
    "Entrada", "Saida", "action_items", "acceptance_criteria",
]
SKILL_FM_KEYS = [
    "name", "description", "version", "owner_squad", "megabrain_tier",
    "context", "agent", "user-invocable",
]
HUMAN_GATES = {"G1", "G2", "G3", "G4", "G5"}
SKILL_BODY_MARKERS = ["> **Auto-Trigger:**", "> **Keywords:**", "> **Prioridade:**", "> **Tools:**"]

# Padrões proibidos montados por concatenação para o validador não se autodenunciar.
FORBIDDEN_PATTERNS = [
    "squads/" + "copy/",
    "Mega" + "brain-main",
    "B" + ":/",
    "B" + ":\\",
    "C" + ":\\Users",
    "/" + "Users/",
    "/" + "home/",
    "file" + "://",
    "{" + "{",
    "bil" + "hon",  # comparado sem diferenciar maiúsculas
    "AI" + "OX",    # palavra inteira, sem diferenciar maiúsculas
    "Str" + "ata",  # palavra inteira, sem diferenciar maiúsculas
]
CASE_INSENSITIVE = {"bil" + "hon"}
# Comparados como palavra inteira e sem diferenciar maiúsculas.
WORD_INSENSITIVE = {"AI" + "OX", "Str" + "ata"}
# Qualquer letra de unidade de disco seguida de separador de caminho; não casa "http" + "://".
DRIVE_LETTER_RE = re.compile("(?<![A-Za-z0-9])[A-Za-z]:[" + chr(92) + chr(92) + "/]")
# Segredos e credenciais com formato conhecido.
SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|eyJ[A-Za-z0-9_-]{20,}\.)"
)
# Padrões de unidade de disco só valem quando não precedidos por letra (evita "Tab:/").
BOUNDARY_PATTERNS = {"B" + ":/", "B" + ":\\", "C" + ":\\Users"}


class Report:
    def __init__(self) -> None:
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def error(self, check: str, message: str) -> None:
        self.errors.append({"severity": "ERROR", "check": check, "message": message})

    def warn(self, check: str, message: str) -> None:
        self.warnings.append({"severity": "WARN", "check": check, "message": message})

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
        }


# ---------------------------------------------------------------- utilidades

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


_YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
_YAML_CACHE: dict = {}


def yaml_load(text: str):
    """yaml.safe_load com libyaml (quando existe) e memória por texto: o mesmo arquivo é lido
    em várias checagens e, em testes, quase nada muda entre execuções. O resultado é somente
    leitura; erros de YAML não são memorizados."""
    if text in _YAML_CACHE:
        return _YAML_CACHE[text]
    data = yaml.load(text, Loader=_YAML_LOADER)  # noqa: S506 (SafeLoader)
    if len(_YAML_CACHE) > 2000:
        _YAML_CACHE.clear()
    _YAML_CACHE[text] = data
    return data


def load_yaml_file(path: Path):
    return yaml_load(read_text(path))


def split_frontmatter(text: str):
    """Retorna (dict|None, corpo). None se ausente ou inválido."""
    text = text.lstrip("﻿")
    if not text.startswith("---"):
        return None, text
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    if not m:
        return None, text
    try:
        data = yaml_load(m.group(1))
    except yaml.YAMLError:
        return None, text[m.end():]
    if not isinstance(data, dict):
        return None, text[m.end():]
    return data, text[m.end():]


def first_yaml_block(text: str):
    m = re.search(r"```yaml[ \t]*\r?\n(.*?)\r?\n```", text, re.S)
    if not m:
        return None, "bloco cercado yaml não encontrado"
    try:
        return yaml_load(m.group(1)), None
    except yaml.YAMLError as exc:
        return None, f"YAML inválido: {str(exc).splitlines()[0]}"


def count_lines(text: str) -> int:
    return len(text.splitlines())


def as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def resolve_repo(repo_arg: str | None) -> Path:
    if repo_arg:
        return Path(repo_arg).resolve()
    # squads/copy-squad/scripts/<este arquivo> -> raiz do repo 3 níveis acima da pasta scripts
    return Path(__file__).resolve().parents[3]


class Ctx:
    def __init__(self, repo: Path) -> None:
        self.repo = repo
        self.squad = repo / "squads" / SQUAD_NAME
        self.config: dict = {}
        self.agent_ids: list[str] = []
        self.task_ids: list[str] = []
        self.skills: list[str] = []
        self.quality_gate_ids: set[str] = set()
        self.allow_missing_jsonschema = False

    def rel(self, path: Path) -> str:
        try:
            return path.relative_to(self.repo).as_posix()
        except ValueError:
            return path.as_posix()


# ----------------------------------------------------------------- checagens

def check_structure(ctx: Ctx, rep: Report) -> None:
    if not ctx.squad.is_dir():
        rep.error("structure", f"pasta do squad ausente: squads/{SQUAD_NAME}")
        return
    for d in REQUIRED_DIRS:
        if not (ctx.squad / d).is_dir():
            rep.error("structure", f"diretório obrigatório ausente: {d}/")
    for f in REQUIRED_FILES:
        if not (ctx.squad / f).is_file():
            rep.error("structure", f"arquivo obrigatório ausente: {f}")
    for p in ctx.squad.rglob("*"):
        if p.is_file() and p.name.lower() == "claude.md":
            rep.error("structure", f"CLAUDE.md proibido dentro do squad: {ctx.rel(p)}")


def _stems(directory: Path, pattern: str, suffix: str) -> set[str]:
    if not directory.is_dir():
        return set()
    return {p.name[: -len(suffix)] for p in directory.glob(pattern) if p.is_file()}


def check_config(ctx: Ctx, rep: Report) -> None:
    path = ctx.squad / "config.yaml"
    if not path.is_file():
        return
    try:
        cfg = load_yaml_file(path)
    except yaml.YAMLError as exc:
        rep.error("config", f"config.yaml com YAML inválido: {str(exc).splitlines()[0]}")
        return
    if not isinstance(cfg, dict):
        rep.error("config", "config.yaml não é um mapeamento")
        return
    ctx.config = cfg

    for key in ("name", "version", "entry_agent", "pack"):
        if not cfg.get(key):
            rep.error("config", f"campo obrigatório ausente: {key}")
    if cfg.get("name") and cfg["name"] != SQUAD_NAME:
        rep.error("config", f"name deve ser {SQUAD_NAME}, encontrado {cfg['name']}")
    meta = cfg.get("metadata") or {}
    if "score" not in meta:
        rep.error("config", "campo obrigatório ausente: metadata.score")
    elif not isinstance(meta["score"], (int, float)) or isinstance(meta["score"], bool):
        rep.error("config", "metadata.score deve ser numérico")
    level = (cfg.get("workspace_integration") or {}).get("level")
    if level not in WORKSPACE_LEVELS:
        rep.error("config", f"workspace_integration.level inválido: {level!r}")

    comps = cfg.get("components") or {}
    for key in ("agents", "tasks", "workflows", "checklists", "templates",
                "data", "knowledge", "contracts"):
        if key not in comps:
            rep.error("config", f"components.{key} ausente")

    ctx.agent_ids = list(comps.get("agents") or [])
    ctx.task_ids = list(comps.get("tasks") or [])
    ctx.skills = list(comps.get("skills") or [])

    s = ctx.squad
    data_stems = set()
    if (s / "data").is_dir():
        data_stems = {p.stem for p in (s / "data").iterdir() if p.is_file()}
    knowledge_stems = {x for x in _stems(s / "knowledge", "*.md", ".md") if x.upper() != "INDEX"}
    disk = {
        "agents": _stems(s / "agents", "*.md", ".md"),
        "tasks": _stems(s / "tasks", "*.md", ".md"),
        "workflows": _stems(s / "workflows", "*.yaml", ".yaml") | _stems(s / "workflows", "*.yml", ".yml"),
        "checklists": _stems(s / "checklists", "*.md", ".md"),
        "templates": _stems(s / "templates", "*-tmpl.md", ".md"),
        "data": data_stems,
        "knowledge": knowledge_stems,
        "contracts": _stems(s / "contracts", "*.schema.json", ".schema.json"),
    }
    for key, on_disk in disk.items():
        declared = set(comps.get(key) or [])
        for missing in sorted(declared - on_disk):
            rep.error("config", f"components.{key} lista '{missing}' sem arquivo no disco")
        for extra in sorted(on_disk - declared):
            rep.error("config", f"arquivo em disco '{extra}' ({key}) não listado em components.{key}")

    agents_decl = cfg.get("agents") or []
    ids_in_agents = []
    for entry in agents_decl:
        if not isinstance(entry, dict):
            rep.error("config", "item de agents[] não é mapeamento")
            continue
        ids_in_agents.append(entry.get("id"))
        f = entry.get("file")
        if not f or not (s / f).is_file():
            rep.error("config", f"agents[].file inexistente para {entry.get('id')}: {f}")
    if set(ids_in_agents) != set(ctx.agent_ids):
        rep.error("config", "agents[].id diverge de components.agents")
    entry_agent = cfg.get("entry_agent")
    if entry_agent and not (s / "agents" / f"{entry_agent}.md").is_file():
        rep.error("config", f"entry_agent sem arquivo: agents/{entry_agent}.md")

    qpath = s / "data" / "quality-gates.yaml"
    if qpath.is_file():
        ctx.quality_gate_ids = set(re.findall(r"QG-[A-Z0-9]+(?:-[A-Z0-9]+)*", read_text(qpath)))


def check_registry(ctx: Ctx, rep: Report) -> None:
    path = ctx.squad / "agent-registry.yaml"
    if not path.is_file():
        return
    try:
        reg = load_yaml_file(path) or {}
    except yaml.YAMLError as exc:
        rep.error("registry", f"agent-registry.yaml com YAML inválido: {str(exc).splitlines()[0]}")
        return
    if not isinstance(reg, dict):
        rep.error("registry", "agent-registry.yaml não é um mapeamento")
        return
    spec = reg.get("specialists")
    ids = set(spec) if isinstance(spec, dict) else {
        x.get("id") for x in as_list(spec) if isinstance(x, dict)}
    declared = set(ctx.agent_ids)
    if ids != declared:
        rep.error("registry", f"specialists diverge de components.agents: {sorted(str(x) for x in ids ^ declared)}")
    if reg.get("total_agents") != len(ctx.agent_ids):
        rep.error("registry", f"total_agents {reg.get('total_agents')!r} difere de len(components.agents) = {len(ctx.agent_ids)}")
    if reg.get("entry_agent") != ctx.config.get("entry_agent"):
        rep.error("registry", "entry_agent diverge do config.yaml")
    entries = [e for e in as_list(ctx.config.get("agents")) if isinstance(e, dict)]
    ai_count = sum(1 for e in entries if e.get("executor_type") == "Agent")
    if reg.get("ai_agents") != ai_count:
        rep.error("registry", f"ai_agents {reg.get('ai_agents')!r} difere dos agentes de IA do config.yaml ({ai_count})")
    if reg.get("human_roles") != len(entries) - ai_count:
        rep.error("registry", f"human_roles {reg.get('human_roles')!r} difere dos papéis humanos do config.yaml ({len(entries) - ai_count})")
    if isinstance(spec, dict):
        for key, item in spec.items():
            if isinstance(item, dict) and item.get("id") != key:
                rep.error("registry", f"specialists.{key}.id difere da chave: {item.get('id')!r}")


def check_syntax(ctx: Ctx, rep: Report) -> None:
    """Sintaxe de todo YAML e JSON do squad (data, context, registry, knowledge, templates)."""
    if not ctx.squad.is_dir():
        return
    for p in sorted(ctx.squad.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.suffix in (".yaml", ".yml"):
            try:
                yaml_load(read_text(p))
            except yaml.YAMLError as exc:
                rep.error("syntax", f"{ctx.rel(p)}: YAML inválido: {str(exc).splitlines()[0]}")
            except UnicodeDecodeError:
                rep.error("syntax", f"{ctx.rel(p)}: não é UTF-8")
        elif p.suffix == ".json":
            try:
                json.loads(read_text(p))
            except json.JSONDecodeError as exc:
                rep.error("syntax", f"{ctx.rel(p)}: JSON inválido ({exc.msg}, linha {exc.lineno})")
            except UnicodeDecodeError:
                rep.error("syntax", f"{ctx.rel(p)}: não é UTF-8")


def check_handoff_matrix(ctx: Ctx, rep: Report) -> None:
    path = ctx.squad / "data" / "handoff-matrix.yaml"
    if not path.is_file():
        return
    try:
        doc = load_yaml_file(path) or {}
    except yaml.YAMLError:
        return  # a sintaxe já é reportada em check_syntax
    known = set(ctx.agent_ids) | {"approval-owner"}
    names: list[str] = []
    for edge in as_list(doc.get("edges")):
        if isinstance(edge, dict):
            names += [str(edge.get("from")), str(edge.get("to"))]
    for agent, targets in (doc.get("handoff_to_by_agent") or {}).items():
        names.append(str(agent))
        names += [str(t) for t in as_list(targets)]
    for name in sorted(set(names)):
        if name not in known:
            rep.error("handoff-matrix", f"handoff-matrix.yaml cita agente inexistente: {name}")


# Início válido de uma referência: fora de outro caminho, ou logo após o prefixo do squad.
_B = r"(?:(?<![A-Za-z0-9_./-])|(?<=squads/copy-squad/))"
_REF_PATTERNS = [
    ("task", _B + r"tasks/([a-z0-9-]+)\.md", "tasks", ".md"),
    ("contrato", r"contracts/([a-z0-9-]+)\.schema\.json", "contracts", ".schema.json"),
    ("checklist", _B + r"checklists/([a-z0-9-]+)\.md", "checklists", ".md"),
    ("data", _B + r"data/([a-z0-9-]+)\.(?:yaml|md)", "data", None),
    ("template", _B + r"templates/([a-z0-9-]+-tmpl)\.md", "templates", ".md"),
    ("workflow", _B + r"workflows/(wf-[a-z0-9-]+)\.yaml", "workflows", ".yaml"),
    ("conhecimento", _B + r"knowledge/([a-z0-9-]+)\.md", "knowledge", ".md"),
]


@functools.lru_cache(maxsize=8192)
def _ref_names(rx: str, text: str) -> tuple:
    return tuple(sorted(set(re.findall(rx, text))))


def check_dangling_refs(ctx: Ctx, rep: Report) -> None:
    """Referências cruzadas em texto livre a tasks, contratos, checklists e data do squad."""
    for path in iter_scan_files(ctx):
        if "__pycache__" in path.parts or path.suffix not in (".md", ".yaml", ".yml", ".json"):
            continue
        try:
            text = read_text(path)
        except (UnicodeDecodeError, OSError):
            continue
        for kind, rx, d, ext in _REF_PATTERNS:
            for name in _ref_names(rx, text):
                folder = ctx.squad / d
                if ext is None:
                    ok = any((folder / f"{name}{e}").is_file() for e in (".yaml", ".md"))
                else:
                    ok = (folder / f"{name}{ext}").is_file()
                if not ok:
                    rep.error("refs", f"{ctx.rel(path)}: {kind} inexistente: {name}")
        for name in _ref_names(r"contract:([a-z0-9-]+)", text):
            if not (ctx.squad / "contracts" / f"{name}.schema.json").is_file():
                rep.error("refs", f"{ctx.rel(path)}: contract:{name} inexistente")


_DRAFT_CHECKLISTS = [
    "conversion-copy-checklist", "email-crm-checklist", "content-quality-checklist",
    "video-script-checklist", "ux-copy-checklist",
]


def _checklist_executor(path: Path):
    text = read_text(path)
    block, _err = first_yaml_block(text)
    if isinstance(block, dict) and block.get("executor") is not None:
        return str(block["executor"]).lstrip("@")
    m = re.search(r"^executor:\s*([A-Za-z0-9_-]+)", text, re.M)
    return m.group(1) if m else None


def _check_gate_checklists(ctx: Ctx, rep: Report) -> None:
    """executor no metadata do checklist de cada gate == executor do gate (D7)."""
    for g in _gate_defs(ctx):
        expected = str(g.get("executor", "")).lstrip("@")
        rels = []
        if isinstance(g.get("checklist"), str):
            rels.append(g["checklist"])
        if g["id"] == "QG-DRAFT":
            rels += [f"checklists/{n}.md" for n in _DRAFT_CHECKLISTS]
        for rel in dict.fromkeys(rels):
            cpath = ctx.squad / rel
            if not cpath.is_file():
                rep.error("checklists", f"{g['id']}: checklist inexistente: {rel}")
                continue
            got = _checklist_executor(cpath)
            if got != expected:
                rep.error("checklists", f"{rel}: executor '{got}' difere do executor de {g['id']} ('{expected}')")


def check_checklists(ctx: Ctx, rep: Report) -> None:
    gates = ctx.config.get("quality_gates") or {}
    cdir = ctx.squad / "checklists"
    min_lines = int(gates.get("checklist_min_lines", 50))
    if cdir.is_dir():
        for path in sorted(cdir.glob("*.md")):
            n = count_lines(read_text(path))
            if n < min_lines:
                rep.error("checklists", f"checklists/{path.name}: {n} linhas (mínimo {min_lines})")
    _check_gate_checklists(ctx, rep)
    if gates.get("knowledge_required"):
        kdir = ctx.squad / "knowledge"
        has_index = any((kdir / f"INDEX{e}").is_file() for e in (".yaml", ".yml", ".md"))
        if not has_index:
            rep.error("knowledge", "knowledge_required: knowledge/INDEX.yaml (ou INDEX.md) ausente")
        topics = [p for p in kdir.glob("*.md") if p.stem.upper() != "INDEX"] if kdir.is_dir() else []
        if not topics:
            rep.error("knowledge", "knowledge_required: nenhum arquivo de conhecimento além do INDEX")
    if gates.get("readme_required") and not (ctx.squad / "README.md").is_file():
        rep.error("structure", "readme_required: README.md ausente")


def _path_exists(ctx: Ctx, ref: str) -> bool:
    return (ctx.squad / ref).exists() or (ctx.repo / ref).exists()


_DEP_EXT = {
    "tasks": [".md"], "templates": ["-tmpl.md", ".md"], "checklists": [".md"],
    "data": [".yaml", ".yml", ".md", ".json"], "contracts": [".schema.json", ".json"],
    "knowledge": [".md", ".yaml"], "workflows": [".yaml", ".yml"], "agents": [".md"],
}


def _dep_resolves(ctx: Ctx, kind: str, ref: str) -> bool:
    if "/" in ref or ref.endswith((".md", ".yaml", ".yml", ".json")):
        return _path_exists(ctx, ref)
    for ext in _DEP_EXT.get(kind, [".md"]):
        if (ctx.squad / kind / f"{ref}{ext}").exists():
            return True
    return False


def check_agents(ctx: Ctx, rep: Report) -> None:
    min_lines = int((ctx.config.get("quality_gates") or {}).get("agent_min_lines", 300))
    adir = ctx.squad / "agents"
    if not adir.is_dir():
        return
    existing = {p.stem for p in adir.glob("*.md")}
    for path in sorted(adir.glob("*.md")):
        aid = path.stem
        label = f"agents/{path.name}"
        text = read_text(path)
        fm, _ = split_frontmatter(text)
        if fm is None:
            rep.error("agents", f"{label}: frontmatter YAML ausente ou inválido")
            fm = {}
        elif fm.get("megabrain_type") != "Agent":
            rep.error("agents", f"{label}: megabrain_type deve ser Agent")
        if "ACTIVATION-NOTICE" not in text:
            rep.error("agents", f"{label}: ACTIVATION-NOTICE ausente")
        n = count_lines(text)
        if n < min_lines:
            rep.error("agents", f"{label}: {n} linhas (mínimo {min_lines})")
        block, err = first_yaml_block(text)
        if err:
            rep.error("agents", f"{label}: {err}")
            continue
        if not isinstance(block, dict):
            rep.error("agents", f"{label}: bloco yaml não é mapeamento")
            continue
        agent = block.get("agent") or {}
        if agent.get("id") != aid:
            rep.error("agents", f"{label}: agent.id {agent.get('id')!r} difere do arquivo {aid!r}")
        cmds = [str(c) for c in as_list(block.get("commands"))]
        for needed in ("*help", "*exit"):
            if not any(c.strip().startswith(needed) for c in cmds):
                rep.error("agents", f"{label}: commands sem {needed}")
        for tgt in as_list(fm.get("handoff_to")):
            if tgt not in existing:
                rep.error("agents", f"{label}: handoff_to aponta para agente inexistente '{tgt}'")
        loader = block.get("command_loader") or {}
        if isinstance(loader, dict):
            for cmd, spec in loader.items():
                for ref in as_list((spec or {}).get("requires")):
                    if isinstance(ref, str) and "{" not in ref and not _path_exists(ctx, ref):
                        rep.error("agents", f"{label}: command_loader[{cmd}].requires inexistente: {ref}")
        deps = block.get("dependencies") or {}
        if isinstance(deps, dict):
            for kind, refs in deps.items():
                for ref in as_list(refs):
                    if not isinstance(ref, str) or "{" in ref:
                        continue
                    if not _dep_resolves(ctx, kind, ref):
                        # tasks, contracts, checklists, templates, data etc. são sempre
                        # arquivos do squad: não resolver é ERROR; só tipos desconhecidos viram WARN.
                        explicit = "/" in ref or ref.endswith((".md", ".yaml", ".yml", ".json"))
                        (rep.error if (explicit or kind in _DEP_EXT) else rep.warn)(
                            "agents", f"{label}: dependencies.{kind} não resolve: {ref}")


def _cited_by(ctx: Ctx, tid: str, texts: list[str]) -> bool:
    needle = f"tasks/{tid}.md"
    return any(needle in t for t in texts)


def check_tasks(ctx: Ctx, rep: Report) -> None:
    min_lines = int((ctx.config.get("quality_gates") or {}).get("task_min_lines", 100))
    tdir = ctx.squad / "tasks"
    if not tdir.is_dir():
        return
    agents = {p.stem for p in (ctx.squad / "agents").glob("*.md")} if (ctx.squad / "agents").is_dir() else set()
    workflows = {p.stem for p in (ctx.squad / "workflows").glob("*.y*ml")} if (ctx.squad / "workflows").is_dir() else set()
    agent_texts = [read_text(p) for p in sorted((ctx.squad / "agents").glob("*.md"))] if agents else []
    wf_texts = [read_text(p) for p in sorted((ctx.squad / "workflows").glob("*.y*ml"))] if workflows else []
    skill_texts = []
    for sk in ctx.skills:
        sp = ctx.repo / ".claude" / "skills" / sk / "SKILL.md"
        if sp.is_file():
            skill_texts.append(read_text(sp))

    for path in sorted(tdir.glob("*.md")):
        tid = path.stem
        label = f"tasks/{path.name}"
        text = read_text(path)
        fm, _ = split_frontmatter(text)
        if fm is None:
            rep.error("tasks", f"{label}: frontmatter YAML ausente ou inválido")
            continue
        for key in TASK_KEYS:
            if key not in fm:
                rep.error("tasks", f"{label}: chave de frontmatter ausente: {key}")
        for key in ("task", "task_id", "name"):
            if key in fm and fm.get(key) != tid:
                rep.error("tasks", f"{label}: {key} {fm.get(key)!r} difere do nome do arquivo {tid!r}")
        qg = fm.get("quality_gate")
        if qg not in (None, "null", "") and ctx.quality_gate_ids and qg not in ctx.quality_gate_ids:
            rep.error("tasks", f"{label}: quality_gate {qg} inexistente em data/quality-gates.yaml")
        hg_raw = fm.get("human_gate")
        if hg_raw not in (None, "null", ""):
            for hg in as_list(hg_raw):
                if hg not in HUMAN_GATES:
                    rep.error("tasks", f"{label}: human_gate inválido: {hg!r}")
        for key in ("acceptance_criteria", "action_items"):
            if key in fm and not as_list(fm.get(key)):
                rep.error("tasks", f"{label}: {key} vazio")
        if fm.get("atomic_layer") != "Molecule":
            rep.error("tasks", f"{label}: atomic_layer deve ser Molecule")
        resp = str(fm.get("responsavel", "")).lstrip("@").strip()
        if resp not in agents:
            rep.error("tasks", f"{label}: responsavel '{resp}' não é agente existente")
        cl = fm.get("checklist")
        if cl and not (ctx.squad / str(cl)).is_file():
            rep.error("tasks", f"{label}: checklist inexistente: {cl}")
        skill = fm.get("skill")
        if skill not in (None, "null", "") and skill not in ctx.skills:
            rep.error("tasks", f"{label}: skill '{skill}' fora de components.skills")
        for wf in as_list(fm.get("workflows")):
            if wf not in workflows:
                rep.error("tasks", f"{label}: workflow inexistente: {wf}")
        n = count_lines(text)
        if n < min_lines:
            rep.error("tasks", f"{label}: {n} linhas (mínimo {min_lines})")
        resp_path = ctx.squad / "agents" / f"{resp}.md"
        by_agent = _cited_by(ctx, tid, [read_text(resp_path)]) if resp_path.is_file() else False
        by_flow = _cited_by(ctx, tid, wf_texts)
        by_skill = any(_cited_by(ctx, tid, [t]) or re.search(rf"(?<![A-Za-z0-9-]){re.escape(tid)}(?![A-Za-z0-9-])", t) for t in skill_texts)
        if not by_agent:
            rep.error("tasks", f"{label}: órfã, o agente responsável '{resp}' não cita tasks/{tid}.md")
        if not (by_flow or by_skill):
            rep.error("tasks", f"{label}: órfã, nenhum workflow ou skill a cita")


def _walk_agent_refs(node, found: set[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("agent", "agents", "owner"):
                for x in as_list(v):
                    if isinstance(x, str):
                        found.add(x.lstrip("@"))
            _walk_agent_refs(v, found)
    elif isinstance(node, list):
        for x in node:
            _walk_agent_refs(x, found)


def _collect_key(node, key: str, found: list) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key and isinstance(v, str):
                found.append(v)
            _collect_key(v, key, found)
    elif isinstance(node, list):
        for x in node:
            _collect_key(x, key, found)


def _task_responsaveis(ctx: Ctx) -> dict[str, str]:
    out: dict[str, str] = {}
    tdir = ctx.squad / "tasks"
    if not tdir.is_dir():
        return out
    for path in tdir.glob("*.md"):
        fm, _ = split_frontmatter(read_text(path))
        if fm:
            out[path.stem] = str(fm.get("responsavel", "")).lstrip("@").strip()
    return out


def _gate_defs(ctx: Ctx) -> list[dict]:
    qpath = ctx.squad / "data" / "quality-gates.yaml"
    if not qpath.is_file():
        return []
    try:
        doc = yaml_load(read_text(qpath)) or {}
    except yaml.YAMLError:
        return []  # a sintaxe já é reportada em check_syntax
    return [g for g in as_list(doc.get("quality_gates")) if isinstance(g, dict) and g.get("id")]


def _gate_executors(ctx: Ctx) -> dict[str, str]:
    return {str(g["id"]): str(g.get("executor", "")).lstrip("@") for g in _gate_defs(ctx)}


def _collect_gate_defs(node) -> list[dict]:
    found: list[dict] = []
    if isinstance(node, dict):
        if "gate_id" in node:
            found.append(node)
        for v in node.values():
            found.extend(_collect_gate_defs(v))
    elif isinstance(node, list):
        for x in node:
            found.extend(_collect_gate_defs(x))
    return found


def check_workflows(ctx: Ctx, rep: Report) -> None:
    min_lines = int((ctx.config.get("quality_gates") or {}).get("workflow_min_lines", 150))
    wdir = ctx.squad / "workflows"
    if not wdir.is_dir():
        return
    agents = {p.stem for p in (ctx.squad / "agents").glob("*.md")} if (ctx.squad / "agents").is_dir() else set()
    tasks = {p.stem for p in (ctx.squad / "tasks").glob("*.md")} if (ctx.squad / "tasks").is_dir() else set()
    responsaveis = _task_responsaveis(ctx)
    gate_seq: dict = {}
    gate_exec = _gate_executors(ctx)
    qpath = ctx.squad / "data" / "quality-gates.yaml"
    if qpath.is_file():
        try:
            gate_seq = (yaml_load(read_text(qpath)) or {}).get("gate_sequence_by_workflow") or {}
        except yaml.YAMLError:
            gate_seq = {}
    for path in sorted(wdir.glob("*.y*ml")):
        label = f"workflows/{path.name}"
        text = read_text(path)
        try:
            doc = yaml_load(text)
        except yaml.YAMLError as exc:
            rep.error("workflows", f"{label}: YAML inválido: {str(exc).splitlines()[0]}")
            continue
        if not isinstance(doc, dict):
            rep.error("workflows", f"{label}: raiz não é mapeamento")
            continue
        sm = doc.get("state_machine")
        if not isinstance(sm, dict) or not sm.get("states") or not sm.get("transitions"):
            rep.error("workflows", f"{label}: state_machine com states e transitions ausente")
        else:
            states = set(as_list(sm.get("states")))
            for tr in as_list(sm.get("transitions")):
                if not isinstance(tr, dict):
                    continue
                for k in ("from", "to"):
                    for st in as_list(tr.get(k)):
                        if st not in states and st != "*":
                            rep.error("workflows", f"{label}: transição {k}={st!r} fora de states")
            if sm.get("initial") not in states:
                rep.error("workflows", f"{label}: state_machine.initial fora de states: {sm.get('initial')!r}")
            for st in as_list(sm.get("terminal_states")):
                if st not in states:
                    rep.error("workflows", f"{label}: terminal_state {st!r} fora de states")
        phases = doc.get("phases")
        if not isinstance(phases, list) or not phases:
            rep.error("workflows", f"{label}: phases ausente")
        else:
            for ph in phases:
                if not isinstance(ph, dict) or not ph.get("checkpoint"):
                    rep.error("workflows", f"{label}: fase sem checkpoint: {(ph or {}).get('id') if isinstance(ph, dict) else ph}")
        for tid in sorted(set(re.findall(r"tasks/([a-z0-9-]+)\.md", text))):
            if tid not in tasks:
                rep.error("workflows", f"{label}: cita task inexistente tasks/{tid}.md")
        if isinstance(phases, list):
            for ph in phases:
                if not isinstance(ph, dict):
                    continue
                for tk in as_list(ph.get("tasks")):
                    if not isinstance(tk, dict) or not tk.get("task") or not tk.get("agent"):
                        continue
                    tname = re.sub(r"^.*/|\.md$", "", str(tk["task"]))
                    resp = responsaveis.get(tname)
                    ag = str(tk["agent"]).lstrip("@")
                    if resp and ag != resp:
                        rep.error("workflows", f"{label}: fase {ph.get('id')}: task {tname} tem responsavel '{resp}', mas a fase usa agent '{ag}'")
        gate_ids: list[str] = []
        _collect_key(doc, "gate_id", gate_ids)
        expected = gate_seq.get(path.stem)
        if expected is None:
            rep.error("workflows", f"{label}: ausente em gate_sequence_by_workflow de data/quality-gates.yaml")
        elif set(gate_ids) != set(expected):
            rep.error("workflows", f"{label}: gates {sorted(set(gate_ids))} divergem de gate_sequence_by_workflow {sorted(expected)}")
        for gdef in _collect_gate_defs(doc):
            gid, gex = gdef.get("gate_id"), gdef.get("executor")
            if gid in gate_exec and gex is not None and str(gex).lstrip("@") != gate_exec[gid]:
                rep.error("workflows", f"{label}: executor de {gid} é '{gex}', mas data/quality-gates.yaml define '{gate_exec[gid]}'")
        refs: set[str] = set()
        _walk_agent_refs(phases, refs)
        for a in sorted(refs):
            if a not in agents:
                rep.error("workflows", f"{label}: cita agente inexistente '{a}'")
        for qg in sorted(set(re.findall(r"QG-[A-Z0-9]+(?:-[A-Z0-9]+)*", text))):
            if qg not in ctx.quality_gate_ids:
                rep.error("workflows", f"{label}: {qg} ausente em data/quality-gates.yaml")
        n = count_lines(text)
        if n < min_lines:
            rep.error("workflows", f"{label}: {n} linhas (mínimo {min_lines})")


def _json_load(path: Path):
    return json.loads(read_text(path))


def _format_checker():
    """FORMAT_CHECKER padrão mais verificação própria de date-time (sem libs opcionais)."""
    fc = jsonschema.FormatChecker()
    for name, fn in Draft202012Validator.FORMAT_CHECKER.checkers.items():
        fc.checkers[name] = fn

    @fc.checks("date", raises=ValueError)
    def _date(value):
        if isinstance(value, str):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError("date fora do formato AAAA-MM-DD")
            date.fromisoformat(value)
        return True

    @fc.checks("date-time", raises=ValueError)
    def _date_time(value):
        if isinstance(value, str):
            if not re.search(r"[Tt ]\d{2}:\d{2}", value):
                raise ValueError("date-time sem hora")
            datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))
        return True

    return fc


@functools.lru_cache(maxsize=512)
def _schema_problem(schema_text: str) -> str:
    """Mensagem de erro do metaschema, ou '' quando o schema é válido (memorizado por texto)."""
    try:
        Draft202012Validator.check_schema(json.loads(schema_text))
    except jsonschema.SchemaError as exc:
        return exc.message
    return ""


@functools.lru_cache(maxsize=1024)
def _instance_problems(schema_text: str, inst_text: str) -> tuple:
    """[(local, mensagem)] dos primeiros erros de validação da instância (memorizado por par de textos)."""
    validator = Draft202012Validator(json.loads(schema_text), format_checker=_format_checker())
    errors = sorted(validator.iter_errors(json.loads(inst_text)), key=lambda e: list(e.absolute_path))[:5]
    return tuple(("/".join(str(x) for x in e.absolute_path) or "(raiz)", e.message[:160]) for e in errors)


def check_contracts(ctx: Ctx, rep: Report) -> None:
    names = list((ctx.config.get("components") or {}).get("contracts") or [])
    if jsonschema is None:
        (rep.warn if ctx.allow_missing_jsonschema else rep.error)(
            "contracts",
            "jsonschema ausente: instale jsonschema>=4 (validação de contratos e fixtures é obrigatória; "
            "--allow-missing-jsonschema só para diagnóstico parcial)")
    for name in names:
        spath = ctx.squad / "contracts" / f"{name}.schema.json"
        label = f"contracts/{name}.schema.json"
        if not spath.is_file():
            rep.error("contracts", f"{label}: ausente")
            continue
        try:
            schema = _json_load(spath)
        except json.JSONDecodeError as exc:
            rep.error("contracts", f"{label}: JSON inválido ({exc.msg}, linha {exc.lineno})")
            continue
        sid = schema.get("$id", "") if isinstance(schema, dict) else ""
        if not str(sid).startswith("urn:megabrain:copy-squad:contract:"):
            rep.error("contracts", f"{label}: $id deve começar com urn:megabrain:copy-squad:contract: (atual {sid!r})")
        schema_text = read_text(spath)
        schema_ok = True
        if jsonschema is not None:
            bad = _schema_problem(schema_text)
            if bad:
                schema_ok = False
                rep.error("contracts", f"{label}: schema inválido: {bad}")
        for kind, rel in (("fixture", f"fixtures/{name}.valid.json"),
                          ("template", f"templates/json/{name}.example.json")):
            ipath = ctx.squad / rel
            if not ipath.is_file():
                rep.error("contracts", f"{rel}: ausente")
                continue
            inst_text = read_text(ipath)
            try:
                json.loads(inst_text)
            except json.JSONDecodeError as exc:
                rep.error("contracts", f"{rel}: JSON inválido ({exc.msg}, linha {exc.lineno})")
                continue
            if jsonschema is not None and schema_ok:
                for loc, message in _instance_problems(schema_text, inst_text):
                    rep.error("contracts", f"{rel}: não valida no schema em {loc}: {message}")


def canonical_payload_sha256(payload) -> str:
    """Hash D1: sha256 do JSON canônico do payload (mesmo método de scripts/approval_tools.py)."""
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def check_approval_fixtures(ctx: Ctx, rep: Report) -> None:
    """payload_sha256 do approval-request == hash D1 do payload; a decision repete o mesmo hash."""
    for req_rel, dec_rel in DECISION_FIXTURE_PAIRS:
        req_path, dec_path = ctx.squad / req_rel, ctx.squad / dec_rel
        req = dec = None
        try:
            if req_path.is_file():
                req = _json_load(req_path)
            if dec_path.is_file():
                dec = _json_load(dec_path)
        except json.JSONDecodeError:
            continue  # a sintaxe já é reportada em check_syntax
        if not isinstance(req, dict):
            continue
        expected = canonical_payload_sha256(req.get("payload"))
        if req.get("payload_sha256") != expected:
            rep.error("approval-fixtures", f"{req_rel}: payload_sha256 {req.get('payload_sha256')!r} difere do hash D1 recalculado {expected}")
        if isinstance(dec, dict) and dec.get("payload_sha256") != req.get("payload_sha256"):
            rep.error("approval-fixtures", f"{dec_rel}: payload_sha256 da decision difere do approval-request")
        if isinstance(dec, dict) and isinstance(req.get("meta"), dict) \
                and dec.get("approval_request_id") != req["meta"].get("artifact_id"):
            rep.error("approval-fixtures", f"{dec_rel}: approval_request_id difere do artifact_id do approval-request")


def _failed_checks(out) -> list[str]:
    return [c.get("name", "?") for c in (out or {}).get("checks", []) if not c.get("ok")]


def check_approval_verify(ctx: Ctx, rep: Report) -> None:
    """Executa `approval_tools.py verify --for-execution --payload` na fixture em modo teste (E1, E8).

    Reproduz o fluxo documentado: numa pasta de rodada temporária (`06-approval/<asset>/g4-r1/`) grava o
    `payload.json` (igual a `request.payload`), o pedido e a decisão, e roda o verify. O caminho feliz precisa
    dar ok=true; os casos negativos (bound_to divergente, approved_with_edits, expirado, hash alterado,
    payload.json divergente, business ou campanha da decisão trocados, destination/channel vazios,
    --now fora do modo teste) precisam falhar na checagem esperada."""
    req_rel, dec_rel = DECISION_FIXTURE_PAIRS[0]
    tools_path = ctx.squad / "scripts" / "approval_tools.py"
    if not (ctx.squad / req_rel).is_file() or not (ctx.squad / dec_rel).is_file() or not tools_path.is_file():
        return
    try:
        req0, dec0 = _json_load(ctx.squad / req_rel), _json_load(ctx.squad / dec_rel)
        spec = importlib.util.spec_from_file_location("_copy_squad_approval_tools_check", tools_path)
        tools = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tools)
        decided = tools.parse_iso(dec0["decided_at"])
        expires = tools.parse_iso(dec0["expires_at"])
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError, SyntaxError, ImportError) as exc:
        rep.error("approval-verify", f"não foi possível preparar o verify da fixture: {type(exc).__name__}: {exc}")
        return
    if not isinstance(req0, dict) or not isinstance(dec0, dict):
        return
    now_ok = (decided + timedelta(hours=1)).isoformat()
    now_expired = (expires + timedelta(seconds=1)).isoformat()

    business = str((req0.get("meta") or {}).get("business", ""))
    reviewer = dec0.get("reviewer")
    with tempfile.TemporaryDirectory() as tmp:
        tdir = Path(tmp)
        # pasta de rodada real: o payload.json mora ao lado do pedido e da decisão (E8)
        round_dir = tdir / "06-approval" / str(req0.get("asset_id", "asset")) / "g4-r1"
        round_dir.mkdir(parents=True)
        # E8: os aprovadores vêm do negócio do PEDIDO; "default" não inclui o reviewer de propósito
        cfg = tdir / "config.yaml"
        cfg.write_text("human_gates:\n  approvers:\n    default: [nao-e-o-revisor]\n    "
                       + json.dumps(business, ensure_ascii=False) + ": [" + json.dumps(reviewer, ensure_ascii=False)
                       + "]\n", encoding="utf-8", newline="\n")
        cfg_default_only = tdir / "config-default.yaml"
        cfg_default_only.write_text("human_gates:\n  approvers:\n    default: [" + json.dumps(reviewer, ensure_ascii=False)
                                    + "]\n    " + json.dumps(business, ensure_ascii=False) + ": [somente-o-dono]\n",
                                    encoding="utf-8", newline="\n")

        def run(request, decision, now, extra=None, test_mode=True, payload="request", config=None):
            rp, dp, pp = round_dir / "approval-request.json", round_dir / "approval-decision.json", round_dir / "payload.json"
            rp.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8", newline="\n")
            dp.write_text(json.dumps(decision, ensure_ascii=False), encoding="utf-8", newline="\n")
            body = req0.get("payload") if payload == "request" else payload
            pp.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8", newline="\n")
            argv = ["verify", "--request", str(rp), "--decision", str(dp), "--for-execution", "--payload", str(pp),
                    "--now", now, "--config", str(config or cfg)]
            if extra:
                argv += extra
            old = os.environ.get(tools.TEST_MODE_ENV)
            if test_mode:
                os.environ[tools.TEST_MODE_ENV] = "1"
            else:
                os.environ.pop(tools.TEST_MODE_ENV, None)
            out, err = io.StringIO(), io.StringIO()
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    code = tools.main(argv)
            finally:
                if old is None:
                    os.environ.pop(tools.TEST_MODE_ENV, None)
                else:
                    os.environ[tools.TEST_MODE_ENV] = old
            try:
                parsed = json.loads(out.getvalue())
            except json.JSONDecodeError:
                parsed = None
            return code, parsed

        code, out = run(req0, dec0, now_ok)
        if code != 0 or not (out or {}).get("ok"):
            rep.error("approval-verify",
                      f"verify --for-execution da fixture {req_rel} + {dec_rel} deveria dar ok=true em modo teste "
                      f"(exit {code}; checagens que falharam: {_failed_checks(out)})")

        def expect_fail(label: str, request, decision, now, expected_check: str, **kw):
            c, o = run(request, decision, now, **kw)
            if c == 0 or (o or {}).get("ok") or expected_check not in _failed_checks(o):
                rep.error("approval-verify",
                          f"caso negativo '{label}' deveria reprovar em '{expected_check}' "
                          f"(exit {c}; falhas: {_failed_checks(o)})")

        d = copy.deepcopy(dec0)
        d["bound_to"] = dict(d.get("bound_to") or {}, destination="destino diferente do pedido")
        expect_fail("bound_to divergente", req0, d, now_ok, "bound_to_igual_ao_pedido")

        d = copy.deepcopy(dec0)
        d.pop("bound_to", None)
        expect_fail("decisão sem bound_to", req0, d, now_ok, "bound_to_igual_ao_pedido")

        d = copy.deepcopy(dec0)
        d["decision"] = "approved_with_edits"
        d.setdefault("meta", {})["status"] = "needs_approval"
        expect_fail("approved_with_edits", req0, d, now_ok, "decision_approved")

        expect_fail("decisão expirada", req0, dec0, now_expired, "dentro_da_validade")

        r = copy.deepcopy(req0)
        r["payload"] = dict(r.get("payload") or {}, headline=str((r.get("payload") or {}).get("headline", "")) + " (alterado)")
        expect_fail("hash alterado (payload do pedido)", r, dec0, now_ok, "hash_request_igual_recalculado")

        d = copy.deepcopy(dec0)
        d["expires_at"] = (decided + timedelta(hours=96)).isoformat()
        expect_fail("expires_at maior que 72 h", req0, d, now_ok, "janela_de_72h")

        r = copy.deepcopy(req0)
        r["gate"] = "G1"
        expect_fail("gate diferente de G4 na execução", r, dec0, now_ok, "execucao_gate_g4")

        # E8: o conteúdo executado (payload.json) diverge do aprovado
        divergent = dict(req0.get("payload") or {})
        divergent["headline"] = str(divergent.get("headline", "")) + " (executado diferente do aprovado)"
        expect_fail("payload.json divergente do aprovado", req0, dec0, now_ok, "hash_do_conteudo_a_executar",
                    payload=divergent)

        # E8: business e campanha da decisão precisam ser os do pedido
        d = copy.deepcopy(dec0)
        d.setdefault("meta", {})["business"] = "outro-negocio"
        expect_fail("decision.meta.business trocado", req0, d, now_ok, "decision_business_igual_ao_pedido")
        expect_fail("aprovadores do negócio do pedido, não da decisão", req0, d, now_ok, "reviewer_em_approvers",
                    config=cfg_default_only)

        d = copy.deepcopy(dec0)
        d.setdefault("meta", {}).pop("business", None)
        expect_fail("decision.meta.business removido", req0, d, now_ok, "decision_business_igual_ao_pedido")

        d = copy.deepcopy(dec0)
        d.setdefault("meta", {})["campaign_id"] = "camp-outra-campanha"
        expect_fail("decision.meta.campaign_id trocado", req0, d, now_ok, "decision_campaign_igual_ao_pedido")

        r = copy.deepcopy(req0)
        d = copy.deepcopy(dec0)
        r.setdefault("meta", {})["artifact_type"] = "approval-decision"
        d.setdefault("meta", {})["artifact_type"] = "approval-request"
        expect_fail("meta.artifact_type trocado", r, d, now_ok, "request_artifact_type")

        # E8: destination, channel e bound_to completos em --for-execution
        r, d = copy.deepcopy(req0), copy.deepcopy(dec0)
        r["destination"] = ""
        d["bound_to"]["destination"] = ""
        expect_fail("destination vazio no pedido e na decisão", r, d, now_ok, "execucao_destination_channel_preenchidos")

        r, d = copy.deepcopy(req0), copy.deepcopy(dec0)
        r.pop("channel", None)
        d["bound_to"].pop("channel", None)
        expect_fail("channel ausente no pedido e na decisão", r, d, now_ok, "execucao_bound_to_completo")

        c, _o = run(req0, dec0, now_ok, test_mode=False)
        if c != 2:
            rep.error("approval-verify", f"--now e --config sem COPY_SQUAD_TEST_MODE=1 deveriam sair com exit 2 (exit {c})")


def check_skills(ctx: Ctx, rep: Report) -> None:
    registry: dict[str, str] = {}
    rpath = ctx.repo / ".claude" / "skills" / "skill-registry.yaml"
    if rpath.is_file():
        try:
            reg = load_yaml_file(rpath)
            for item in (reg or {}).get("skills", []) or []:
                if isinstance(item, dict) and item.get("name"):
                    registry[str(item["name"])] = str(item.get("version"))
        except yaml.YAMLError as exc:
            rep.error("skills", f"skill-registry.yaml inválido: {str(exc).splitlines()[0]}")
    else:
        rep.error("skills", ".claude/skills/skill-registry.yaml ausente")
    skills_dir = ctx.repo / ".claude" / "skills"
    if skills_dir.is_dir():
        on_disk = {p.name for p in skills_dir.glob("copy-*") if p.is_dir()}
        for extra in sorted(on_disk ^ set(ctx.skills)):
            rep.error("skills", f"copy-* em disco difere de components.skills: {extra}")
    for sk in ctx.skills:
        label = f".claude/skills/{sk}/SKILL.md"
        path = ctx.repo / ".claude" / "skills" / sk / "SKILL.md"
        if not path.is_file():
            rep.error("skills", f"{label}: ausente")
            continue
        text = read_text(path)
        fm, body = split_frontmatter(text)
        if fm is None:
            rep.error("skills", f"{label}: frontmatter ausente ou inválido")
            continue
        for key in SKILL_FM_KEYS:
            if key not in fm or fm[key] in (None, ""):
                rep.error("skills", f"{label}: frontmatter sem {key}")
        if fm.get("name") != sk:
            rep.error("skills", f"{label}: name {fm.get('name')!r} difere da pasta {sk!r}")
        if fm.get("owner_squad") != SQUAD_NAME:
            rep.error("skills", f"{label}: owner_squad deve ser {SQUAD_NAME}")
        if fm.get("context") not in ("conversation", "fork"):
            rep.error("skills", f"{label}: context deve ser conversation ou fork")
        n_lines = count_lines(text)
        if not 80 <= n_lines <= 160:
            rep.warn("skills", f"{label}: {n_lines} linhas (esperado entre 80 e 160)")
        head = "\n".join(body.splitlines()[:40])
        for marker in SKILL_BODY_MARKERS:
            if marker not in head:
                rep.error("skills", f"{label}: '{marker}' ausente nas primeiras 40 linhas do corpo")
        if not re.search(r"^#{1,6}\s*Quando\s+N[ÃA]O\s+Ativar", body, re.I | re.M):
            rep.error("skills", f"{label}: seção 'Quando NÃO Ativar' ausente")
        if sk not in registry:
            rep.error("skills", f"{sk}: não registrada em skill-registry.yaml")
        elif registry[sk] != str(fm.get("version")):
            rep.error("skills", f"{sk}: versão no registry ({registry[sk]}) difere do SKILL.md ({fm.get('version')})")


def check_wrappers(ctx: Ctx, rep: Report) -> None:
    for entry in ctx.config.get("agents") or []:
        if not isinstance(entry, dict):
            continue
        aid = entry.get("id")
        wpath = ctx.repo / ".claude" / "agents" / f"{SQUAD_NAME}--{aid}.md"
        label = f".claude/agents/{SQUAD_NAME}--{aid}.md"
        if entry.get("executor_type") == "Agent":
            if not wpath.is_file():
                rep.error("wrappers", f"{label}: ausente")
                continue
            fm, _ = split_frontmatter(read_text(wpath))
            if fm is None:
                rep.error("wrappers", f"{label}: frontmatter ausente ou inválido")
                continue
            expected = f"{SQUAD_NAME}--{aid}"
            if fm.get("name") != expected:
                rep.error("wrappers", f"{label}: name deve ser {expected}")
            if fm.get("agent") != expected:
                rep.error("wrappers", f"{label}: agent deve ser {expected}")
            if fm.get("context") not in ("fork", "conversation"):
                rep.error("wrappers", f"{label}: context deve ser fork ou conversation")
            if not str(fm.get("description") or "").strip():
                rep.error("wrappers", f"{label}: description vazia")
            tools_raw = fm.get("tools")
            tools = [str(t).strip() for t in (tools_raw if isinstance(tools_raw, list) else str(tools_raw or "").split(","))
                     if str(t).strip()]
            if "tools" not in fm or not tools:
                rep.error("wrappers", f"{label}: linha tools: ausente ou vazia (menor privilégio, D18)")
            for t in tools:
                if t.startswith("mcp__"):
                    rep.error("wrappers", f"{label}: ferramenta mcp__ proibida em subagent: {t}")
            if "Bash" in tools and aid not in BASH_AGENTS:
                rep.error("wrappers", f"{label}: Bash só para {sorted(BASH_AGENTS)} (D18)")
            if {"WebSearch", "WebFetch"} & set(tools) and aid not in WEB_AGENTS:
                rep.error("wrappers", f"{label}: WebSearch e WebFetch só para {sorted(WEB_AGENTS)} (D18)")
            if f"squads/{SQUAD_NAME}/agents/{aid}.md" not in read_text(wpath):
                rep.error("wrappers", f"{label}: corpo não referencia squads/{SQUAD_NAME}/agents/{aid}.md")
        elif wpath.exists():
            rep.error("wrappers", f"{label}: wrapper não permitido para executor {entry.get('executor_type')}")
    stray = ctx.repo / ".claude" / "agents" / f"{SQUAD_NAME}--approval-owner.md"
    if stray.exists():
        rep.error("wrappers", f"{ctx.rel(stray)}: approval-owner não pode ter wrapper")


def iter_scan_files(ctx: Ctx):
    roots = []
    if ctx.squad.is_dir():
        roots.append(ctx.squad)
    skills_dir = ctx.repo / ".claude" / "skills"
    if skills_dir.is_dir():
        roots.extend(sorted(p for p in skills_dir.glob("copy-*") if p.is_dir()))
    files = []
    for root in roots:
        files.extend(p for p in root.rglob("*") if p.is_file())
    agents_dir = ctx.repo / ".claude" / "agents"
    if agents_dir.is_dir():
        files.extend(p for p in agents_dir.glob(f"{SQUAD_NAME}--*") if p.is_file())
    return files


_WORD_RES = {pat: re.compile(r"\b" + re.escape(pat.lower()) + r"\b") for pat in WORD_INSENSITIVE}
_BOUNDARY_RES = {pat: re.compile(r"(?<![A-Za-z])" + re.escape(pat)) for pat in BOUNDARY_PATTERNS}


@functools.lru_cache(maxsize=4096)
def _find_forbidden(text: str) -> tuple:
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if IGNORE_MARKER in line:
            continue
        low = line.lower()
        for pat in FORBIDDEN_PATTERNS:
            if pat in WORD_INSENSITIVE:
                found = _WORD_RES[pat].search(low) is not None
            elif pat in CASE_INSENSITIVE:
                found = pat in low
            elif pat in BOUNDARY_PATTERNS:
                found = _BOUNDARY_RES[pat].search(line) is not None
            else:
                found = pat in line
            if found:
                hits.append((lineno, pat))
        if DRIVE_LETTER_RE.search(line):
            hits.append((lineno, "caminho com letra de unidade"))
        if SECRET_RE.search(line):
            hits.append((lineno, "possível segredo ou credencial"))
    return tuple(hits)


def find_forbidden(text: str) -> list[tuple[int, str]]:
    """Retorna [(linha, padrão)] das ocorrências proibidas no texto (resultado memorizado por texto)."""
    return list(_find_forbidden(text))


def scan_files_for_forbidden(files, rel, rep: Report, check: str = "independence") -> None:
    for path in files:
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".png", ".jpg", ".gif", ".pdf"):
            continue
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if b"\r\n" in raw:
            rep.error(check, f"{rel(path)}: CRLF proibido (usar quebras de linha LF)")
        for lineno, pat in find_forbidden(text):
            rep.error(check, f"{rel(path)}:{lineno}: padrão proibido '{pat}'")


# Revisões sempre versionadas (D14/E3) e pastas de rodada sempre em minúsculas (E3).
REVIEW_PATH_RE = re.compile(r"05-review/[^\s`\"'),;|<>]*")
REVIEW_NAME_RE = re.compile(r"^(edit-report|brand-review|compliance-review|localization)")
REVIEW_VERSION_RE = re.compile(r"-v(\{n\}|\d+)$")
ROUND_UPPER_RE = re.compile(r"(?<![A-Za-z0-9])(?:G[1-4]|SAMPLING)-r(?=\{|\d)")


def find_convention_violations(text: str) -> list[tuple[int, str]]:
    """[(linha, mensagem)] de caminhos 05-review sem -v{n} e de pastas de rodada em maiúsculas."""
    return list(_convention_violations(text))


@functools.lru_cache(maxsize=4096)
def _convention_violations(text: str) -> tuple:
    hits = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in REVIEW_PATH_RE.finditer(line):
            ref = m.group(0).rstrip(".:")
            name = ref.rsplit("/", 1)[-1]
            if name.endswith(".json") and REVIEW_NAME_RE.match(name) and not REVIEW_VERSION_RE.search(name[:-5]):
                hits.append((lineno, "caminho de revisão sem -v" + "{n}" + f": {ref}"))
        for m in ROUND_UPPER_RE.finditer(line):
            hits.append((lineno, f"pasta de rodada com gate em maiúsculas ('{m.group(0)}...'); use minúsculas, ex.: g4-r1"))
    return tuple(hits)


def check_conventions(ctx: Ctx, rep: Report) -> None:
    for path in iter_scan_files(ctx):
        if "__pycache__" in path.parts or path.suffix in (".pyc", ".png", ".jpg", ".gif", ".pdf"):
            continue
        try:
            text = read_text(path)
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, msg in find_convention_violations(text):
            rep.error("conventions", f"{ctx.rel(path)}:{lineno}: {msg}")


def check_independence(ctx: Ctx, rep: Report) -> None:
    scan_files_for_forbidden(iter_scan_files(ctx), ctx.rel, rep)


CHECKS = [
    check_structure, check_config, check_registry, check_syntax, check_handoff_matrix,
    check_checklists, check_agents, check_tasks, check_workflows, check_dangling_refs,
    check_contracts, check_approval_fixtures, check_approval_verify, check_skills, check_wrappers,
    check_conventions, check_independence,
]


def run_all(repo: Path, allow_missing_jsonschema: bool = False) -> Report:
    ctx = Ctx(repo)
    ctx.allow_missing_jsonschema = allow_missing_jsonschema
    rep = Report()
    for fn in CHECKS:
        try:
            fn(ctx, rep)
        except Exception as exc:  # falha de uma checagem não derruba as demais
            rep.error(fn.__name__.replace("check_", ""), f"exceção inesperada: {type(exc).__name__}: {exc}")
    return rep


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Valida o copy-squad de forma determinística.")
    parser.add_argument("--repo", help="raiz do repositório (padrão: deduzida deste arquivo)")
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    parser.add_argument("--allow-missing-jsonschema", "--allow-no-jsonschema", dest="allow_missing_jsonschema",
                        action="store_true",
                        help="aceita a ausência do pacote jsonschema (vira WARN); só para diagnóstico parcial")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    rep = run_all(resolve_repo(args.repo), allow_missing_jsonschema=args.allow_missing_jsonschema)
    if args.json:
        print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2))
    else:
        for item in rep.errors + rep.warnings:
            print(f"[{item['severity']}] {item['check']}: {item['message']}")
        status = "OK" if rep.ok else "FALHOU"
        print(f"\ncopy-squad: {status} — {len(rep.errors)} erro(s), {len(rep.warnings)} aviso(s)")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
