---
task: optimize-ctas
name: optimize-ctas
task_name: "Otimizar CTAs por intenção, funil e canal"
version: "1.0.0"
squad: copy-squad
task_id: optimize-ctas
category: production
difficulty: intermediate
responsavel: '@conversion-copywriter'
responsavel_type: Agent
responsible_executor: conversion-copywriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 15-45min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: current_copy
  tipo: contract:conversion-copy
  obrigatorio: false
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
input: [brief, conversion-copy, offer-canvas, performance-analysis]
output: [conversion-copy]
action_items:
  - "Mapear cada CTA por intenção, estágio do funil e canal"
  - "Diagnosticar CTAs atuais (vagos, desalinhados, sem benefício)"
  - "Reescrever CTAs com verbo, objeto e benefício"
  - "Gerar variações de teste com uma variável e hipótese"
  - "Validar limites de caracteres do canal"
  - "Persistir v{n} e emitir envelope ao copy-editor"
acceptance_criteria:
  - "Draft válido no schema conversion-copy com ctas e variations preenchidos"
  - "Cada CTA mapeado a intenção, estágio do funil e canal"
  - "Pelo menos 5 variações por CTA principal, cada uma com hipótese"
  - "0 CTAs genéricos ('saiba mais', 'clique aqui') quando existe ação específica"
  - "0 estouros de limite de caracteres; 0 urgência sem legitimate_urgency real"
pre_condition: "Brief e offer canvas válidos; canal e ação desejada definidos"
post_condition: "CTAs e variações persistidos em v{n}; envelope emitido ao copy-editor"
checklist: checklists/conversion-copy-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: copy-cta-optimizer
workflows: [wf-copy-production, wf-fast-variation, wf-performance-loop]
performance:
  error_handling: "needs_input se a ação desejada não estiver definida; CTA com promessa sensível vira needs_approval; nunca prometer o que a página não entrega"
---

# Task: Otimizar CTAs por intenção, funil e canal

## Objetivo

Criar ou reescrever chamadas para ação alinhadas à intenção do visitante, ao estágio do funil e ao canal, transformando CTAs vagos em ações específicas com benefício claro, e entregando variações testáveis com hipótese. Implementa o CTA Optimizer do squad.

## Quando usar / quando não usar

**Usar quando:**
- Uma página, anúncio, e-mail ou vídeo tem CTAs genéricos ou desalinhados com a ação do brief.
- O cro-analyst indicou hipótese de CTA para teste.
- Na fast lane, para variações de CTA de uso interno/teste em uma peça já aprovada. CTA veiculado em anúncio pago é high; em página alterada, no mínimo medium, com G4 (D6).

**Não usar quando:**
- A ação desejada ainda não foi definida no brief (devolver needs_input ao brief-master).
- O problema é a oferta ou o ângulo, não o CTA (escalar ao copy-chief).
- O CTA é texto de interface de produto (ux-writer).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | brief | Sim | brief-master (ação e KPI primário) |
| current_copy | conversion-copy | Não | conversion-copywriter ou peça existente |
| offer_canvas | offer-canvas | Sim | offer-strategist |
| performance_analysis | performance-analysis | Não | cro-analyst |

## Passos

1. **Inventariar os CTAs.** Listar cada CTA existente ou necessário, com posição (hero, meio, final, rodapé, anúncio, e-mail), canal e ação desejada pelo brief.
2. **Classificar intenção e funil.** Para cada CTA registrar a intenção do visitante (aprender, comparar, decidir, comprar, voltar) e o estágio do funil (topo, meio, fundo, pós-venda), vinculando ao awareness_stage.
3. **Diagnosticar.** Marcar os CTAs vagos (sem verbo ou objeto), desalinhados (pedem compra a quem está aprendendo), sem benefício ou que prometem mais do que o destino entrega.
4. **Reescrever com a fórmula verbo + objeto + benefício.** Exemplo ilustrativo: "Baixar o guia de fluxo de caixa" em vez de "Saiba mais". Ajustar o grau de compromisso ao estágio: topo pede ações de baixo atrito; fundo pede ação direta.
5. **Verificar a coerência com o destino.** O CTA não pode prometer algo que a página, o formulário ou o e-mail seguinte não entrega; checar preço e garantia contra o offer canvas.
6. **Gerar variações de teste.** Para cada CTA principal, no mínimo 5 variações que mudam uma variável (verbo, benefício, grau de compromisso, primeira pessoa, microcopy de apoio), cada uma com hipótese.
7. **Validar limites do canal.** Conferir `data/channel-specs.yaml` (botões, anúncios, assuntos) e reescrever o que exceder.
8. **Aplicar política ética.** Sem urgência ou escassez fabricadas; CTAs com promessa de resultado ou preço sem prova entram em needs_approval.
9. **Priorizar o teste.** Indicar controle e variantes, sem declarar vencedor.
10. **Persistir e entregar.** Gravar `v{n}` em `04-drafts/{asset_id}/`, emitir envelope ao copy-editor e registrar o agent-run.

