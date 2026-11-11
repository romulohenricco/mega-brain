---
task: plan-execution
name: plan-execution
task_name: "Planejar execução e escolher workflow"
version: "1.0.0"
squad: copy-squad
task_id: plan-execution
category: operations
difficulty: advanced
responsavel: '@copy-chief'
responsavel_type: Agent
responsible_executor: copy-chief
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 20-40min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: demand_intake
  tipo: contract:demand-intake
  obrigatorio: true
- campo: politica_de_risco
  tipo: data/risk-policy.yaml
  obrigatorio: true
Saida:
- campo: execution_plan
  tipo: contract:execution-plan
  persistido_em: .data/copy-squad/{business}/{campaign_id}/00-intake/execution-plan.json
input: [demand-intake]
output: [execution-plan]
action_items:
  - "Confirmar demand-intake ready"
  - "Calcular risk_level pela política (D6: toda ação externa é no mínimo medium)"
  - "Escolher um dos 5 workflows"
  - "Montar passos com agente, task, contrato, gate e critérios"
  - "Validar AP05 e gates exigidos; persistir e enviar ao brief-master"
acceptance_criteria:
  - "execution-plan válido em contracts/execution-plan.schema.json"
  - "workflow_id é um dos 5 workflows do squad"
  - "todo task do plano segue o padrão tasks/{id}.md e existe no squad"
  - "gates exigidos pelo risk_level estão presentes e cada gate humano é precedido de prepare-approval-package"
  - "QG-INTAKE aplicado pelo brief-master (executor), nunca pelo copy-chief (produtor do plano)"
  - "nenhum passo atribui validação ao produtor do artefato (AP05)"
pre_condition: "demand-intake com status ready e business identificado"
post_condition: "execution-plan persistido com next_action definido e envelope enviado ao brief-master"
checklist: checklists/intake-checklist.md
quality_gate: QG-INTAKE
human_gate: null
skill: copy-squad
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "se faltar informação para decidir o workflow, voltar a intake-demand com até 5 perguntas; em dúvida de risco, tratar como high"
---

# Task: Planejar execução e escolher workflow

## Objetivo

Converter o `demand-intake` em um `execution-plan`: classificar o risco, escolher o workflow entre os cinco do squad e detalhar os passos (agente, task, contrato de saída, gate humano e critérios de sucesso). O plano é o contrato de trabalho da campanha e o que o `monitor-pipeline` acompanha. O `copy-chief` não escreve copy; ele define quem faz o quê, em que ordem e com qual controle.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Logo após `intake-demand` com status `ready` | Com `demand-intake` em `needs_input` |
| Quando o objetivo, o escopo ou o risco da campanha mudar | Para executar passos do plano (cada agente executa o seu) |
| Quando um bloqueio exigir replanejamento | Para aprovar gates (task `approve-gate`, humana) |
| Quando o `cro-analyst` entregar hipóteses que abram um novo ciclo | Para produzir o brief (task `create-brief`) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| demand_intake | `demand-intake` | sim | `intake-demand` |
| política de risco | `data/risk-policy.yaml` | sim | squad |
| catálogo de workflows | `workflows/wf-*.yaml` | sim | squad |
| matriz de handoff | `data/handoff-matrix.yaml` | sim | squad |
| aprendizados anteriores | `learning-record` | não | `_library/learnings/` |

## Passos

