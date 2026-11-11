---
name: copy-brand-voice-check
description: "Revisa se uma peça segue o guia de voz do negócio, com score 0-100, desvios por severidade e reescritas mínimas que preservam fatos e claims."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[asset_id ou texto a revisar]"
---

# /copy-brand-voice-check — Revisão de Tom e Voz da Marca

> **Auto-Trigger:** pedido para revisar tom de voz, voz da marca ou consistência verbal de um texto
> **Keywords:** "tom de voz da copy", "tom de voz da marca da campanha", "revisar o tom de voz da copy", "revisa o tom de voz da copy", "revisar tom de voz da copy", "voz da marca da campanha", "brand voice da campanha", "guia de voz da marca da campanha", "criar guia de voz da marca da campanha"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Compara uma peça já editada com o `brand-voice-guide` do negócio e emite um `brand-review`: score de alinhamento (0-100), issues por severidade, reescritas mínimas e decisão `approved_for_next_stage`, sem tocar em fatos, preços ou claims.

## Quando ativar

- O usuário pede para criar o guia de voz da marca (a skill conduz `define-brand-voice`, sem revisar).
- Uma peça editada (e-mail, anúncio, página, post, roteiro, microcopy) precisa de validação de tom antes do compliance.
- O usuário pergunta se um texto "está na voz da marca" ou quer revisar o tom.
- Uma variação de uso interno (risco low) caiu na amostragem de 20% e o copy-publisher abriu o pedido SAMPLING.
- Houve correção humana de tom e é preciso reavaliar peças relacionadas.

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| `business` e `campaign_id` | Sim | argumento da skill ou contexto da conversa |
| Peça editada (`edit-report` + draft) | Sim | `.data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/edit-report-v{n}.json` |
| `brand-voice-guide` | Sim | `.data/copy-squad/{business}/_brand/brand-voice-guide.json` |
| Nível de risco da peça | Não | execution-plan ou brief |

Se o guia não existir, a skill não revisa: ela ativa apenas para propor e conduzir a definição do guia (`tasks/define-brand-voice.md`, com G1 na primeira vez).

## Procedimento

1. Ler `squads/copy-squad/agents/brand-voice-guardian.md` e assumir o papel de Brand Voice Guardian em modo revisão, **ou** delegar ao subagent `copy-squad--brand-voice-guardian` via Agent tool.
2. Carregar a task `squads/copy-squad/tasks/review-brand-voice.md` e o checklist `squads/copy-squad/checklists/brand-voice-review-checklist.md`.
3. Confirmar que o guia existe, é do mesmo `{business}` e que o revisor não é o produtor nem o editor da peça (AP05). Este passo é o QG-BRAND: produtor é o `copy-editor` (versão editada) e executor é o `brand-voice-guardian`.
4. Comparar a peça, seção a seção, com personalidade, tom do contexto, vocabulário preferido e proibido, formalidade e regras de estilo.
5. Registrar cada desvio com `severity` (critical, medium, low), `excerpt` literal, `problem`, `suggested_revision` mínima e `reason` ligada a regra do guia.
6. Congelar preços, números, prazos, garantias e claims; se algum parecer errado, escalar ao `compliance-checker` em vez de reescrever.
7. Calcular `brand_alignment_score` e decidir `approved_for_next_stage` (verdadeiro somente com score >= 80 e zero issue critical).
8. Persistir `brand-review-v{n}.json` (nova versão a cada revisão; nunca sobrescreve) em `.data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/` e anexar o envelope a `handoffs.jsonl` (para `compliance-checker` se aprovada; para `copy-editor` se reprovada).
9. Resumir ao usuário: score, issues críticas, reescritas sugeridas e lacunas do guia.

## Saída

- **Contrato:** `squads/copy-squad/contracts/brand-review.schema.json`.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/brand-review-v{n}.json`.
- **Envelope:** `handoff-envelope` com `from_agent: brand-voice-guardian` e `gate: null`.

## Gates humanos e risco

- Sem gate humano direto; o `brand-review` compõe o pacote do G4 (peças de risco medium e high).
- **G1:** exigido apenas quando a skill precisar criar a primeira versão do guia. O guia é validado pelo humano em G1; `define-brand-voice` não passa por QG-BRAND (o revisor seria o próprio produtor, AP05).
- **G5:** correções humanas de tom viram exemplos do/don't em nova versão do guia.
- Máximo de 2 ciclos de rework com o `copy-editor`; depois, escalar ao `copy-chief`.
- A skill nunca publica nem envia nada.

## Exemplo

Pedido: "/copy-brand-voice-check eml-nutricao-v2" (exemplo ilustrativo).

```json
{
  "text_id": "eml-nutricao-v2",
  "brand_guide_id": "bvg-negocio-exemplo-v1",
  "brand_alignment_score": 74,
  "tone_match": "Parcial: início próximo, meio técnico demais",
  "issues": [
    {"severity": "critical", "excerpt": "otimize seu EBITDA", "problem": "Jargão proibido sem definição", "suggested_revision": "melhore o resultado antes de juros e impostos (EBITDA)", "reason": "vocabulary.forbidden: jargão sem explicação"}
  ],
  "approved_for_next_stage": false
}
```

## Anti-padrões

- Revisar sem guia, com tom presumido.
- Reescrever a peça inteira em vez de ajustes mínimos.
- Alterar preço, número, prazo ou claim para "soar melhor".
- Aprovar com issue critical aberta por pressão de prazo.
- Criticar por gosto sem citar a regra do guia.
- Criar argumentos ou promessas novas durante a revisão.

## Quando NÃO Ativar

- Para revisar sem guia de voz: não revise; conduza antes a definição do guia (tarefa `define-brand-voice`).
- Quando o texto é rascunho não editado: passe antes pelo `copy-editor` (`/copy-concision-editor`).
- Quando o foco é verificar fatos, promessas ou conformidade legal: use `/copy-fact-checker`.
- Quando o pedido é criar copy nova ou mudar a estratégia da mensagem.
- Quando o "tom de voz" se refere a áudio, fala ou dublagem, e não a texto.
