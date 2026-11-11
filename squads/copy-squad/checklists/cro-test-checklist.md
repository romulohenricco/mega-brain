# Checklist: Qualidade de Análise e Teste de CRO

## Metadata
```yaml
id: cro-test-checklist
name: "Checklist de Análise de Performance, Hipóteses e Desenho de Teste A/B"
version: 1.0.0
executor: copy-chief            # valida a saída do cro-analyst (validador diferente do produtor)
self_check_by: cro-analyst       # produtor: a autoavaliação é pré-checagem e não aprova o resultado
related_task: analyze-performance
related_tasks: [analyze-performance, build-cro-hypotheses, design-ab-test]
quality_gate: null              # sem QG dedicado; aprendizados derivados passam pelo QG-LEARNING
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que toda análise de performance, lista de hipóteses e desenho de teste produzidos pelo `cro-analyst` sejam estatisticamente honestos, rastreáveis e acionáveis: comparados com referência, com amostra avaliada, sem vencedor declarado sem critério, com hipóteses de variável única priorizadas por ICE e com critério de parada definido antes do teste. Cada item é verificável por inspeção do JSON `performance-analysis`.

Tipos: **blocking** (falha impõe veto ou retrabalho obrigatório) e **quality** (afeta o score, sem veto isolado).

---

## Fase 1: Dados e referências

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | Período (início e fim) declarado e coerente com os dados fornecidos | blocking | [ ] | |
| 2 | Toda métrica tem denominador e unidade explícitos | blocking | [ ] | |
| 3 | Dados vêm do solicitante ou do runtime do squad, com fonte registrada em `meta.sources` | blocking | [ ] | |
| 4 | Baseline declarado (ou lacuna registrada em `meta.assumptions`) | quality | [ ] | |
| 5 | Meta declarada (ou lacuna registrada) | quality | [ ] | |
| 6 | Comparação com período anterior presente (ou lacuna registrada) | quality | [ ] | |
| 7 | `meta.confidence` reduzida quando alguma referência está ausente | quality | [ ] | |
| 8 | Dados de um único `business` | blocking | [ ] | |

**Score Fase 1:** ___/8

---

## Fase 2: Amostra e significância

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 9 | `sample_size` informado e consistente com as métricas | blocking | [ ] | |
| 10 | Suficiência de amostra avaliada em pelo menos um `statistical_note` | blocking | [ ] | |
| 11 | Duração cobre pelo menos um ciclo semanal completo (ou ressalva registrada) | quality | [ ] | |
| 12 | `winner_declared = true` apenas com `confidence_level` >= `AB_CONFIDENCE_LEVEL` (0,95) e amostra por variante >= `AB_MIN_SAMPLE_PER_VARIANT`, ou critério diferente pré-registrado no `design-ab-test` e atendido | blocking | [ ] | |
| 13 | `significance` com método, `p_value` e `confidence_level` numérico (fração, nunca texto) quando houver teste controlado | quality | [ ] | |
| 14 | Resultado sem significância rotulado como "tendência" ou "inconclusivo" | blocking | [ ] | |
| 15 | Variáveis confundidoras (mídia, oferta, público, sazonalidade) listadas | quality | [ ] | |

**Score Fase 2:** ___/7

---

## Fase 3: Achados e separação epistêmica

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 16 | Todo achado tem `evidence` numérica rastreável aos dados | blocking | [ ] | |
| 17 | Nenhuma causalidade atribuída quando mais de uma variável mudou | blocking | [ ] | |
| 18 | `epistemic.facts` com `[FONTE:...]` em cada item | quality | [ ] | |
| 19 | `epistemic.recommendations` com Posição, Justificativa e Confiança (ALTA, MEDIA ou BAIXA) | quality | [ ] | |
| 20 | `epistemic.hypotheses` com validação requerida e risco se errada | quality | [ ] | |
| 21 | Nenhum dado inventado para preencher lacuna | blocking | [ ] | |

**Score Fase 3:** ___/6

---

## Fase 4: Hipóteses e priorização

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 22 | Toda hipótese com `hypothesis`, `variable`, `expected_effect`, `test_design` e `priority` | blocking | [ ] | |
| 23 | Toda hipótese com `ice` (impact, confidence, ease de 1 a 10) | blocking | [ ] | |
| 24 | Justificativa registrada para cada nota de ICE | quality | [ ] | |
| 25 | Cada hipótese altera uma única variável | blocking | [ ] | |
| 26 | Fila ordenada pelo score ICE (média) com desempate por facilidade | quality | [ ] | |
| 27 | Nenhuma repetição injustificada de teste já registrado como concluído | quality | [ ] | |
| 28 | Hipóteses com novo claim sensível sinalizadas para G3 | blocking | [ ] | |

**Score Fase 4:** ___/7

---

## Fase 5: Desenho de teste

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 29 | Variável única e métrica primária definidas | blocking | [ ] | |
| 30 | MDE definido com justificativa de negócio | blocking | [ ] | |
| 31 | Tamanho de amostra por variação calculado com premissas explícitas | blocking | [ ] | |
| 32 | Duração estimada a partir do volume real informado | quality | [ ] | |
| 33 | Critério de parada e de decisão registrado antes do início, com regra de empate | blocking | [ ] | |
| 34 | Métricas de proteção (guardrails) com limite de tolerância | quality | [ ] | |
| 35 | Execução em produção condicionada a `approval-decision` (G4), com pacote montado pelo `copy-publisher` | blocking | [ ] | |

**Score Fase 5:** ___/7

---

## Fase 6: Contrato, handoff e segurança

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 36 | JSON válido contra `contracts/performance-analysis.schema.json` | blocking | [ ] | |
| 37 | `meta` completo (artifact_id `prf-*`, produced_by, version, confidence) e `analysis_phase` correto (`planning` só com hypotheses/next_actions; `result` com period, metrics, sample_size, findings, winner_declared) | quality | [ ] | |
| 38 | `next_actions` concretas, com responsável sugerido | quality | [ ] | |
| 39 | Envelope de handoff emitido e acrescentado em `handoffs.jsonl` | quality | [ ] | |
| 40 | Nenhum acesso a GA4, Ads, CRM ou UTM: análise feita somente a partir de exports fornecidos | blocking | [ ] | |
| 41 | Nenhum dado pessoal de cliente ou segredo no artefato | blocking | [ ] | |

**Score Fase 6:** ___/6

---

## Veto conditions

Qualquer condição abaixo bloqueia a emissão do contrato (VETO), independentemente do score:

1. `winner_declared = true` sem atingir `AB_CONFIDENCE_LEVEL` e `AB_MIN_SAMPLE_PER_VARIANT` (ou sem critério diferente pré-registrado no `design-ab-test` e atendido).
2. Causalidade atribuída com mais de uma variável alterada, sem rótulo de hipótese.
3. Hipótese ou teste com mais de uma variável.
4. Teste sem critério de parada, sem métrica primária ou sem MDE.
5. Métrica, baseline, meta ou amostra inventados.
6. Acesso a conta externa (o cro-analyst trabalha só com exports).
7. Mistura de dados de negócios diferentes.
8. Execução proposta em produção sem previsão de `approval-decision` (G4).
9. Hipótese com novo claim sensível (preço, garantia, resultado, autoridade, depoimento, comparativo, saúde, financeiro) sem sinalização G3.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Item 2 ou 9 (denominador ou amostra ausente) | Pedir o dado ao solicitante com `needs_input`; não estimar |
| Item 12 ou 14 (vencedor sem critério) | Mudar para `winner_declared = false`, rotular como tendência e registrar o que falta |
| Item 17 (causalidade) | Reclassificar o achado como HIPÓTESE e listar confundidores |
| Item 22 ou 23 (hipótese incompleta) | Voltar ao passo de formulação e pontuação ICE de `build-cro-hypotheses` |
| Item 25 (várias variáveis) | Dividir a hipótese em testes independentes |
| Itens 29 a 33 (desenho incompleto) | Reabrir `design-ab-test` e completar os seis elementos antes de seguir |
| Item 36 (schema inválido) | Corrigir campos e tipos; reexecutar a validação |
| Qualquer veto | Máximo de 2 ciclos de rework; persistindo, escalar ao `copy-chief` |

## Edge cases

- **Tráfego muito baixo:** se a amostra necessária exige duração inviável, registre o trade-off (aumentar o MDE, usar métrica intermediária, teste qualitativo); não reduza o rigor em silêncio.
- **Testes concorrentes na mesma página:** registre risco de interação; recomende sequenciamento ou segmentação.
- **Empate estatístico:** o resultado é válido; mantenha a versão atual e registre como aprendizado (não é fracasso).
- **Sazonalidade ou evento atípico no período:** informe como confundidor e, se possível, sugira repetir o teste.
- **Resultado negativo (a variação piora):** registrar com a mesma seriedade que um positivo; verificar guardrails.
- **Métrica com atribuição ambígua (vários canais):** declarar a janela e o modelo de atribuição usados; sem isso, rotule como estimativa.
- **Dados revisados depois da análise:** gerar nova versão (`meta.version + 1`) sem apagar a anterior.
- **Pedido para "só confirmar" um resultado desejado:** aplicar o mesmo protocolo; o checklist não admite exceções por pressão de prazo.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 41. Cálculo: `score = itens_ok / 41`. Itens não aplicáveis (por exemplo, Fase 5 numa análise sem desenho de teste) são removidos do total e registrados nas notas. Qualquer veto condition ativa anula o score e impõe VETO.

| Score | Decisão | Ação |
|---|---|---|
| >= 0.80 e sem veto | APPROVE | Emitir envelope e encaminhar ao `knowledge-curator` e ao `copy-chief` |
| 0.60 a 0.79 | REVIEW | Corrigir os itens falhos e reaplicar (máximo 2 ciclos) |
| < 0.60 ou veto | VETO | Escalar ao `copy-chief`; registrar causa em `agent-evaluation` |
