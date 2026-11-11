---
name: copy-objection-handler
description: "Mapeia objeções do comprador por categoria e frequência e cria respostas ancoradas em prova, mecanismo ou redução de risco, sem promessas novas."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta da oferta]"
---

# /copy-objection-handler — Mapa de Objeções e Respostas

> **Auto-Trigger:** pedido para mapear, quebrar ou responder objeções de compra de uma oferta
> **Keywords:** "quebrar objeções da oferta", "quebrar objecoes da oferta", "quebrar as objeções da oferta", "quebrar as objecoes da oferta", "quebra as objeções da oferta", "quebra as objecoes da oferta", "mapa de objeções da oferta", "mapa de objecoes da oferta", "responder objeções da oferta", "responder objecoes da oferta", "objeções da oferta", "objecoes da oferta", "objeções de compra da oferta", "objection handler da oferta"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Transforma as resistências do comprador em um mapa de objeções com categoria, frequência, evidência e resposta ancorada em prova, mecanismo ou redução de risco, atualizando o campo `objection_responses` do `offer-canvas` do squad de copy.

## Quando ativar

- O usuário quer listar e responder as objeções de preço, confiança, complexidade, risco, tempo, compatibilidade ou necessidade de uma oferta.
- O `conversion-copywriter` ou o `email-crm-copywriter` precisa de respostas prontas para FAQ, seção de objeções ou sequência.
- O `audience-voc` entregou objeções e falta transformá-las em respostas estruturadas.
- Há `offer-canvas` existente para uma campanha e a seção de objeções está vazia ou fraca.

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| `campaign_id` e `business` | Sim | argumento da skill ou contexto da conversa |
| `audience-voc` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/audience-voc.json` |
| `brief` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| `offer-canvas` anterior | Não | `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json` |
| Feedback de vendas/suporte | Não | fornecido pelo usuário |

Se faltar `audience-voc` ou `brief`, peça ao usuário (ou acione o `copy-chief`) em vez de inventar objeções.

## Procedimento

1. Ler `squads/copy-squad/agents/offer-strategist.md` e assumir o papel de Offer & Positioning Strategist, **ou** delegar ao subagent `copy-squad--offer-strategist` via Agent tool com o contexto acima.
2. Carregar a task `squads/copy-squad/tasks/map-objections.md` e o checklist `squads/copy-squad/checklists/offer-quality-checklist.md`.
3. Consolidar objeções do `audience-voc`, do brief e do research packet; deduplicar mantendo a linguagem do cliente.
4. Categorizar cada objeção (price, trust, complexity, risk, time, compatibility, need, other) e estimar `frequency` com evidência; sem evidência, `low` e resposta como hipótese.
5. Redigir a resposta ancorada em `proof_ids`, `mechanism` ou redução de risco aprovada; nunca com promessa, número ou prazo novos.
6. Listar claims sensíveis (preço, garantia, resultado, autoridade, depoimento, comparativo) em `needs_approval` para o gate G3.
7. Persistir uma nova versão do `offer-canvas.json` (sem sobrescrever a anterior) e registrar o envelope em `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl`.
8. Informar ao usuário as 3 objeções dominantes, as respostas ancoradas e o que ficou como hipótese ou pendência.

## Saída

- **Contrato:** `squads/copy-squad/contracts/offer-canvas.schema.json` (campo `objection_responses`: `objection`, `response`, `proof_ids`, `mechanism`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json`.
- **Envelope:** `handoff-envelope` para `hook-angle-creator` ou `conversion-copywriter`, `gate: G3` quando houver claim sensível.

## Gates humanos e risco

- **G3:** obrigatório quando alguma resposta citar preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças.
- Risco do artefato: `low` enquanto for insumo interno (`offer-canvas`); `high` e G3 se houver claim sensível. Quando as respostas forem usadas em copy publicada, herdam o risco da peça de destino (mínimo medium, G4).
- A skill nunca publica, envia nem altera páginas. Não valida o próprio trabalho: o `compliance-checker` e o `approval-owner` fazem a validação.

## Exemplo

Pedido: "/copy-objection-handler camp-mentoria-caixa" (exemplo ilustrativo).

Resultado resumido:

```json
{
  "objection_responses": [
    {
      "objection": "Não tenho tempo para aprender planilha",
      "response": "O modelo já vem preenchido e a revisão semanal é conduzida pelo mentor",
      "proof_ids": ["prv-demo-modelo"],
      "mechanism": "Modelo pré-configurado e revisão guiada"
    }
  ],
  "needs_approval": []
}
```

## Anti-padrões

- Inventar objeções "típicas" sem evidência do público.
- Responder objeção com promessa de resultado ou estatística sem fonte.
- Responder à objeção de preço citando valor que o humano ainda não aprovou.
- Misturar objeções de públicos ou de negócios diferentes.
- Sobrescrever a versão anterior do `offer-canvas`.
- Escrever a copy final da página ou do e-mail (papel de outros agentes).

## Quando NÃO Ativar

- Quando o pedido é escrever a seção de FAQ ou a landing page final: use `/copy-landing-page-architect`.
- Quando o objetivo é organizar depoimentos e dados: use `/copy-proof-builder`.
- Quando ainda não existe público nem brief: use `/copy-voc-extractor` ou `/copy-briefing-master` antes.
- Quando a conversa é sobre objeções em contexto não comercial (reuniões internas, conflitos pessoais).
- Quando o usuário quer apenas definir preço ou garantia: é decisão humana, não da skill.