1. **Validar a entrada**: confirme que o `demand-intake` está `ready`, com `demand_type` e sem `missing_information` crítica; caso contrário, volte para `intake-demand`.
2. **Calcular o risco**: aplique `data/risk-policy.yaml`. `low` vale só para uso interno (rascunho, pesquisa, variações para backlog ou teste, ideias); nada `low` é publicado, enviado ou veiculado. Toda ação externa é no mínimo `medium` e exige G4: post orgânico, artigo e e-mail de nutrição são `medium`; anúncio pago, landing page, e-mail de venda, promessa de resultado, preço, garantia, dados de cliente, depoimento, comparativo, saúde e finanças são `high`. Qualquer `claim_type` em price, guarantee, result, authority, testimonial, comparison, health ou financial escala para `high` e exige G3.
3. **Escolher o workflow** pela árvore de decisão: ativo longo a derivar em formatos -> `wf-content-repurposing`; dados de performance para otimizar -> `wf-performance-loop`; variações para uso interno ou teste (risco `low`, nunca publicadas direto) -> `wf-fast-variation` (se uma variação for publicada, ela sai da pista rápida e segue `wf-copy-production` com `prepare-approval-package` e G4, mais G3 e compliance completo se `high`); dois ou mais ativos ou canais, ou lançamento -> `wf-campaign-launch`; demais casos -> `wf-copy-production`. Nos workflows completos o mínimo é `MIN_ANGLES_FULL` = 20 ângulos; na pista rápida, `MIN_ANGLES_FAST_LANE` = 5. Justifique em uma frase.
3a. **Rotear `brand` e `research` (D15)**: `demand_type: brand` (manifesto, tagline) vai para `write-content-piece` com o `content-copywriter` (`content-piece.format` = `manifesto` ou `tagline`), com revisão obrigatória do `brand-voice-guardian` (`review-brand-voice`); o guia de voz, se faltar, vem antes por `define-brand-voice`. `demand_type: research` vai para `build-research-packet` e o entregável é o research packet; case study e white paper (fundo de funil) são do `content-copywriter` (`format` = `case_study` ou `white_paper`), usando o research packet como insumo. O `brand-voice-guardian` e o `offer-strategist` não escrevem esse material.
4. **Carregar as fases do workflow escolhido** e traduza cada fase em passos numerados, usando apenas tasks existentes (`tasks/{id}.md`).
5. **Definir cada passo**: `agent`, `task`, `input_required`, `output_contract`, `human_approval`, `gate` (G1 a G4, SAMPLING ou null) e `success_criteria` mensuráveis. Nos gates de nível campanha (G1, G2, G3 de oferta) o `asset_id` do pedido é o `campaign_id`; os passos de publicação terminam na emissão do pacote de execução e do `publish-receipt`, e a execução externa é do humano ou da sessão principal, nunca de subagent (E4).
6. **Posicionar gates conforme o risco**: G1 após `consolidate-brief` (medium e high); G2 após `generate-angles-hooks` (high ou campanha multi-ativo), com o caminho `hook-angle-creator` -> `copy-chief` (QG-ANGLES) -> `copy-publisher` (`prepare-approval-package`) -> `approval-owner`; G3 de oferta no pacote do G1 quando o risco é high ou há claim sensível (o gatilho do G3 é claim sensível, `data_privacy` ou urgência/escassez, E5), e G3 de texto após `check-compliance` e `fact-check-claims` para claim não pré-aprovado (D10); G4 em toda ação externa. Todo gate humano é precedido de `prepare-approval-package` (copy-publisher, produtor único do pedido, D5). Em low (uso interno), apenas amostragem determinística (`approval_tools.py sample`), registrada como `internal_use`; G5 não usa pedido (`correct-agent-failure`). Se o brief e os ângulos de uma campanha anterior estiverem aprovados, vigentes e inalterados, `wf-performance-loop` e `wf-content-repurposing` herdam G1 e G2 (D12); G3 e G4 seguem o risco da peça nova.
7. **Checar AP05**: nenhum agente valida o próprio artefato; editor edita, `brand-voice-guardian` e `compliance-checker` validam, `approval-owner` aprova.
8. **Estimar esforço e definir `next_action`**: normalmente `brief-master` aplica o QG-INTAKE ao intake e ao plano (executor do gate) e depois executa `create-brief`; use `priority` do `demand-intake` para posicionar a campanha na fila; registre `estimated_effort` por faixa (ex.: 1 a 2 dias úteis, exemplo ilustrativo).
9. **Validar, persistir e emitir**: valide no schema, aplique o checklist, grave `execution-plan.json`, registre o envelope para `brief-master` e o evento no journey log.

## Saída

