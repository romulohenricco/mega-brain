---
task: write-landing-page
name: write-landing-page
task_name: "Escrever landing page de conversão"
version: "1.0.0"
squad: copy-squad
task_id: write-landing-page
category: production
difficulty: advanced
responsavel: '@conversion-copywriter'
responsavel_type: Agent
responsible_executor: conversion-copywriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 60-120min
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
- campo: audience_voc
  tipo: contract:audience-voc
  obrigatorio: false
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: false
Saida:
- campo: conversion_copy
  tipo: contract:conversion-copy
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, angles, research-packet, offer-canvas, audience-voc, brand-voice-guide]
output: [conversion-copy]
action_items:
  - "Verificar insumos aprovados (brief, ângulo, research packet, offer canvas)"
  - "Definir ordem das seções pelo estágio de consciência"
  - "Escrever hero, problema, mecanismo, prova, oferta, objeções, FAQ e CTA"
  - "Marcar claims, proof_used e needs_approval por seção"
  - "Gerar CTAs e variações de hero para teste"
  - "Autochecar, persistir nova versão e emitir envelope ao copy-editor"
acceptance_criteria:
  - "Draft válido no schema conversion-copy com format landing_page ou sales_page"
  - "Seções mínimas presentes: hero, problema, mecanismo, prova, oferta, objeções/FAQ, CTA final"
  - "100% dos claims sensíveis com proof_id verificado ou registrados em needs_approval"
  - "0 menções de urgência sem legitimate_urgency.exists true"
  - "Abertura coerente com o awareness_stage do brief"
  - "CTA final específico (verbo + objeto + benefício) coerente com a ação do brief"
pre_condition: "Brief aprovado (G1 quando risco medium ou high), ângulo aprovado (G2 só em high ou campanha multi-ativo), research packet e offer canvas válidos"
post_condition: "Draft v{n} persistido, envelope de handoff emitido ao copy-editor e itens needs_approval consolidados para G3"
checklist: checklists/conversion-copy-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: copy-landing-page-architect
workflows: [wf-copy-production, wf-campaign-launch]
performance:
  error_handling: "needs_input listando insumos ausentes; nunca inventar prova, preço ou garantia; claim sem prova vira needs_approval"
---

# Task: Escrever landing page de conversão

## Objetivo

Produzir o draft de uma landing page ou página de vendas, estruturado por seções, a partir de brief, ângulo aprovado, research packet e offer canvas. A task entrega um artefato `conversion-copy` rastreável: cada afirmação aponta para uma prova ou está marcada como pendente de aprovação. É a implementação operacional do Landing Page Architect (hero, problema, mecanismo, prova, oferta, FAQ, CTA).

## Quando usar / quando não usar

**Usar quando:**
- O execution-plan prevê página de captura, landing page de campanha ou página de vendas.
- Existem brief, ângulo aprovado, research packet e offer canvas validados.
- É preciso reescrever uma página a partir de performance-analysis (nova versão v+1).

**Não usar quando:**
- Faltam brief, ângulo ou research packet (devolver needs_input ao copy-chief).
- O pedido é jornada de e-mail (usar `build-email-sequence`) ou conteúdo editorial (content-copywriter).
- O pedido é apenas variações de anúncio (usar `write-ad-variations`) ou CTAs (usar `optimize-ctas`).
- O pedido é publicar ou alterar uma página no ar (ação externa exclusiva do copy-publisher após approval-decision válido).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | brief | Sim | brief-master, `01-strategy/brief.json` |
| angle | angles (ângulo aprovado) | Sim | hook-angle-creator, `03-angles/angles.json` |
| research_packet | research-packet | Sim | research-analyst, `02-research/research-packet.json` |
| offer_canvas | offer-canvas | Sim | offer-strategist, `01-strategy/offer-canvas.json` |
| audience_voc | audience-voc | Não | audience-voc, `01-strategy/audience-voc.json` |
| brand_voice_guide | brand-voice-guide | Não | brand-voice-guardian, `_brand/brand-voice-guide.json` |

## Passos

1. **Resolver contexto.** Identificar business, campaign_id, brief_id, angle_id, asset_id e o formato (landing_page, sales_page). Conferir no brief o primary_kpi, a ação desejada e o awareness_stage.
2. **Verificar insumos e gates.** Validar brief, ângulo, research packet e offer canvas nos schemas. Conferir G1 (brief) quando o risco for medium ou high e G2 (ângulo) apenas em risco high ou campanha multi-ativo. Se faltar algo, parar com `needs_input` (CS-CV-001).
3. **Mapear provas e claims disponíveis.** Listar do offer canvas os proof_ids verificados (`verified: true`, `usage_rights: granted`), o preço, a garantia e a legitimate_urgency. Tudo o que não estiver aqui não pode aparecer como fato.
4. **Definir a ordem pelo estágio de consciência.** unaware abre pela história/sintoma; problem_aware pelo problema; solution_aware pela comparação de mecanismos; product_aware por prova e diferenciais; most_aware pela oferta e CTA (CS-CV-003).
5. **Escrever as seções.** Hero (promessa específica + subtítulo + CTA), problema (linguagem do cliente), mecanismo (como funciona, sem jargão), prova (somente proof_ids verificados), oferta (o que está incluído, preço e condições do canvas), objeções (resposta com prova e mecanismo), reversão de risco (garantia do canvas), FAQ e CTA final.
6. **Registrar claims por seção.** Para cada seção preencher `claims`, `proof_used` (proof_ids) e `needs_approval` (claim sem prova, preço ou garantia não confirmados). Aplicar CS-CV-002.
7. **Aplicar a política de urgência.** Remover qualquer urgência ou escassez sem `legitimate_urgency.exists == true` (CS-CV-004).
8. **Gerar CTAs e variações de teste.** Criar 3 a 5 variações do hero e do CTA, uma variável por variação, com hipótese (CS-CV-005, CS-CV-006).
9. **Conferir limites do canal.** Validar títulos, meta descrições e textos de botão contra `data/channel-specs.yaml`.
10. **Autochecar e persistir.** Rodar `checklists/conversion-copy-checklist.md` como controle do produtor, calcular confidence e risk_level, gravar `04-drafts/{asset_id}/v{n}.json` (nunca sobrescrever versão anterior) e emitir o envelope ao copy-editor.

