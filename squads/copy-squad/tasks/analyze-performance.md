---
task: analyze-performance
name: analyze-performance
task_name: "Analisar performance de copy"
version: "1.0.0"
squad: copy-squad
task_id: analyze-performance
category: intelligence
difficulty: advanced
responsavel: '@cro-analyst'
responsavel_type: Agent
responsible_executor: cro-analyst
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 30-60min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: metricas_fornecidas
  tipo: dados do solicitante (export, planilha ou colagem)
  obrigatorio: true
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: publish_receipts
  tipo: contract:publish-receipt
  obrigatorio: false
Saida:
- campo: performance_analysis
  tipo: contract:performance-analysis
  persistido_em: .data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json
input: [metricas_fornecidas, brief, publish-receipt]
output: [performance-analysis]
action_items:
  - "Validar completude dos dados (período, métrica, denominador, canal, ativo)"
  - "Fixar baseline, meta e período anterior"
  - "Calcular comparações com denominador e amostra"
  - "Avaliar suficiência de amostra e duração"
  - "Registrar significância ou critério pré-definido; sem isso, winner_declared = false"
  - "Redigir achados com evidência e nota estatística"
  - "Separar FATOS, RECOMENDAÇÃO e HIPÓTESE"
  - "Emitir performance-analysis e envelope de handoff"
acceptance_criteria:
  - "performance-analysis válido contra contracts/performance-analysis.schema.json"
  - "100% dos achados com evidência numérica e denominador"
  - "sample_size informado e suficiência avaliada em pelo menos um statistical_note"
  - "winner_declared = true apenas com significance.criterion preenchido e atendido"
  - "Nenhuma causalidade atribuída com mais de uma variável alterada"
  - "Bloco epistemic com FATOS (com fonte), RECOMENDAÇÃO (posição, justificativa, confiança) e HIPÓTESE (validação requerida)"
  - "Score do checklists/cro-test-checklist.md >= 0.80"
pre_condition: "Métricas do período fornecidas pelo solicitante ou gravadas no runtime; brief da campanha disponível com objetivo e KPI primário"
post_condition: "performance-analysis gravado em 08-performance, envelope emitido para knowledge-curator e copy-chief, lacunas de dado registradas"
checklist: checklists/cro-test-checklist.md
quality_gate: null
human_gate: null
skill: null
workflows: [wf-copy-production, wf-performance-loop]
performance:
  error_handling: "needs_input com até 5 perguntas quando faltar período, métrica, denominador ou referência; nunca estimar dado ausente; nunca acessar conta externa (trabalha só com exports fornecidos)"
---

# Task: Analisar performance de copy

## Objetivo

Transformar métricas de performance de uma ou mais peças de copy em um diagnóstico confiável: o que aconteceu, contra qual referência, com qual volume e o que ainda não se pode afirmar. A saída é o contrato `performance-analysis`, que alimenta a construção de hipóteses (`build-cro-hypotheses`), o desenho de testes (`design-ab-test`) e o registro de aprendizado (`register-learning`).

## Quando usar / quando não usar

**Usar quando:**
- Uma peça, campanha ou teste tem dados de um período e o squad precisa decidir o próximo passo.
- O `wf-performance-loop` chega à fase de leitura de resultados.
- O `copy-chief` pede um relatório de performance para decidir novo ciclo de produção.
- Um teste A/B terminou (ou foi interrompido) e é preciso verificar se há vencedor.

**Não usar quando:**
- Não há dados do período (primeiro peça um export ou aguarde a coleta).
- O pedido é só uma ideia de teste sem dados (use `build-cro-hypotheses`).
- O pedido é montar um teste novo (use `design-ab-test`).
- O pedido exige acessar contas de mídia ou analytics: recusar e solicitar o export (o cro-analyst trabalha só com exports; acesso a contas é do humano ou da sessão principal, fora do subagent).

## Entradas

| Campo | Contrato / formato | Obrigatório | Origem |
|---|---|---|---|
| metricas_fornecidas | export, planilha ou colagem com período, métrica, denominador, canal e ativo | Sim | Solicitante ou `.data/copy-squad/{business}/{campaign_id}/08-performance/` |
| brief | `contract:brief` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| publish_receipts | `contract:publish-receipt` | Não | `.data/copy-squad/{business}/{campaign_id}/07-published/{asset_id}/publish-receipt.json` |
| baseline / meta / período anterior | números com período de origem | Recomendado | Solicitante, brief ou análise anterior |
| learning_records anteriores | `contract:learning-record` | Não | via `knowledge-curator` (`retrieve-knowledge`) |

