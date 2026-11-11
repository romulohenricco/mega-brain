---
task: monitor-pipeline
name: monitor-pipeline
task_name: "Monitorar pipeline e destravar bloqueios"
version: "1.0.0"
squad: copy-squad
task_id: monitor-pipeline
category: operations
difficulty: intermediate
responsavel: '@copy-chief'
responsavel_type: Agent
responsible_executor: copy-chief
execution_type: Agent
atomic_layer: Molecule
elicit: false
estimated_time: 10-20min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: execution_plan
  tipo: contract:execution-plan
  obrigatorio: true
- campo: handoffs
  tipo: handoffs.jsonl (contract:handoff-envelope por linha)
  obrigatorio: true
Saida:
- campo: status_envelope
  tipo: contract:handoff-envelope
  persistido_em: .data/copy-squad/{business}/{campaign_id}/handoffs.jsonl
input: [execution-plan, handoff-envelope]
output: [handoff-envelope]
action_items:
  - "Ler handoffs.jsonl e reconstruir o estado por passo"
  - "Comparar com o plano e o SLA"
  - "Detectar bloqueios, vetos e conflitos"
  - "Acionar responsáveis ou escalar ao approval-owner"
  - "Registrar o quadro de status e o journey log"
  - "Executar as quatro cadências (D19): diária, semanal, mensal e trimestral, cada uma quando sua data vencer"
acceptance_criteria:
  - "estado de todos os passos do plano reportado (pendente, em andamento, concluído, bloqueado)"
  - "todo bloqueio tem dono, causa e prazo de resolução"
  - "conflitos entre agentes resolvidos pela precedência ou escalados"
  - "alerta emitido para SLA excedido em 50 por cento ou mais"
  - "envelope de status registrado em handoffs.jsonl"
  - "no modo diário, fila, bloqueios, falhas e aprovações pendentes reportados; no semanal, performance por campanha, canal e agente"
  - "nos modos mensal e trimestral, checklist de governança preenchido, com responsável, decisões e prazos registrados"
pre_condition: "execution-plan persistido e ao menos um passo iniciado"
post_condition: "quadro de status atualizado, bloqueios endereçados e escalonamentos registrados"
checklist: checklists/agent-evaluation-scorecard.md
quality_gate: null
human_gate: null
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "se handoffs.jsonl estiver ausente ou corrompido, reconstruir pelo conteúdo de .data e registrar a inconsistência; nunca apagar linhas"
---

# Task: Monitorar pipeline e destravar bloqueios

## Objetivo

Dar visibilidade e ritmo à campanha em andamento. O `copy-chief` lê o `handoffs.jsonl`, compara o realizado com o `execution-plan` e o SLA, identifica bloqueios, vetos de quality gate e conflitos entre agentes, e age: aciona o responsável, aplica a precedência de decisão ou escala para o `approval-owner`. Consolida o papel de Project Manager do organograma original.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Após cada handoff relevante ou em ciclos (diário em campanhas ativas) | Antes de existir `execution-plan` |
| Quando um passo ultrapassar o SLA ou estiver `blocked` ou `needs_input` | Para executar o passo bloqueado em lugar do agente |
| Quando dois artefatos entrarem em conflito | Para decidir questões estratégicas (vão ao humano) |
| Quando o solicitante perguntar "como está a campanha?" | Para publicar ou aprovar |
| Em revisão semanal, mensal ou trimestral (modos de cadência abaixo) | Para alterar prompt, voz ou permissão sem decisão do `approval-owner` |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| execution_plan | `execution-plan` | sim | `00-intake/execution-plan.json` |
| handoffs | `handoff-envelope` (por linha) | sim | `handoffs.jsonl` |
| quality gates | `data/quality-gates.yaml` | sim | squad |
| matriz de handoff | `data/handoff-matrix.yaml` | sim | squad |
| telemetria | `agent-run` | não | `.data/copy-squad/{business}/_telemetry/agent-runs.jsonl` |

## Passos

