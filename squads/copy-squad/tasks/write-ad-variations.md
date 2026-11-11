---
task: write-ad-variations
name: write-ad-variations
task_name: "Gerar variações de anúncio para teste"
version: "1.0.0"
squad: copy-squad
task_id: write-ad-variations
category: production
difficulty: intermediate
responsavel: '@conversion-copywriter'
responsavel_type: Agent
responsible_executor: conversion-copywriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 30-60min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: angle
  tipo: contract:angles
  obrigatorio: true
- campo: research_packet
  tipo: contract:research-packet
  obrigatorio: true
- campo: offer_canvas
  tipo: contract:offer-canvas
  obrigatorio: true
- campo: performance_analysis
  tipo: contract:performance-analysis
  obrigatorio: false
Saida:
- campo: conversion_copy
  tipo: contract:conversion-copy
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, angles, research-packet, offer-canvas, performance-analysis]
output: [conversion-copy]
action_items:
  - "Confirmar canal, formato e limites de data/channel-specs.yaml"
  - "Definir a variável testada e a hipótese de cada lote"
  - "Escrever variações de headline, corpo e CTA respeitando limites"
  - "Marcar claims, provas e needs_approval por variação"
  - "Registrar hipótese e ordem de prioridade do teste"
  - "Persistir v{n} e emitir envelope ao copy-editor"
acceptance_criteria:
  - "Draft válido no schema conversion-copy com format ad"
  - "Mínimo de 5 variações por elemento testado, cada uma com variation_id, element, text e hypothesis"
  - "Cada lote muda uma única variável"
  - "0 estouros dos limites de caracteres do canal em data/channel-specs.yaml"
  - "0 claims sensíveis sem proof_id ou sem needs_approval"
  - "0 urgências ou escassez sem legitimate_urgency.exists true"
pre_condition: "Brief aprovado (G1 em medium ou high) e ângulo aprovado (G2 só em high ou campanha multi-ativo), research packet e offer canvas válidos, canal informado"
post_condition: "Variações persistidas em v{n}, hipótese por variação registrada e envelope emitido ao copy-editor"
checklist: checklists/conversion-copy-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: copy-ad-variation-generator
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop]
performance:
  error_handling: "needs_input se canal ou limite não estiver definido; truncar com reescrita, nunca com corte seco; anúncio com claim sensível sobe para high"
---

# Task: Gerar variações de anúncio para teste

## Objetivo

Gerar variações de headline, corpo e CTA de anúncio prontas para teste A/B, a partir do brief, do ângulo aprovado e das provas verificadas, respeitando os limites de cada canal declarados em `data/channel-specs.yaml`. Cada variação carrega uma hipótese explícita para que o cro-analyst possa ler o resultado sem ambiguidade. Implementa o Ad Variation Generator.

## Quando usar / quando não usar

**Usar quando:**
- A campanha precisa de anúncios pagos ou orgânicos patrocinados em um ou mais canais.
- Na fast lane (`wf-fast-variation`), para novas variações de uso interno/teste (backlog) de uma peça já aprovada. Se a variação for veiculada, sai da pista rápida: anúncio pago é risco high (D6), com `prepare-approval-package` e G4.
- No ciclo de performance, quando o cro-analyst entrega hipóteses para novos testes.

**Não usar quando:**
- Faltam brief, ângulo ou offer canvas.
- A tarefa é página de destino (usar `write-landing-page`) ou apenas CTA (usar `optimize-ctas`).
- O pedido envolve comprar mídia, subir anúncio ou ativar campanha (ação exclusiva do copy-publisher após approval-decision válido).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | brief | Sim | brief-master |
| angle | angles (aprovado) | Sim | hook-angle-creator |
| research_packet | research-packet | Sim | research-analyst |
| offer_canvas | offer-canvas | Sim | offer-strategist |
| performance_analysis | performance-analysis | Não | cro-analyst (iterações) |

## Passos

1. **Definir canal e formato.** Confirmar canal (por exemplo, rede social paga, busca, display) e formato do anúncio; abrir `data/channel-specs.yaml` e anotar os limites de caracteres de cada elemento.
2. **Verificar insumos.** Validar brief, ângulo, research packet e offer canvas; sem eles, `needs_input`.
3. **Escolher a variável do lote.** Definir uma única variável por lote (ângulo da headline, tipo de prova, formato do CTA, tom). Registrar a hipótese principal, por exemplo "pergunta de dor aumenta o CTR frente à afirmação de benefício".
4. **Selecionar provas e claims permitidos.** Listar do offer canvas os proof_ids verificados; qualquer claim de preço, garantia, resultado ou comparativo sem prova vai para needs_approval.
5. **Escrever as variações.** Para cada elemento (headline, corpo, CTA) produzir pelo menos 5 variações distintas, cada uma com `variation_id`, `element`, `text` e `hypothesis`. Variar a estrutura (pergunta, afirmação, número verificável, contraste, história curta), não apenas sinônimos.
6. **Adaptar ao estágio de consciência.** Públicos unaware pedem sintoma; problem_aware pedem problema; solution_aware pedem mecanismo; product_aware e most_aware pedem prova e oferta.
7. **Validar limites.** Contar caracteres de cada variação e reescrever as que excedem; registrar em assumptions qualquer adaptação por limite.
8. **Aplicar política ética.** Remover urgência sem `legitimate_urgency.exists == true`, promessas absolutas e comparativos sem fonte (CS-CV-002, CS-CV-004).
9. **Priorizar o teste.** Ordenar as variações por hipótese e risco, indicando um controle (baseline) e as variantes; não declarar vencedor.
10. **Persistir e entregar.** Gravar `04-drafts/{asset_id}/v{n}.json`, emitir o envelope ao copy-editor e registrar o agent-run.

