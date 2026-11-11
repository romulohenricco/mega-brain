---
name: copy-ad-variation-generator
description: "Gera variações de headline, corpo e CTA de anúncio para teste, com hipótese por variação e respeito aos limites de caracteres do canal."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id, canal e elemento a testar]"
---

# /copy-ad-variation-generator — Gerador de Variações de Anúncio

> **Auto-Trigger:** pedido para criar copy de anúncio ou variações de anúncio para teste
> **Keywords:** "variações de anúncio", "variacoes de anuncio", "variações do anúncio", "variacoes do anuncio", "copy de anúncio", "copy de anuncio", "ad variations de anúncio", "anúncios para teste de copy", "anuncios para teste de copy"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Gera variações de headline, corpo e CTA de anúncio prontas para teste A/B, cada uma com hipótese explícita, respeitando os limites de caracteres do canal e usando apenas fatos e provas verificados.

Esta skill é a porta de entrada do Ad Variation Generator do `copy-squad`. Não compra mídia, não sobe anúncio e não declara vencedor de teste.

## Quando ativar

- Pedido de copy de anúncio para um ou mais canais, com ou sem material de partida.
- Fast lane (`wf-fast-variation`): novas variações para uso interno ou teste a partir de uma peça já aprovada.
- Ciclo de performance: o cro-analyst entregou hipóteses e é preciso novos testes.
- O `execution-plan` do copy-chief inclui a task `write-ad-variations`.

## Entradas

| Insumo | Obrigatório | Onde fica |
|---|---|---|
| campaign_id, business, canal | Sim | informado ou do execution-plan |
| brief | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| ângulo aprovado | Sim | `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json` |
| research packet e offer canvas | Sim | `02-research/research-packet.json` e `01-strategy/offer-canvas.json` |
| performance-analysis | Não | `.data/copy-squad/{business}/{campaign_id}/08-performance/` |

## Procedimento

1. Ler `squads/copy-squad/agents/conversion-copywriter.md` e assumir o papel, ou delegar ao subagent `copy-squad--conversion-copywriter` via Agent tool.
2. Carregar `squads/copy-squad/tasks/write-ad-variations.md` e seguir os passos.
3. Abrir `squads/copy-squad/data/channel-specs.yaml` e anotar os limites de caracteres do canal e do formato.
4. Definir a variável do lote (uma por vez) e a hipótese principal.
5. Escrever no mínimo 5 variações por elemento testado (headline, corpo, CTA), variando estrutura e não apenas sinônimos; cada uma com `variation_id`, `element`, `text` e `hypothesis`.
6. Marcar claims e provas; claim de preço, garantia, resultado ou comparativo sem prova vai para `needs_approval`; remover urgência sem `legitimate_urgency.exists == true`.
7. Conferir os limites de caracteres e reescrever o que exceder; indicar controle (baseline) e prioridade do teste.
8. Autochecar com `squads/copy-squad/checklists/conversion-copy-checklist.md`.
9. Persistir em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` e emitir o envelope ao `copy-editor`.

## Saída

- **Contrato:** `squads/copy-squad/contracts/conversion-copy.schema.json` com `format: "ad"`, `ctas` e `variations`.
- **Caminho:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Para o humano:** copy deck (`templates/copy-deck-tmpl.md`) com tabela de variações e hipóteses.

## Gates humanos e risco

Risco `low` vale só para uso interno: variações de headline e CTA para backlog ou teste interno seguem pela fast lane com `QG-COMPLIANCE` em modo leve (reclassificação independente de claims) e amostragem humana de 20% (gate SAMPLING, pedido montado pelo copy-publisher). Anúncio pago é sempre risco high (`paid_ad`): G1, G2, G3 e G4 e compliance completo, e qualquer variação que seja veiculada sai da fast lane. Claim de preço, garantia, resultado, autoridade, depoimento ou comparativo também é high e exige G3. A skill nunca compra mídia nem ativa campanha. A execução externa exige `approval-decision` com `decision == approved` (`approved_with_edits` nunca autoriza), dentro de 72 h da decisão, e `payload_sha256` igual ao do pedido e ao hash recalculado por `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; o modelo nunca calcula o hash de cabeça. Quem monta o pedido é o `copy-publisher` (`prepare-approval-package`).

## Exemplo

Pedido: "gera variações de anúncio para o SaaS de fluxo de caixa, testando a estrutura da headline" (exemplo ilustrativo). Resultado: 5 headlines (pergunta de dor, mecanismo, contraste temporal, número verificável, afirmação de benefício), cada uma com hipótese, todas dentro do limite do canal; sem claim sensível, risk_level low enquanto forem só para teste interno (se for veicular como anúncio pago, passa a high).

## Anti-padrões

- Variar duas ou mais coisas no mesmo lote.
- Trocar só sinônimos e chamar de teste.
- Ignorar o limite de caracteres do canal.
- Declarar vencedor sem dados (decisão do cro-analyst).
- Usar números, prêmios ou depoimentos sem fonte.
- Subir ou ativar o anúncio por conta própria.

## Quando NÃO Ativar

- Para landing pages (use `/copy-landing-page-architect`) ou jornadas de e-mail (`/copy-email-sequence-builder`).
- Para roteiros de vídeo (`/copy-script-writer`) ou legendas de conteúdo orgânico (video-social-scriptwriter).
- Quando o pedido é comprar mídia, publicar ou ativar anúncios.
- Quando o objetivo é só ajustar o botão ou a chamada (use `/copy-cta-optimizer`).
