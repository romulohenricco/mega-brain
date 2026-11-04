"""The session health hook must check the governance rules actually shipped."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


HOOK = Path(__file__).resolve().parents[2] / ".claude/hooks/startup_health.py"


def _installation(tmp_path, *, rules=True):
    for directory in (
        "engine", "agents/_registry", "knowledge/external", ".claude/hooks",
        ".claude/skills", "artifacts",
    ):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    if rules:
        (tmp_path / ".claude/rules").mkdir()
        (tmp_path / ".claude/rules/agent-authority.md").write_text("# Rules\n", encoding="utf-8")
    (tmp_path / "engine/__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "engine/paths.py").write_text("ROUTING = {}\n", encoding="utf-8")
    (tmp_path / "agents/_registry/ecosystem-registry.yaml").write_text("agents: []\n", encoding="utf-8")
    (tmp_path / ".claude/settings.json").write_text("{}\n", encoding="utf-8")
    target = tmp_path / ".claude/hooks/startup_health.py"
    shutil.copyfile(HOOK, target)
    return target


def _run(hook):
    result = subprocess.run(
        [sys.executable, str(hook)], capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=10, check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_shipped_rules_directory_is_healthy(tmp_path):
    output = _run(_installation(tmp_path))

    assert "[Health] 14/14 checks OK" in output
    assert "docs/governance/rules" not in output


def test_absent_local_rules_are_still_reported(tmp_path):
    output = _run(_installation(tmp_path, rules=False))

    assert "[Health] 13/14 OK" in output
    assert "Missing: .claude/rules" in output


def test_other_critical_files_are_still_checked(tmp_path):
    hook = _installation(tmp_path)
    (tmp_path / "agents/_registry/ecosystem-registry.yaml").unlink()

    output = _run(hook)

    assert "[Health] 13/14 OK" in output
    assert "Missing: agents/_registry/ecosystem-registry.yaml" in output
