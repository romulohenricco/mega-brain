# Checklist: Qualidade de Jornada de E-mail e CRM

## Metadata
```yaml
id: email-crm-checklist
name: "Checklist de jornada de e-mail e mensagens de CRM"
version: 1.0.0
executor: copy-chief           # validador do gate QG-DRAFT (D7)
self_check_by: email-crm-copywriter  # produtor; a autochecagem não aprova o gate
related_task: build-email-sequence
related_tasks: [build-email-sequence, write-crm-message]
quality_gate: QG-DRAFT
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que uma jornada ou mensagem de CRM tenha objetivo, público, gatilho, frequência e métrica definidos em cada e-mail, respeite consentimento, LGPD e anti-spam, e chegue à edição com variações por segmento justificadas, fallback para quem não abre e aprovação humana obrigatória antes de qualquer envio.

---

## Fase 1: Estrutura da jornada

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | O artefato valida no schema `email-journey` (meta, objective, audience_segment, consent_basis, emails)? | blocking | [ ] | |
| 2 | O objetivo da jornada é único e mensurável (ex.: ativar, nutrir, converter, reativar)? | quality | [ ] | |
| 3 | Cada e-mail tem `trigger`, `delay` e `success_metric` definidos? | blocking | [ ] | |
| 4 | Cada e-mail tem um objetivo único e um CTA principal? | quality | [ ] | |
| 5 | A frequência respeita o brief e `data/channel-specs.yaml` (sem fadiga evidente)? | quality | [ ] | |
| 6 | A ordem dos e-mails segue uma progressão lógica (valor antes da oferta, quando aplicável)? | quality | [ ] | |

**Score Fase 1:** ___/6

---

## Fase 2: Consentimento, LGPD e anti-spam

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 7 | `consent_basis` está declarada e cobre o segmento da jornada? | blocking | [ ] | |
| 8 | Todo e-mail de marketing tem descadastro funcional e identificação clara do remetente? | blocking | [ ] | |
| 9 | O motivo do recebimento é explicado quando o contato não espera a mensagem? | quality | [ ] | |
| 10 | `exit_conditions` incluem descadastro, e o contato sai da jornada ao descadastrar? | blocking | [ ] | |
| 11 | A personalização usa apenas campos aprovados; dado pessoal além do necessário foi sinalizado em `lgpd_flags`? | blocking | [ ] | |
| 12 | Nenhum assunto engana (falso "Re:", falso "Fwd:", promessa que o corpo não cumpre)? | blocking | [ ] | |

**Score Fase 2:** ___/6

---

## Fase 3: Conteúdo, claims e segmentos

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 13 | Assunto tem até 80 caracteres e descreve o conteúdo real? | blocking | [ ] | |
| 14 | `preview_text` tem até 140 caracteres e complementa o assunto? | quality | [ ] | |
| 15 | Preço, garantia, prazo e resultado vêm do offer canvas ou estão marcados como pendentes de aprovação? | blocking | [ ] | |
| 16 | Não há urgência ou escassez sem `legitimate_urgency.exists == true`? | blocking | [ ] | |
| 17 | Nenhum depoimento, número ou prêmio foi inventado? | blocking | [ ] | |
| 18 | `segment_variations` existem apenas quando há diferença real, com o critério do segmento explícito? | quality | [ ] | |
| 19 | A linguagem usa termos reais do cliente e respeita o brand-voice-guide? | quality | [ ] | |

**Score Fase 3:** ___/7

---

## Fase 4: Governança e fallback

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 20 | Todos os e-mails têm `requires_approval: true`? | blocking | [ ] | |
| 21 | `fallback_for_non_openers` está definido, sem reenvio infinito? | quality | [ ] | |
| 22 | O `risk_level` está correto (nutrição medium, venda high, claim sensível high)? | blocking | [ ] | |
| 23 | O envelope indica `human_approval_required: true` e o gate adequado (G3 para claims, G4 para envio)? | blocking | [ ] | |
| 24 | A nova versão preserva a anterior (sem sobrescrever)? | quality | [ ] | |

**Score Fase 4:** ___/5

---

## Veto conditions

Qualquer item abaixo leva a VETO imediato:

1. Jornada sem `consent_basis` (item 7).
2. E-mail de marketing sem descadastro ou sem identificação do remetente (item 8).
3. Assunto enganoso ou falsa escassez (itens 12, 16).
4. Claim sensível sem fonte e sem registro de aprovação (item 15).
5. E-mail sem `requires_approval: true`, ou qualquer indício de envio/agendamento (item 20).
6. Uso de dado pessoal sensível sem lgpd_flag (item 11).

## Auto-correção (o que fazer quando falha)

| Item que falhou | Ação |
|---|---|
| 3, 4 | Reescrever o mapa da jornada antes do corpo; consolidar e-mails redundantes |
| 7 | `needs_input` ao solicitante via copy-chief; não escrever |
| 8, 10 | Incluir rodapé de descadastro e a condição de saída |
| 12, 13 | Reescrever assunto para descrever o conteúdo real e caber em 80 caracteres |
| 15, 17 | Remover ou marcar `needs_approval`; elevar risco; sinalizar G3 |
| 16 | Remover urgência; usar custo de esperar verificável |
| 18 | Remover variações sem diferença real |
| 21 | Definir reenvio único com novo assunto, canal alternativo aprovado ou pausa |

Máximo de 2 ciclos de retrabalho; depois escalar ao copy-chief.

## Edge cases

- **Mensagem transacional:** descadastro pode não se aplicar, mas a classificação deve estar no brief; na dúvida, tratar como marketing.
- **Reativação de contatos antigos:** confirmar que a base de consentimento ainda é válida; se incerta, sinalizar ao compliance-checker.
- **Carrinho abandonado:** gatilho de comportamento exige consentimento para esse tipo de rastreamento; registrar em `consent_basis`.
- **Segmento muito pequeno:** não criar variações; usar versão única e registrar a hipótese.
- **Jornada multilíngue:** enviar à localização e ao compliance após aprovação do conteúdo-base.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 24. Itens blocking não atendidos rebaixam o resultado para no máximo REVIEW; qualquer veto condition leva a VETO.
