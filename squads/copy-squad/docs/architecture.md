# Arquitetura do Copy Squad

> Documento no padrão Teaching Mode: onde cada elemento vive, o que é, com o que se conecta, quem o aciona, o que quebra se for removido, e por que foi desenhado assim.

## 1. Árvore do squad

Raiz: `squads/copy-squad/`

```text
squads/copy-squad/
├── config.yaml                  → fonte de verdade: nomes, componentes, gates, persistência
├── README.md                    → visão geral e guia de uso
├── context.yaml                 → contexto e escopo do squad
├── agent-registry.yaml          → registro dos 19 agentes
├── agents/                      → 19 definições (18 IA + 1 humano)
│   ├── copy-chief.md            → orquestrador
│   ├── brief-master.md  audience-voc.md  offer-strategist.md  brand-voice-guardian.md
│   ├── research-analyst.md  hook-angle-creator.md
│   ├── conversion-copywriter.md  content-copywriter.md  ux-writer.md
│   ├── video-social-scriptwriter.md  email-crm-copywriter.md  localization-specialist.md
│   ├── copy-editor.md  compliance-checker.md
│   ├── cro-analyst.md  knowledge-curator.md  copy-publisher.md
│   └── approval-owner.md        → papel humano
├── tasks/                       → 42 tarefas (Molecules)
├── workflows/                   → 5 fluxos (Organisms)
├── contracts/                   → 26 schemas JSON (*.schema.json)
├── fixtures/                    → 1 exemplo válido por contrato (*.valid.json)
├── templates/                   → 11 modelos .md e templates/json/ (*.example.json)
├── checklists/                  → 20 checklists
├── data/                        → políticas e registros (risk-policy, quality-gates, ...)
├── knowledge/                   → 6 documentos de conhecimento + INDEX.yaml
├── docs/                        → ADR-001 (governance-decisions.md), arquitetura, primeiros passos, banco, changelog
└── scripts/                     → validate_copy_squad.py (validador estrutural) e approval_tools.py (hash, verify, sample, decide)

.claude/
├── skills/copy-*/SKILL.md       → 17 skills (portas de entrada por intenção)
└── agents/copy-squad--*.md      → wrappers de subagente (18, sem o humano)

.data/copy-squad/                → runtime (gitignorado)
├── _telemetry/                  → agent-runs.jsonl e agent-evaluations.jsonl
└── {business}/
    ├── _brand/                  → brand-voice-guide.json
    ├── _library/                → ativos aprovados, provas, aprendizados
    └── {campaign_id}/           → 00-intake ... 08-performance e handoffs.jsonl
```

## 2. X-Ray dos componentes

