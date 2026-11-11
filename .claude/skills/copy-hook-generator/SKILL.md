---
name: copy-hook-generator
description: "Gera 20+ ângulos e hooks ranqueados a partir do brief e do research packet, sem promessas sem prova."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta]"
---

# /copy-hook-generator — Gerador de Hooks e Ângulos

> **Auto-Trigger:** pedido para criar hooks, headlines, ganchos ou ângulos de copy
> **Keywords:** "hooks de anúncio", "hooks de anuncio", "hooks de copy", "hooks para a campanha", "hooks da campanha", "gerar hooks e ângulos de copy", "gerar hooks e angulos de copy", "ganchos de abertura de anúncio", "ganchos de anúncio", "ganchos de anuncio", "headlines de anúncio", "headlines de anuncio", "headlines de venda", "ângulos e hooks de anúncio", "angulos e hooks de anuncio", "ângulos de copy", "angulos de copy"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Gera o banco de ângulos e hooks da campanha (mínimo de 20 distintos no modo completo, `MIN_ANGLES_FULL`; mínimo de 5 no fast lane, `MIN_ANGLES_FAST_LANE`; shortlist de 5 para o G2, `ANGLES_SHORTLIST_SIZE`), cada um com promessa específica, mecanismo, prova necessária, risco e força prevista justificada. Executa a task `generate-angles-hooks` pelo agente hook-angle-creator.

## Quando ativar

- Brief aprovado e research packet disponível, antes de produzir peças.
- Fast lane: variações rápidas de headline, CTA ou post para uso interno ou teste.
- Derivar variações de ângulos aprovados por estágio de consciência ou formato.
- Renovar ângulos quando houver fadiga indicada pelo cro-analyst.

## Entradas

| Entrada | Obrigatória | Observação |
|---|---|---|
| business e campaign_id | sim | Define o escopo e os caminhos em `.data/copy-squad/` |
| brief aprovado (`01-strategy/brief.json`) | sim | Objetivo, público, oferta, canal e estágio de consciência |
| research packet (`02-research/research-packet.json`) | sim no modo completo | Fatos, provas, objeções e lacunas |
| offer-canvas e audience-voc | não | Mecanismo, provas, urgência legítima e frases do cliente |
| modo (completo, fast ou variants) | sim | Padrão: completo; fast lane só para uso interno ou teste (risco low) |

## Procedimento

1. Ler `squads/copy-squad/agents/hook-angle-creator.md` e assumir o papel, OU delegar ao subagent `copy-squad--hook-angle-creator` via Agent tool.
2. Carregar `squads/copy-squad/tasks/generate-angles-hooks.md` e conferir pré-condições (brief aprovado, packet no modo completo).
3. Consultar a biblioteca do negócio por ângulos vencedores e learnings aprovados (`tasks/retrieve-knowledge.md`).
4. Planejar as dimensões (dor, desejo, mecanismo, prova, contraste, identidade, custo de não agir, história, curiosidade, objeção), com limite de 35% por dimensão.
5. Gerar os ângulos com hook, promessa específica, mecanismo e prova necessária; remover escassez, urgência e autoridade falsas (urgência só com `legitimate_urgency.exists` true).
6. Classificar `risk_level`, marcar `needs_approval` conforme `squads/copy-squad/data/risk-policy.yaml` e preencher `predicted_strength` com `reason`.
7. Derivar variações por estágio de consciência e formato quando o brief exigir.
8. Persistir em `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json`, aplicar `squads/copy-squad/checklists/angle-quality-checklist.md` (QG-ANGLES: produtor hook-angle-creator, executor `copy-chief`) e emitir o handoff-envelope; se houver ângulo de risco alto ou campanha multi-ativo, endereçar ao approval-owner com gate G2.

## Saída

- Contrato: `squads/copy-squad/contracts/angles.schema.json`.
- Caminho: `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json`.
- Envelope: `squads/copy-squad/contracts/handoff-envelope.schema.json`, registrado em `handoffs.jsonl` da campanha.

## Gates humanos e risco

- **G2 (aprovação de ângulo):** obrigatório em risco alto ou campanha multi-ativo; nenhuma produção em escala antes dele.
- **G3 (claims):** ângulos com preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças ficam `needs_approval` e risco alto.
- Fast lane: só uso interno ou teste (risco low), com `QG-COMPLIANCE` em modo leve e amostragem humana de 20% (gate SAMPLING, pedido montado pelo copy-publisher). Ângulo que será publicado, enviado ou veiculado é no mínimo medium, e ângulo de risco alto sai da fast lane.

## Exemplo

Pedido: "/copy-hook-generator camp-saas-fluxo-caixa — gerar hooks de anúncio para o SaaS de fluxo de caixa".

Resultado esperado (exemplo ilustrativo): 22 ângulos em 8 dimensões, 5 recomendados para o G2; ângulo "clareza antes de controle" com risco baixo e força 71 justificada; ângulo de economia de tempo com número marcado risco alto, `needs_approval` true e prova necessária listada; ângulo de urgência descartado por falta de base real.

## Anti-padrões

- Entregar 20 variações da mesma promessa.
- Usar escassez, urgência ou autoridade falsas.
- Prometer resultado sem evidência no packet.
- Tratar a força prevista como resultado medido.
- Pular o G2 em risco alto.
- Escrever a página, o e-mail ou o anúncio completos.

## Quando NÃO Ativar

- Quando o pedido é a peça completa (página, e-mail, anúncio, roteiro): use o copywriter do formato.
- Quando falta o brief aprovado: acione `/copy-briefing-master` primeiro.
- Quando falta pesquisa no modo completo: acione a task `build-research-packet`.
- Quando o objetivo é otimizar CTAs existentes: use `/copy-cta-optimizer`.
- Quando a decisão é de posicionamento, preço ou promessa: é decisão humana (G1).