## Passos

1. **Confirmar escopo.** Registre `business`, `campaign_id`, `asset_ids` e o período (início e fim). Se algum faltar, interrompa com `needs_input`.
2. **Ler o brief.** Extraia objetivo de negócio e KPI primário. A análise gira em torno desse KPI; métricas secundárias entram como contexto.
3. **Validar os dados.** Para cada métrica, confirme o denominador (ex.: conversões sobre sessões, cliques sobre impressões), o período e a unidade. Identifique dados duplicados, lacunas de dias e mudanças de definição de métrica.
4. **Fixar referências.** Defina baseline, meta e período anterior, nesta ordem de preferência. Se faltar alguma, registre em `meta.assumptions` e reduza `meta.confidence`. Nunca invente referência.
5. **Listar variáveis alteradas no período.** Copy, oferta, preço, público, mídia, orçamento, canal, sazonalidade, página. Se mais de uma mudou, qualquer achado causal passa a ser HIPÓTESE.
6. **Calcular comparações.** Variação absoluta e relativa contra cada referência, por ativo, canal e segmento. Mostre sempre o denominador ao lado do percentual.
7. **Avaliar amostra.** Verifique conversões absolutas, duração e cobertura de ciclo semanal. Classifique: suficiente, tendência inicial ou insuficiente. Para declarar vencedor, a amostra por variante precisa ser de pelo menos `AB_MIN_SAMPLE_PER_VARIANT` (1000 sessões ou destinatários), ou atingir o tamanho amostral calculado e documentado no desenho do teste; além disso, exija pelo menos 7 dias e cobertura de ciclo semanal. Abaixo disso, a leitura é tendência inicial ou insuficiente.
8. **Aplicar significância ou critério.** Em teste controlado, registre `significance.method`, `p_value` e `confidence_level` (número em fração, por exemplo 0,93; a explicação textual vai em `significance.criterion`). Sem teste, omita `confidence_level`. O critério pré-registrado pode acrescentar exigências (duração, método), mas nunca relaxar o nível de confiança: `winner_declared = true` exige `confidence_level` >= `AB_CONFIDENCE_LEVEL` (0,95) e a amostra do passo 7. Sem teste controlado ou abaixo desses mínimos, `winner_declared = false`; sem teste, `significance.p_value = null`.
9. **Redigir achados.** Cada item de `findings` tem `finding`, `evidence` (números e fonte) e `statistical_note` (amostra, intervalo, confundidores).
10. **Montar o bloco epistêmico.** FATOS com `[FONTE:...]`; RECOMENDAÇÃO com Posição, Justificativa e Confiança (ALTA, MEDIA ou BAIXA); HIPÓTESE com validação requerida e risco se errada.
11. **Listar próximas ações.** Inclua coleta de dado faltante, continuação de teste, hipóteses a priorizar (`build-cro-hypotheses`) e registro de aprendizado (`register-learning`).
12. **Validar e persistir.** Aplique o checklist, valide o JSON contra o schema, grave o arquivo em `08-performance/`, registre `agent-run` e emita o envelope.

## Saída

