---
task: intake-demand
name: intake-demand
task_name: "Receber e qualificar demanda de copy"
version: "1.0.0"
squad: copy-squad
task_id: intake-demand
category: operations
difficulty: basic
responsavel: '@copy-chief'
responsavel_type: Agent
responsible_executor: copy-chief
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 15-30min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: raw_request
  tipo: texto
  obrigatorio: true
- campo: business
  tipo: slug
  obrigatorio: true
- campo: contexto_workspace
  tipo: leitura de workspace/businesses/{business}/L0-identity, L1-strategy, L2-tactical
  obrigatorio: false
Saida:
- campo: demand_intake
  tipo: contract:demand-intake
  persistido_em: .data/copy-squad/{business}/{campaign_id}/00-intake/demand-intake.json
input: [raw_request, business]
output: [demand-intake]
action_items:
  - "Identificar business, solicitante e campaign_id"
  - "Extrair objetivo, canais, público, oferta, prazo e restrições"
  - "Classificar demand_type"
  - "Classificar a prioridade operacional (priority e priority_rationale) para ordenar a fila e o SLA"
  - "Listar missing_information e formular até 5 perguntas"
  - "Persistir demand-intake e registrar envelope"
acceptance_criteria:
  - "demand-intake válido em contracts/demand-intake.schema.json"
  - "demand_type preenchido com um dos 7 valores permitidos"
  - "no máximo 5 perguntas, todas objetivas e necessárias"
  - "nenhuma suposição sobre preço, garantia, prazo ou resultado"
  - "priority (urgent, high, normal ou low) com priority_rationale preenchidos; a prioridade comercial final é decisão humana"
  - "intake-checklist com score ≥ 0,80, aplicado pelo brief-master (QG-INTAKE)"
pre_condition: "Existe um pedido bruto do solicitante e o business está identificado"
post_condition: "demand-intake persistido com status ready (completo) ou needs_input (com perguntas)"
checklist: checklists/intake-checklist.md
quality_gate: QG-INTAKE
human_gate: null
skill: copy-squad
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "needs_input com até 5 perguntas; nunca presumir preço, garantia, prazo ou resultado"
---

# Task: Receber e qualificar demanda de copy

## Objetivo

Transformar um pedido bruto (em linguagem natural, às vezes vago) em um `demand-intake` estruturado: o que o negócio quer, para quem, em qual canal, com qual oferta, até quando e sob quais restrições. A task também decide se a demanda já está completa para planejamento ou se precisa de perguntas, com limite de 5. É o primeiro passo de todos os workflows e é de responsabilidade do `copy-chief`, que consolida o papel de Brief Intake descrito na pesquisa de domínio.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Qualquer nova demanda de copy, de qualquer canal | Quando já existe um `demand-intake` válido para a campanha (use `plan-execution`) |
| Reabertura de campanha com mudança de objetivo, oferta ou público | Para criar o brief operacional (use `create-brief`, do `brief-master`) |
| Pedido de variações, repurposing ou performance que precise de contexto | Para escrever qualquer texto de copy |
| Pedido ambíguo que mistura vários formatos | Quando a única ação é consultar status (use `monitor-pipeline`) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| raw_request | texto livre | sim | Solicitante |
| business | slug (`^[a-z0-9]+(-[a-z0-9]+)*$`) | sim | Solicitante ou contexto da sessão |
| requester | texto | sim | Solicitante |
| contexto do workspace | leitura somente | não | `workspace/businesses/{business}/L0-identity/`, `L1-strategy/`, `L2-tactical/` |
| dados anteriores | `performance-analysis`, `learning-record`, `knowledge-query-result` | não | `.data/copy-squad/{business}/` |

## Passos

1. **Identificar o escopo**: registre `business`, `requester` e, se houver, o `campaign_id` existente; para campanha nova, gere `camp-{slug}` em kebab-case a partir do objetivo (ex.: `camp-mentoria-gestao-financeira`, exemplo ilustrativo).
2. **Ler o contexto disponível**: consulte, em modo somente leitura, `L0-identity`, `L1-strategy` e `L2-tactical` do business; se não existirem, registre isso em `assumptions` sem inventar conteúdo.
3. **Extrair campos do pedido**: preencha `objective`, `channels`, `audience_hint`, `offer_hint`, `deadline`, `constraints` e `prior_data`; copie o texto original em `raw_request` sem alterações.
4. **Classificar `demand_type`**: escolha entre `conversion`, `content`, `crm`, `product_ux`, `video`, `brand`, `research`; se houver mais de um, use o dominante e registre os demais em `constraints` como formatos secundários.
5. **Checar a lista crítica**: objetivo, público, canal, oferta, KPI, prazo, restrições e risco. Cada item ausente vira uma entrada em `missing_information`.
6. **Detectar sinais de risco**: procure claims de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou financeiro e registre em `constraints` como `claim_sensivel:{tipo}` para o `plan-execution` escalar.
7. **Classificar a prioridade operacional**: defina `priority` (`urgent`, `high`, `normal` ou `low`) com `priority_rationale` (prazo, impacto, dependência), para ordenar a fila e o SLA. É prioridade de fila; a prioridade comercial entre campanhas continua decisão humana.
8. **Formular perguntas**: para cada lacuna que impeça produção ou crie risco, escreva uma pergunta objetiva (máx. 5, ordenadas por impacto); proibido perguntar o que já está no workspace ou no pedido.
9. **Definir o status**: `ready` se não houver lacunas críticas; `needs_input` caso contrário; em `needs_input`, pare e aguarde a resposta do solicitante.
10. **Validar e persistir**: valide contra `contracts/demand-intake.schema.json`, envie ao `brief-master` para aplicar `checklists/intake-checklist.md` (QG-INTAKE; o `copy-chief` só faz autochecagem), grave em `00-intake/demand-intake.json` e registre envelope e evento no journey log.

