# INF-1 — Referências locais portáveis

Os quatro consumidores deste ticket apontavam para um framework ausente.
Eles agora usam componentes presentes nesta distribuição pública:

```text
.claude/hooks/
  precompact-session-digest.js → precompact_digest.py
.claude/rules/
  online-publishing.md → agent-authority.md
  portable-paths.md → docs/CONTRIBUTING.md
workspace/_templates/business-template-v3/L0-identity/
  people-registry.yaml → hub_registry opcional
tests/hooks/
  test_precompact_session_digest.py
```

| Componente | Quem aciona e o que conecta | Formato e motivo | Consequência da ausência |
|---|---|---|---|
| Entrada PreCompact | Claude Code envia JSON ao escritor Python local | CommonJS e JSON, mantendo o contrato registrado | O resumo da sessão deixa de ser salvo |
| Escritor de resumo | Lê a transcrição e grava `.synapse/sessions/` | Python existente; JSON estruturado | Não há resumo para consulta posterior |
| Regras locais | Publicação consulta a autoridade; exemplos usam documentos reais | Markdown com caminhos relativos | Os agentes perdem as instruções locais |
| Modelo de pessoas | Cadastro da própria empresa; hub somente quando configurado | YAML com nulo explícito para ausência | Perde-se o modelo de cadastro |

O manual passa a apontar para os formulários e responsáveis que a instalação
realmente tem, como em uma operação que usa seu cadastro local até contratar
um cadastro compartilhado.

O hook recebe JSON por stdin e também mantém a função exportada. Executa Python
sem shell, em UTF-8, com limites de tempo; uma falha permite que a compactação
continue. No Windows, a cadeia de alternativas pode consumir até 7,5 dos dez
segundos registrados, uma limitação de baixa severidade a acompanhar.

O cadastro compartilhado é opcional conforme `.claude/rules/hub-governance.md`.
Se uma instalação configurar `hub_registry`, deverá usar um caminho relativo
existente e manter os IDs compatíveis. O código local não consome esse campo.

Constituição e configuração central possuem tickets separados. Esta mudança
não instala outro framework nem requer serviços ou credenciais externos.

Validação: `python -m pytest tests/hooks/test_precompact_session_digest.py -q`
exercita processos reais, caminho com espaços, acentos e emoji, entrada vazia
ou inválida e ausência de Python. Verifique também
`node --check .claude/hooks/precompact-session-digest.js` e `git diff --check`.

Rollback: reverter apenas o commit deste ticket com `git revert`, preservando
as alterações do usuário e os resumos locais. A conclusão do card exige os
gates de revisão e integração aplicáveis ao repositório.