1. **Ler o log**: carregue `handoffs.jsonl` em ordem e valide cada linha contra `handoff-envelope`; linhas inválidas viram anomalia registrada (não são apagadas).
2. **Reconstruir o estado**: para cada `steps[]` do plano, marque `pendente`, `em_andamento`, `concluido` ou `bloqueado`, usando o último envelope do `output_id` correspondente.
3. **Medir prazo e SLA**: compare timestamps (`created_at`) com `estimated_effort` e o `deadline`; calcule o consumo de SLA por passo.
4. **Detectar bloqueios**: status `blocked`, `needs_input`, `failed`, vetos de quality gate, aprovações pendentes (pedido sem resposta além do prazo de 72h permanece pendente; silêncio nunca é aprovação), decisões prestes a expirar (janela de execução de 72h a partir de `decided_at`) e dependências não entregues.
5. **Classificar a causa**: falta de informação, veto de QG, gate humano pendente, falha técnica, conflito entre agentes ou decisão estratégica.
6. **Agir por causa**: informação faltante -> pergunta objetiva ao solicitante; veto QG -> rework (máx. 2 ciclos) ao produtor; gate pendente -> alerta ao `approval-owner` via `approve-gate`; falha -> reexecutar com a mesma entrada uma vez; conflito -> precedência (compliance-checker > brand-voice-guardian > copy-editor > produtores).
7. **Escalar quando devido**: após 2 alertas sem resposta, rework esgotado, conflito estratégico ou risco crítico, encaminhe ao `approval-owner` com as posições em conflito e a recomendação (Posição, Justificativa, Confiança).
8. **Emitir o status**: gere o resumo (passo atual, próximos, bloqueios, prazos, riscos) e registre um `handoff-envelope` de status.
9. **Registrar**: acrescente linha em `handoffs.jsonl` e evento no journey log; atualize a avaliação operacional do `copy-chief` (taxa de retrabalho, latência).

## Modos de cadência (mensal e trimestral)

A cadência (D19) tem quatro níveis, com dono `copy-chief`. **Diária**: fila, bloqueios, falhas de agente e aprovações pendentes (passos acima). **Semanal**: performance por campanha, canal e agente, lendo os `performance-analysis` do `cro-analyst` e as avaliações dos agentes; o `copy-chief` consolida o quadro e aciona o `cro-analyst` para hipóteses (`build-cro-hypotheses`). **Mensal** e **trimestral**: modos abaixo. Os modos mensal e trimestral são disparados pelo `copy-chief` por data (primeiro dia útil do mês; primeiro dia útil do trimestre) ou por `review_prompt_trigger` de `data/agent-metrics.yaml`, e geram um relatório de governança em `.data/copy-squad/{business}/_telemetry/governance-review-{yyyymm}.md` (referências, sem conteúdo bruto de clientes), com evento no journey log. O `copy-chief` conduz e o `approval-owner` decide; nenhuma mudança é aplicada sem essa decisão.

### Modo mensal (atualização delegada aos donos; responsável: `copy-chief`, decisão: `approval-owner`)

| Item | O que verificar | Fonte |
|---|---|---|
| Guia de voz | Aderência recente (`brand-review`), termos novos, exemplos desatualizados | `_brand/brand-voice-guide.json` |
| Provas | Provas vencidas (`expires_at`), sem fonte ou sem permissão de uso | `_library/` e `build-proof-stack` |
| Objeções | Objeções novas vindas de vendas, suporte e VOC | `map-objections`, `audience-voc` |
| Prompts e `prompt_version` | Agentes com avaliação reprovada, retrabalho alto ou `confidence` baixo; abrir revisão do `prompt_version` e registrar no changelog do agente | `agent-runs`, `agent-evaluations` |
| Rubricas | Rubricas dos quality gates que falham ou aprovam em excesso | `data/quality-gates.yaml` |

### Modo trimestral (responsável: `copy-chief`, decisão: `approval-owner`)

| Item | O que verificar | Fonte |
|---|---|---|
| Arquitetura | Agentes ou tasks subutilizados, gargalos de handoff, fluxos novos necessários | `handoffs.jsonl`, `agent-registry.yaml` |
| Modelos | Adequação do modelo por agente (qualidade, custo, latência) | `agent-runs`, `config.yaml` |
| Custos | Tokens e custo por ativo aprovado, por campanha e por agente | telemetria |
| Permissões | Escopo de ferramentas de cada subagent (`tools:` dos wrappers), `approver_role` e executores externos (`PUBLISH_EXECUTORS = [human, main_session]`); nenhum subagent recebe ferramenta de envio ou publicação, e nenhuma execução externa ocorre sem gate | `data/risk-policy.yaml` |
| Riscos | Incidentes de compliance, vetos recorrentes, falhas de agente (`correct-agent-failure`) | `compliance-review`, `agent-evaluations` |

