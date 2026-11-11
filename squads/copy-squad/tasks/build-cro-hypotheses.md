---
task: build-cro-hypotheses
name: build-cro-hypotheses
task_name: "Construir hipóteses de CRO"
version: "1.0.0"
squad: copy-squad
task_id: build-cro-hypotheses
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
- campo: performance_analysis
  tipo: contract:performance-analysis
  obrigatorio: true
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: learning_records
  tipo: contract:learning-record
  obrigatorio: false
Saida:
- campo: hypotheses
  tipo: contract:performance-analysis (campo hypotheses, com ice e priority)
  persistido_em: .data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json
input: [performance-analysis, brief, learning-record]
output: [performance-analysis]
action_items:
  - "Ler achados e lacunas da análise de performance"
  - "Consultar aprendizados anteriores para não repetir testes"
  - "Converter cada achado relevante em hipótese testável de variável única"
  - "Pontuar ICE (impacto, confiança, facilidade) com justificativa"
  - "Definir priority e ordenar a fila de testes"
  - "Sinalizar hipóteses que dependem de novo claim como needs_approval"
  - "Atualizar performance-analysis e emitir envelope"
acceptance_criteria:
  - "Toda hipótese com hypothesis, variable, expected_effect, test_design, priority e ice (impact, confidence, ease de 1 a 10)"
  - "Cada hipótese altera uma única variável"
  - "Cada ICE com justificativa curta registrada nas recomendações do bloco epistemic"
  - "Fila ordenada por score ICE (média) com desempate por facilidade"
  - "Nenhuma hipótese repete um teste já registrado como concluído sem justificar a repetição"
  - "Hipóteses com novo claim sensível marcadas para aprovação G3"
  - "Score do checklists/cro-test-checklist.md >= 0.80"
pre_condition: "performance-analysis existente para a campanha com achados e lacunas; brief disponível"
post_condition: "performance-analysis atualizado (nova versão) com hipóteses priorizadas; envelope emitido para knowledge-curator e copy-chief"
checklist: checklists/cro-test-checklist.md
quality_gate: null
human_gate: null
skill: copy-cro-hypothesis-builder
workflows: [wf-copy-production, wf-performance-loop]
performance:
  error_handling: "needs_input se não houver achados ou KPI primário; hipótese sem evidência é marcada BAIXA confiança, nunca omitida da justificativa"
---

# Task: Construir hipóteses de CRO

## Objetivo

Transformar achados de performance em hipóteses de otimização testáveis, de variável única, priorizadas por ICE, de modo que o squad saiba o que testar primeiro e por quê. A task não declara resultados e não escreve copy: ela produz a fila de experimentos que orienta os copywriters e o desenho de testes.

## Quando usar / quando não usar

**Usar quando:**
- Existe `performance-analysis` com achados e o squad precisa decidir o que testar.
- O `wf-performance-loop` chega à fase de hipóteses.
- Um teste terminou e é preciso planejar o seguinte.
- O `copy-chief` pede um backlog de otimização para uma peça ou campanha.

**Não usar quando:**
- Não há dados nem análise (execute antes `analyze-performance`).
- O pedido é desenhar o teste de uma hipótese já escolhida (use `design-ab-test`).
- O pedido é gerar ângulos novos de copy (papel do `hook-angle-creator`).

## Entradas

| Campo | Contrato / formato | Obrigatório | Origem |
|---|---|---|---|
| performance_analysis | `contract:performance-analysis` | Sim | `.data/copy-squad/{business}/{campaign_id}/08-performance/` |
| brief | `contract:brief` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| learning_records | `contract:learning-record` | Não | `retrieve-knowledge` (knowledge-curator) |
| copy atual da peça | `contract:conversion-copy` ou equivalente | Recomendado | `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/` |
| restrições do negócio (tráfego, ferramenta de teste, prazos) | texto do solicitante | Não | Solicitante |

## Passos

