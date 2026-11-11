---
task: build-email-sequence
name: build-email-sequence
task_name: "Construir sequência de e-mails por objetivo"
version: "1.0.0"
squad: copy-squad
task_id: build-email-sequence
category: production
difficulty: advanced
responsavel: '@email-crm-copywriter'
responsavel_type: Agent
responsible_executor: email-crm-copywriter
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
- campo: audience_voc
  tipo: contract:audience-voc
  obrigatorio: false
- campo: offer_canvas
  tipo: contract:offer-canvas
  obrigatorio: false
- campo: consent_basis
  tipo: string
  obrigatorio: true
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: false
Saida:
- campo: email_journey
  tipo: contract:email-journey
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, angles, audience-voc, offer-canvas, brand-voice-guide]
output: [email-journey]
action_items:
  - "Confirmar objetivo, segmento, oferta e base de consentimento"
  - "Mapear a jornada: e-mails, gatilhos, atrasos, métricas"
  - "Escrever assunto, preview, corpo, CTA e descadastro de cada e-mail"
  - "Criar variações por segmento apenas quando justificadas"
  - "Definir condições de saída e fallback para não abridores"
  - "Persistir v{n} com requires_approval true e emitir envelope"
acceptance_criteria:
  - "Draft válido no schema email-journey"
  - "consent_basis, exit_conditions e fallback_for_non_openers preenchidos"
  - "Todos os e-mails com trigger, delay, subject (até 80 caracteres), preview_text (até 140), body, cta, success_metric e requires_approval true"
  - "Descadastro e identificação do remetente em 100% das mensagens de marketing"
  - "0 urgências ou escassez sem legitimate_urgency real; 0 claims sensíveis sem fonte"
  - "Cada e-mail com objetivo único e métrica distinta ou justificada"
pre_condition: "Brief aprovado (G1 quando medium ou high), ângulo aprovado (G2 só em high ou campanha multi-ativo), segmento e objetivo definidos, consent_basis informado"
post_condition: "Jornada persistida em v{n}, nunca disparada; envelope emitido ao copy-editor com human_approval_required true"
checklist: checklists/email-crm-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: copy-email-sequence-builder
workflows: [wf-copy-production, wf-campaign-launch, wf-content-repurposing]
performance:
  error_handling: "needs_input com até 5 perguntas se faltar objetivo, segmento ou consent_basis; nunca enviar; claim sem fonte vira needs_approval"
---

# Task: Construir sequência de e-mails por objetivo

## Objetivo

Construir uma jornada de e-mails (boas-vindas, nutrição, venda, reativação, carrinho abandonado ou retenção) com objetivo, público, gatilho, frequência e métrica definidos para cada mensagem, respeitando consentimento, LGPD e regras de anti-spam, e prevendo variações por segmento e fallback para quem não abre. Implementa o Email Sequence Builder. A task nunca dispara mensagens.

## Quando usar / quando não usar

**Usar quando:**
- O execution-plan prevê jornada de e-mail para uma campanha, lançamento ou ciclo de vida.
- Um ativo longo precisa virar sequência (`wf-content-repurposing`).
- É preciso reativar contatos inativos ou recuperar carrinhos.

**Não usar quando:**
- Falta objetivo, segmento ou base de consentimento (CS-EC-001).
- É uma mensagem única de CRM (usar `write-crm-message`).
- O pedido é disparar, agendar ou importar lista de contatos (fora do escopo; ação do copy-publisher após aprovação).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | brief | Sim | brief-master |
| angle | angles (aprovado) | Sim | hook-angle-creator |
| audience_voc | audience-voc | Não | audience-voc |
| offer_canvas | offer-canvas | Não (obrigatório em jornada de venda) | offer-strategist |
| consent_basis | texto | Sim | solicitante, via brief |
| brand_voice_guide | brand-voice-guide | Não | brand-voice-guardian |

## Passos

1. **Resolver contexto.** Identificar business, campaign_id, asset_id, tipo de jornada e segmento; abrir o brief e conferir G1 (medium ou high) e G2 (high ou campanha multi-ativo).
2. **Validar consentimento e objetivo.** Registrar a `consent_basis` e verificar que ela cobre o segmento. Se faltar objetivo, segmento ou consentimento, parar com `needs_input` e até 5 perguntas.
3. **Escolher o arquétipo da jornada.** Boas-vindas (ativação), nutrição (educação e confiança), venda (decisão), reativação (retorno), carrinho abandonado (recuperação) ou retenção (valor continuado). Definir a quantidade e o ritmo de e-mails coerentes com o brief e com `data/channel-specs.yaml`.
4. **Mapear antes de escrever.** Para cada e-mail definir objetivo único, `trigger`, `delay` e `success_metric` (abertura, clique, resposta, conversão). Conferir que a frequência não gera fadiga.
5. **Definir segmentos.** Criar `segment_variations` apenas quando houver diferença real de dor, estágio ou objeção (CS-EC-005), documentando o critério do segmento.
6. **Escrever cada e-mail.** Assunto honesto (até 80 caracteres), preview (até 140), corpo escaneável, um CTA principal, descadastro e identificação do remetente. Usar frases do cliente do audience-voc.
7. **Tratar claims.** Preço, garantia, prazo e resultado só do offer canvas; sem fonte, needs_approval e risk high (CS-EC-004). Urgência só com `legitimate_urgency.exists == true`.
8. **Definir saída e fallback.** `exit_conditions` (conversão, resposta, descadastro, mudança de segmento) e `fallback_for_non_openers` (reenvio único com novo assunto, canal alternativo aprovado ou pausa).
9. **Autochecar.** Rodar `checklists/email-crm-checklist.md` e corrigir.
10. **Persistir e entregar.** Gravar `v{n}`, marcar `requires_approval: true` em todos os e-mails, emitir o envelope ao copy-editor e registrar o agent-run.

