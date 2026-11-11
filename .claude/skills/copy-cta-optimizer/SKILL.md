---
name: copy-cta-optimizer
description: "Cria e reescreve CTAs alinhados à intenção, ao estágio do funil e ao canal, com variações testáveis e hipótese."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou CTA atual a otimizar]"
---

# /copy-cta-optimizer — Otimizador de CTA

> **Auto-Trigger:** pedido para melhorar, criar ou testar chamadas para ação
> **Keywords:** "otimizar o cta da campanha", "otimizar o cta do anúncio", "otimiza o cta da campanha", "otimiza o cta do anúncio", "melhorar o cta da campanha", "melhorar o cta do anúncio", "melhora o cta da campanha", "melhora o cta do anúncio", "reescrever o cta da campanha", "reescrever o cta do anúncio", "reescrever cta da campanha", "variações de cta de anúncio", "variacoes de cta de anuncio", "variações de cta da campanha", "variacoes de cta da campanha", "cta optimizer de anúncio"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Cria ou reescreve CTAs alinhados à intenção do visitante, ao estágio do funil e ao canal, transformando chamadas vagas em ações específicas (verbo, objeto e benefício) e entregando variações testáveis com hipótese.

Esta skill é a porta de entrada do CTA Optimizer do `copy-squad`. Não altera páginas, anúncios ou e-mails em produção.

## Quando ativar

- CTAs genéricos ("Saiba mais", "Clique aqui") ou desalinhados com a ação do brief.
- O cro-analyst indicou hipótese de CTA para teste.
- Fast lane: variações de CTA para uso interno ou teste de uma peça já aprovada.
- O `execution-plan` do copy-chief inclui a task `optimize-ctas`.

## Entradas

| Insumo | Obrigatório | Onde fica |
|---|---|---|
| campaign_id, business e canal | Sim | informado ou do execution-plan |
| brief (ação desejada e KPI) | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| offer canvas | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json` |
| copy atual com os CTAs | Não | `04-drafts/{asset_id}/` ou texto colado pelo solicitante |
| performance-analysis | Não | `.data/copy-squad/{business}/{campaign_id}/08-performance/` |

## Procedimento

1. Ler `squads/copy-squad/agents/conversion-copywriter.md` e assumir o papel, ou delegar ao subagent `copy-squad--conversion-copywriter` via Agent tool.
2. Carregar `squads/copy-squad/tasks/optimize-ctas.md` e seguir os passos.
3. Inventariar cada CTA com posição, canal e ação desejada; classificar intenção do visitante e estágio do funil.
4. Diagnosticar CTAs vagos, desalinhados, sem benefício ou que prometem mais do que o destino entrega.
5. Reescrever com a fórmula verbo + objeto + benefício e ajustar o grau de compromisso ao estágio do funil.
6. Gerar no mínimo 5 variações por CTA principal, uma variável por variação, cada uma com hipótese; conferir limites de `squads/copy-squad/data/channel-specs.yaml`.
7. Remover urgência sem `legitimate_urgency.exists == true`; CTA com promessa de preço ou resultado sem prova vai para `needs_approval`.
8. Autochecar com `squads/copy-squad/checklists/conversion-copy-checklist.md`.
9. Persistir em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` e emitir o envelope ao `copy-editor`.

## Saída

- **Contrato:** `squads/copy-squad/contracts/conversion-copy.schema.json` com `ctas` e `variations` preenchidos.
- **Caminho:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Para o humano:** tabela de CTAs com intenção, funil, canal e hipóteses (`templates/copy-deck-tmpl.md`).

## Gates humanos e risco

Risco `low` vale só para uso interno: variações de CTA para backlog ou teste interno seguem pela fast lane com `QG-COMPLIANCE` em modo leve e amostragem humana de 20% (gate SAMPLING). CTA que será publicado, enviado ou veiculado é no mínimo medium (G1 e G4) e sai da fast lane; se estiver em anúncio pago, página de vendas ou e-mail de venda, é high, e se prometer resultado, preço ou garantia sem prova exige compliance e G3. A skill não altera nada no ar. A execução externa exige `approval-decision` com `decision == approved` (`approved_with_edits` nunca autoriza), dentro de 72 h da decisão, e `payload_sha256` igual ao do pedido e ao hash recalculado por `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; o modelo nunca calcula o hash de cabeça. Quem monta o pedido é o `copy-publisher` (`prepare-approval-package`).

## Exemplo

Pedido: "melhora o CTA da página de captura do guia de fluxo de caixa" (exemplo ilustrativo). Resultado: de "Saiba mais" para "Baixar o guia de fluxo de caixa", com variações "Quero meu guia gratuito" e "Receber o guia no meu e-mail", cada uma com hipótese de atrito e clareza.

## Anti-padrões

- Pedir compra a quem ainda está aprendendo.
- Prometer no botão o que a página não entrega.
- Testar mais de uma variável por vez.
- Inventar prazo ou escassez para forçar o clique.
- Declarar vencedor sem dados.

## Quando NÃO Ativar

- Para reescrever a página inteira (use `/copy-landing-page-architect`) ou criar anúncios completos (`/copy-ad-variation-generator`).
- Para textos de botão de interface de produto, que são do ux-writer.
- Quando a ação desejada ainda não foi definida no brief: acione `/copy-briefing-master`.
- Quando o pedido é alterar o CTA diretamente em página, anúncio ou e-mail publicado.
