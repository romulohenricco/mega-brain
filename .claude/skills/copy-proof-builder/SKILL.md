---
name: copy-proof-builder
description: "Organiza depoimentos, cases, dados, demonstrações e garantias em uma pilha de provas verificada, com direito de uso e lacunas explícitas."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta das provas disponíveis]"
---

# /copy-proof-builder — Pilha de Provas da Oferta

> **Auto-Trigger:** pedido para organizar, classificar ou verificar provas (depoimentos, cases, dados) de uma oferta
> **Keywords:** "pilha de provas da oferta", "pilha de provas da campanha", "pilha de prova da oferta", "proof stack da oferta", "organizar os depoimentos da oferta", "organiza os depoimentos da oferta", "organizar as provas da oferta", "organiza as provas da oferta", "provas da oferta", "mapa de provas da oferta", "provas da campanha"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Constrói a pilha de provas (`proof_stack`) do `offer-canvas`: cada prova com tipo, fonte, status de verificação e direito de uso, mapeada aos claims da promessa, com lacunas e plano de coleta, sem inventar nem melhorar nenhuma prova.

## Quando ativar

- O usuário tem depoimentos, cases, dados, demonstrações, garantias, certificações ou menções de mídia a organizar.
- A promessa da oferta precisa de sustentação e não há mapa promessa-prova.
- O `compliance-checker` devolveu claims sem fonte ou sem autorização de uso.
- Antes de gerar ângulos ou copy, para saber o que pode ser afirmado.

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| `campaign_id` e `business` | Sim | argumento da skill ou contexto da conversa |
| Provas brutas (texto, link, arquivo) | Sim (ou declaração de que não há) | fornecidas pelo usuário |
| `brief` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| `offer-canvas` anterior | Não | `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json` |
| Biblioteca do negócio | Não | `.data/copy-squad/{business}/_library/` |

## Procedimento

1. Ler `squads/copy-squad/agents/offer-strategist.md` e assumir o papel de Offer & Positioning Strategist, **ou** delegar ao subagent `copy-squad--offer-strategist` via Agent tool.
2. Carregar a task `squads/copy-squad/tasks/build-proof-stack.md` e o checklist `squads/copy-squad/checklists/offer-quality-checklist.md`.
3. Inventariar todas as provas com origem (arquivo, URL, quem forneceu, data).
4. Classificar cada prova (`testimonial`, `case`, `data`, `demo`, `guarantee`, `certification`, `media`), registrar `source`, definir `verified` e `usage_rights` (`granted`, `pending`, `unknown`).
5. Resumir sem distorcer: citações permanecem literais e números exatos; nunca arredondar, completar ou "melhorar".
6. Mapear prova para claim e para objeção dominante; registrar claims sem prova como lacunas e propor ações de coleta com responsável.
7. Marcar usos sensíveis (resultado de cliente, autoridade, saúde, financeiro, dado pessoal) em `needs_approval` para o G3.
8. Persistir nova versão do `offer-canvas.json` (sem sobrescrever) e registrar o envelope em `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl`.
9. Informar ao usuário o que está liberado para copy, o que está bloqueado e o plano de coleta.

## Saída

- **Contrato:** `squads/copy-squad/contracts/offer-canvas.schema.json` (campo `proof_stack`: `proof_id` com prefixo `prv-`, `type`, `summary`, `source`, `verified`, `usage_rights`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json`.
- **Envelope:** `handoff-envelope` para `hook-angle-creator` ou `conversion-copywriter`, `gate: G3` quando houver prova sensível.

## Gates humanos e risco

- **G3:** obrigatório para depoimento, resultado, autoridade, dado de cliente identificável e qualquer prova sem direito de uso confirmado.
- Provas com `verified: false` ou `usage_rights` diferente de `granted` são proibidas em copy até aprovação.
- Dado pessoal de cliente exige revisão LGPD do `compliance-checker` antes de qualquer uso.
- Frases do banco de voz do cliente (`audience-voc.customer_phrases`) não são depoimento: só viram prova com `usage_rights: granted` e passam por G3 (D17).
- A skill não publica nada e não valida o próprio trabalho.

## Exemplo

Pedido: "/copy-proof-builder camp-mentoria-caixa" com dois itens fornecidos (exemplo ilustrativo).

```json
{
  "proof_stack": [
    {"proof_id": "prv-dado-renovacao", "type": "data", "summary": "Taxa de renovação transcrita do relatório interno", "source": "fornecida pelo solicitante (exemplo ilustrativo)", "verified": false, "usage_rights": "pending"},
    {"proof_id": "prv-msg-cliente-01", "type": "testimonial", "summary": "Mensagem sobre a clareza do onboarding", "source": "internal: mensagem recebida", "verified": false, "usage_rights": "pending"}
  ],
  "needs_approval": [
    "testimonial: Há autorização escrita para uso do nome e do texto da mensagem do cliente?"
  ]
}
```

## Anti-padrões

- Reescrever ou "melhorar" a fala de um cliente.
- Arredondar números ou generalizar amostra pequena.
- Usar prova de outro negócio ou campanha sem checar escopo.
- Liberar para a copy prova sem fonte ou sem autorização.
- Omitir lacunas para a pilha parecer completa.
- Criar prova inexistente para preencher a promessa.

## Quando NÃO Ativar

- Quando o pedido é escrever o depoimento ou criar um caso fictício: é proibido (No Invention).
- Quando o objetivo é mapear objeções: use `/copy-objection-handler`.
- Quando falta a oferta inteira: use o fluxo `design-offer` pelo `/copy-squad`.
- Quando o usuário só quer coletar elogios informais sem intenção de uso comercial.
- Quando a conversa trata de provas jurídicas ou periciais (fora do escopo de copy).
