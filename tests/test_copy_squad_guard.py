"""Testes de squads/copy-squad/scripts/guard_approval_decision.py (ADR-001: D4 e E8).

Suíte rápida: a lógica é exercida em memória; só alguns casos sobem um processo para
conferir o contrato do hook (JSON no stdin, exit 2 e mensagem em português no stderr).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SQUAD = REPO / "squads" / "copy-squad"
GUARD_PATH = SQUAD / "scripts" / "guard_approval_decision.py"
VALIDATOR_PATH = SQUAD / "scripts" / "validate_copy_squad.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load("guard_approval_decision", GUARD_PATH)


def _bash(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def _write(tool: str, file_path: str) -> dict:
    return {"tool_name": tool, "tool_input": {"file_path": file_path, "content": "{}", "new_string": "{}"}}


def _run(payload, raw: str | None = None):
    stdin = raw if raw is not None else json.dumps(payload)
    return subprocess.run([sys.executable, "-I", str(GUARD_PATH)], input=stdin, capture_output=True,
                          text=True, encoding="utf-8", timeout=60, check=False)


# ----------------------------------------------------------------------- Bash

@pytest.mark.parametrize("command", [
    "python squads/copy-squad/scripts/approval_tools.py decide --request r.json --decision approved --reviewer x --confirm abc",
    "python3 ./squads/copy-squad/scripts/approval_tools.py   decide --request r.json",
    "python \"squads/copy-squad/scripts/approval_tools.py\" decide --request r.json",
    "H=$(python squads/copy-squad/scripts/approval_tools.py hash r.json) && python squads/copy-squad/scripts/approval_tools.py decide --confirm ${H:0:12}",
    "cd squads/copy-squad/scripts && python approval_tools.py decide --request r.json",
    "python squads\\copy-squad\\scripts\\approval_tools.py decide --request r.json",
])
def test_blocks_bash_running_decide(command):
    message = guard.evaluate(_bash(command))
    assert message and "uso exclusivo do humano" in message


@pytest.mark.parametrize("command", [
    "python squads/copy-squad/scripts/approval_tools.py hash r.json",
    "python squads/copy-squad/scripts/approval_tools.py verify --request r --decision d --for-execution --payload p",
    "python squads/copy-squad/scripts/approval_tools.py sample cvc-lp-mentoria",
    "python squads/copy-squad/scripts/approval_tools.py content-hash x.json",
    "python squads/copy-squad/scripts/validate_copy_squad.py",
    "cat .data/copy-squad/x/y/06-approval/cvc/g4-r1/approval-decision.json",
    ("python squads/copy-squad/scripts/approval_tools.py verify --request 06-approval/a/g4-r1/approval-request.json "
     "--decision 06-approval/a/g4-r1/approval-decision.json 2>&1"),
    "ls 06-approval/_campaign/g1-r1/",
    "echo decide",
])
def test_allows_other_bash(command):
    assert guard.evaluate(_bash(command)) is None


@pytest.mark.parametrize("command", [
    "echo '{}' > .data/copy-squad/x/y/06-approval/cvc/g4-r1/approval-decision.json",
    "echo '{}' >> 06-approval/cvc/g4-r1/approval-decision.json",
    "cat d.json | tee 06-approval/cvc/g4-r1/approval-decision.json",
    "cp d.json 06-approval/cvc/g4-r1/approval-decision.json",
    "mv d.json 06-approval/cvc/g4-r1/approval-decision.json",
    "sed -i 's/rejected/approved/' 06-approval/cvc/g4-r1/approval-decision.json",
    "echo {} > 06-approval\\cvc\\g4-r1\\approval-decision.json",
])
def test_blocks_bash_writing_the_decision_file(command):
    message = guard.evaluate(_bash(command))
    assert message and "approval-decision.json" in message


# ------------------------------------------------------------- Write/Edit/MultiEdit

@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit"])
@pytest.mark.parametrize("path", [
    ".data/copy-squad/exemplo/camp-x/06-approval/cvc-lp-mentoria/g4-r1/approval-decision.json",
    "06-approval/_campaign/g1-r1/approval-decision.json",
    "06-approval/approval-decision.json",
    "somewhere/else/06-approval/a/b/c/approval-decision.json",
    ".data\\copy-squad\\x\\06-approval\\a\\g4-r2\\approval-decision.json",
    ".DATA/COPY-SQUAD/X/06-APPROVAL/A/G4-R1/APPROVAL-DECISION.JSON",
])
def test_blocks_write_and_edit_of_the_decision_file(tool, path):
    message = guard.evaluate(_write(tool, path))
    assert message and "06-approval" in message


@pytest.mark.parametrize("path", [
    ".data/copy-squad/x/y/06-approval/cvc/g4-r1/approval-request.json",
    ".data/copy-squad/x/y/06-approval/cvc/g4-r1/payload.json",
    ".data/copy-squad/x/y/05-review/cvc/compliance-review-v1.json",
    "approval-decision.json",
    "docs/approval-decision.json",
    "squads/copy-squad/fixtures/approval-decision.valid.json",
    "squads/copy-squad/templates/json/approval-decision.example.json",
    "06-approval/cvc/g4-r1/approval-decision.json.bak",
    "06-approval/cvc/g4-r1/not-approval-decision.json",
])
def test_allows_other_writes(path):
    assert guard.evaluate(_write("Write", path)) is None
    assert guard.evaluate(_write("Edit", path)) is None


@pytest.mark.parametrize("payload", [
    {"tool_name": "Read", "tool_input": {"file_path": "06-approval/a/g4-r1/approval-decision.json"}},
    {"tool_name": "Grep", "tool_input": {"pattern": "approval_tools.py decide"}},
    {"tool_name": "Write", "tool_input": {}},
    {"tool_name": "Bash", "tool_input": {}},
    {"tool_name": "Bash"},
    {"tool_name": "Bash", "tool_input": "texto"},
    {},
    [],
    None,
])
def test_ignores_other_tools_and_malformed_payloads(payload):
    assert guard.evaluate(payload) is None


# ---------------------------------------------------------------- contrato do hook

def test_hook_process_exits_2_with_portuguese_message_on_stderr():
    proc = _run(_bash("python squads/copy-squad/scripts/approval_tools.py decide --request r.json"))
    assert proc.returncode == 2
    assert "BLOQUEADO" in proc.stderr and "humano" in proc.stderr and "!" in proc.stderr
    assert proc.stdout == ""


def test_hook_process_blocks_write_of_decision_file():
    proc = _run(_write("Write", ".data/copy-squad/x/y/06-approval/a/g4-r1/approval-decision.json"))
    assert proc.returncode == 2 and "approval-decision.json" in proc.stderr


def test_hook_process_allows_normal_calls_silently():
    proc = _run(_bash("python squads/copy-squad/scripts/approval_tools.py hash r.json"))
    assert proc.returncode == 0 and proc.stdout == "" and proc.stderr == ""
    proc = _run(_write("Write", ".data/copy-squad/x/y/06-approval/a/g4-r1/approval-request.json"))
    assert proc.returncode == 0


@pytest.mark.parametrize("raw", ["", "   ", "não é json", "{", "[1, 2]", "null"])
def test_hook_process_fails_open_on_unreadable_input(raw):
    assert _run(None, raw=raw).returncode == 0


# ------------------------------------------------------------------ higiene do script

def test_guard_source_is_clean_and_portable():
    validator = _load("validate_copy_squad_for_guard_scan", VALIDATOR_PATH)
    assert validator.find_forbidden(GUARD_PATH.read_text(encoding="utf-8")) == []
    assert validator.find_forbidden(Path(__file__).read_text(encoding="utf-8")) == []
    assert b"\r" not in GUARD_PATH.read_bytes()


def test_guard_wiring_is_documented_in_the_scripts_readme():
    readme = (SQUAD / "scripts" / "README.md").read_text(encoding="utf-8")
    assert "guard_approval_decision.py" in readme and "PreToolUse" in readme and "$CLAUDE_PROJECT_DIR" in readme
    assert "human-chat-confirmed" in readme