| Componente | O que é | Onde vive | Conecta-se a | Quem aciona | O que contém | Formato e por quê | O que quebra se for removido |
|---|---|---|---|---|---|---|---|
| Agentes | Cargos com escopo, prompt-base, heurísticas e métricas | `agents/*.md` | Tasks, contratos, checklists | Skills, `@copy-squad--{id}`, `copy-chief` | YAML de operação mais corpo explicativo | Markdown com YAML: legível por humanos e interpretável por IA | O cargo deixa de existir; handoffs ficam sem destinatário |
| Tasks | Unidades de trabalho (Molecules) | `tasks/*.md` | Agente dono, contrato de saída, checklist, gate | Comandos `*` dos agentes e workflows | Frontmatter, passos, critérios, exemplo | Markdown com frontmatter: passo a passo auditável | O agente perde o procedimento e improvisa |
| Workflows | Sequências completas (Organisms) | `workflows/*.yaml` | Tasks, gates de qualidade, gates humanos | `copy-chief` ao escolher o fluxo | Máquina de estados, fases, checkpoints | YAML: estrutura formal e validável | Sem ordem nem checkpoints entre as fases |
| Contratos | Schemas JSON dos artefatos | `contracts/*.schema.json` | Agentes, fixtures, validador | Todos os agentes na entrada e saída | Campos obrigatórios, enums, padrões | JSON Schema 2020-12: validação automática | Handoffs sem garantia de estrutura |
| Fixtures e exemplos | Instâncias de teste e esqueletos | `fixtures/`, `templates/json/` | Contratos, validador | Testes e agentes ao montar saídas | JSON ilustrativo | JSON: provam que o schema funciona | Sem referência de formato e sem testes |
| Checklists | Critérios mensuráveis por entrega | `checklists/*.md` | Tasks e quality gates | Validadores (diferentes do produtor) | Itens bloqueantes, vetos, correção | Markdown com tabela: verificação objetiva | O gate perde o critério |
| Dados | Políticas e registros | `data/*.yaml` | Agentes, workflows, validador | Todos | Risco, gates, métricas, handoffs, canais | YAML: configuração sem mudar código | Sem política de risco, métricas ou limites |
| Conhecimento | Bases de domínio | `knowledge/*.md` | Agentes (consulta sob demanda) | Agentes ao precisarem de contexto | Profissão, modelo, ética, frameworks | Markdown: texto longo legível | Os agentes perdem a base conceitual |
| Skills | Portas de entrada por intenção | `.claude/skills/copy-*/SKILL.md` | Agente dono, task | Roteador de skills por palavra-chave | Gatilhos, procedimento, saída | Markdown: o roteador lê o corpo | O usuário precisa chamar o agente manualmente |
| Wrappers | Subagentes carregáveis | `.claude/agents/copy-squad--*.md` | Agentes do squad | Ferramenta de subagente da IDE | Ponteiro para a definição | Markdown: invocação por `@` | Sem delegação paralela |
| Runtime | Artefatos de cada execução | `.data/copy-squad/` | Todos | Agentes em execução | JSON e JSONL por campanha | Arquivos: auditáveis e versionáveis | Sem memória nem trilha de auditoria |
| ADR-001 | Decisões de governança que prevalecem sobre os demais arquivos | `docs/governance-decisions.md` | Política de risco, gates, contratos, workflows, skills | Quem editar qualquer arquivo do squad | 23 decisões (D1 a D23) | Markdown: uma regra por tema, com o arquivo canônico | Os arquivos voltam a divergir entre si |
| Ferramenta de aprovação | CLI determinística em Python (somente biblioteca padrão) | `scripts/approval_tools.py` | `approval-request`, `approval-decision`, `config.yaml` | `copy-publisher`, `copy-chief` e o humano (`decide`) | Subcomandos `hash`, `content-hash`, `verify` (`--for-execution`, `--payload`), `sample`, `decide` | Python: o hash e a verificação não dependem de um modelo calcular SHA-256 | Sem prova de integridade do payload aprovado |

## 3. Mapa de conexões

```text
Solicitante ── pede ──► skill /copy-squad ── ativa ──► copy-chief
copy-chief ── executa ──► tasks/intake-demand ── grava ──► 00-intake/demand-intake.json
copy-chief ── executa ──► tasks/plan-execution ── escolhe ──► workflows/wf-*.yaml
copy-chief ── envia (handoff) ──► brief-master
brief-master ── consulta ──► audience-voc, offer-strategist, research-analyst
research-analyst ── grava ──► 02-research/research-packet.json
brief-master ── consolida ──► 01-strategy/brief.json
copy-publisher ── monta (prepare-approval-package) ──► 06-approval/_campaign/g1-r1/approval-request.json ── aguarda ──► approval-owner (G1)
hook-angle-creator ── lê ──► brief + research-packet ── grava ──► 03-angles/angles.json ── envia ──► copy-chief (QG-ANGLES) ── aciona ──► copy-publisher (G2: 06-approval/_campaign/g2-r1/) ── aguarda ──► approval-owner
copywriters ── leem ──► ângulo aprovado ── gravam ──► 04-drafts/{asset_id}/v{n}.json
copy-editor ── edita ──► draft ── grava ──► 05-review/{asset_id}/edit-report-v{n}.json
brand-voice-guardian ── valida ──► 05-review/{asset_id}/brand-review-v{n}.json
compliance-checker ── verifica claims ──► 05-review/{asset_id}/compliance-review-v{n}.json (G3 de texto)
copy-publisher ── monta ──► 06-approval/{asset_id}/g4-r1/approval-request.json (payload + sha256 por approval_tools.py hash)
approval-owner ── decide (human-cli ou human-chat-confirmed) ──► 06-approval/{asset_id}/g4-r1/approval-decision.json (G4; bound_to copiado do pedido)
(pós-decisão) copy-publisher ── roda approval_tools.py verify --for-execution ──► copy-chief reexecuta sem flags e contra-assina (QG-PUBLISH-PREFLIGHT)
humano ou sessão principal ── executa (somente decision == approved) ──► copy-publisher registra ──► 07-published/{asset_id}/publish-receipt.json
cro-analyst ── lê métricas ──► 08-performance/performance-analysis-{data}.json
knowledge-curator ── registra ──► _library/learnings e index.jsonl
Todos os agentes ── anexam ──► handoffs.jsonl, agent-runs.jsonl, journey log
```