## Saída

- **Contrato:** `contracts/demand-intake.schema.json` (`artifact_id` com prefixo `dmd-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/00-intake/demand-intake.json`.
- **Envelope de handoff:** `from_agent: copy-chief`, `to_agent: copy-chief` (próximo passo `plan-execution`) quando `ready`; quando `needs_input`, `to_agent` é o solicitante (via `copy-chief`) com `status: needs_input`, `human_approval_required: false`, `gate: null`.

## Acceptance Criteria (Critérios de aceite)

- `demand-intake` valida no schema e traz `demand_type` entre os 7 valores.
- `missing_information` lista todas as lacunas críticas; `questions` tem no máximo 5 itens.
- Nenhum preço, garantia, prazo ou resultado foi presumido (verificável por busca nos campos).
- `raw_request` preservado literalmente.
- Score do `intake-checklist` ≥ 0,80 (APPROVE), aplicado pelo `brief-master`.
- Registro no journey log com `campaign_id` e `artifact_id`.

## Quality gate e checklist

- **Gate:** `QG-INTAKE` (escala 0 a 1; APPROVE ≥ 0,80, REVIEW 0,60 a 0,79, VETO < 0,60).
- **Checklist:** `checklists/intake-checklist.md`.
- **Executor do gate:** `brief-master` (validador, conforme `data/quality-gates.yaml`); o `copy-chief` é o produtor e faz apenas autochecagem, que não aprova o gate (AP05). Se o score ficar em REVIEW, o rework tem no máximo 2 ciclos.
- **Veto:** objetivo ausente, canal ausente, prioridade ausente ou mais de 5 perguntas.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Pedido vazio ou ininteligível | `needs_input` com a pergunta única "qual é o objetivo de negócio desta demanda?" |
| Business não identificado | Parar e perguntar; nunca assumir outro business |
| Workspace sem contexto | Registrar em `assumptions` e seguir só com o que o solicitante informou |
| Mais de 5 lacunas | Priorizar as 5 de maior impacto; as demais entram em `missing_information` sem pergunta e serão tratadas no brief |
| Solicitante insiste em pular o intake | Aplicar `objection_algorithms` do `copy-chief`; reduzir escopo se necessário |
| Falha de validação do schema | Corrigir o campo apontado e revalidar; nunca persistir inválido |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| `ready` | `brief-master` aplica o QG-INTAKE; aprovado, `copy-chief` executa `plan-execution` | `demand-intake` | nenhum |
| `needs_input` | Solicitante responde; retomada em `intake-demand` | `demand-intake` | nenhum |
| Demanda fora do escopo do squad | Solicitante, com explicação | texto | nenhum |

## Exemplo

Entrada resumida (exemplo ilustrativo): "Preciso de uma página para vender a mentoria de gestão financeira para pequenas empresas, tem que sair no mês que vem."

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "dmd-camp-mentoria-gestao-001",
    "artifact_type": "demand-intake",
    "campaign_id": "camp-mentoria-gestao",
    "business": "{business}",
    "produced_by": "copy-chief",
    "produced_at": "2026-11-10T12:00:00Z",
    "version": 1,
    "status": "needs_input"
  },
  "raw_request": "Preciso de uma página para vender a mentoria de gestão financeira para pequenas empresas, tem que sair no mês que vem.",
  "requester": "responsável comercial",
  "objective": "Vender a mentoria de gestão financeira",
  "demand_type": "conversion",
  "priority": "high",
  "priority_rationale": "Prazo de publicação no mês seguinte e dependência de preço e provas ainda não informados",
  "channels": ["landing_page"],
  "audience_hint": "pequenas empresas",
  "missing_information": ["preço e condições", "KPI e meta", "data limite exata", "provas disponíveis"],
  "questions": ["Qual é o preço e as condições de pagamento?", "Qual meta de conversão ou vendas define sucesso?", "Qual é a data limite exata de publicação?", "Há depoimentos ou resultados autorizados para uso?"]
}
```

## Anti-padrões

- Preencher preço, garantia ou prazo "por padrão" para não perguntar.
- Fazer mais de 5 perguntas ou perguntas que o workspace já responde.
- Classificar tudo como `conversion` sem olhar o canal e o objetivo.
- Reescrever o `raw_request` em vez de preservá-lo.
- Iniciar o planejamento com `status: needs_input`.
- Ignorar sinais de claim sensível no pedido.
- Aplicar o QG-INTAKE no próprio demand-intake em vez de enviá-lo ao `brief-master`.
- Deixar a demanda sem `priority`.
- Escrever qualquer trecho de copy durante o intake.