1. **Ler achados e lacunas.** Liste cada achado de `findings` e cada item de `next_actions` ligado a otimização. Descarte achados sem evidência numérica.
2. **Consultar aprendizados.** Peça ao `knowledge-curator` (`retrieve-knowledge`) learnings da mesma oferta, público, canal e formato. Registre testes já concluídos para evitar repetição.
3. **Mapear a jornada.** Identifique onde está a perda: atenção (anúncio, assunto de e-mail), interesse (headline, hero), decisão (oferta, prova, preço), ação (CTA, formulário).
4. **Escrever hipóteses no formato padrão.** "Se mudarmos {variável} de {A} para {B}, então {métrica primária} deve {efeito}, porque {razão baseada em evidência ou aprendizado}."
5. **Garantir variável única.** Cada hipótese muda exatamente um elemento (título, CTA, posição da prova, oferta, extensão, formato). Hipóteses compostas são divididas.
6. **Definir efeito esperado mensurável.** Direção e ordem de grandeza (por exemplo, aumento relativo de 10% no clique do CTA), rotulado como expectativa, não como fato.
7. **Pontuar ICE.** Impacto (efeito potencial no KPI primário), Confiança (força da evidência e dos aprendizados) e Facilidade (esforço de produção e de implementação), de 1 a 10 cada. Registre a justificativa em uma linha por critério.
8. **Calcular score e prioridade.** Score = média de impacto, confiança e facilidade. Prioridade `high` para os maiores scores e os que atacam o principal ponto de perda; `medium` e `low` para os demais. Em empate, vence a maior facilidade.
9. **Rascunhar o `test_design`.** Escreva em uma frase o desenho preliminar (variável, métrica primária, critério de parada); o desenho completo é feito em `design-ab-test`.
10. **Sinalizar riscos.** Hipóteses que exigem novo claim (preço, garantia, resultado, autoridade, depoimento, comparativo, saúde, financeiro) são marcadas `needs_approval` e vinculadas ao gate G3.
11. **Montar o bloco epistêmico.** Recomendações com Posição, Justificativa e Confiança; hipóteses com "sem evidência direta" quando for o caso, validação requerida e risco se errada.
12. **Validar e persistir.** Aplique o checklist, grave nova versão do `performance-analysis`, registre `agent-run` e emita o envelope.

## Saída