## Saída

- **Contrato:** `contracts/conversion-copy.schema.json` (campos: meta, brief_id, angle_id, format, awareness_stage, sections, ctas, variations, confidence).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Renderização humana:** `templates/copy-deck-tmpl.md` (copy deck legível para revisão).
- **Envelope de handoff** (append em `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl`): from_agent `conversion-copywriter`, to_agent `copy-editor`, artifact_type `conversion-copy`, status `ready` ou `needs_approval`, risk_level conforme os claims, human_approval_required verdadeiro quando houver needs_approval, gate `G3` quando houver claims sensíveis.

## Acceptance Criteria (Critérios de aceite)

- Schema conversion-copy válido, com `format` igual a `landing_page` ou `sales_page`.
- Seções mínimas: hero, problema, mecanismo, prova, oferta, objeções/FAQ e CTA final.
- 100% dos claims de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde e financeiro com proof_id verificado ou em needs_approval.
- 0 depoimentos, números ou prêmios sem fonte; 0 urgências sem legitimate_urgency real.
- Abertura coerente com o estágio de consciência do brief.
- Entre 3 e 5 variações de hero/CTA, cada uma com uma variável e hipótese.
- Limites de caracteres de channel-specs respeitados (0 estouros).

## Quality gate e checklist

- **Quality gate:** QG-DRAFT (executor: copy-chief, com `checklists/conversion-copy-checklist.md`, D7; self_check_by: conversion-copywriter; APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60).
- **Checklist:** `checklists/conversion-copy-checklist.md`. O produtor usa o checklist como autochecagem; a pontuação oficial do gate é do copy-editor.
- Revisões seguintes: edição (QG-EDIT), voz da marca (QG-BRAND) e compliance (QG-COMPLIANCE); landing page é risco high por política.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Falta insumo obrigatório | `needs_input` com a lista exata; não escrever |
| Prova ausente para claim | Reescrever sem o claim ou mover para needs_approval; risk_level high |
| Preço ou garantia não confirmados | Não escrever valor; usar marcador `[a confirmar no offer canvas]` e registrar needs_approval |
| Estágio de consciência ausente | Assumir problem_aware, registrar em assumptions e pedir confirmação |
| Conflito entre ângulo e voz da marca | Priorizar o brand-voice-guide para tom e o ângulo para a tese; registrar em assumptions |
| Retorno do editor, compliance ou approval-owner | Criar v+1 com apenas as correções pedidas; preservar a versão anterior |
| Rework acima de 2 ciclos | Escalar ao copy-chief (on_veto do gate) |

## Handoff

Entrega ao `copy-editor` com o envelope descrito em Saída. Após o QG-DRAFT pelo copy-chief, o copy-editor edita a concisão e a clareza (QG-EDIT, executor copy-chief) e encaminha ao brand-voice-guardian e ao compliance-checker. O copy-publisher só prepara o approval-request depois dessas revisões. Esta task nunca publica nem altera página.

## Exemplo

Entrada resumida (ilustrativa): mentoria de gestão financeira para pequenas empresas; público problem_aware; ângulo `ang-caixa-sem-surpresa`; offer canvas com garantia ainda não confirmada.

```json
{
  "meta": {"schema_version": "1.0.0", "artifact_id": "cvc-mentoria-lp-v1", "artifact_type": "conversion-copy", "campaign_id": "camp-mentoria-fluxo", "business": "exemplo-negocio", "produced_by": "conversion-copywriter", "produced_at": "2026-11-10T10:00:00Z", "version": 1, "status": "needs_approval", "risk_level": "high"},
  "brief_id": "brf-mentoria-fluxo",
  "angle_id": "ang-caixa-sem-surpresa",
  "format": "landing_page",
  "awareness_stage": "problem_aware",
  "sections": [
    {"section": "hero", "copy": "Descubra para onde vai o dinheiro da sua empresa e organize o fluxo de caixa.", "cta": "Quero organizar meu fluxo de caixa", "claims": [], "proof_used": [], "needs_approval": []},
    {"section": "risco", "copy": "[Garantia a confirmar no offer canvas]", "claims": ["garantia"], "proof_used": [], "needs_approval": ["termos da garantia não confirmados"]}
  ],
  "confidence": 0.7
}
```

## Anti-padrões

- Escrever com base apenas no brief, sem ângulo aprovado ou research packet.
- Preencher o espaço de prova com depoimento ou número plausível.
- Reutilizar a mesma abertura para todos os estágios de consciência.
- Esconder o CTA no fim sem transições entre seções.
- Colocar preço ou garantia que não estejam no offer canvas.
- Sobrescrever a versão anterior em vez de criar v+1.
- Pular o copy-editor e o compliance por tratar a página como urgente.
