---
task: correct-agent-failure
name: correct-agent-failure
task_name: "Corrigir falha de agente e gerar referência"
version: "1.0.0"
squad: copy-squad
task_id: correct-agent-failure
category: governance
difficulty: intermediate
responsavel: '@approval-owner'
responsavel_type: Human
responsible_executor: approval-owner
execution_type: Human
atomic_layer: Molecule
elicit: true
estimated_time: 10-30min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: output_com_falha
  tipo: artefato de qualquer contrato do squad
  obrigatorio: true
- campo: correcao_humana
  tipo: texto corrigido e motivo
  obrigatorio: true
Saida:
- campo: learning_record
  tipo: contract:learning-record
  persistido_em: .data/copy-squad/{business}/_library/learnings/{lrn-id}.json
input: [artefato com falha, correção humana]
output: [learning-record, agent-evaluation]
action_items:
  - "Localizar o run_id em _telemetry/agent-runs.jsonl (se ausente, registrar o run antes)"
  - "Identificar o agente, a execução e a regra violada"
  - "Registrar o trecho antes e depois com o motivo"
  - "Classificar a falha e sua severidade"
  - "Solicitar o learning-record ao knowledge-curator"
  - "Registrar a avaliação do agente"
acceptance_criteria:
  - "falha registrada com agent_name, run_id (prefixo run-, existente em agent-runs.jsonl) e regra violada"
  - "reference_example com before, after e reason"
  - "learning-record válido com origin human_correction e learning_status definido"
  - "agent-evaluation emitido na camada quality"
  - "ação de prevenção definida (ajuste de prompt, heurística ou checklist)"
pre_condition: "o humano corrigiu ou rejeitou um output de agente por erro de conteúdo, regra ou processo"
post_condition: "correção registrada como referência (G5) e disponível para o agente e o squad"
checklist: checklists/approval-gate-checklist.md
quality_gate: QG-LEARNING
human_gate: G5
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "localizar o run_id em .data/copy-squad/{business}/_telemetry/agent-runs.jsonl; se ausente, registrar o agent-run retroativo (run-... com input_ref = artifact_id) antes da avaliação, para que agent_run_id satisfaça ^run-; nunca descartar a correção por falta de rastreio"
---

# Task: Corrigir falha de agente e gerar referência

## Objetivo

Quando o humano corrige ou reprova um output de agente, a correção não pode se perder: ela vira exemplo de referência (G5) para evitar reincidência. G5 não usa `approval-request` (D5): o ponto de entrada é esta task e o resultado é o `learning-record`. A task, executada pelo `approval-owner`, documenta o que falhou, como foi corrigido e por quê, e aciona o `knowledge-curator` para gerar o `learning-record` (origem `human_correction`). Também gera uma `agent-evaluation` para medir a qualidade do agente ao longo do tempo.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Humano reescreveu ou cortou trecho de uma copy gerada por agente | Para decidir um gate (use `approve-gate`) |
| Reprovação por claim sem fonte, urgência falsa, tom errado ou erro factual | Para ajuste estético sem erro de regra (opcional, a critério do humano) |
| Erro de classificação de risco, de contrato ou de roteamento | Para registrar aprendizado de performance (isso é `register-learning` a partir do CRO) |
| Falha recorrente do mesmo agente | Quando o erro for do solicitante (informação errada no pedido) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| output_com_falha | contrato do artefato | sim | `.data/copy-squad/{business}/{campaign_id}/` |
| correção humana | texto e motivo | sim | `approval-owner` |
| run | `agent-run` | sim (localizar; se ausente, registrar antes) | `.data/copy-squad/{business}/_telemetry/agent-runs.jsonl` |
| decisão associada | `approval-decision` | recomendado | `06-approval/{asset_id}/{gate}-r{n}/` (ou `06-approval/_campaign/{gate}-r{n}/` em G1, G2 e G3 de oferta), com `{gate}` em minúsculas |

## Passos

1. **Localizar a execução**: busque em `.data/copy-squad/{business}/_telemetry/agent-runs.jsonl` o `agent-run` cujo `input_ref` ou artefato de saída corresponde ao `artifact_id` com falha e anote `agent_name`, `run_id` (padrão `^run-`) e `prompt_version`. Se não houver o run, registre-o antes (agent-run retroativo, `run_id` com prefixo `run-`, `input_ref` igual ao `artifact_id`), pois a avaliação do passo 7 exige `agent_run_id`.
2. **Classificar a falha**: tipo (factual, claim sem fonte, urgência ou prova falsa, tom de voz, contrato inválido, risco mal classificado, violação de escopo, AP05), severidade (critical, medium, low) e se houve exposição externa.
3. **Identificar a regra violada**: relacione ao princípio, à heurística (`CS-XX-NNN`) ou ao item de checklist que deveria ter evitado o erro.
4. **Registrar o exemplo de referência**: `before` (trecho original), `after` (trecho corrigido) e `reason` (por que o `after` é correto). Use apenas trechos do próprio artefato, sem inventar dados.
5. **Definir a ação de prevenção**: ajuste de prompt, nova heurística, item de checklist, exemplo no knowledge, ou mudança de gate. Seja específico.
6. **Solicitar o `learning-record`**: envie ao `knowledge-curator` a correção para execução de `register-learning`, com `origin: human_correction`, `result`, `decision`, `next_action`, `applies_to` e `learning_status: approved` (ou `draft` se ainda houver dúvida).
7. **Emitir a `agent-evaluation`**: `agent_run_id` (o `run_id` do passo 1), `layer: quality`, `metric_name` (ex.: `claims_sem_fonte`), `score`, `threshold`, `passed: false`, `feedback` e, se aplicável, `seniority_level_observed`.
8. **Reincidência**: se for a 2ª ocorrência do mesmo erro no mesmo agente em 30 dias, sinalize ao `copy-chief` para revisar prompt ou limitar o escopo do agente.
9. **Registrar no journey log** e fechar o desdobramento no `handoffs.jsonl`.