Cada seta de "envia (handoff)" carrega um `handoff-envelope` com `input_ids`, `output_id`, `status`, `confidence`, `assumptions`, `sources` e a indicação de gate.

## 4. Analogia de negócio

O squad funciona como uma **agência de publicidade bem organizada**:

| Elemento do squad | Equivalente na agência |
|---|---|
| `copy-chief` | Diretor de atendimento e planejamento: recebe o cliente, define quem faz o quê e acompanha prazos |
| `brief-master`, `audience-voc`, `offer-strategist` | Planejamento: transformam um pedido vago em estratégia |
| `research-analyst` | Pesquisa de mercado |
| `hook-angle-creator` e copywriters | Criação: ideias e peças |
| `copy-editor` | Revisão de texto |
| `brand-voice-guardian` | Guardião da marca |
| `compliance-checker` | Jurídico e checagem de fatos |
| `approval-owner` | O cliente (ou o dono do negócio) que aprova antes de ir ao ar |
| `copy-publisher` | Tráfego e produção: só coloca no ar o que está aprovado e idêntico à versão aprovada |
| `cro-analyst` e `knowledge-curator` | Inteligência e memória: medem o que funcionou e guardam para a próxima campanha |
| Contratos JSON | Os formulários padronizados que cada setor preenche e entrega |
| Gates G1 a G5 | As reuniões de aprovação obrigatórias |

Nenhuma agência séria publica um anúncio sem aprovação do cliente. Aqui isso é uma regra técnica: o publisher confere, por script (`approval_tools.py`), a impressão digital (sha256) do que foi aprovado, e só a decisão humana `approved` libera a execução.

## 5. Decisões técnicas

### D1. Um agente por responsabilidade (18 agentes, não um superagente)

- **O quê:** cada agente tem um escopo estreito e um contrato de saída.
- **Por quê:** reduz contaminação de contexto, facilita auditoria e permite substituir um agente sem quebrar o pipeline.
- **Alternativa:** um agente único que pesquisa, escreve, edita e valida.
- **Consequência:** mais handoffs, compensados por contratos estruturados e pelas consolidações de papéis (Brief Intake em `brief-master`, Project Manager em `copy-chief`, Version Control em `copy-publisher`, Asset Library em `knowledge-curator`, Audience e VoC em `audience-voc`, Positioning e Offer em `offer-strategist`, Analytics e CRO em `cro-analyst`).

### D2. Produtor diferente de validador (AP05)

- **O quê:** quem escreve não valida o próprio artefato.
- **Por quê:** o autor tende a ignorar os próprios erros; a verificação independente reduz claims sem suporte.
- **Alternativa:** auto-revisão.
- **Consequência:** `copy-editor`, `brand-voice-guardian` e `compliance-checker` existem como etapas separadas e usam contexto novo (esforço alto no `compliance-checker`).

### D3. Contratos JSON Schema autocontidos

- **O quê:** 26 schemas, cada um com `$defs.meta` e `$defs.source` idênticos, sem `$ref` entre arquivos.
- **Por quê:** o validador funciona arquivo a arquivo e o contrato pode ser copiado para outro ambiente sem dependências.
- **Alternativa:** schemas com referências cruzadas.
- **Consequência:** duplicação controlada de definições comuns, com verificação de igualdade pelo validador.

### D4. Aprovação por risco com payload imutável

