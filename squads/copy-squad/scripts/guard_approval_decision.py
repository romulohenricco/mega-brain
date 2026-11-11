#!/usr/bin/env python3
"""Hook PreToolUse do copy-squad: impede o Claude de fabricar a decisão humana (ADR-001: D4 e E8).

Bloqueia (exit 2, mensagem em português na saída de erro):

  * Bash cujo comando contém `approval_tools.py decide`;
  * Bash que grava `approval-decision.json` por redirecionamento, tee, cp, mv ou sed -i;
  * Write, Edit ou MultiEdit cujo file_path case com `06-approval/**/approval-decision.json`.

O bloqueio vale para a sessão principal e para subagents. Comandos que o humano digita com
o prefixo `!` no Claude Code não passam por hooks, então `approval_tools.py decide` com
`recorded_via: human-cli` continua funcionando. Com este hook ligado, `human-chat-confirmed`
deixa de ser possível: o único meio de registrar a decisão passa a ser `human-cli`.

Entrada: JSON no stdin, como nos demais hooks do repositório (`tool_name` e `tool_input`).
Saída: exit 0 sem texto (permitido) ou exit 2 com a razão em stderr (bloqueado). Entrada
ilegível é permitida (fail-open, igual aos outros hooks do repositório): o hook não tem como
julgar uma chamada que não consegue ler.

NÃO está ligado ao settings.json por padrão; ver scripts/README.md. Somente biblioteca padrão.
"""
from __future__ import annotations

import json
import re
import sys

DECISION_FILE = "approval-decision.json"

# 06-approval/<qualquer subpasta, inclusive nenhuma>/approval-decision.json, em qualquer base.
_DECISION_PATH = re.compile(r"(?:^|/)06-approval/(?:.+/)?approval-decision\.json$", re.IGNORECASE)

# `approval_tools.py decide`, tolerando aspas, caminho antes do script e espaços extras.
_DECIDE_COMMAND = re.compile(r"approval_tools\.py[\"']?\s+(?:--\S+\s+)*decide\b", re.IGNORECASE)

# Escrita em approval-decision.json por shell (heurística: não cobre código arbitrário).
_SHELL_WRITES = (
    re.compile(r"(?<![0-9&<>])>>?\s*[\"']?[^\s\"'|;&]*approval-decision\.json", re.IGNORECASE),
    re.compile(r"\btee\b[^|;&\n]*approval-decision\.json", re.IGNORECASE),
    re.compile(r"\b(?:cp|mv|install|ln)\b[^|;&\n]*approval-decision\.json", re.IGNORECASE),
    re.compile(r"\bsed\b[^|;&\n]*\s-[a-z]*i[a-z]*\b[^|;&\n]*approval-decision\.json", re.IGNORECASE),
)

WRITE_TOOLS = ("write", "edit", "multiedit")

MESSAGE_DECIDE = (
    "BLOQUEADO (copy-squad, ADR-001 D4/E8): `approval_tools.py decide` é de uso exclusivo do humano. "
    "A decisão de aprovação não pode ser gravada pelo Claude nem por subagents. "
    "Peça ao humano que rode o comando ele mesmo, com o prefixo `!` no Claude Code."
)
MESSAGE_FILE = (
    "BLOQUEADO (copy-squad, ADR-001 D4/E8): `approval-decision.json` em 06-approval/ só pode ser criado "
    "pelo humano, via `approval_tools.py decide` (prefixo `!`). Agentes e a sessão principal não escrevem "
    "esse arquivo."
)


def normalize(path: str) -> str:
    return str(path or "").replace("\\", "/")


def is_decision_path(path: str) -> bool:
    return bool(_DECISION_PATH.search(normalize(path)))


def bash_blocked(command: str) -> bool:
    text = str(command or "")
    if _DECIDE_COMMAND.search(text):
        return True
    if DECISION_FILE in text.lower() and "06-approval" in text.replace("\\", "/"):
        return any(rx.search(text.replace("\\", "/")) for rx in _SHELL_WRITES)
    return False


def evaluate(hook_input) -> str | None:
    """Devolve a mensagem de bloqueio, ou None quando a chamada é permitida."""
    if not isinstance(hook_input, dict):
        return None
    tool_name = str(hook_input.get("tool_name", "")).lower()
    tool_input = hook_input.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    if tool_name == "bash":
        command = tool_input.get("command", "")
        if _DECIDE_COMMAND.search(str(command or "")):
            return MESSAGE_DECIDE
        if bash_blocked(command):
            return MESSAGE_FILE
        return None
    if tool_name in WRITE_TOOLS:
        if is_decision_path(tool_input.get("file_path", "")):
            return MESSAGE_FILE
    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw) if raw.strip() else None
    except (OSError, ValueError):
        return 0
    try:
        message = evaluate(hook_input)
    except Exception:  # fail-open: erro interno não deve travar o trabalho
        return 0
    if message:
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.write(message + "\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
