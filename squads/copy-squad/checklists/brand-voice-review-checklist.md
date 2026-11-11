# Checklist: Revisão de Voz da Marca

## Metadata
```yaml
id: brand-voice-review-checklist
name: "Checklist de Definição e Revisão da Voz da Marca"
version: 1.0.0
executor: brand-voice-guardian   # validador do QG-BRAND sobre a versão editada pelo copy-editor (ADR-001 D7)
self_check_by: copy-editor       # produtor da versão revisada; a autoverificação não aprova o gate
related_task: review-brand-voice
quality_gate: QG-BRAND
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que (a) o `brand-voice-guide` seja baseado em evidência e completo e (b) cada `brand-review` seja objetivo, preserve fatos e produza uma decisão `approved_for_next_stage` coerente com a regra: score >= 80 e zero issue critical. Cobre as tasks `define-brand-voice` (Fase 1) e `review-brand-voice` (Fases 2 a 4).

Tipos de item: `blocking` (falha = veto) e `quality` (falha reduz score).

**Quem aplica o quê (ADR-001 D7).** Fases 2 a 4 (revisão de peça) são o `QG-BRAND`: produtor `copy-editor`, executor `brand-voice-guardian`, obrigatório em todas as peças, sem amostragem. A Fase 1 (definição do guia) **não** é `QG-BRAND`: o `brand-voice-guardian` produz o guia, então a Fase 1 é só autoverificação do produtor, e a validação é do humano em G1 na primeira versão.

---

## Fase 1: Guia de voz (definição)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | `personality` com >= 3 traços, cada um com evidência ou marcado como hipótese em `assumptions` | blocking | [ ] | |
| 2 | `tone_by_context` cobre todos os canais usados na campanha | quality | [ ] | |
| 3 | `vocabulary.preferred` e `vocabulary.forbidden` preenchidos, com motivo das proibições | blocking | [ ] | |
| 4 | `formality` definida e coerente com os materiais | quality | [ ] | |
| 5 | >= 3 `do_examples` e >= 3 `dont_examples` baseados em materiais reais | quality | [ ] | |
| 6 | `confidence` coerente com o nº de materiais (< 3 materiais => <= 0.6) | quality | [ ] | |
| 7 | G1 solicitado e registrado na primeira versão do guia | blocking | [ ] | |

**Score Fase 1:** ___/7

---

## Fase 2: Pré-condições da revisão

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 8 | Guia de voz existente para o mesmo `{business}` e aprovado em G1 | blocking | [ ] | |
| 9 | `edit-report` referencia `original_copy_id` válido | blocking | [ ] | |
| 10 | Revisor diferente do produtor e do editor da peça (AP05) | blocking | [ ] | |
| 11 | Contexto da peça identificado e relacionado a `tone_by_context` (ou lacuna registrada) | quality | [ ] | |

**Score Fase 2:** ___/4

---

## Fase 3: Qualidade do brand-review

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 12 | Cada issue contém `severity`, `excerpt` literal, `problem` e `reason` | blocking | [ ] | |
| 13 | A `reason` de cada issue cita regra do guia (vocabulário, tom, formalidade, style_rules) | quality | [ ] | |
| 14 | `suggested_revision` é mínima e preserva a intenção do autor | quality | [ ] | |
| 15 | Nenhuma sugestão altera preço, número, prazo, garantia, depoimento ou claim | blocking | [ ] | |
| 16 | Nenhuma sugestão cria argumento ou promessa nova | blocking | [ ] | |
| 17 | `brand_alignment_score` (0-100) calculado de forma consistente com as issues | quality | [ ] | |
| 18 | `tone_match` descreve em 1 a 2 frases o grau de alinhamento | quality | [ ] | |
| 19 | Termos de `vocabulary.forbidden` presentes foram marcados como critical | blocking | [ ] | |

**Score Fase 3:** ___/8

---

## Fase 4: Decisão e entrega

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 20 | `approved_for_next_stage` = true somente se score >= 80 e zero critical | blocking | [ ] | |
| 21 | Lacunas do guia registradas como sugestão de extensão, sem reprovar por elas | quality | [ ] | |
| 22 | JSON válido em `contracts/brand-review.schema.json` (ou `brand-voice-guide.schema.json`) | blocking | [ ] | |
| 23 | Artefato gravado sem sobrescrever versões anteriores | quality | [ ] | |
| 24 | Envelope emitido ao agente correto (`compliance-checker` se aprovada; `copy-editor` se reprovada) | quality | [ ] | |
| 25 | Ciclos de rework <= 2; no 3º, escalado ao `copy-chief` | quality | [ ] | |

**Score Fase 4:** ___/6

---

## Veto conditions

Qualquer uma abaixo força `VETO`:

1. Revisão realizada sem guia de voz aprovado.
2. Reescrita sugerida que altera fato, preço, número, prazo, garantia ou claim.
3. Criação de promessa ou argumento novo dentro da revisão.
4. `approved_for_next_stage = true` com score < 80 ou com issue critical aberta.
5. Revisor igual ao produtor ou ao editor da peça.
6. Guia com personalidade inventada (sem evidência nem marcação de hipótese).
7. Mistura de guia ou materiais de dois negócios.
8. Primeira versão do guia usada sem G1.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Sem guia | Acionar `tasks/define-brand-voice.md` e aguardar G1 |
| Reescrita toca em fato | Remover a sugestão, manter o trecho original e escalar ao `compliance-checker` |
| Issue sem trecho literal | Localizar o trecho exato na peça e reescrever a issue |
| Score inconsistente | Recalcular: 100 - 20 por critical - 8 por medium - 2 por low (piso 0) e ajustar a decisão |
| Guia sem evidência | Marcar traços como hipótese, reduzir `confidence`, pedir 3 a 5 materiais reais |
| Contexto sem tom definido | Registrar lacuna e propor nova linha em `tone_by_context` |
| Reprovação repetida | Após 2 ciclos, escalar ao `copy-chief` |

## Edge cases

- **Peça traduzida:** o guia se aplica ao idioma de destino apenas se houver `tone_by_context` correspondente; caso contrário, registrar lacuna e consultar o `localization-specialist`.
- **Peça de UX (microcopy):** limites de caracteres podem exigir adaptação; priorizar clareza e glossário antes de personalidade.
- **Peça com citação literal de cliente:** a citação não é reescrita, mesmo se fora do tom; sinalizar contexto, não alterar.
- **Negócio com vozes distintas por linha de produto:** tratar como `tone_by_context` ou, se forem negócios distintos, guias separados.
- **Conflito entre brief e guia:** seguir o guia, registrar o conflito e escalar ao `copy-chief`.
- **Peça de baixo risco:** o QG-BRAND roda completo em todas as peças low (risk-policy e wf-fast-variation); a amostragem (`SAMPLING_RATE_LOW = 0.20`) aplica-se só à revisão humana do `approval-owner`, nunca a este gate.
- **Correção humana (G5):** transformar em exemplo do/don't e criar nova versão do guia; não reaprovar retroativamente peças antigas.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 25 (Fase 1 aplica-se somente à definição; Fases 2 a 4 aplicam-se à revisão; em cada uso, exclua do total as fases não aplicáveis). Fórmula: `score = itens_OK / itens_aplicáveis`.

| Faixa | Decisão | Ação |
|---|---|---|
| >= 0.80 sem veto | APPROVE | Guia pronto para o pedido de G1 (liberado ao squad só após G1 `approved`) ou peça enviada ao `compliance-checker` |
| 0.60 a 0.79 | REVIEW | Rework com o `copy-editor` ou revisão do guia (máx. 2 ciclos) |
| < 0.60 ou veto | VETO | Escalar ao `copy-chief`; humano decide em caso de conflito de marca |

**Score final:** ___/___ = ___ → ______
