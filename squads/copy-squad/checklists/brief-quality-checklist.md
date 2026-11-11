# Checklist: Qualidade do Brief

## Metadata
```yaml
id: brief-quality-checklist
name: "Checklist de Qualidade do Brief de Copy"
version: 1.0.0
executor: copy-chief             # validador do QG-BRIEF (quality-gates.yaml, ADR-001 D7)
self_check_by: brief-master      # produtor: a autoverificação não aprova o gate
related_task: create-brief
quality_gate: QG-BRIEF
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que o brief entregue à produção é completo, sem suposições escondidas, com KPI único, restrições explícitas e critérios de aceite verificáveis. A Fase 4 aplica-se apenas ao brief consolidado (task `consolidate-brief`) antes do G1.

---

## Fase 1: Completude e contrato

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | O JSON valida contra `contracts/brief.schema.json` (todos os campos `required` presentes; com `meta.status: needs_input` o contrato admite campo não confirmado ausente ou vazio, desde que listado em `open_questions`) | blocking | [ ] | |
| 2 | `business_objective` descrito em uma frase, com resultado de negócio claro | blocking | [ ] | |
| 3 | `channel` e pelo menos um item em `formats` informados | blocking | [ ] | |
| 4 | `tone_of_voice` preenchido, citando o brand-voice-guide quando existir | non-blocking | [ ] | |
| 5 | `deadline` informado ou justificado como ausente | non-blocking | [ ] | |
| 6 | `meta.version` incrementada e a versão anterior preservada (sem sobrescrita) | blocking | [ ] | |
**Score Fase 1:** ___/6

---

## Fase 2: Fatos, hipóteses e KPI

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 7 | `primary_kpi` é único e tem métrica, unidade e janela de tempo | blocking | [ ] | |
| 8 | Todo item de `confirmed_facts` tem fonte rastreável (em `meta.sources` ou no próprio texto) | blocking | [ ] | |
| 9 | Preço, garantia, prazo, bônus e resultado sem fonte estão em `hypotheses_to_validate`, não em fatos | blocking | [ ] | |
| 10 | `awareness_stage` declarado, com evidência ou rótulo de hipótese em `meta.assumptions` | blocking | [ ] | |
| 11 | `secondary_kpis` não competem com o KPI primário (sem segundo objetivo disfarçado) | non-blocking | [ ] | |
| 12 | `meta.confidence` coerente com a quantidade de hipóteses abertas | non-blocking | [ ] | |
**Score Fase 2:** ___/6

---

## Fase 3: Restrições, risco e critérios de aceite

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 13 | Restrições legais, de marca, de canal e de produto listadas em `must_avoid` ou `offer.constraints` | blocking | [ ] | |
| 14 | `meta.risk_level` coerente com a política de risco (claims de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças implicam `high`) | blocking | [ ] | |
| 15 | `acceptance_criteria` com pelo menos 5 itens | blocking | [ ] | |
| 16 | 100% dos critérios de aceite são verificáveis por um revisor externo (sem termos subjetivos) | blocking | [ ] | |
| 17 | `open_questions` com no máximo 5 itens, cada um com o motivo | blocking | [ ] | |
| 18 | `must_include` contém apenas itens com fonte ou decisão humana registrada | non-blocking | [ ] | |
| 19 | Nenhuma headline, hook, ângulo ou copy final aparece no brief | blocking | [ ] | |
**Score Fase 3:** ___/7

---

## Fase 4: Consolidação e G1 (somente brief consolidado)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 20 | audience-voc, offer-canvas e research-packet da mesma campanha foram integrados, com `artifact_id` de origem registrado | blocking | [ ] | |
| 21 | Contradições entre artefatos estão em `open_questions` com as duas fontes | blocking | [ ] | |
| 22 | Provas citadas existem no `proof_stack` com `verified` e `usage_rights` conhecidos | blocking | [ ] | |
| 23 | Claims sensíveis, `data_privacy` e urgência/escassez sinalizados para G3; nenhum entra como fato sem fonte | blocking | [ ] | |
| 24 | Pacote G1 de uma página lista as decisões humanas pendentes | non-blocking | [ ] | |
| 25 | `meta.status` coerente (`needs_approval` para risco medium ou high; `ready` apenas se a política dispensar o G1) | blocking | [ ] | |
**Score Fase 4:** ___/6 (marcar N/A no brief v1)

---

## Veto conditions

Qualquer uma das condições abaixo força VETO, independentemente do score:

1. Preço, garantia, prazo, bônus ou resultado tratado como fato sem fonte (CS-BM-002).
2. Mais de um KPI como primário, sem escolha registrada, ou KPI sem métrica (CS-BM-003).
3. Critério de aceite subjetivo que não pode ser verificado por terceiro (CS-BM-004).
4. Claim de risco presente com `risk_level` diferente de `high` (CS-BM-005).
5. Contradição entre artefatos resolvida sem registro ou sem decisão humana.
6. Brief marcado como aprovado sem `approval-decision` válido.
7. Versão anterior do brief sobrescrita.
8. Copy final, headline ou ângulo escrito dentro do brief.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Itens 1 a 6 | Completar o campo a partir do intake; se faltar informação, mover para `open_questions` e definir `needs_input` |
| Itens 7, 11 | Escolher o KPI de maior impacto no objetivo, propor a janela e pedir confirmação em uma pergunta |
| Itens 8, 9 | Mover para `hypotheses_to_validate` tudo o que não tiver fonte; só promover com fonte |
| Item 10 | Inferir o estágio a partir do audience-voc ou do pedido e rotular como hipótese |
| Itens 13, 14 | Reler a política de risco, listar os claims e reclassificar; informar o copy-chief para escalonar |
| Itens 15, 16 | Reescrever cada critério como condição mensurável (limite, presença ou ausência de elemento, referência a id) |
| Item 17 | Priorizar por impacto e cortar para 5, mantendo o motivo de cada pergunta |
| Itens 20 a 23 | Refazer a matriz de integração, citar as fontes e abrir G3 para claims sensíveis |

Após a correção, reaplicar o checklist. Máximo de 2 ciclos de retrabalho; depois, escalar ao copy-chief.

## Edge cases

- **Campanha de uso interno (risco low) e fast-lane:** o G1 pode ser dispensado pela política (G1 é obrigatório em medium e high); a Fase 4 é aplicada de forma reduzida (itens 20, 21 e 25) e o brief segue com `ready`.
- **Briefing com poucos dados e prazo curto:** emitir brief v1 com `needs_input` e hipóteses rotuladas em vez de inventar; a produção só começa depois da resposta.
- **Várias campanhas em um pedido:** separar por `campaign_id`; um brief por campanha.
- **Reaprovação após mudança de oferta:** nova versão obrigatória; o hash do payload anterior é invalidado e o G1 é reaberto.
- **Brief herdando de uma campanha anterior:** copiar apenas fatos com fonte ainda válida; revalidar preços e prazos.
- **Conflito entre solicitante e dados:** registrar ambos em `open_questions`; a decisão é humana.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 25 (brief consolidado) ou 19 (brief v1). Itens `blocking` não atendidos impedem APPROVE mesmo com score alto: a decisão passa a REVIEW com o item descrito.
