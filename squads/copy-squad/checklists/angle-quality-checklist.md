# Checklist: Qualidade do Banco de Ângulos e Hooks

## Metadata
```yaml
id: angle-quality-checklist
name: "Checklist de Qualidade do Banco de Ângulos e Hooks"
version: 1.0.0
executor: copy-chief            # validador do gate QG-ANGLES (D7); compliance-checker revisa também os ângulos high
self_check_by: hook-angle-creator  # produtor; a autochecagem não aprova o gate
validator_at_gate: brief-master
related_task: generate-angles-hooks
quality_gate: QG-ANGLES
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que o banco de ângulos seja amplo, distinto, específico e honesto: quantidade mínima atingida, cada ângulo com promessa, mecanismo e prova necessária, risco declarado, força prevista justificada, nenhuma escassez, urgência ou autoridade falsas e G2 acionado quando necessário. A autoavaliação do hook-angle-creator é preparatória; a pontuação do gate é feita por validador diferente do produtor (AP05).

Tipos: **blocking** = falha aciona veto; **required** = conta no score e exige correção; **advisory** = melhoria recomendada.

---

## Fase 1: Quantidade, distinção e estrutura

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | O número de ângulos atinge o mínimo do modo (>= 20 completo; >= 5 fast lane)? | blocking | [ ] | Total: ___ |
| 2 | Os ângulos são distintos em promessa ou mecanismo (não só em palavras)? | blocking | [ ] | |
| 3 | Cada ângulo tem angle_id único no padrão ang-*? | required | [ ] | |
| 4 | Cada ângulo tem hook, promise e mechanism preenchidos? | blocking | [ ] | |
| 5 | Cada ângulo tem proof_required (lista, mesmo que vazia com justificativa)? | required | [ ] | |
| 6 | Nenhuma dimensão (dor, desejo, mecanismo, prova, contraste, identidade, custo de não agir, história, curiosidade, objeção) passa de 35%? | required | [ ] | Maior: ___% |
| 7 | O JSON é válido contra contracts/angles.schema.json (incluindo meta e brief_id)? | blocking | [ ] | |

**Score Fase 1:** ___/7

---

## Fase 2: Especificidade e aderência

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 8 | As promessas são específicas (público, benefício ou processo concreto), sem clichês genéricos? | required | [ ] | |
| 9 | Os hooks são curtos, claros e compreensíveis sem contexto adicional? | advisory | [ ] | |
| 10 | Os ângulos correspondem ao estágio de consciência do brief? | required | [ ] | |
| 11 | Há variações por estágio de consciência e formato quando o brief as exige? | required | [ ] | |
| 12 | A linguagem usa termos reais do cliente presentes no packet ou no audience-voc? | advisory | [ ] | |
| 13 | Os hooks respeitam limites do canal (data/channel-specs.yaml)? | advisory | [ ] | |
| 14 | O banco inclui pelo menos uma aposta divergente e pelo menos um ângulo seguro de baixo risco? | advisory | [ ] | |

**Score Fase 2:** ___/7

---

## Fase 3: Ética e prova

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 15 | Não há escassez falsa (vagas, estoque ou prazo inexistentes)? | blocking | [ ] | |
| 16 | Não há urgência sem legitimate_urgency.exists true e motivo real no offer-canvas? | blocking | [ ] | |
| 17 | Não há autoridade falsa (títulos, prêmios, mídia, números não verificados)? | blocking | [ ] | |
| 18 | Toda promessa de resultado, prazo, número ou comparação tem evidência no packet ou está needs_approval true com risk_level high? | blocking | [ ] | |
| 19 | proof_required lista a prova que sustentaria cada promessa? | required | [ ] | |
| 20 | Nenhum depoimento, número ou prêmio foi inventado? | blocking | [ ] | |
| 21 | Ângulos que dependem de prova ausente foram sinalizados ao research-analyst como lacuna? | advisory | [ ] | |

**Score Fase 3:** ___/7

---

## Fase 4: Risco, força prevista e governança

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 22 | Cada ângulo tem risk_level coerente com data/risk-policy.yaml? | required | [ ] | |
| 23 | Preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças elevam para high e needs_approval true? | blocking | [ ] | |
| 24 | predicted_strength está entre 0 e 100 em todos os ângulos? | required | [ ] | |
| 25 | Cada predicted_strength tem reason concreta (especificidade, aderência, prova, diversidade)? | required | [ ] | |
| 26 | A força prevista é tratada como hipótese, sem linguagem de resultado medido? | required | [ ] | |
| 27 | O conjunto recomendado para G2 está destacado (shortlist de exatamente 5 ângulos) com riscos? | required | [ ] | |
| 28 | G2 foi solicitado quando há ângulo high ou campanha multi-ativo? | blocking | [ ] | |
| 29 | O envelope de handoff aponta o copy-chief (QG-ANGLES) como destino, e nunca o approval-owner diretamente (G2 segue copy-chief → copy-publisher → approval-owner)? | required | [ ] | |
| 30 | O banco não contém peça completa (página, e-mail, anúncio ou roteiro)? | blocking | [ ] | |

**Score Fase 4:** ___/9

---

## Veto conditions

Qualquer uma abaixo aciona VETO imediato, independentemente do score:

1. Menos ângulos que o mínimo do modo (item 1).
2. Ângulos que são reescritas da mesma promessa (item 2).
3. Escassez, urgência ou autoridade falsas em qualquer ângulo (itens 15, 16 e 17).
4. Promessa de resultado sem evidência e sem needs_approval (item 18).
5. Prova, número, depoimento ou prêmio inventados (item 20).
6. Ângulo sem promessa ou sem mecanismo (item 4).
7. G2 omitido em risco alto ou campanha multi-ativo (item 28).
8. Peça completa dentro do banco (item 30).
9. JSON inválido (item 7).

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Abaixo do mínimo | Gerar novos ângulos em dimensões sub-representadas; nunca duplicar |
| Duplicatas | Aplicar o teste de distinção e substituir |
| Concentração de dimensão | Redistribuir e gerar ângulos nas demais dimensões |
| Escassez, urgência ou autoridade falsas | Remover; usar custo de não agir verdadeiro, mecanismo ou prova verified |
| Resultado sem evidência | Reescrever em termos sustentáveis (processo, método, clareza) e manter o original como candidato needs_approval alto risco |
| Força prevista sem reason | Reescrever com critérios explícitos; se incerto, reduzir a força e declarar a incerteza |
| G2 omitido | Parar o handoff aos copywriters e solicitar G2 via copy-chief |
| Peça completa no banco | Remover o texto longo e deixar apenas hook, promessa e mecanismo |

Limite: 2 ciclos de rework. No terceiro, escalar ao copy-chief (on_veto: copy-chief / approval-owner).

## Edge cases

- **Oferta muito restrita:** se não for possível atingir 20 ângulos distintos, entregar o máximo distinto com justificativa e pedir decisão do copy-chief; não preencher com duplicatas.
- **Fast lane:** mínimo de 5 (MIN_ANGLES_FAST_LANE), apenas para risco low e uso interno; qualquer ângulo high obriga a sair do fast lane e abrir G2.
- **Setor regulado (saúde, finanças):** praticamente todo ângulo de resultado é high; priorizar ângulos de processo, clareza e educação.
- **Packet com confiança baixa:** marcar ângulos dependentes de prova como needs_approval e devolver lacunas ao research-analyst.
- **Sem urgência legítima:** não criar urgência; trabalhar com custo de não agir baseado em dor verificada.
- **Campanha multi-ativo:** o G2 é obrigatório mesmo que todos os ângulos sejam low.
- **Variações por formato:** respeitar limites de caracteres do canal; a variação não pode alterar a promessa ou a prova.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 30. Cálculo: score = itens OK / 30. Registrar o resultado, o validador, a data e a decisão (APPROVE, REVIEW com lista de correções, ou VETO com a condição acionada) no handoff-envelope e na avaliação em `.data/copy-squad/_telemetry/agent-evaluations.jsonl`.
