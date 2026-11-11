---
task: write-crm-message
name: write-crm-message
task_name: "Escrever mensagem avulsa de CRM"
version: "1.0.0"
squad: copy-squad
task_id: write-crm-message
category: production
difficulty: basic
responsavel: '@email-crm-copywriter'
responsavel_type: Agent
responsible_executor: email-crm-copywriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 15-30min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: trigger_context
  tipo: string
  obrigatorio: true
- campo: audience_segment
  tipo: string
  obrigatorio: true
- campo: consent_basis
  tipo: string
  obrigatorio: true
- campo: offer_canvas
  tipo: contract:offer-canvas
  obrigatorio: false
Saida:
- campo: email_journey
  tipo: contract:email-journey
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, offer-canvas, audience-voc, brand-voice-guide]
output: [email-journey]
action_items:
  - "Confirmar gatilho, segmento, objetivo e consentimento"
  - "Definir a métrica e o CTA da mensagem"
  - "Escrever assunto, preview e corpo curtos, com descadastro"
  - "Tratar claims e dados pessoais"
  - "Persistir como email-journey de 1 mensagem com requires_approval true"
acceptance_criteria:
  - "Draft válido no schema email-journey com exatamente 1 e-mail"
  - "Mensagem com objetivo único, trigger, delay, success_metric, cta e requires_approval true"
  - "consent_basis declarada; descadastro e identificação do remetente presentes"
  - "0 claims sensíveis sem fonte; 0 urgências falsas; 0 dados pessoais além do aprovado"
pre_condition: "Brief ou instrução de contexto com objetivo, gatilho, segmento e consent_basis"
post_condition: "Mensagem persistida em v{n}, não enviada, com envelope emitido ao copy-editor"
checklist: checklists/email-crm-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: null
workflows: [wf-copy-production]
performance:
  error_handling: "needs_input com até 5 perguntas; mensagem transacional vs marketing registrada em assumptions; nunca enviar"
---

# Task: Escrever mensagem avulsa de CRM

## Objetivo

Escrever uma única mensagem de e-mail ou CRM disparada por um gatilho específico (por exemplo, aviso de renovação, resposta a um evento do produto, convite para diagnóstico, pedido de feedback), com os mesmos controles de uma jornada: objetivo, público, gatilho, métrica, consentimento e descadastro. A saída usa o contrato `email-journey` com um único e-mail.

## Quando usar / quando não usar

**Usar quando:**
- A demanda é uma mensagem pontual, sem necessidade de sequência.
- Um evento de CRM (cadastro, compra, inatividade, aniversário de contrato) pede uma comunicação única.
- Um item de uma jornada precisa ser reescrito isoladamente.

**Não usar quando:**
- O objetivo exige mais de uma mensagem encadeada (usar `build-email-sequence`).
- O conteúdo é editorial (newsletter, artigo), que é do content-copywriter.
- O pedido é enviar ou agendar a mensagem.

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | brief | Sim | brief-master ou instrução do copy-chief |
| trigger_context | texto | Sim | solicitante |
| audience_segment | texto | Sim | solicitante ou audience-voc |
| consent_basis | texto | Sim | solicitante |
| offer_canvas | offer-canvas | Não | offer-strategist (quando houver oferta) |

## Passos

1. **Classificar a mensagem.** Determinar se é marketing, relacionamento ou transacional. Em caso de dúvida, tratar como marketing (descadastro incluído) e registrar em assumptions.
2. **Validar insumos.** Conferir objetivo, gatilho, segmento e consent_basis. Se faltar algo, `needs_input` com até 5 perguntas.
3. **Definir métrica e CTA.** Escolher uma única ação desejada e a métrica de sucesso (clique, resposta, agendamento, renovação).
4. **Levantar o contexto do contato.** Usar apenas campos de personalização aprovados (por exemplo, primeiro nome, produto contratado); registrar lgpd_flag para qualquer dado além do necessário.
5. **Escrever o assunto.** Até 80 caracteres, honesto e específico; sem falso "Re:" ou "Fwd:".
6. **Escrever o preview e o corpo.** Preview até 140 caracteres; corpo curto, com a razão do contato, o valor para o leitor, o CTA único e o descadastro quando for marketing.
7. **Tratar claims.** Preço, prazo e garantia somente do offer canvas; sem fonte, needs_approval e risk high.
8. **Prever fallback.** Definir `fallback_for_non_openers` simples (um reenvio com novo assunto ou nenhuma ação) e `exit_conditions`.
9. **Autochecar.** Rodar `checklists/email-crm-checklist.md` (itens aplicáveis a uma mensagem).
10. **Persistir e entregar.** Gravar `v{n}` com um e-mail e `requires_approval: true`; emitir o envelope ao copy-editor.