- **O quê:** risco baixo vale só para uso interno e avança com log e amostragem; toda ação externa é no mínimo médio e exige G4; claim sensível, `data_privacy` ou urgência/escassez exigem G3. O payload aprovado é travado por `payload_sha256` (`sha256` do JSON canônico do `payload`, com `ensure_ascii=False`), sempre calculado por `scripts/approval_tools.py`.
- **Por quê:** o humano não deve revisar tudo, mas deve decidir o que afeta dinheiro, reputação e dados pessoais; o hash impede troca de conteúdo após a aprovação, e um script (não um modelo) calcula o hash.
- **Alternativa:** aprovação humana em tudo, ou aprovação sem trava de conteúdo.
- **Consequência:** a decisão é amarrada ao pedido (`channel` no pedido; `bound_to` = `{gate, operation, destination, channel}` na decisão). Depois da decisão, o `copy-publisher` roda `approval_tools.py verify --for-execution` e o `copy-chief` reexecuta sem flags e contra-assina o preflight (pós-decisão, não pré-requisito do G4); divergência de hash, `destination`, `channel`, `operation` ou `bound_to` é VETO. Nenhum subagent executa ação externa: a execução é do humano ou da sessão principal. O pedido tem 72 horas para resposta e a decisão tem 72 horas de janela de execução a partir de `decided_at`. Só `approved` autoriza execução (`approved_with_edits` abre nova rodada).

### D5. Filesystem como fonte de verdade

- **O quê:** todo artefato fica em `.data/copy-squad/{business}/{campaign_id}/`.
- **Por quê:** auditável, sem infraestrutura e com isolamento por pasta; combina com drafts versionados e logs append-only.
- **Alternativa:** banco de dados desde o início.
- **Consequência:** consultas entre campanhas dependem de varredura; por isso existe a proposta em `docs/database-proposal.md` (não aplicada).

### D6. Workspace somente leitura

- **O quê:** o squad lê `workspace/businesses/{business}/L0-identity`, `L1-strategy` e `L2-tactical` quando existirem e nunca escreve neles.
- **Por quê:** o workspace pertence à estratégia da unidade; o squad produz artefatos de campanha, não altera identidade ou estratégia.
- **Alternativa:** gravar também no workspace.
- **Consequência:** sem contexto disponível, o agente para e pede o que falta (`halt-with-missing-context`).

### D7. Roteamento de modelos por tier

- **O quê:** tiers padrão usam esforço médio; `tier_2` (qualidade) usa esforço alto; `copy-publisher` usa modelo leve e esforço baixo.
- **Por quê:** verificação exige mais cuidado; empacotamento é determinístico e barato.
- **Alternativa:** um modelo único para todos.
- **Consequência:** menor custo por campanha, com revisão trimestral (ver `knowledge/metrics-and-evaluation.md`).

### D8. Skills como portas por intenção

- **O quê:** 17 skills com frases-gatilho, cada uma ligada a um agente e a uma ou duas tasks.
- **Por quê:** o usuário pede em linguagem natural ("gerar hooks"), e o roteador encontra a capacidade certa.
- **Alternativa:** exigir que o usuário conheça os agentes.
- **Consequência:** as palavras-chave são frases (não palavras soltas) para evitar ativações indevidas; cada skill tem a seção "Quando NÃO ativar".

### D9. Proveniência humana da decisão

- **O quê:** o `approval-decision` é escrito somente pelo humano, por `approval_tools.py decide` (`recorded_via: human-cli`, com o prefixo `!` no Claude Code) ou por confirmação explícita transcrita do chat (`recorded_via: human-chat-confirmed`). Exige `human_attested: true` e `reviewer` presente em `config.yaml → human_gates.approvers`.
- **Por quê:** sem isso, qualquer agente com escrita em `.data/` poderia gravar uma decisão com o hash correto.
- **Alternativa:** assinatura criptográfica (fora do escopo da versão 1.0).
- **Consequência:** a proveniência é procedimental. Endurecimento recomendado: hook `PreToolUse` que bloqueie a escrita de agentes em `06-approval/**/approval-decision.json`. Subagents do squad nunca escrevem a decisão.

### D10. Governança por ADR

- **O quê:** `docs/governance-decisions.md` (ADR-001) fixa uma regra por tema e prevalece sobre qualquer outro arquivo.
- **Por quê:** o squad foi escrito em paralelo e a revisão encontrou regras divergentes (por exemplo, três para `approved_with_edits`).
- **Alternativa:** manter a regra repetida em cada arquivo.
- **Consequência:** ao mudar uma regra, atualiza-se o ADR primeiro e depois os arquivos canônicos que ele indica.

## 6. O que cada nível de profundidade responde

- Nível 1: o squad transforma uma demanda em copy aprovada, medida e arquivada.
- Nível 2: faz isso com agentes especializados, contratos JSON e gates humanos baseados em risco.
- Nível 3 (sob demanda): detalhes de cada agente em `agents/{id}.md`, de cada política em `data/*.yaml`, e dos formatos em `contracts/`.
