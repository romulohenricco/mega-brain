"""Exercise the registered PreCompact command, including its stdin contract.

INF-1: invoking the JS hook used to load an absent framework runner and never
write a digest. Use a real Node/Python process and synthetic session data.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude/hooks/precompact-session-digest.js"
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is required for the hook")


def _run(project, payload, *, env=None, args=None):
    return subprocess.run(
        [NODE, *(args or [str(HOOK)])],
        input=payload,
        text=True,
        encoding="utf-8",
        capture_output=True,
        cwd=project,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(project), **(env or {})},
        timeout=15,
        check=False,
    )


def _digest(project):
    directory = project / ".synapse/sessions"
    pointer = json.loads((directory / "_latest-digest.json").read_text(encoding="utf-8"))
    digest_path = Path(pointer["path"])
    assert digest_path.parent == directory
    return json.loads(digest_path.read_text(encoding="utf-8"))


def test_registered_command_writes_session_digest(tmp_path):
    project = tmp_path / "project with spaces"
    project.mkdir()
    transcript = project / "transcript.jsonl"
    transcript.write_text(
        json.dumps({"type": "user", "message": {"content": "Preserve this decision: revisão 🧠"}})
        + "\n"
        + json.dumps({"type": "assistant", "content": [{"text": "Saved /src/example.py"}]}),
        encoding="utf-8",
    )
    payload = {"session_id": "inf1-test-session", "matcher": "manual", "cwd": str(project),
               "transcript_path": str(transcript)}

    result = _run(project, json.dumps(payload))

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    digest = _digest(project)
    assert digest["session_id"] == payload["session_id"]
    assert digest["matcher"] == "manual"
    assert "Preserve this decision: revisão 🧠" in digest["summary"]
    assert "/src/example.py" in digest["files_modified"]


def test_exported_handler_uses_same_writer(tmp_path):
    code = f"require({json.dumps(str(HOOK))})({{session_id: 'imported-hook'}})"

    result = _run(tmp_path, "", args=["-e", code])

    assert result.returncode == 0, result.stderr
    assert _digest(tmp_path)["session_id"] == "imported-hook"


def test_empty_stdin_uses_project_environment(tmp_path):
    result = _run(tmp_path, "")

    assert result.returncode == 0, result.stderr
    assert _digest(tmp_path)["session_id"] == "unknown"


def test_invalid_stdin_does_not_block_compaction(tmp_path):
    result = _run(tmp_path, "{invalid")

    assert result.returncode == 0
    assert result.stdout == ""
    assert "{invalid" not in result.stderr
    assert not (tmp_path / ".synapse").exists()


def test_missing_python_does_not_block_compaction(tmp_path):
    result = _run(tmp_path, "{}", env={"PATH": ""})

    assert result.returncode == 0
    assert result.stdout == ""
    assert "[PreCompact Hook]" in result.stderr
    assert not (tmp_path / ".synapse").exists()
