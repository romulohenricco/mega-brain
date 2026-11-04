# BUG-3 — Caminho das regras no health check

O diagnóstico de sessão considerava crítica uma pasta ausente da distribuição.
As regras reais ficam em `.claude/rules/`, conforme o índice `.claude/CLAUDE.md`
e a lista de arquivos distribuídos no `package.json`.

```text
.claude/
  CLAUDE.md → indexa rules/*.md
  hooks/startup_health.py → verifica rules/
tests/hooks/test_startup_health.py → executa o hook em instalações artificiais
```

| Elemento | Quem aciona e o que conecta | Formato | Efeito da ausência |
|---|---|---|---|
| `.claude/hooks/startup_health.py` | SessionStart verifica diretórios e arquivos críticos | Python | Perde-se o diagnóstico inicial |
| `.claude/rules/` | Índice de governança fornece as regras aos agentes | Markdown | O hook deve continuar acusando regras ausentes |
| `tests/hooks/test_startup_health.py` | Pytest executa o hook real contra instalações temporárias | Python | A referência quebrada pode reaparecer sem detecção |

É como conferir o arquivo de normas da empresa no endereço atual do escritório.
O nome do endereço muda; a obrigação de haver normas continua.

O ajuste preserva a detecção de regras realmente ausentes e de outros arquivos
críticos. Os três testes falhavam antes da correção; cobrem instalação saudável,
ausência das regras locais e ausência de outro arquivo crítico.

Verificar com `python -m pytest tests/hooks/test_startup_health.py -q` e com
`python .claude/hooks/startup_health.py`. A pontuação de saúde também depende
dos dados ingeridos; um checkout novo pode ter avisos de corpus vazio.

Rollback: `git revert` do commit deste ticket. Não há alteração de dados,
serviços externos, publicação de site nem dependência de ambiente privado.
