# STORY-COPY-SQUAD — Squad de Copy agêntico (time profissional de copywriting)

**Status:** InReview — implementação concluída pelo @dev (v1.0.2); Título/Descrição/AC ainda pendentes de validação do @po (`*validate-story-draft`) e do @qa gate
**Origem:** Homer, 2026-11-10 — pesquisa Perplexity "como um copywriter atua / quais graus de especialização" + organograma + prompts/escopos, fluxo, base de dados, métricas e integração humana, "para criação de squad/agent/skill aqui dentro do megabrain"
**Executor:** @dev (sessão Claude Code) · push/PR: somente @devops

## Story

Como operador do Mega Brain, quero um squad de copy que funcione como um time profissional (estratégia, pesquisa, criação, edição, conformidade, dados e operação), com um agente por responsabilidade, skills reutilizáveis, contratos de handoff e aprovação humana baseada em risco, para produzir copy que gera ação mensurável sem inventar provas e sem publicar nada sem aprovação.

## Decisões do Homer (2026-11-10)

- **Local:** `squads/copy-squad/` neste repositório, portável e agnóstico de marca (a marca entra por `{business}` e pelo workspace).
- **Relação com o squad `copy` da engine:** independente — nenhuma referência a ele.
- **Escopo:** completo consolidado — 18 agentes de IA + 1 papel humano, 16 skills de produção + 1 skill de entrada, rubricas de senioridade, métricas e gates de risco.
- **Banco:** só contratos JSON Schema + filesystem; o SQL da pesquisa fica documentado como migration proposta, **sem aplicar**.

## Contexto (antes)

- O repositório tinha um único squad (`squads/orquestrador-global`).
- Não havia papéis funcionais de copy (Brief Master, Editor, Compliance, CRO etc.) nem contratos de handoff para produção de copy.

## Acceptance Criteria

1. AC1 — `squads/copy-squad/` contém `config.yaml` (com `pack:`, `score:`, `entry_agent: copy-chief`, `workspace_integration.level` válido), `context.yaml`, `README.md`, `agent-registry.yaml`, e os diretórios `agents/ tasks/ workflows/ templates/ checklists/ data/ contracts/ fixtures/ knowledge/ docs/ scripts/`.
2. AC2 — 18 agentes de IA + 1 papel humano (`approval-owner`) em `agents/`, cada um com `ACTIVATION-NOTICE`, frontmatter `megabrain_type: Agent`, prompt-base, escopo (faz / nunca faz), heurísticas com veto e fallback, handoffs, métricas e rubrica de senioridade; mínimo de 300 linhas por agente.
3. AC3 — Tasks atômicas (Molecule) com frontmatter local + os 8 campos de Task Anatomy; nenhuma task órfã (toda task é referenciada por um agente e por um workflow ou skill).
4. AC4 — 5 workflows (Organism) com `state_machine`, checkpoints por fase, gates humanos, quality gate antes do output final e tratamento de erro/rework.
5. AC5 — 26 contratos JSON Schema 2020-12 em `contracts/` + fixtures válidas que passam no `jsonschema`.
6. AC6 — 17 skills em `.claude/skills/copy-*/SKILL.md` (frontmatter com 8 campos + cabeçalho `Auto-Trigger/Keywords/Prioridade/Tools` + seção "Quando NÃO Ativar"), registradas em `.claude/skills/skill-registry.yaml` e indexadas pelo `skill_indexer`.
7. AC7 — 18 wrappers `.claude/agents/copy-squad--{agent}.md` aceitos pelo `agent_namespace_validator.py`.
8. AC8 — Persistência de runtime só em `.data/copy-squad/` (gitignorado) + journey log append-only em `.data/logs/journey/lifecycle-events.jsonl`; SQL documentado em `squads/copy-squad/docs/` como proposta, não aplicado.
9. AC9 — Independência e portabilidade: zero referências ao squad `copy` da engine e zero caminhos absolutos de máquina dentro do squad e das skills.
10. AC10 — Aprovação humana baseada em risco (baixo/médio/alto), gates G1–G5 e payload aprovado imutável (verificação por sha256 antes de executar).
11. AC11 — Validador próprio (`squads/copy-squad/scripts/validate_copy_squad.py`) + teste pytest passam; validadores da engine (`validate-squad-structure.py`, `validate-squad-quality.py`, só leitura) sem bloqueios e com nota ≥ 7.0.