## Saída

- **Contrato:** `contracts/email-journey.schema.json` (meta, objective, audience_segment, consent_basis, emails, exit_conditions, fallback_for_non_openers).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Renderização humana:** `templates/email-journey-tmpl.md`.
- **Envelope:** from `email-crm-copywriter`, to `copy-editor`, artifact_type `email-journey`, status `needs_approval`, risk_level `medium` (nutrição) ou `high` (venda ou claims sensíveis), human_approval_required `true`, gate `G3` se houver claims sensíveis.

## Acceptance Criteria (Critérios de aceite)

- Jornada válida no schema, com todos os e-mails marcados `requires_approval: true`.
- consent_basis coerente com o segmento; descadastro e remetente em toda mensagem.
- trigger, delay, assunto, corpo, CTA e success_metric em 100% dos e-mails.
- exit_conditions incluem descadastro e conversão; fallback_for_non_openers definido sem reenvio infinito.
- Variações por segmento justificadas, ou ausência registrada.
- 0 claims sensíveis sem fonte; 0 urgências falsas.

## Quality gate e checklist

- **Quality gate:** QG-DRAFT, executor copy-chief (D7), com `checklists/email-crm-checklist.md` (self_check_by: email-crm-copywriter); depois QG-BRAND e QG-COMPLIANCE. E-mail de venda é risco high por política (data/risk-policy.yaml); envio é ação externa, no mínimo medium (D6). Declare `consent_basis`, descadastro e LGPD; customer_phrases só como inspiração anonimizada, citação literal exige `usage_rights: granted` e G3 (D17).
- **Checklist:** `checklists/email-crm-checklist.md`.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| consent_basis ausente | `needs_input`; não escrever |
| Segmento amplo demais | Propor divisão em até 3 segmentos e registrar em assumptions |
| Oferta sem preço ou prazo confirmados | Marcar needs_approval; usar texto neutro |
| Frequência incompatível com o brief | Reduzir o número de e-mails e justificar |
| Conteúdo depende de dado pessoal sensível | Registrar lgpd_flag no envelope para o compliance-checker |
| Rework acima de 2 ciclos | Escalar ao copy-chief |

## Handoff

Entrega ao `copy-editor` (edição e concisão), depois brand-voice-guardian e compliance-checker (consentimento, LGPD, claims). O copy-publisher monta o approval-request; o envio só ocorre após approval-decision válida e com payload_sha256 igual.

## Exemplo

Entrada resumida (ilustrativa): mentoria de gestão financeira; jornada de nutrição de 3 e-mails para leads de material gratuito.

```json
{
  "objective": "Educar sobre fluxo de caixa e levar o lead ao diagnóstico gratuito",
  "audience_segment": "leads de material gratuito, últimos 14 dias (exemplo ilustrativo)",
  "consent_basis": "Opt-in explícito no formulário do material gratuito",
  "emails": [
    {"email_id": "eml-nt-01", "trigger": "dia 2 após o cadastro", "delay": "48h", "subject": "O erro de caixa que quase todo mundo comete", "preview_text": "Leva 3 minutos para corrigir.", "body": "Olá! Hoje o assunto é...", "cta": "Ver o passo a passo", "success_metric": "taxa de clique", "requires_approval": true}
  ],
  "exit_conditions": ["agendou diagnóstico", "descadastrou", "respondeu"],
  "fallback_for_non_openers": "Reenviar uma vez após 3 dias com novo assunto; se não abrir, pausar por 30 dias."
}
```

## Anti-padrões

- Escrever e-mails sem mapear gatilho, atraso e métrica.
- Jornada sem consentimento ou sem descadastro.
- Assunto que promete algo que o corpo não entrega.
- Falsa escassez em todos os e-mails.
- Reenvio infinito para quem não abre.
- Segmentar sem diferença real, só para parecer sofisticado.
- Disparar ou agendar o envio por conta própria.