## Saída

- **Contrato:** `contracts/email-journey.schema.json` com `emails` de tamanho 1.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Renderização humana:** `templates/email-journey-tmpl.md`.
- **Envelope:** from `email-crm-copywriter`, to `copy-editor`, artifact_type `email-journey`, status `needs_approval`, risk_level `medium` (envio é ação externa, D6; `low` só para rascunho interno) e `high` com claim sensível ou dado de CRM, human_approval_required `true`.

## Acceptance Criteria (Critérios de aceite)

- Exatamente 1 e-mail no contrato, com todos os campos obrigatórios e `requires_approval: true`.
- Objetivo único, CTA único e métrica definida.
- Consentimento declarado; descadastro e remetente presentes em mensagem de marketing.
- Sem claims sensíveis sem fonte, sem urgência falsa, sem dado pessoal além do aprovado.
- Assunto de até 80 caracteres e preview de até 140.

## Quality gate e checklist

- **Quality gate:** QG-DRAFT, executor copy-chief (D7), com `checklists/email-crm-checklist.md`; self_check_by: email-crm-copywriter. Mensagem enviada é no mínimo medium e exige G4; com oferta, preço ou claim sensível é high e exige G3. Consentimento/LGPD e descadastro obrigatórios; customer_phrases só como inspiração anonimizada (D17).
- **Checklist:** `checklists/email-crm-checklist.md`.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Classificação transacional vs marketing incerta | Aplicar o padrão conservador de marketing e sinalizar ao compliance-checker |
| consent_basis ausente | `needs_input`; não escrever |
| Dado pessoal sensível necessário à personalização | Registrar lgpd_flag e escalar ao compliance-checker |
| Objetivo múltiplo | Dividir em mensagens e propor `build-email-sequence` |
| Rework acima de 2 ciclos | Escalar ao copy-chief |

## Handoff

Entrega ao `copy-editor`; depois brand-voice-guardian e compliance-checker conforme o risco. O envio só é feito pelo copy-publisher após approval-decision válida.

## Exemplo

Entrada resumida (ilustrativa): aviso a clientes de um SaaS de fluxo de caixa sobre fim do período de teste.

```json
{
  "objective": "Lembrar o fim do período de teste e convidar ao diagnóstico de plano",
  "audience_segment": "contas em teste que usaram o produto ao menos uma vez (exemplo ilustrativo)",
  "consent_basis": "Relacionamento contratual de teste e preferência de comunicação ativa",
  "emails": [
    {"email_id": "eml-av-01", "trigger": "3 dias antes do fim do teste", "delay": "automático", "subject": "Seu período de teste termina em 3 dias", "preview_text": "Veja o que você já configurou e o que falta.", "body": "Olá! Seu período de teste termina em breve...", "cta": "Ver meu resumo de uso", "success_metric": "clique no resumo", "requires_approval": true}
  ],
  "exit_conditions": ["contratou plano", "descadastrou"],
  "fallback_for_non_openers": "Nenhum reenvio; manter a régua padrão."
}
```

## Anti-padrões

- Tratar como transacional uma mensagem que é de marketing, para dispensar o descadastro.
- Misturar vários objetivos e vários CTAs em uma mensagem.
- Assunto que cria falsa urgência.
- Usar dados do contato além do aprovado.
- Enviar ou agendar o envio.
- Esquecer o remetente claro e o motivo do contato.