## Saída

- **Contrato:** `contracts/conversion-copy.schema.json` com `ctas` (lista de CTAs finais) e `variations` (cada uma com variation_id, element, text e hypothesis). Se a otimização for de uma peça existente, preservar `brief_id`, `angle_id` e `format` da peça de origem.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope:** from `conversion-copywriter`, to `copy-editor`, artifact_type `conversion-copy`, status `ready` (ou `needs_approval`), risk_level `low` só para uso interno/teste sem claim sensível; CTA que será publicado tem no mínimo `medium` (D6).

## Acceptance Criteria (Critérios de aceite)

- Cada CTA tem intenção, estágio do funil e canal documentados em assumptions ou nas seções.
- Todos os CTAs finais seguem verbo + objeto + benefício.
- Mínimo de 5 variações por CTA principal, cada uma com uma variável e hipótese.
- Nenhum CTA promete algo que o destino não entrega.
- 0 estouros de limite do canal.

## Quality gate e checklist

- **Quality gate:** QG-DRAFT, executor copy-chief (D7), com `checklists/conversion-copy-checklist.md`; self_check_by: conversion-copywriter. Em uso interno (low), segue a fast lane com QG-COMPLIANCE leve e amostragem determinística.
- **Checklist:** `checklists/conversion-copy-checklist.md`.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Ação desejada indefinida | `needs_input` ao brief-master via copy-chief |
| Funil com várias ações concorrentes | Propor uma ação primária e demais secundárias; registrar a decisão em assumptions |
| CTA depende de condição comercial não confirmada | Marcar needs_approval e usar texto neutro |
| Dados de performance insuficientes | Não indicar vencedor; apenas hipóteses de teste |
| Rework acima de 2 ciclos | Escalar ao copy-chief |

## Handoff

Entrega ao `copy-editor`, que valida clareza e concisão (QG-EDIT). O cro-analyst usa as hipóteses das variações para desenhar o teste; o squad não altera páginas ou anúncios em produção.

## Exemplo

Entrada resumida (ilustrativa): página de captura de material gratuito para um SaaS de fluxo de caixa; CTA atual "Saiba mais".

```json
{
  "ctas": ["Baixar o guia de fluxo de caixa", "Quero meu guia gratuito"],
  "variations": [
    {"variation_id": "v-c1", "element": "cta", "text": "Baixar o guia gratuito", "hypothesis": "Verbo direto com 'gratuito' reduz o atrito frente a 'Saiba mais'."},
    {"variation_id": "v-c2", "element": "cta", "text": "Quero organizar meu caixa", "hypothesis": "Primeira pessoa com benefício aumenta o clique."},
    {"variation_id": "v-c3", "element": "cta", "text": "Receber o guia no meu e-mail", "hypothesis": "Explicitar o canal de entrega reduz a incerteza."}
  ]
}
```

## Anti-padrões

- "Saiba mais" ou "Clique aqui" quando existe ação específica.
- CTA de compra para visitante em fase de aprendizado.
- Prometer no botão o que a página não entrega.
- Testar mais de uma variável ao mesmo tempo.
- Inventar prazo ou escassez para forçar clique.
- Declarar vencedor sem dados do cro-analyst.