Cada revisão termina com: decisões tomadas, responsável e prazo por ação, e, quando houver mudança de política, volta a `plan-execution` ou abre `correct-agent-failure`.

## Saída

- **Contrato:** `contracts/handoff-envelope.schema.json` (envelope de status; `artifact_type` descreve o artefato em foco).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl` (append-only).
- **Envelope de handoff:** `from_agent: copy-chief`, `to_agent` o responsável acionado (ou `approval-owner`), `status` conforme a situação (`ready`, `needs_input`, `blocked`), `reason` com a causa e o prazo, `gate` quando o bloqueio for humano.

## Acceptance Criteria (Critérios de aceite)

- Todos os passos do plano aparecem no resumo de status.
- Cada bloqueio traz dono, causa, ação e data-limite.
- Conflitos resolvidos pela precedência registram a regra aplicada; os estratégicos têm escalonamento registrado.
- Alertas de SLA emitidos quando o consumo atingir 50 por cento ou mais do prazo do passo.
- Nenhuma linha de `handoffs.jsonl` foi alterada ou removida.
- Journey log atualizado.

## Quality gate e checklist

- **Gate:** nenhum (`quality_gate: null`). Vetos de quality gate apenas são lidos, não decididos aqui. Quando houver replanejamento, a task `plan-execution` reaplica `QG-INTAKE`, validado pelo `brief-master`.
- **Checklist:** `checklists/agent-evaluation-scorecard.md` (avaliação operacional do `copy-chief`: taxa de retrabalho e latência).
- **Frequência sugerida:** a cada handoff; diária em campanha ativa; semanal em campanha estável; mensal e trimestral conforme os modos de cadência.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| `handoffs.jsonl` ausente | Reconstruir do conteúdo de `.data/copy-squad/{business}/{campaign_id}/` e registrar anomalia |
| Envelope fora do schema | Registrar anomalia, notificar o agente emissor, não apagar |
| Agente não responde | Reacionar uma vez; depois escalar ao `approval-owner` |
| Dois conflitos simultâneos | Resolver primeiro o que afeta risco legal (compliance), depois voz, depois clareza |
| Decisão prestes a expirar ou pedido sem resposta | Alertar o `copy-publisher` e o `approval-owner` com antecedência de pelo menos 12h; pedido vencido continua pendente e o `copy-chief` reenvia ou escala, sem veto automático |
| Mudança de escopo no meio da campanha | Voltar a `plan-execution` para replanejar |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Bloqueio por informação | Solicitante via `copy-chief` | `handoff-envelope` | null |
| Veto de QG | Agente produtor (rework) | `handoff-envelope` | null |
| Gate pendente ou conflito estratégico | `approval-owner` (pedido produzido pelo `copy-publisher` via `prepare-approval-package`) | `approval-request` ou resumo | G1 a G4 |
| Replanejamento | `copy-chief` (`plan-execution`) | `execution-plan` | null |

## Exemplo

Entrada resumida (exemplo ilustrativo): campanha `camp-mentoria-gestao`, passo 6 (landing) concluído há 3 dias, passo 7 (edição) em andamento, aprovação G4 expirando em 10h.

```json
{
  "envelope_id": "env-camp-mentoria-gestao-014",
  "campaign_id": "camp-mentoria-gestao",
  "business": "{business}",
  "from_agent": "copy-chief",
  "to_agent": "approval-owner",
  "input_ids": ["apr-camp-mentoria-lp-001"],
  "output_id": "apr-camp-mentoria-lp-001",
  "artifact_type": "approval-request",
  "artifact_path": ".data/copy-squad/{business}/camp-mentoria-gestao/06-approval/cvc-camp-mentoria-lp-001/g4-r1/approval-request.json",
  "status": "needs_approval",
  "confidence": 0.9,
  "risk_level": "high",
  "human_approval_required": true,
  "gate": "G4",
  "reason": "Pedido G4 sem resposta; o prazo de 72h vence em 10h. Decidir; se vencer, o pedido permanece pendente e é reenviado.",
  "created_at": "2026-11-10T14:00:00Z"
}
```

## Anti-padrões

- Reportar "tudo certo" sem ler `handoffs.jsonl`.
- Editar ou apagar linhas do log para "limpar" o histórico.
- Resolver conflito estratégico por conta própria.
- Alertar sem dono nem prazo.
- Reexecutar um agente em loop sem limite de rework.
- Tratar `needs_approval` como aprovado.
- Ignorar aprovações a expirar.