## Saída

- **Contrato:** `contracts/conversion-copy.schema.json`, com `format: "ad"`, `sections` (por exemplo, `headline`, `corpo`, `cta`), `ctas` e `variations`.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Renderização humana:** `templates/copy-deck-tmpl.md`.
- **Envelope:** from `conversion-copywriter`, to `copy-editor`, artifact_type `conversion-copy`, status `ready` ou `needs_approval`, risk_level `low` só para variação de uso interno/teste sem claim sensível; anúncio pago a veicular é sempre `high` (D6). Use só claims pré-aprovados; claim novo vira `needs_approval` e vai a G3 (D10).

## Acceptance Criteria (Critérios de aceite)

- Mínimo de 5 variações por elemento testado, todas com hipótese.
- Uma única variável por lote de teste.
- 0 estouros de limite de caracteres; 0 claims sensíveis sem tratamento.
- Variações realmente distintas em estrutura, não apenas em palavras.
- Controle (baseline) identificado e prioridade de teste registrada.
- Envelope emitido com risk_level correto.

## Quality gate e checklist

- **Quality gate:** QG-DRAFT, executor copy-chief (D7), com `checklists/conversion-copy-checklist.md`; self_check_by: conversion-copywriter.
- **Checklist:** `checklists/conversion-copy-checklist.md`.
- Risco low vale só para uso interno (variações de headline e CTA para backlog/teste sem claim sensível); segue a fast lane com QG-COMPLIANCE leve e amostragem determinística (`approval_tools.py sample`, SAMPLING_RATE_LOW de 0.20, registrada como `internal_use`). Anúncio pago a veicular é high e exige G4; com claim sensível exige também G3.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Canal sem limites em channel-specs | `needs_input`; usar limites conservadores e registrar em assumptions |
| Poucas provas verificadas | Priorizar ângulos de problema e mecanismo; sinalizar a lacuna ao research-analyst |
| Variação excede limite | Reescrever; nunca truncar no meio de uma palavra |
| Hipótese ausente | A variação não segue; preencher ou remover |
| Resultado de performance anterior indica fadiga | Propor novo ângulo ao hook-angle-creator via copy-chief |
| Rework acima de 2 ciclos | Escalar ao copy-chief |

## Handoff

Entrega ao `copy-editor`. Em uso interno (low), a amostragem é determinística; anúncio pago (high) segue edição, voz, compliance, G3 e G4. Depois da aprovação, o copy-publisher entrega o pacote ao responsável pela mídia; o squad não compra nem ativa anúncios.

## Exemplo

Entrada resumida (ilustrativa): SaaS de fluxo de caixa, público solution_aware, canal de redes sociais pagas, variável testada: estrutura da headline.

```json
{
  "format": "ad",
  "sections": [
    {"section": "headline", "copy": "Veja para onde vai o dinheiro da sua empresa.", "claims": [], "proof_used": [], "needs_approval": []}
  ],
  "variations": [
    {"variation_id": "v-h1", "element": "headline", "text": "Seu caixa fecha o mês no vermelho? Entenda por quê.", "hypothesis": "Pergunta de dor gera mais cliques que a afirmação de benefício."},
    {"variation_id": "v-h2", "element": "headline", "text": "Fluxo de caixa em uma tela, sem planilha.", "hypothesis": "Mecanismo concreto atrai solution_aware."},
    {"variation_id": "v-h3", "element": "headline", "text": "Pare de descobrir o saldo só no fim do mês.", "hypothesis": "Contraste temporal aumenta a identificação."}
  ]
}
```

## Anti-padrões

- Misturar duas variáveis no mesmo lote e depois atribuir causa.
- Variar só sinônimos e chamar de teste.
- Ignorar limites de caracteres do canal.
- Declarar vencedor sem dados (decisão do cro-analyst).
- Usar números, prêmios ou depoimentos sem fonte para "dar força".
- Tratar anúncio com claim sensível como baixo risco.
