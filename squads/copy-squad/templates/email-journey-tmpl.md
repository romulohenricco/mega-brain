# Jornada de E-mail — {journey_title}

> Renderização humana do contrato `email-journey` (contracts/email-journey.schema.json).
> Produzido por: email-crm-copywriter · QG-DRAFT: copy-chief (executor) · Revisão obrigatória: copy-editor, brand-voice-guardian, compliance-checker · Aprovação: approval-owner (G3 claims, G4 envio).
> Nenhuma mensagem deste documento pode ser enviada sem approval-decision válido (decision `approved`, payload_sha256 igual ao recalculado por `approval_tools.py` e dentro da janela de execução da decisão; `approved_with_edits` nunca autoriza envio). Persistido em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.

## 1. Identificação

| Campo | Valor |
|---|---|
| artifact_id | {asset_id}-v{n} |
| campaign_id | camp-{slug} |
| business | {business} |
| asset_id | {asset_id} |
| versão | v{n} |
| tipo de jornada | boas-vindas / nutrição / venda / reativação / carrinho abandonado / retenção / mensagem avulsa |
| risk_level | low / medium / high |
| status | draft / needs_approval |
| confidence | 0.00 |
| produzido em | {data} |

## 2. Objetivo, público e consentimento

- **Objetivo da jornada (mensurável):** {objective}
- **Segmento (audience_segment) e critério de entrada:** {segmento}
- **Base de consentimento (consent_basis):** {opt-in, contrato, legítimo interesse documentado, etc.}
- **Frequência máxima e janela de envio:** {frequência}
- **Remetente e identificação:** {nome do remetente}
- **Regra de descadastro:** {como funciona e onde aparece}

## 3. Mapa da jornada

| # | email_id | Gatilho (trigger) | Atraso (delay) | Objetivo do e-mail | Métrica de sucesso | Segmento |
|---|---|---|---|---|---|---|
| 1 | eml-{id} | {gatilho} | {delay} | {objetivo} | {métrica} | {segmento} |

## 4. E-mails

Repita o bloco abaixo para cada e-mail.

### E-mail {n}: {email_id}

| Campo | Conteúdo |
|---|---|
| trigger | {gatilho} |
| delay | {atraso} |
| subject (até 80 caracteres) | {assunto} |
| preview_text (até 140 caracteres) | {preview} |
| cta | {CTA principal} |
| success_metric | {métrica} |
| requires_approval | true |

**Corpo**

{corpo do e-mail}

---
{rodapé: identificação do remetente, motivo do recebimento, link de descadastro}

**Variações por segmento (segment_variations)**

| Segmento | Critério | Assunto alternativo | Trecho alterado |
|---|---|---|---|
| {segmento} | {critério} | {assunto} | {trecho} |

**Claims neste e-mail**

| Claim | Tipo | Fonte (offer canvas / research packet) | Status |
|---|---|---|---|
| {claim} | {price / guarantee / result / ...} | {fonte} | verified / unverified |

## 5. Condições de saída e fallback

- **exit_conditions:** {conversão, resposta, descadastro, mudança de segmento, outro}
- **fallback_for_non_openers:** {reenvio único com novo assunto após N dias | canal alternativo aprovado | pausa de N dias}
- **Limite de tentativas:** {número}

## 6. Conformidade e risco

- **LGPD e dados pessoais usados na personalização:** {campos aprovados}
- **lgpd_flags para o compliance-checker:** {lista}
- **Urgência / escassez:** {não usada | usada, com legitimate_urgency real}
- **Claims sensíveis e gate necessário:** {G3 se houver}
- **Suposições (assumptions):** {lista}

## 7. Autochecagem do produtor

Referência: `checklists/email-crm-checklist.md` (a pontuação oficial é do copy-editor).

- [ ] consent_basis declarada e coerente com o segmento
- [ ] Descadastro e remetente em todas as mensagens de marketing
- [ ] trigger, delay e success_metric em todos os e-mails
- [ ] Assunto honesto, até 80 caracteres; preview até 140
- [ ] Sem urgência ou escassez sem legitimate_urgency real
- [ ] Fallback para quem não abre e exit_conditions definidos
- [ ] requires_approval true em todos os e-mails

## 8. Handoff

| Campo | Valor |
|---|---|
| from_agent | email-crm-copywriter |
| to_agent | copy-editor |
| envelope_id | env-{slug} |
| artifact_path | .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json |
| status | needs_approval / needs_input |
| human_approval_required | true |
| gate | G3 / G4 |
| motivo | {consentimento, claims, frequência a observar} |
