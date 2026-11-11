# Checklist: Intake de Demanda e Plano de Execução

## Metadata
```yaml
id: intake-checklist
name: "Checklist de intake de demanda e plano de execução"
version: 1.0.0
executor: brief-master        # validador do QG-INTAKE (D7, quality-gates.yaml)
self_check_by: copy-chief     # produtor do intake e do plano; a autochecagem não aprova o gate (AP05)
related_task: intake-demand
quality_gate: QG-INTAKE
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que a demanda entre no squad completa, classificada e com risco avaliado antes de qualquer produção, e que o plano de execução escolha o workflow certo, posicione os gates exigidos e respeite a regra de que quem produz não valida. O `copy-chief` produz o intake e o plano e faz apenas autochecagem com este checklist; a decisão do QG-INTAKE ao final de `intake-demand` e de `plan-execution` (e, de forma reduzida, em replanejamentos de `monitor-pipeline`) é do `brief-master`, validador distinto do produtor (AP05). Contexto novo não substitui validador distinto. Em risco high, o plano é conferido também pelo `approval-owner` no G1.

## Fase 1: Completude do intake

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | `raw_request` preservado literalmente, sem reescrita | blocking | [ ] | |
| 2 | `objective` descreve resultado de negócio (não apenas formato) | blocking | [ ] | |
| 3 | `demand_type` é um dos 7 valores (conversion, content, crm, product_ux, video, brand, research) | blocking | [ ] | |
| 4 | Pelo menos um canal em `channels` ou pergunta equivalente em `questions` | blocking | [ ] | |
| 5 | Público (`audience_hint`) preenchido ou lacuna listada em `missing_information` | blocking | [ ] | |
| 6 | Oferta (`offer_hint`) preenchida ou lacuna listada | blocking | [ ] | |
| 7 | Prazo (`deadline`) informado ou lacuna listada | recommended | [ ] | |
| 8 | Restrições (`constraints`) registradas, incluindo `claim_sensivel:{tipo}` quando houver | recommended | [ ] | |
| 9 | `prior_data` referencia análises ou aprendizados existentes, quando houver | recommended | [ ] | |
| 10 | `priority` (urgent, high, normal ou low) e `priority_rationale` preenchidos; a prioridade comercial final é decisão humana | recommended | [ ] | |

**Score Fase 1:** ___/10

## Fase 2: Perguntas e suposições

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 11 | `questions` tem no máximo 5 itens | blocking | [ ] | |
| 12 | Toda pergunta é objetiva e destrava produção ou reduz risco | blocking | [ ] | |
| 13 | Nenhuma pergunta repete informação já presente no pedido ou no workspace | recommended | [ ] | |
| 14 | Nenhum preço, garantia, prazo ou resultado foi presumido | blocking | [ ] | |
| 15 | `status` coerente: `needs_input` se há lacuna crítica; `ready` se não há | blocking | [ ] | |
| 16 | Suposições necessárias estão em `assumptions` com marcação explícita | recommended | [ ] | |

**Score Fase 2:** ___/6

## Fase 3: Risco e classificação

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 17 | `risk_level` calculado pela política de `data/risk-policy.yaml`; `low` só para uso interno e toda ação externa é no mínimo `medium` (post orgânico `medium`, anúncio pago `high`) | blocking | [ ] | |
| 18 | Qualquer claim de price, guarantee, result, authority, testimonial, comparison, health ou financial escalou o risco para high | blocking | [ ] | |
| 19 | Em dúvida de classificação, o risco foi tratado como high | recommended | [ ] | |
| 20 | Urgência mencionada no pedido só foi aceita com motivo real (`legitimate_urgency`) | recommended | [ ] | |

**Score Fase 3:** ___/4

## Fase 4: Plano de execução

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 21 | `workflow_id` é um dos 5 workflows do squad e há justificativa em uma frase; `wf-fast-variation` só para uso interno ou teste | blocking | [ ] | |
| 22 | Cada `steps[].task` segue `tasks/{id}.md` e existe no squad | blocking | [ ] | |
| 23 | Cada passo tem `agent`, `output_contract`, `human_approval`, `gate` e `success_criteria` mensuráveis | blocking | [ ] | |
| 24 | Gates exigidos pelo risco estão no plano (G1 em medium e high; G2 em high ou multi-ativo; G3 com claims sensíveis, data_privacy ou urgência/escassez; G4 em toda ação externa) e cada gate humano é precedido de `prepare-approval-package` (copy-publisher) | blocking | [ ] | |
| 25 | Nenhum passo atribui validação ao agente que produziu o artefato (AP05) | blocking | [ ] | |
| 26 | A saída de cada fase é a entrada da seguinte, sem passo órfão | recommended | [ ] | |
| 27 | `next_action` indica agente, task e entrada | recommended | [ ] | |
| 28 | Plano com até 12 passos, ou decomposição justificada | recommended | [ ] | |

**Score Fase 4:** ___/8

## Veto conditions

Qualquer uma abaixo impede o avanço, independentemente do score (QG-INTAKE em VETO):

1. `objective` ausente ou apenas de formato ("fazer uma landing") sem resultado de negócio.
2. Mais de 5 perguntas, ou preço, garantia, prazo ou resultado presumidos.
3. Claim sensível presente e `risk_level` abaixo de high.
4. `workflow_id` fora dos 5 workflows ou task inexistente no plano.
5. Gate obrigatório ausente no plano para o nível de risco, ou gate humano sem `prepare-approval-package` antes.
6. Violação de AP05 (produtor valida o próprio artefato).
7. Qualquer trecho de copy final dentro do intake ou do plano.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Lacuna crítica sem pergunta | Formular a pergunta (respeitando o máximo de 5) e voltar a `needs_input` |
| Mais de 5 perguntas | Priorizar por impacto; mover as demais para `missing_information` e tratá-las no brief |
| Risco subestimado | Recalcular pela política; inserir os gates exigidos (G1, G2, G3, G4 conforme o risco); atualizar o workflow se necessário |
| Task inexistente | Substituir pela task correta da lista do squad ou sinalizar lacuna ao responsável |
| AP05 violado | Reatribuir a validação para `copy-editor`, `brand-voice-guardian` ou `compliance-checker` |
| Gate ausente | Inserir o gate na posição correta e atualizar `human_approval` |
| Texto de copy no plano | Remover e substituir por critério de aceite |

Ciclos de rework: no máximo 2 (`REWORK_MAX_CYCLES`); depois, escalar ao `copy-chief` e, se a decisão for estratégica, ao `approval-owner`.

## Edge cases

- **Demanda dupla (ex.: landing page e e-mails):** classifique pelo dominante, use `wf-campaign-launch` e registre os formatos nos `channels`.
- **Pedido de performance sem dados:** `needs_input` pedindo período, métricas e baseline; não iniciar `wf-performance-loop`.
- **Business sem contexto no workspace:** seguir apenas com o informado, marcando `assumptions`; sem inventar posicionamento.
- **Solicitante pede para "pular a aprovação":** recusar; oferecer `wf-fast-variation` apenas se as peças forem de uso interno ou teste (low); qualquer publicação é no mínimo medium e passa por G4.
- **Reabertura de campanha existente:** reutilizar `campaign_id`, versionar o intake (v2) e replanejar apenas os passos afetados.
- **Pedido fora do escopo (ex.: compra de mídia, design):** registrar e encaminhar ao solicitante; o squad não executa mídia nem design. Manifesto, tagline, case study e white paper estão no escopo (D15): vão para `write-content-piece`.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 28 (Fase 1: 10, Fase 2: 6, Fase 3: 4, Fase 4: 8). Item bloqueante reprovado em qualquer fase implica VETO, mesmo com score numérico alto.

**Score final:** ___/28 = ___ → [ ] APPROVE  [ ] REVIEW  [ ] VETO
