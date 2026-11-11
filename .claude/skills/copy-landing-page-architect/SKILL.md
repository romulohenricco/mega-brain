---
name: copy-landing-page-architect
description: "Estrutura e escreve landing pages e páginas de vendas por seções (hero, problema, mecanismo, prova, oferta, FAQ, CTA) usando apenas fatos e provas verificados."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta da página]"
---

# /copy-landing-page-architect — Arquiteto de Landing Page

> **Auto-Trigger:** pedido para estruturar ou escrever landing page, página de captura ou página de vendas
> **Keywords:** "copy da landing page", "copy de landing page", "copy da landing", "copy da página de vendas", "copy da pagina de vendas", "copy de página de vendas", "copy da página de captura", "copy da pagina de captura", "escrever a página de vendas", "escrever a pagina de vendas", "escrever página de vendas", "escrever pagina de vendas", "monta a landing page da", "montar a landing page da", "monta a landing page de venda", "montar a landing page de venda", "landing page da oferta", "landing page da campanha", "estrutura da landing page da oferta", "estrutura de lp da oferta"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Estrutura e escreve a copy de uma landing page ou página de vendas por seções, na ordem que o estágio de consciência do público pede, usando somente fatos e provas do research packet e do offer canvas, com claims marcados e CTA específico.

Esta skill é a porta de entrada do Landing Page Architect do `copy-squad`. Ela não publica páginas nem altera nada em produção; entrega um draft versionado para edição, revisão de voz, compliance e aprovação humana.

## Quando ativar

- Pedido de landing page, página de captura, página de vendas ou revisão da estrutura de uma LP.
- O `execution-plan` do copy-chief inclui a task `write-landing-page`.
- Há dados de performance (performance-analysis) pedindo nova versão da página.
- Existem, ou podem ser obtidos, brief, ângulo aprovado, research packet e offer canvas.

## Entradas

| Insumo | Obrigatório | Onde fica |
|---|---|---|
| campaign_id e business | Sim | informado ou do execution-plan |
| brief | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| ângulo aprovado | Sim | `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json` |
| research packet | Sim | `.data/copy-squad/{business}/{campaign_id}/02-research/research-packet.json` |
| offer canvas | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json` |
| audience-voc e brand-voice-guide | Não | `01-strategy/audience-voc.json` e `_brand/brand-voice-guide.json` |

Se faltar insumo obrigatório, devolva `needs_input` listando o que falta; não escreva copy.

## Procedimento

1. Ler `squads/copy-squad/agents/conversion-copywriter.md` e assumir o papel, ou delegar ao subagent `copy-squad--conversion-copywriter` via Agent tool, passando business, campaign_id e os caminhos dos insumos.
2. Carregar `squads/copy-squad/tasks/write-landing-page.md` e seguir os passos na ordem.
3. Validar insumos e gates (G1 em risco medium ou high; G2 só em risco high ou campanha multi-ativo); resolver o estágio de consciência do brief.
4. Escrever as seções: hero, problema, mecanismo, prova, oferta, objeções, risco, FAQ e CTA final, reordenadas pelo estágio de consciência.
5. Registrar por seção `claims`, `proof_used` e `needs_approval`; não afirmar preço, garantia ou resultado sem prova verificada.
6. Remover urgência ou escassez sem `legitimate_urgency.exists == true`; conferir limites em `squads/copy-squad/data/channel-specs.yaml`.
7. Autochecar com `squads/copy-squad/checklists/conversion-copy-checklist.md`.
8. Persistir em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` (nova versão, nunca sobrescrever) e renderizar `squads/copy-squad/templates/copy-deck-tmpl.md`.
9. Emitir o envelope de handoff (`contracts/handoff-envelope.schema.json`) ao `copy-editor` e acrescentar uma linha em `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl`.

## Saída

- **Contrato:** `squads/copy-squad/contracts/conversion-copy.schema.json` (format `landing_page` ou `sales_page`).
- **Caminho:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Para o humano:** copy deck em Markdown e a lista de itens `needs_approval`.

## Gates humanos e risco

Landing page e página de vendas são risco high por política (`landing_page`, `sales_page`): exigem compliance completo e G1, G2, G3 e G4 com o approval-owner (conforme `data/risk-policy.yaml`). A skill nunca publica nem sobe página: a execução externa cabe ao copy-publisher. A execução externa exige `approval-decision` com `decision == approved` (`approved_with_edits` nunca autoriza), dentro de 72 h da decisão, e `payload_sha256` igual ao do pedido e ao hash recalculado por `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; o modelo nunca calcula o hash de cabeça. Quem monta o pedido é o `copy-publisher` (`prepare-approval-package`).

## Exemplo

Pedido: "monta a landing page da mentoria de gestão financeira para pequenas empresas" (exemplo ilustrativo). Resultado: draft com hero, problema, mecanismo, prova, oferta, FAQ e CTA; a seção de garantia fica marcada `needs_approval` porque o offer canvas ainda não confirma os termos; `risk_level` high; envelope ao copy-editor com gate G3.

## Anti-padrões

- Escrever a página sem ângulo aprovado ou sem research packet.
- Inventar depoimento, número, prêmio ou garantia para preencher a seção de prova.
- Usar a mesma abertura para todos os estágios de consciência.
- Colocar urgência sem prazo real registrado no offer canvas.
- Pular o copy-editor e o compliance por pressa.
- Publicar ou alterar a página por conta própria.

## Quando NÃO Ativar

- Para VSL ou qualquer vídeo de vendas: o dono é o `video-social-scriptwriter` (use `/copy-script-writer`, `format: vsl`); `vsl` não é formato desta skill.
- Para jornada de e-mail (use `/copy-email-sequence-builder`), variações de anúncio (`/copy-ad-variation-generator`) ou ajuste só de CTA (`/copy-cta-optimizer`).
- Para artigos, newsletters e posts (content-copywriter) ou textos de interface de produto (ux-writer).
- Quando o pedido é publicar, subir, alterar ou ativar página no ar.
- Quando faltam brief, ângulo aprovado e dados de oferta e o solicitante não quer completar o intake: acione primeiro `/copy-squad`.