## Tasks

- [x] Blueprint de arquitetura (nomes, contratos, handoffs, posse de arquivos)
- [x] Fundação: config, context, registry, data/, knowledge/, docs/, README
- [x] Contratos JSON Schema + fixtures + exemplos
- [x] Agentes + tasks + checklists + templates + skills por núcleo
- [x] Workflows
- [x] Wrappers `.claude/agents/` + registro no `skill-registry.yaml`
- [x] Validador + pytest + validadores da engine
- [x] Verificação adversarial e correções (4 rodadas; ADR `squads/copy-squad/docs/governance-decisions.md`)
- [ ] @po `*validate-story-draft`
- [ ] @qa gate
- [ ] Preencher `human_gates.approvers` por negócio no `config.yaml` (vazio bloqueia qualquer G4 — por desenho)

## Runtime Probe (2026-11-11, sem mocks)

| Verificação | Comando | Resultado |
|------|------|-----------|
| Validador do squad | `python -I squads/copy-squad/scripts/validate_copy_squad.py` | ✅ 0 erros, 0 avisos |
| Testes | `python -m pytest tests/test_copy_squad.py tests/test_copy_squad_approval_tools.py tests/test_copy_squad_guard.py -q` | ✅ 258 passed (≈ 2 min 20 s no disco B:) |
| Estrutura (engine, só leitura) | `validate-squad-structure.py squads/copy-squad` | ✅ READY, 0 bloqueios, 0 órfãs |
| Qualidade (engine, só leitura) | `validate-squad-quality.py squads/copy-squad` | ✅ PASS 100/100 |
| Skills indexadas | `.claude/hooks/skill_indexer.py` | ✅ 17 skills `copy-*` no índice |
| Wrappers | `agent_namespace_validator.py` em cada `.claude/agents/copy-squad--*.md` | ✅ 18/18 aceitos, todos com `tools:` |
| Preflight adversarial | `approval_tools.py verify --for-execution` (modo teste) | ✅ baseline ok; barrados: destino adulterado, payload adulterado, sem `--payload`, `approved_with_edits`, `--now` fora do modo teste |

Veredito do probe: **PASS** (estrutural + ferramenta de aprovação). Nenhuma campanha real executada: o probe de ponta a ponta com um negócio real fica para o primeiro uso.

## Limitações conhecidas

- Proveniência humana da decisão é procedimental: o guard `squads/copy-squad/scripts/guard_approval_decision.py` existe, mas **não está ligado** ao `.claude/settings.json` (decisão do responsável pelo repo).
- O `skill_router` do repositório ordena só por prioridade: prompt de copy que contenha keyword ALTA genérica de outra skill pode ir para ela. A invocação explícita `/copy-squad` e `/copy-<skill>` sempre funciona. Proposta de melhoria do router guardada à parte (não aplicada).
- `docs/proposed-migration.sql` é proposta: não aplicada e não executada em Postgres.

## File List

- `docs/stories/STORY-COPY-SQUAD.md` (este arquivo)
- `squads/copy-squad/**` (novo — 19 agentes, 42 tasks, 5 workflows, 20 checklists, 11 templates + 26 exemplos JSON, 26 contratos + 26 fixtures, 10 data, 7 knowledge, 6 docs, 6 scripts)
- `.claude/skills/copy-*/SKILL.md` (17 novos)
- `.claude/agents/copy-squad--*.md` (18 novos)
- `.claude/skills/skill-registry.yaml` (modificado: +17 entradas)
- `tests/test_copy_squad.py`, `tests/test_copy_squad_approval_tools.py`, `tests/test_copy_squad_guard.py` (novos)

## Change Log

| Data | Agente | Mudança |
|------|--------|---------|
| 2026-11-10 | @dev | Rascunho da story com as 4 decisões do Homer e AC1–AC11 |
| 2026-11-10 | @dev | Construção v1.0.0 (15 escritores paralelos a partir do blueprint) + revisão adversarial (121 achados) + ADR-001 |
| 2026-11-11 | @dev | v1.0.2: emendas E1–E8, rechecks, runtime probe PASS; status → InReview |
| 2026-11-11 | @dev | Knowledge (apps/knowledge) populado a pedido do Homer: 102 entidades do copy-squad em /agente, add-ons e busca; 3 skills corrigidas para `squads/copy-squad/scripts/approval_tools.py` (caminho relativo à raiz) |
