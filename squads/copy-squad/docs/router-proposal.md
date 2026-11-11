# Proposta (não aplicada): melhoria do skill_router do repositório

> Status: **proposta** · 2026-11-11 · Afeta `.claude/hooks/skill_router.py`, que é compartilhado por todas as skills do repositório. Aplicar só com decisão do responsável pelo repo.

## Problema

O router ordena as skills casadas só por prioridade (ALTA vence MÉDIA) e casa substring em `prompt.lower()` sem remover acentos. Consequências observadas no copy-squad:

- prompt de copy que contenha uma palavra genérica de skill ALTA ("briefing", "pipeline", "documento", "processar") vai para essa outra skill;
- `objeções` não casa `objecoes` (e vice-versa);
- a injeção automática mostra só as 20 primeiras linhas do SKILL.md.

## Mudança proposta

1. A frase mais longa vence; a prioridade só desempata.
2. Normalização sem diacríticos (NFKD + casefold) no prompt e na keyword.
3. O resumo injetado termina com o caminho do SKILL.md completo.

Pendente de avaliar: limite de palavra (evita `copy` casar `copyright`).

## Diff

```diff
diff --git a/.claude/hooks/skill_router.py b/.claude/hooks/skill_router.py
index 162f8dd..e330d1f 100644
--- a/.claude/hooks/skill_router.py
+++ b/.claude/hooks/skill_router.py
@@ -21,6 +21,7 @@ ARQUITETURA:
 """
 
 import json
+import unicodedata
 import os
 import re
 from pathlib import Path
@@ -226,7 +227,7 @@ def match_prompt(prompt: str, index: dict = None) -> list[dict]:
         else:
             index = build_index()
 
-    prompt_lower = prompt.lower()
+    prompt_lower = _normalize_text(prompt)
     matches = []
     seen_items = set()
 
@@ -235,7 +236,7 @@ def match_prompt(prompt: str, index: dict = None) -> list[dict]:
 
     for keyword, item_list in index.get("keyword_map", {}).items():
         # Match por palavra inteira ou substring significativa
-        if keyword in prompt_lower:
+        if _normalize_text(keyword) in prompt_lower:
             for item_info in item_list:
                 item_name = item_info["name"]
                 if item_name not in seen_items:
@@ -251,11 +252,23 @@ def match_prompt(prompt: str, index: dict = None) -> list[dict]:
                     )
 
     # Ordena por prioridade
-    matches.sort(key=lambda x: priority_order.get(x["priority"], 1))
+    # Frase mais específica (keyword mais longa) vence a palavra solta; prioridade desempata
+    matches.sort(
+        key=lambda x: (
+            -len(x["matched_keyword"]),
+            priority_order.get(x["priority"], 1),
+        )
+    )
 
     return matches
 
 
+def _normalize_text(text: str) -> str:
+    """Minúsculas e sem diacríticos, para casar 'objeções' com 'objecoes'."""
+    decomposed = unicodedata.normalize("NFKD", text.casefold())
+    return "".join(c for c in decomposed if not unicodedata.combining(c))
+
+
 def get_skill_instructions(skill_path: str) -> str:
     """Retorna instruções principais da skill para injeção."""
     full_path = PROJECT_ROOT / skill_path / "SKILL.md"
@@ -284,7 +297,12 @@ def get_skill_summary(skill_path: str) -> str:
         return ""
 
     lines = content.split("\n")[:20]
-    return "\n".join(lines)
+    summary = "\n".join(lines)
+    summary += (
+        f"\n\nInstruções completas: {skill_path}/SKILL.md — "
+        "leia o arquivo e siga o Procedimento antes de agir."
+    )
+    return summary
 
 
 def get_subagent_context(subagent_path: str) -> str:
```

Como aplicar (depois de aprovado): salvar o bloco acima como arquivo `.patch` e rodar `git apply` na raiz do repositório; depois rodar o `skill_indexer` e conferir o roteamento das demais skills.