- **Contrato:** `contracts/performance-analysis.schema.json` (campo `hypotheses`, com `priority` e `ice`).
- **Fase pré-teste (E6):** esta task entrega `performance-analysis` com `analysis_phase: "planning"`. Nessa fase só `hypotheses` e `next_actions` são obrigatórios, além de `meta` e `epistemic`. Os campos de resultado (`period`, `metrics`, `sample_size`, `findings`, `winner_declared`) ficam ausentes: não preencha valores neutros nem estime números antes do teste. Eles só se tornam obrigatórios na fase `result`, produzida por `analyze-performance`.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json` (nova versão; a versão anterior é preservada).
- **Template humano:** `templates/performance-report-tmpl.md` (seção Hipóteses e Fila de testes).
- **Envelope de handoff:**
  - `from_agent: cro-analyst`; `to_agent: copy-chief` (priorização) e `knowledge-curator` (acompanhamento)
  - `artifact_type: performance-analysis`; `status: ready`
  - `human_approval_required: true` se alguma hipótese envolver novo claim (gate G3)

## Acceptance Criteria (Critérios de aceite)

- 100% das hipóteses com os seis campos obrigatórios e o objeto `ice`.
- Todas as hipóteses com variável única e métrica primária identificável.
- Ordenação consistente com o score ICE e prioridade coerente.
- Justificativa registrada para cada pontuação de ICE.
- Nenhuma repetição injustificada de teste já concluído.
- Hipóteses sensíveis sinalizadas para G3.
- Nenhuma afirmação de resultado: tudo é expectativa.

## Quality gate e checklist

- **Checklist:** `checklists/cro-test-checklist.md` (itens de hipótese, ICE e variável única).
- **Quality gate:** sem QG próprio; a verificação é pelo checklist (APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60).
- **Rework:** máximo 2 ciclos; veto escala ao `copy-chief`.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Sem performance-analysis | Executar `analyze-performance` primeiro ou `needs_input` |
| Achados sem evidência numérica | Descartar do backlog e registrar a lacuna |
| Hipótese composta (várias variáveis) | Dividir em hipóteses independentes |
| Aprendizado anterior contradiz a hipótese | Reduzir confiança, citar o learning e exigir justificativa para repetir |
| Sem acesso à ferramenta de teste | Manter a hipótese e registrar a limitação em `test_design` |
| Volume de tráfego inviável para o MDE | Marcar facilidade baixa e sugerir teste sequencial ou métrica intermediária |

## Handoff

- **Para `copy-chief`:** fila priorizada, para decidir o próximo ciclo e acionar produtores (`hook-angle-creator`, `conversion-copywriter`) para criar as variações dos testes aprovados.
- **Para `knowledge-curator`:** hipóteses em acompanhamento, para registro com `learning_status: testing` quando o teste começar.
- Para executar qualquer teste em produção, o `copy-publisher` prepara o pacote de aprovação (G4).

## Exemplo

Entrada resumida (exemplo ilustrativo): página de vendas de um SaaS de fluxo de caixa; o `performance-analysis` mostra queda de 62% do scroll entre o hero e a seção de preço e baixo clique no CTA de preço.

Trecho da saída:

```json
{
  "analysis_phase": "planning",
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "prf-lp-saas-hipoteses-20261110",
    "artifact_type": "performance-analysis",
    "campaign_id": "camp-exemplo",
    "business": "exemplo-negocio",
    "produced_by": "cro-analyst",
    "produced_at": "2026-11-10T14:30:00-03:00",
    "version": 1,
    "prompt_version": "1.0.0",
    "model": "sonnet",
    "status": "ready",
    "confidence": 0.6,
    "risk_level": "medium",
    "assumptions": ["Exemplo ilustrativo; dados não são resultados reais."]
  },
  "hypotheses": [
    {
      "hypothesis": "Se movermos o bloco de garantia para acima do botão de preço, então o clique no CTA de preço deve aumentar, porque a objeção de risco aparece antes da decisão.",
      "variable": "posição do bloco de garantia",
      "expected_effect": "aumento relativo de 10% na taxa de clique do CTA de preço",
      "test_design": "A/B de variável única; métrica primária: clique no CTA; critério de parada: o pré-registrado no design-ab-test (amostra mínima por variante e confiança de 0,95).",
      "priority": "high",
      "ice": {"impact": 8, "confidence": 6, "ease": 9}
    },
    {
      "hypothesis": "Se trocarmos o título do hero de benefício genérico para a dor específica de fluxo de caixa, então o scroll até a seção de preço deve aumentar.",
      "variable": "título do hero",
      "expected_effect": "aumento relativo de 8% no scroll até a seção de preço",
      "test_design": "A/B de variável única; métrica primária: scroll até preço; critério de parada: o pré-registrado no design-ab-test (amostra mínima por variante e confiança de 0,95).",
      "priority": "medium",
      "ice": {"impact": 7, "confidence": 5, "ease": 8}
    }
  ],
  "epistemic": {
    "facts": ["Queda de 62% do scroll entre o hero e a seção de preço [FONTE: performance-analysis anterior, exemplo ilustrativo]."],
    "recommendations": ["Posição: testar primeiro a posição da garantia. Justificativa: maior score ICE. Confiança: MEDIA."],
    "hypotheses": ["Mover a garantia aumenta o clique no CTA de preço (sem evidência direta; validação requerida: teste A/B)."]
  },
  "next_actions": [
    "Desenhar o teste da hipótese de maior score com design-ab-test.",
    "Registrar as hipóteses em acompanhamento com o knowledge-curator."
  ]
}
```

Exemplo completo e válido da fase de planejamento: os campos de resultado estão ausentes de propósito. Scores (exemplo): primeira hipótese (8+6+9)/3 = 7,7; segunda (7+5+8)/3 = 6,7.

## Anti-padrões

- Hipóteses vagas ("melhorar a página") sem variável nem efeito mensurável.
- Várias variáveis na mesma hipótese.
- ICE sem justificativa ou todos os itens com a mesma nota.
- Priorizar pelo gosto de quem pediu.
- Repetir teste já concluído sem justificar.
- Afirmar efeito como fato antes do teste.
- Propor teste que exige claim novo sem sinalizar G3.
