# Relatório de Performance — {campaign_id}

> Template humano do contrato `performance-analysis` (`contracts/performance-analysis.schema.json`).
> Preenchido pelo `cro-analyst`. Persistência do JSON: `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json`.
> Regra: tudo que não veio dos dados fornecidos é lacuna declarada, nunca estimativa silenciosa.

## 1. Identificação

| Campo | Valor |
|---|---|
| Negócio (`business`) | {business} |
| Campanha (`campaign_id`) | {campaign_id} |
| Análise (`meta.artifact_id`) | prf-{slug} |
| Fase (`analysis_phase`) | {planning (hipóteses e plano de teste, sem resultado) ou result (resultado medido)} |
| Versão (`meta.version`) | {versão} |
| Produzido por | cro-analyst |
| Data da análise (`meta.produced_at`) | {data-hora} |
| Período analisado (`period.start` a `period.end`) | {início} a {fim} |
| Ativos analisados (`asset_ids`) | {lista de ids} |
| Fonte dos dados (`meta.sources`) | {export, planilha, caminho no runtime e data de extração} |
| Status (`meta.status`) | ready / needs_input |
| Confiança (`meta.confidence`) | {0 a 1} |
| Nível de risco (`meta.risk_level`) | low / medium / high |

## 2. Objetivo e KPI

- **Objetivo de negócio (do brief):** {objetivo}
- **KPI primário:** {kpi}
- **KPIs secundários:** {lista}

## 3. Métricas, referências e amostra

| Métrica | Valor no período | Denominador | Baseline | Meta | Período anterior | Variação vs. referência |
|---|---|---|---|---|---|---|
| {métrica 1} | {valor} | {denominador} | {baseline} | {meta} | {anterior} | {abs / %} |
| {métrica 2} | {valor} | {denominador} | {baseline} | {meta} | {anterior} | {abs / %} |

- **Tamanho de amostra (`sample_size`):** {n}
- **Suficiência da amostra:** suficiente / tendência inicial / insuficiente. Justificativa: {conversões absolutas, duração, ciclo semanal}
- **Referências ausentes (lacunas):** {baseline / meta / período anterior ausentes e impacto na confiança}
- **Variáveis alteradas no período:** {copy, oferta, preço, público, mídia, orçamento, canal, sazonalidade, página}

## 4. Achados

| # | Achado (`finding`) | Evidência (`evidence`) | Nota estatística (`statistical_note`) |
|---|---|---|---|
| 1 | {achado} | {números e fonte} | {amostra, intervalo, confundidores} |
| 2 | {achado} | {números e fonte} | {amostra, intervalo, confundidores} |

## 5. Significância e vencedor

| Campo | Valor |
|---|---|
| Vencedor declarado (`winner_declared`) | sim / não |
| Método (`significance.method`) | {método} |
| p-value (`significance.p_value`) | {valor ou null} |
| Nível de confiança (`significance.confidence_level`) | {número em fração, por exemplo 0.93; omitir sem teste controlado} |
| Critério de decisão (`significance.criterion`) | {padrão: confiança >= 0,95 (`AB_CONFIDENCE_LEVEL`) e amostra >= `AB_MIN_SAMPLE_PER_VARIANT` por variante; desvio só se pré-registrado no design-ab-test} |

Regra: "sim" só se confiança >= 0,95 e amostra mínima por variante (ou critério pré-registrado no design-ab-test) foram atendidos. Caso contrário, escrever "tendência favorável a {X}, não conclusiva" e indicar o que falta.

## 6. Separação epistêmica

### FATOS
- {fato} [FONTE:{caminho ou arquivo de dados}]

### RECOMENDAÇÃO
- **Posição:** {o que recomendo}
- **Justificativa:** {por quê}
- **Confiança:** ALTA | MEDIA | BAIXA
- **Evidência ausente (se MEDIA ou BAIXA):** {o que falta para subir a confiança}

### HIPÓTESE
- **Hipótese:** {extrapolação sem evidência direta}
- **Validação requerida:** {como confirmar}
- **Risco se errada:** {consequência}

## 7. Hipóteses priorizadas e fila de testes

| Ordem | Hipótese | Variável (única) | Efeito esperado | Impacto | Confiança | Facilidade | Score ICE | Prioridade | Justificativa |
|---|---|---|---|---|---|---|---|---|---|
| 1 | {hipótese} | {variável} | {efeito} | {1-10} | {1-10} | {1-10} | {média} | high / medium / low | {uma linha por critério} |
| 2 | {hipótese} | {variável} | {efeito} | {1-10} | {1-10} | {1-10} | {média} | high / medium / low | {justificativa} |

Hipóteses que dependem de novo claim sensível (preço, garantia, resultado, autoridade, depoimento, comparativo, saúde, financeiro): marcar **needs_approval (G3)** na linha correspondente.

## 8. Plano de teste (para a hipótese de ordem 1)

| Elemento | Definição |
|---|---|
| Hipótese | {Se mudarmos {variável} de {A} para {B}, então {métrica} deve {efeito}, porque {razão}} |
| Variável única | {variável} |
| Métrica primária | {métrica, numerador/denominador, janela} |
| Métricas de proteção | {métrica e limite de tolerância} |
| MDE | {efeito mínimo detectável e justificativa de negócio} |
| Baseline usado | {taxa e origem} |
| Tamanho de amostra por variação | {n} (premissas: poder 80%, significância 5% bilateral) |
| Alocação | {ex.: 50/50 por visitante} |
| Duração | {dias, em ciclos semanais completos} |
| Critério de parada | {amostra mínima (>= `AB_MIN_SAMPLE_PER_VARIANT`), duração mínima, confiança >= `AB_CONFIDENCE_LEVEL`; desvio só pré-registrado aqui} |
| Regra de empate | {ex.: manter a versão atual} |
| Aprovações necessárias | G3 {se houver claim}; G4 {execução em produção} |

## 9. Próximas ações (`next_actions`)

| # | Ação | Responsável sugerido | Prazo |
|---|---|---|---|
| 1 | {ação} | {agente ou humano} | {data} |
| 2 | {ação} | {agente ou humano} | {data} |

## 10. Handoff

- **Envelope:** `from_agent: cro-analyst` · `to_agent: knowledge-curator` / `copy-chief` · `artifact_type: performance-analysis`
- **Aprendizado a registrar (`register-learning`):** {sim/não e origem}
- **Aprovação humana necessária:** {sim/não; gate}

## 11. Revisão

| Item | Resultado |
|---|---|
| Checklist `checklists/cro-test-checklist.md` | score {0-1} · {APPROVE / REVIEW / VETO} |
| Revisor | {copy-chief ou approval-owner} |
| Observações | {texto} |
