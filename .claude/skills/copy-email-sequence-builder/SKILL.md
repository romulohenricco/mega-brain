---
name: copy-email-sequence-builder
description: "Constrói jornadas de e-mail por objetivo (boas-vindas, nutrição, venda, reativação, carrinho abandonado, retenção) com consentimento, métrica por e-mail e aprovação humana."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id, objetivo da jornada e segmento]"
---

# /copy-email-sequence-builder — Construtor de Sequência de E-mails

> **Auto-Trigger:** pedido para criar sequência, régua ou fluxo de e-mails por objetivo
> **Keywords:** "sequência de e-mails de venda", "sequência de e-mail de venda", "sequencia de e-mails de venda", "sequencia de e-mail de venda", "sequência de emails de venda", "sequencia de emails de venda", "sequência de e-mails da campanha", "sequencia de e-mails da campanha", "régua de e-mail de venda", "régua de e-mails de venda", "regua de e-mail de venda", "regua de e-mails de venda", "régua de nutrição da campanha", "regua de nutricao da campanha", "fluxo de e-mail da campanha", "fluxo de email da campanha", "jornada de e-mail da campanha", "jornada de email da campanha", "email sequence de venda"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Constrói jornadas de e-mail por objetivo, com gatilho, atraso, métrica e CTA em cada mensagem, consentimento declarado, descadastro, variações por segmento justificadas e fallback para quem não abre. Nenhuma mensagem é enviada.

Esta skill é a porta de entrada do Email Sequence Builder do `copy-squad`.

## Quando ativar

- Pedido de sequência, régua ou fluxo de e-mails: boas-vindas, nutrição, venda, reativação, carrinho abandonado ou retenção.
- Um ativo longo precisa virar sequência (`wf-content-repurposing`).
- O `execution-plan` do copy-chief inclui a task `build-email-sequence`.
- Para uma mensagem única de CRM, use a task `write-crm-message` pelo agente `email-crm-copywriter`.

## Entradas

| Insumo | Obrigatório | Onde fica |
|---|---|---|
| campaign_id e business | Sim | informado ou do execution-plan |
| objetivo da jornada e segmento | Sim | brief ou solicitante |
| consent_basis (base de consentimento) | Sim | solicitante, registrado no brief |
| brief e ângulo aprovado | Sim | `01-strategy/brief.json` e `03-angles/angles.json` |
| audience-voc, offer canvas, brand-voice-guide | Não (offer canvas obrigatório em jornada de venda) | `01-strategy/` e `_brand/` |

Se faltar objetivo, segmento ou consentimento, devolva `needs_input` com até 5 perguntas; não escreva e-mails.

## Procedimento

1. Ler `squads/copy-squad/agents/email-crm-copywriter.md` e assumir o papel, ou delegar ao subagent `copy-squad--email-crm-copywriter` via Agent tool.
2. Carregar `squads/copy-squad/tasks/build-email-sequence.md` e seguir os passos.
3. Validar consentimento e escolher o arquétipo da jornada; mapear antes de escrever: e-mails, `trigger`, `delay`, objetivo único e `success_metric` por e-mail.
4. Definir segmentos e `segment_variations` apenas quando houver diferença real de dor, estágio ou objeção.
5. Escrever cada e-mail: assunto honesto (até 80 caracteres), preview (até 140), corpo escaneável, CTA único, descadastro e remetente.
6. Tratar claims (preço, garantia, prazo, resultado) só com fonte do offer canvas; sem fonte, `needs_approval`. Urgência só com `legitimate_urgency.exists == true`.
7. Definir `exit_conditions` e `fallback_for_non_openers` sem reenvio infinito.
8. Autochecar com `squads/copy-squad/checklists/email-crm-checklist.md`.
9. Persistir em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` com `requires_approval: true` em todos os e-mails, renderizar `squads/copy-squad/templates/email-journey-tmpl.md` e emitir o envelope ao `copy-editor`.

## Saída

- **Contrato:** `squads/copy-squad/contracts/email-journey.schema.json`.
- **Caminho:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Para o humano:** jornada em Markdown com mapa, e-mails, claims e pendências.

## Gates humanos e risco

Nutrição para base própria, sem claim sensível nem dado pessoal na copy, é risco medium (G1 e G4, com copy-editor, brand-voice-guardian e compliance em modo leve aceito). E-mail de venda, com claim sensível ou com dado pessoal de cliente no texto ou na segmentação é high (G1, G2, G3 e G4, compliance completo). Nada é `low`: toda mensagem enviada é ação externa. A execução externa exige `approval-decision` com `decision == approved` (`approved_with_edits` nunca autoriza), dentro de 72 h da decisão, e `payload_sha256` igual ao do pedido e ao hash recalculado por `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; o modelo nunca calcula o hash de cabeça. Quem monta o pedido é o `copy-publisher` (`prepare-approval-package`). Esta skill nunca dispara, agenda ou importa listas.

## Exemplo

Pedido: "monta uma régua de nutrição da campanha com 3 e-mails para leads do material gratuito do SaaS de fluxo de caixa" (exemplo ilustrativo). Resultado: mapa com gatilho no dia 2, 5 e 8; cada e-mail com objetivo e métrica; consentimento via opt-in do formulário; fallback de um reenvio com novo assunto; risk_level medium; todos `requires_approval: true`.

## Anti-padrões

- Escrever e-mails sem mapear gatilho, atraso e métrica.
- Jornada sem consentimento ou sem descadastro.
- Assunto que promete o que o corpo não entrega.
- Falsa escassez em todos os e-mails.
- Reenvio infinito para quem não abre.
- Disparar ou agendar o envio.

## Quando NÃO Ativar

- Para landing page (use `/copy-landing-page-architect`), anúncios (`/copy-ad-variation-generator`) ou CTA isolado (`/copy-cta-optimizer`).
- Para newsletter editorial ou artigo (content-copywriter).
- Quando o pedido é enviar, agendar ou importar contatos.
- Quando não há base de consentimento declarada e o solicitante não quer informá-la.