## Saída

- **Contrato:** `contracts/learning-record.schema.json` (prefixo `lrn-`, produzido pelo `knowledge-curator`) e `contracts/agent-evaluation.schema.json` (prefixo `evl-`).
- **Persistência:** `.data/copy-squad/{business}/_library/learnings/{lrn-id}.json` e linha em `.data/copy-squad/{business}/_telemetry/agent-evaluations.jsonl`.
- **Envelope de handoff:** `from_agent: approval-owner`, `to_agent: knowledge-curator`, `artifact_type: learning-record`, `status: ready`, `gate: G5`, `human_approval_required: false`.

## Acceptance Criteria (Critérios de aceite)

- Cada correção tem `reference_example` completo (`before`, `after`, `reason`).
- `learning-record` válido, `origin: human_correction` e `applies_to` com ao menos um campo preenchido.
- `agent-evaluation` registrada com `passed: false` e `feedback` acionável.
- Ação de prevenção descrita com dono e prazo.
- Nenhum dado pessoal de cliente no exemplo de referência (anonimizar).
- Reincidências sinalizadas ao `copy-chief`.

## Quality gate e checklist

- **Gate:** `QG-LEARNING` (a aceitação do registro pelo `knowledge-curator`).
- **Checklist:** `checklists/approval-gate-checklist.md`, seção de G5.
- **Revisão do aprendizado:** definir `review_after` (ex.: 90 dias) para reavaliar a regra.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Sem `run_id` em `agent-runs.jsonl` | Registrar o `agent-run` retroativo (`run_id` com prefixo `run-`, `agent_name` igual a `produced_by`, `input_ref` igual ao `artifact_id`, `status` conforme o contrato) e usar esse `run_id` como `agent_run_id` da `agent-evaluation`; nunca registrar a avaliação só pelo `artifact_id` |
| Correção sem motivo | Pedir o motivo; sem motivo, registrar como `draft` e não ensinar o agente |
| Exemplo contém dado sensível | Anonimizar antes de persistir |
| Falha sistemática de um agente | `copy-chief` revisa escopo, heurísticas e prompt; avalia reduzir autonomia |
| Dois humanos corrigem de formas diferentes | `approval-owner` define a versão de referência; a outra vira `rejected` |
| Prazo apertado | Registrar o mínimo (before, after, reason) em até 24h |
| Falha irrecuperável (correção humana não resolve e o rework está esgotado) | Escalar ao `copy-chief` (`escalated_to_copy_chief`); nunca encerrar direto como `vetoed` (E5) |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Correção registrada | `knowledge-curator` (`register-learning`) | `learning-record` | G5 |
| Reincidência | `copy-chief` | `agent-evaluation` | G5 |
| Peça reprovada que volta ao produtor | `copy-chief` roteia ao agente | `approval-decision` | G1 a G4 |

## Exemplo

Entrada resumida (exemplo ilustrativo): o `email-crm-copywriter` escreveu "Últimas vagas, corra!" sem prazo ou limite real.

```json
{
  "origin": "human_correction",
  "result": "Urgência sem lastro foi cortada na revisão humana.",
  "decision": "Urgência só com legitimate_urgency.exists true e motivo real.",
  "next_action": "Adicionar item de checklist 'urgência com prazo e motivo' ao email-crm-checklist.",
  "applies_to": {"offer": "mentoria", "audience": "pequenas empresas", "channel": "email", "format": "email-journey"},
  "reference_example": {
    "before": "Últimas vagas, corra!",
    "after": "As inscrições vão até 20/11, quando a turma fecha por limite de acompanhamento (exemplo ilustrativo).",
    "reason": "Urgência legítima exige prazo e motivo reais."
  },
  "learning_status": "approved"
}
```

## Anti-padrões

- Corrigir no texto e não registrar nada.
- Registrar "ficou melhor" sem apontar a regra violada.
- Colocar dados reais de cliente no exemplo de referência.
- Culpar o agente sem verificar se a entrada estava correta.
- Gerar learning-record `approved` com dúvida sobre a correção.
- Ignorar reincidência.
- Alterar o prompt do agente sem passar pelo `copy-chief`.