- **Contrato:** `contracts/performance-analysis.schema.json`
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json`
- **Template humano:** `templates/performance-report-tmpl.md`
- **Envelope de handoff** (acrescentado em `handoffs.jsonl`):
  - `from_agent: cro-analyst`
  - `to_agent: knowledge-curator` (aprendizado) e `copy-chief` (decisão de ciclo)
  - `artifact_type: performance-analysis`
  - `status: ready` ou `needs_input`
  - `human_approval_required: false` para a análise; `true` se houver execução de teste em produção proposta

## Acceptance Criteria (Critérios de aceite)

- JSON válido e conforme o schema, com `meta` completo (`artifact_id` com prefixo `prf-`) e `analysis_phase: "result"` (E6); nesta fase são obrigatórios `period`, `metrics`, `sample_size`, `findings` e `winner_declared`, além de `hypotheses`, `epistemic` e `next_actions`.
- Cada achado tem evidência numérica rastreável aos dados fornecidos.
- `sample_size` preenchido e a suficiência de amostra avaliada.
- `winner_declared` coerente com `significance`: verdadeiro só com `confidence_level` >= 0,95 (`AB_CONFIDENCE_LEVEL`) e amostra mínima por variante atendida (`AB_MIN_SAMPLE_PER_VARIANT`).
- Nenhuma conclusão causal com mais de uma variável alterada.
- Lacunas de baseline, meta ou período anterior registradas em `assumptions` e refletidas em `confidence`.
- Bloco `epistemic` completo.
- `next_actions` com pelo menos uma ação concreta e um responsável sugerido.

## Quality gate e checklist

- **Checklist:** `checklists/cro-test-checklist.md` (escala 0-1; APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60 ou veto_condition).
- **Quality gate:** esta task não possui gate QG próprio; a conformidade é verificada pelo checklist e o aprendizado derivado passa pelo `QG-LEARNING` em `register-learning`.
- **Rework:** em REVIEW, no máximo 2 ciclos; em VETO, escalar ao `copy-chief`.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Período ou métrica ausente | `status: needs_input` com até 5 perguntas objetivas |
| Sem baseline, meta ou período anterior | Declarar a lacuna, usar referência provisória rotulada apenas se o solicitante aceitar, confiança máxima MEDIA |
| Amostra insuficiente | Emitir "tendência inicial, não conclusiva", `winner_declared = false`, prazo estimado para conclusão |
| Pedido de acesso a conta externa | Recusar e solicitar export; registrar `blocked` se insistirem; o acesso a contas é do humano ou da sessão principal |
| Dados inconsistentes (soma não fecha, métricas contraditórias) | Surfacear a contradição, não escolher um lado, pedir correção |
| Mais de uma variável alterada | Classificar achados causais como HIPÓTESE e propor teste de variável única |

## Handoff

- **Para `knowledge-curator`:** quando houver aprendizado (conclusivo ou não) a registrar. Contrato: `performance-analysis`.
- **Para `copy-chief`:** quando houver decisão de prioridade ou novo ciclo no `wf-performance-loop`.
- Se uma hipótese depender de novo claim sensível, marcar `needs_approval` e indicar G3 ao `copy-chief`.

## Exemplo

Entrada resumida (exemplo ilustrativo): campanha de captação para uma mentoria de gestão financeira para pequenas empresas; período de 14 dias; duas variações de headline; A com 118 conversões em 3.900 sessões, B com 141 conversões em 3.950 sessões; baseline de 2,9% fornecido; meta de 3,5%.

Trecho da saída:

```json
{
  "analysis_phase": "result",
  "period": {"start": "2026-10-01", "end": "2026-10-14"},
  "asset_ids": ["cvc-headline-a", "cvc-headline-b"],
  "metrics": {"A": {"sessoes": 3900, "conversoes": 118}, "B": {"sessoes": 3950, "conversoes": 141}},
  "baseline": {"taxa_conversao": 0.029},
  "target": {"taxa_conversao": 0.035},
  "sample_size": 7850,
  "findings": [
    {
      "finding": "A variação B converteu 3,57% contra 3,03% da variação A.",
      "evidence": "A: 118/3.900; B: 141/3.950 (dados fornecidos, 14 dias).",
      "statistical_note": "Mais de 1000 sessões por variação e 14 dias; diferença avaliada com teste de duas proporções (p bilateral aproximado de 0,18), abaixo do nível de confiança de 0,95."
    }
  ],
  "winner_declared": false,
  "significance": {"method": "teste de duas proporções", "p_value": 0.18, "confidence_level": 0.82, "criterion": "Mínimo de confiança 0,95 (AB_CONFIDENCE_LEVEL) não atingido; tendência favorável a B, não conclusiva."}
}
```

Observação do exemplo: a amostra por variante atende o mínimo, mas a confiança (0,82) fica abaixo de 0,95, então o resultado é "tendência favorável a B, não conclusiva"; a próxima ação é continuar o teste até o tamanho amostral calculado. Um critério pré-registrado não autoriza declarar vencedor abaixo do nível de confiança mínimo.

## Anti-padrões

- Declarar vencedor com amostra abaixo de `AB_MIN_SAMPLE_PER_VARIANT`, confiança abaixo de `AB_CONFIDENCE_LEVEL` ou sem critério pré-definido.
- Citar percentual sem denominador.
- Atribuir o efeito ao copy quando mídia, oferta ou público também mudaram.
- Preencher baseline com número inventado.
- Entregar métricas sem hipótese nem próxima ação.
- Acessar contas de GA4, Ads ou CRM (só exports fornecidos).
- Misturar dados de negócios diferentes.
