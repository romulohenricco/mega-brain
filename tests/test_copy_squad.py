"""Testes do copy-squad: roda o validador determinístico contra o repositório real."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO / "squads" / "copy-squad" / "scripts" / "validate_copy_squad.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_copy_squad", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


def test_validator_has_no_self_denunciation():
    # O validador se varre sem exceção (só linhas com a marcação são ignoradas).
    scripts = REPO / "squads" / "copy-squad" / "scripts"
    for path in sorted(scripts.glob("*.py")) + [Path(__file__), Path(__file__).with_name("test_copy_squad_approval_tools.py"),
                                      Path(__file__).with_name("test_copy_squad_guard.py")]:
        assert validator.find_forbidden(path.read_text(encoding="utf-8")) == [], path.name
    rep = validator.Report()
    validator.scan_files_for_forbidden(sorted(scripts.glob("*.py")), lambda p: p.name, rep)
    assert not rep.errors, rep.errors


def test_repo_has_zero_errors():
    rep = validator.run_all(REPO)
    messages = [f"{e['check']}: {e['message']}" for e in rep.errors]
    assert not messages, "\n".join(messages[:50])


def test_each_fixture_validates_against_its_schema():
    import jsonschema
    contracts = REPO / "squads" / "copy-squad" / "contracts"
    fixtures = REPO / "squads" / "copy-squad" / "fixtures"
    schemas = sorted(contracts.glob("*.schema.json"))
    if not schemas:
        pytest.skip("nenhum contrato encontrado ainda")
    failures = []
    for schema_path in schemas:
        name = schema_path.name[: -len(".schema.json")]
        fixture = fixtures / f"{name}.valid.json"
        if not fixture.is_file():
            failures.append(f"{name}: fixture ausente")
            continue
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        data = json.loads(fixture.read_text(encoding="utf-8"))
        v = jsonschema.Draft202012Validator(schema, format_checker=validator._format_checker())
        errs = list(v.iter_errors(data))
        if errs:
            failures.append(f"{name}: {errs[0].message[:120]}")
    assert not failures, "\n".join(failures)


def test_forbidden_pattern_detection_in_tmp_dir(tmp_path):
    squad = tmp_path / "squads" / "copy-squad"
    squad.mkdir(parents=True)
    forbidden_a = "squads/" + "copy/" + "agents/x.md"
    forbidden_b = "bil" + "hon"
    forbidden_c = "C" + ":\\Users\\alguem"
    forbidden_d = "{" + "{variavel}}"
    (squad / "sujo.md").write_text(
        f"ref {forbidden_a}\nmarca {forbidden_b.upper()}\npath {forbidden_c}\ntpl {forbidden_d}\n",
        encoding="utf-8", newline="\n",
    )
    (squad / "limpo.md").write_text("conteúdo limpo com squads/copy-squad/agents\n", encoding="utf-8", newline="\n")
    ctx = validator.Ctx(tmp_path)
    rep = validator.Report()
    validator.check_independence(ctx, rep)
    joined = "\n".join(e["message"] for e in rep.errors)
    assert "sujo.md:1" in joined
    assert "sujo.md:2" in joined
    assert "sujo.md:3" in joined
    assert "sujo.md:4" in joined
    assert "limpo.md" not in joined


def test_find_forbidden_ignores_clean_text():
    assert validator.find_forbidden("texto normal com .data/copy-squad/{business}/") == []


def test_structure_check_flags_missing_squad(tmp_path):
    ctx = validator.Ctx(tmp_path)
    rep = validator.Report()
    validator.check_structure(ctx, rep)
    assert rep.errors and not rep.ok


# ---------------------------------------------------------------- testes de mutação

def _build_base(root: Path) -> None:
    """Cópia mínima do repositório real (squad, skills, registry e wrappers), feita uma vez por sessão."""
    shutil.copytree(
        REPO / "squads" / "copy-squad",
        root / "squads" / "copy-squad",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    skills_dst = root / ".claude" / "skills"
    skills_dst.mkdir(parents=True)
    for d in (REPO / ".claude" / "skills").glob("copy-*"):
        if d.is_dir():
            shutil.copytree(d, skills_dst / d.name, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(REPO / ".claude" / "skills" / "skill-registry.yaml", skills_dst / "skill-registry.yaml")
    agents_dst = root / ".claude" / "agents"
    agents_dst.mkdir(parents=True)
    for f in (REPO / ".claude" / "agents").glob("copy-squad--*"):
        shutil.copy(f, agents_dst / f.name)


def _snapshot(root: Path):
    files = {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    dirs = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()}
    return files, dirs


def _restore(root: Path, snap) -> None:
    """Desfaz a mutação de um teste: só reescreve o que mudou (leitura de bytes, sem recopiar o disco de origem)."""
    files, dirs = snap
    for p in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and rel not in files:
            p.unlink()
        elif p.is_dir() and rel not in dirs:
            shutil.rmtree(p, ignore_errors=True)
    for rel in sorted(dirs):
        (root / rel).mkdir(parents=True, exist_ok=True)
    for rel, data in files.items():
        p = root / rel
        if not p.is_file() or p.read_bytes() != data:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)


@pytest.fixture(scope="session")
def _base_repo(tmp_path_factory):
    root = tmp_path_factory.mktemp("copy_squad_base")
    _build_base(root)
    return root, _snapshot(root)


@pytest.fixture
def repo_copy(_base_repo):
    """Cópia de trabalho feita uma vez por sessão; cada teste muta e, ao final, a mutação é desfeita."""
    root, snap = _base_repo
    _restore(root, snap)
    yield root
    _restore(root, snap)


def _squad(root: Path) -> Path:
    return root / "squads" / "copy-squad"


def _replace_in(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"trecho a mutar não encontrado em {path.name}: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def _m_handoff(root):
    _replace_in(_squad(root) / "agents" / "copy-chief.md", "handoff_to: [brief-master,", "handoff_to: [agente-inexistente, brief-master,")


def _m_wrapper(root):
    (root / ".claude" / "agents" / "copy-squad--copy-chief.md").unlink()


def _m_claude_md(root):
    (_squad(root) / "CLAUDE.md").write_text("proibido\n", encoding="utf-8")


def _m_quality_gate(root):
    _replace_in(_squad(root) / "workflows" / "wf-fast-variation.yaml", "gate_id: QG-INTAKE", "gate_id: QG-INEXISTENTE")
    path = _squad(root) / "workflows" / "wf-fast-variation.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\n# referencia QG-INEXISTENTE\n", encoding="utf-8", newline="\n")


def _m_skill_version(root):
    _replace_in(root / ".claude" / "skills" / "copy-hook-generator" / "SKILL.md", 'version: "1.0.0"', 'version: "9.9.9"')


def _m_workflow_task(root):
    path = _squad(root) / "workflows" / "wf-fast-variation.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\n# usa tasks/task-que-nao-existe.md\n", encoding="utf-8", newline="\n")


def _m_independence(root):
    path = _squad(root) / "README.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nref " + "C" + ":\\Users\\alguem\n", encoding="utf-8", newline="\n")


def _m_missing_dir(root):
    shutil.rmtree(_squad(root) / "checklists")


def _m_agent_id(root):
    _replace_in(_squad(root) / "agents" / "brief-master.md", "megabrain_type: Agent", "megabrain_type: Task")


def _m_contract(root):
    (_squad(root) / "contracts" / "approval-request.schema.json").write_text("{ nao e json", encoding="utf-8", newline="\n")


def _tools_line(root: Path, aid: str, value):
    path = root / ".claude" / "agents" / f"copy-squad--{aid}.md"
    text = re.sub(r"^tools:.*\n", "", path.read_text(encoding="utf-8"), flags=re.MULTILINE)
    if value is not None:
        text = text.replace("\nagent: ", f"\ntools: {value}\nagent: ", 1)
    path.write_text(text, encoding="utf-8", newline="\n")


def _set_gate_executor(path: Path, gate: str, new: str):
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(gate_id: " + re.escape(gate) + r"\n(?:[^\n]*\n){0,5}?\s*executor: )[^\n]+")
    assert pattern.search(text), f"bloco de {gate} sem executor em {path.name}"
    path.write_text(pattern.sub(lambda m: m.group(1) + new, text, count=1), encoding="utf-8", newline="\n")


def _m_gate_set(root):
    _replace_in(_squad(root) / "workflows" / "wf-fast-variation.yaml", "gate_id: QG-EDIT", "gate_id: QG-LEARNING")


def _m_wf_executor(root):
    _set_gate_executor(_squad(root) / "workflows" / "wf-fast-variation.yaml", "QG-BRAND", "copy-chief")


def _m_checklist_executor(root):
    _replace_in(_squad(root) / "checklists" / "intake-checklist.md", "executor: brief-master", "executor: copy-chief")


def _m_registry_total(root):
    _replace_in(_squad(root) / "agent-registry.yaml", "total_agents: 19", "total_agents: 18")


def _m_registry_ai(root):
    _replace_in(_squad(root) / "agent-registry.yaml", "ai_agents: 18", "ai_agents: 17")


def _m_syntax_yaml(root):
    path = _squad(root) / "data" / "risk-policy.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\nchave: [aberta\n", encoding="utf-8", newline="\n")


def _m_syntax_json(root):
    (_squad(root) / "templates" / "json" / "extra-quebrado.json").write_text("{ nao e json", encoding="utf-8", newline="\n")


def _m_task_name(root):
    _replace_in(_squad(root) / "tasks" / "intake-demand.md", "task: intake-demand", "task: outra-coisa")


def _m_task_quality_gate(root):
    _replace_in(_squad(root) / "tasks" / "audit-ux-copy.md", "quality_gate: QG-DRAFT", "quality_gate: QG-FANTASMA")


def _m_task_human_gate(root):
    _replace_in(_squad(root) / "tasks" / "approve-gate.md", "human_gate: [G1, G2, G3, G4]", "human_gate: [G1, G9]")


def _append(path: Path, extra: str):
    path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8", newline="\n")


def _m_forbidden_aiox(root):
    _append(_squad(root) / "README.md", "\nusa o framework " + "AI" + "OX como base\n")


def _m_forbidden_strata(root):
    _append(_squad(root) / "README.md", "\ndepende do " + "Str" + "ata do repositório\n")


def _m_forbidden_other_drive(root):
    _append(_squad(root) / "README.md", "\ncaminho " + "D" + ":\\dados\\x\n")


def _m_forbidden_crlf(root):
    path = _squad(root) / "README.md"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))


def _m_checklist_min_lines(root):
    path = _squad(root) / "checklists" / "intake-checklist.md"
    path.write_text("\n".join(path.read_text(encoding="utf-8").splitlines()[:20]) + "\n", encoding="utf-8", newline="\n")


def _m_extra_task_on_disk(root):
    (_squad(root) / "tasks" / "extra-task.md").write_text("---\ntask: extra-task\n---\n", encoding="utf-8")


def _m_ref_template(root):
    _append(_squad(root) / "README.md", "\nveja templates/inexistente-tmpl.md\n")


def _m_ref_workflow(root):
    _append(_squad(root) / "README.md", "\nveja workflows/wf-nao-existe.yaml\n")


def _m_ref_knowledge(root):
    _append(_squad(root) / "README.md", "\nveja knowledge/nao-existe.md\n")


def _m_ref_contract(root):
    _append(_squad(root) / "README.md", "\nveja contracts/nao-existe.schema.json\n")


def _m_ref_checklist(root):
    _append(_squad(root) / "README.md", "\nveja squads/copy-squad/checklists/nao-existe.md\n")


def _m_ref_data(root):
    _append(_squad(root) / "README.md", "\nveja data/nao-existe.yaml\n")


def _m_dependency(root):
    _replace_in(_squad(root) / "agents" / "copy-chief.md", "  tasks: [intake-demand,", "  tasks: [task-fantasma, intake-demand,")


def _m_fixture_hash(root):
    path = _squad(root) / "fixtures" / "approval-request.valid.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["payload"]["headline"] = data["payload"]["headline"] + " (alterado)"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _m_fixture_decision_hash(root):
    path = _squad(root) / "fixtures" / "approval-decision.valid.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["payload_sha256"] = "0" * 64
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _m_fixture_datetime(root):
    path = _squad(root) / "fixtures" / "approval-request.valid.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["meta"]["produced_at"] = "ontem"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _m_wrapper_no_tools(root):
    _tools_line(root, "copy-editor", None)


def _m_wrapper_mcp(root):
    _tools_line(root, "copy-editor", "Read, mcp__claude_ai_Gmail__create_draft")


def _m_wrapper_bash(root):
    _tools_line(root, "copy-editor", "Read, Bash")


def _m_wrapper_web(root):
    _tools_line(root, "copy-editor", "Read, WebSearch")


def _rewrite_json(path: Path, fn) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _m_review_unversioned(root):
    _append(_squad(root) / "README.md", "\nsalvo em 05-review/{asset_id}/brand-review.json\n")


def _m_review_unversioned_localization(root):
    _append(_squad(root) / "README.md", "\nsalvo em 05-review/{asset_id}/localization-en-US.json\n")


def _m_round_upper(root):
    _append(_squad(root) / "README.md", "\npasta 06-approval/_campaign/G1-r{n}/\n")


def _m_round_upper_sampling(root):
    _append(_squad(root) / "README.md", "\npasta 06-approval/x/SAMPLING-r1/\n")


def _m_verify_no_bound_to(root):
    _rewrite_json(_squad(root) / "fixtures" / "approval-decision.valid.json", lambda d: d.pop("bound_to", None))


def _m_verify_ttl(root):
    def fn(d):
        d["expires_at"] = "2099-01-01T00:00:00-03:00"
    _rewrite_json(_squad(root) / "fixtures" / "approval-decision.valid.json", fn)


def _m_verify_bound_diverges(root):
    def fn(d):
        d["bound_to"]["operation"] = "run_ads"
    _rewrite_json(_squad(root) / "fixtures" / "approval-decision.valid.json", fn)


def _m_verify_test_mode_open(root):
    _replace_in(_squad(root) / "scripts" / "approval_tools.py", 'and os.environ.get(TEST_MODE_ENV) != "1":', "and False:")


def _m_verify_ignores_bound(root):
    _replace_in(_squad(root) / "scripts" / "approval_tools.py", "bound.get(k) != request.get(k)", "False")


def _tools(root):
    return _squad(root) / "scripts" / "approval_tools.py"


def _m_verify_approvers_from_decision(root):
    _replace_in(_tools(root), 'approvers_for(approvers, rmeta.get("business"))', 'approvers_for(approvers, dmeta.get("business"))')


def _m_verify_skips_business_check(root):
    _replace_in(_tools(root), 'dmeta.get("business") == rmeta.get("business")', "True")


def _m_verify_skips_campaign_check(root):
    _replace_in(_tools(root), 'dmeta.get("campaign_id") == rmeta.get("campaign_id")', "True")


def _m_verify_ignores_payload_file(root):
    _replace_in(_tools(root), "if payload is not None:", "if False:")


def _m_verify_accepts_empty_destination(root):
    _replace_in(_tools(root), '_non_empty_str(request.get("destination")) and _non_empty_str(request.get("channel"))', "True")


def _m_verify_accepts_incomplete_bound_to(root):
    _replace_in(_tools(root), "all(_non_empty_str(bound_now.get(k)) for k in BOUND_FIELDS)", "True")


# (mutação, checagem esperada, trecho esperado na mensagem)
MUTATIONS = [
    # as 10 da revisão anterior
    (_m_handoff, "agents", "handoff_to"),
    (_m_wrapper, "wrappers", "ausente"),
    (_m_claude_md, "structure", "CLAUDE.md"),
    (_m_missing_dir, "structure", "checklists/"),
    (_m_quality_gate, "workflows", "QG-INEXISTENTE"),
    (_m_workflow_task, "workflows", "task-que-nao-existe"),
    (_m_skill_version, "skills", "versão"),
    (_m_independence, "independence", "padrão proibido"),
    (_m_agent_id, "agents", "megabrain_type"),
    (_m_contract, "contracts", "JSON inválido"),
    # mutações das novas checagens (ADR-001, grupo J)
    (_m_gate_set, "workflows", "divergem de gate_sequence_by_workflow"),
    (_m_wf_executor, "workflows", "executor de QG-BRAND"),
    (_m_checklist_executor, "checklists", "executor"),
    (_m_registry_total, "registry", "total_agents"),
    (_m_registry_ai, "registry", "ai_agents"),
    (_m_syntax_yaml, "syntax", "YAML inválido"),
    (_m_syntax_json, "syntax", "JSON inválido"),
    (_m_task_name, "tasks", "difere do nome do arquivo"),
    (_m_task_quality_gate, "tasks", "quality_gate"),
    (_m_task_human_gate, "tasks", "human_gate"),
    (_m_forbidden_aiox, "independence", "padrão proibido"),
    (_m_forbidden_strata, "independence", "padrão proibido"),
    (_m_forbidden_other_drive, "independence", "letra de unidade"),
    (_m_forbidden_crlf, "independence", "CRLF"),
    (_m_checklist_min_lines, "checklists", "mínimo"),
    (_m_extra_task_on_disk, "config", "extra-task"),
    (_m_ref_template, "refs", "template inexistente"),
    (_m_ref_workflow, "refs", "workflow inexistente"),
    (_m_ref_knowledge, "refs", "conhecimento inexistente"),
    (_m_ref_contract, "refs", "contrato inexistente"),
    (_m_ref_checklist, "refs", "checklist inexistente"),
    (_m_ref_data, "refs", "data inexistente"),
    (_m_dependency, "agents", "dependencies.tasks não resolve"),
    (_m_fixture_hash, "approval-fixtures", "hash D1"),
    (_m_fixture_decision_hash, "approval-fixtures", "decision difere"),
    (_m_fixture_datetime, "contracts", "date-time"),
    (_m_wrapper_no_tools, "wrappers", "tools:"),
    (_m_wrapper_mcp, "wrappers", "mcp__"),
    (_m_wrapper_bash, "wrappers", "Bash"),
    (_m_wrapper_web, "wrappers", "WebSearch"),
    # E1/E2 e convenções de caminho (rodada 3, grupo J)
    (_m_review_unversioned, "conventions", "sem -v"),
    (_m_review_unversioned_localization, "conventions", "sem -v"),
    (_m_round_upper, "conventions", "maiúsculas"),
    (_m_round_upper_sampling, "conventions", "maiúsculas"),
    (_m_verify_no_bound_to, "approval-verify", "ok=true"),
    (_m_verify_ttl, "approval-verify", "ok=true"),
    (_m_verify_bound_diverges, "approval-verify", "ok=true"),
    (_m_verify_test_mode_open, "approval-verify", "exit 2"),
    (_m_verify_ignores_bound, "approval-verify", "bound_to divergente"),
    # E8: business/campanha da decisão, payload.json da rodada, destination/channel e bound_to completos
    (_m_verify_approvers_from_decision, "approval-verify", "aprovadores do negócio do pedido"),
    (_m_verify_skips_business_check, "approval-verify", "decision.meta.business trocado"),
    (_m_verify_skips_campaign_check, "approval-verify", "decision.meta.campaign_id trocado"),
    (_m_verify_ignores_payload_file, "approval-verify", "payload.json divergente"),
    (_m_verify_accepts_empty_destination, "approval-verify", "destination vazio"),
    (_m_verify_accepts_incomplete_bound_to, "approval-verify", "channel ausente"),
]


def test_unmutated_copy_has_zero_errors(repo_copy):
    rep = validator.run_all(repo_copy)
    assert not rep.errors, "\n".join(f"{e['check']}: {e['message']}" for e in rep.errors[:20])


@pytest.mark.parametrize("mutate,check,needle", MUTATIONS, ids=[m[0].__name__[3:] for m in MUTATIONS])
def test_mutation_is_detected(repo_copy, mutate, check, needle):
    mutate(repo_copy)
    rep = validator.run_all(repo_copy)
    hits = [e for e in rep.errors if e["check"] == check and needle in e["message"]]
    assert hits, (
        f"mutação não detectada por '{check}' com '{needle}'; erros: "
        f"{[(e['check'], e['message'][:80]) for e in rep.errors[:8]]}"
    )


def test_every_mutation_makes_validator_exit_nonzero(repo_copy):
    _m_forbidden_aiox(repo_copy)
    assert validator.main(["--repo", str(repo_copy)]) == 1


def test_skill_length_is_only_a_warning(repo_copy):
    path = repo_copy / ".claude" / "skills" / "copy-hook-generator" / "SKILL.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines + ["linha extra"] * 200) + "\n", encoding="utf-8", newline="\n")
    rep = validator.run_all(repo_copy)
    assert any(w["check"] == "skills" and "linhas" in w["message"] for w in rep.warnings)
    assert not any(e["check"] == "skills" and "linhas" in e["message"] for e in rep.errors)


def test_missing_jsonschema_is_error_unless_allowed(repo_copy, monkeypatch):
    monkeypatch.setattr(validator, "jsonschema", None)
    rep = validator.run_all(repo_copy)
    assert any(e["check"] == "contracts" and "jsonschema ausente" in e["message"] for e in rep.errors)
    rep2 = validator.run_all(repo_copy, allow_missing_jsonschema=True)
    assert not any("jsonschema ausente" in e["message"] for e in rep2.errors)
    assert any("jsonschema ausente" in w["message"] for w in rep2.warnings)


@pytest.mark.parametrize("value,fmt", [("2026-13-45", "date"), ("ontem", "date"), ("2026-11-10", "date-time"),
                                       ("ontem", "date-time"), ("2026-11-10T25:00:00Z", "date-time")])
def test_own_format_checker_rejects_invalid_values(value, fmt):
    jsonschema = pytest.importorskip("jsonschema")
    with pytest.raises(jsonschema.exceptions.FormatError):
        validator._format_checker().check(value, fmt)


@pytest.mark.parametrize("value,fmt", [("2026-11-10", "date"), ("2026-11-10T14:30:00-03:00", "date-time"),
                                       ("2026-11-10T14:30:00Z", "date-time")])
def test_own_format_checker_accepts_valid_values(value, fmt):
    pytest.importorskip("jsonschema")
    validator._format_checker().check(value, fmt)


def test_marker_is_the_only_way_to_silence_a_line():
    forbidden = "squads/" + "copy/" + "x"
    assert validator.find_forbidden(forbidden)
    assert validator.find_forbidden(forbidden + "  # forbidden-pattern-def") == []


def test_validator_scans_its_own_scripts_folder(repo_copy):
    # a varredura de independência inclui scripts/ do squad, inclusive o próprio validador
    path = _squad(repo_copy) / "scripts" / "validate_copy_squad.py"
    _append(path, "\nX = '" + "bil" + "hon'\n")
    rep = validator.run_all(repo_copy)
    assert any(e["check"] == "independence" and "validate_copy_squad.py" in e["message"] for e in rep.errors)


@pytest.mark.parametrize("line", [
    "05-review/{asset_id}/edit-report-v{n}.json",
    "05-review/{asset_id}/brand-review-v2.json",
    "05-review/{asset_id}/compliance-review-v{n}.json.",
    "05-review/{asset_id}/localization-{locale}-v{n}.json",
    "05-review/{asset_id}/ (pasta das revisões)",
    "06-approval/_campaign/g1-r1/ e 06-approval/x/sampling-r2/ e 06-approval/x/g4-r{n}/",
    "o campo gate do JSON continua G4 e SAMPLING",
])
def test_conventions_accept_versioned_paths_and_lowercase_rounds(line):
    assert validator.find_convention_violations(line) == []


@pytest.mark.parametrize("line,needle", [
    ("05-review/{asset_id}/edit-report.json", "sem -v"),
    ("`05-review/{asset_id}/compliance-review.json`", "sem -v"),
    ("05-review/x/localization-pt-BR.json", "sem -v"),
    ("pasta G4-r{n+1}", "maiúsculas"),
    ("06-approval/_campaign/G2-r1/", "maiúsculas"),
    ("06-approval/x/SAMPLING-r1/", "maiúsculas"),
])
def test_conventions_flag_violations(line, needle):
    hits = validator.find_convention_violations(line)
    assert hits and needle in hits[0][1]


def test_yaml_loader_memoizes_and_does_not_cache_errors():
    text = "a: 1" + chr(10) + "b: [1, 2]" + chr(10)
    a = validator.yaml_load(text)
    assert a == {"a": 1, "b": [1, 2]}
    assert validator.yaml_load(text) is a
    for _ in range(2):
        with pytest.raises(validator.yaml.YAMLError):
            validator.yaml_load("a: [aberta" + chr(10))