- **Contrato:** `contracts/execution-plan.schema.json` (`artifact_id` prefixo `pln-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/00-intake/execution-plan.json`.
- **Envelope de handoff:** `from_agent: copy-chief`, `to_agent: brief-master`, `input_ids: [id do demand-intake]`, `output_id: id do plano`, `artifact_type: execution-plan`, `status: ready`, `risk_level` do plano, `human_approval_required: true` em medium e high, `gate: null`.

## Acceptance Criteria (Critérios de aceite)

- Plano válido no schema, com `workflow_id`, `risk_level`, `steps` (≥ 1) e `next_action`.
- Cada `steps[].task` casa com `^tasks/[a-z-]+\.md$` e referencia task existente.
- Gates G1 a G4 presentes conforme a tabela de risco (D11); em claims sensíveis, `data_privacy` ou urgência/escassez, G3 antes de G4; `prepare-approval-package` antes de cada gate humano.
- Nenhum passo viola AP05.
- `success_criteria` de cada passo é verificável (número, contrato ou checklist).
- Justificativa do workflow em uma frase presente em `assumptions` ou `estimated_effort`.

## Quality gate e checklist

- **Gate:** `QG-INTAKE` (APPROVE ≥ 0,80); executor `brief-master`, produtor `copy-chief` (autochecagem não aprova o gate).
- **Checklist:** `checklists/intake-checklist.md` (itens de plano e de risco).
- **Rework:** máximo 2 ciclos; persistindo REVIEW, escalar ao `approval-owner`.
- **Veto:** `workflow_id` fora do catálogo, gate obrigatório ausente, task inexistente ou violação de AP05.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Duas classificações de workflow igualmente plausíveis | Escolher o de maior controle (menor risco de erro) e registrar a alternativa em `assumptions` |
| Risco incerto | Tratar como high até a classificação do `compliance-checker` |
| Plano com mais de 12 passos | Decompor em campanhas ou ciclos menores |
| Task necessária não existe | Não inventar; usar a task mais próxima e registrar a lacuna como `open issue` ao responsável do squad |
| Falha de schema | Corrigir e revalidar antes de persistir |
| Solicitante pede para remover um gate | Recusar e explicar a política de risco; escalar ao `approval-owner` se insistir |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Plano emitido | `brief-master` (`create-brief`) | `execution-plan` | null |
| Decisão estratégica pendente | `approval-owner` | `execution-plan` (resumo) | por decisão |
| Demanda de performance | `cro-analyst` (`analyze-performance`) | `execution-plan` | null |

## Exemplo

Entrada resumida (exemplo ilustrativo): `demand-intake` pronto para landing page da mentoria, com garantia de 30 dias.

```json
{
  "demand_id": "dmd-camp-mentoria-gestao-001",
  "objective": "Vender a mentoria de gestão financeira para pequenas empresas",
  "demand_type": "conversion",
  "risk_level": "high",
  "workflow_id": "wf-copy-production",
  "steps": [
    {"step": 1, "agent": "brief-master", "task": "tasks/create-brief.md", "input_required": ["demand-intake"], "output_contract": "brief", "human_approval": false, "gate": null, "success_criteria": ["brief valida no schema", "perguntas em aberto ≤ 5"]},
    {"step": 2, "agent": "brief-master", "task": "tasks/consolidate-brief.md", "input_required": ["brief", "audience-voc", "offer-canvas"], "output_contract": "brief", "human_approval": true, "gate": "G1", "success_criteria": ["brief aprovado pelo approval-owner"]},
    {"step": 8, "agent": "compliance-checker", "task": "tasks/check-compliance.md", "input_required": ["conversion-copy", "brand-review"], "output_contract": "compliance-review", "human_approval": true, "gate": "G3", "success_criteria": ["claim de garantia verified ou bloqueado"]}
  ],
  "missing_information": [],
  "estimated_effort": "3-5 dias úteis",
  "next_action": "brief-master executa create-brief"
}
```

## Anti-padrões

- Escolher `wf-fast-variation` para peça com preço ou garantia, ou para anúncio ou post a publicar.
- Montar o plano sem os gates exigidos "para ganhar tempo".
- Atribuir `check-compliance` ao mesmo agente que escreveu o texto.
- Copiar o plano padrão sem adequar ao `demand_type`.
- Deixar `success_criteria` vagos ("ficar bom").
- Planejar com task que não existe no squad.
- Escrever trechos de copy dentro do plano.
