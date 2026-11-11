---
name: copy-briefing-master
description: "Cria e consolida o brief operacional de copy (objetivo, KPI, público, oferta, restrições e critérios de aceite), separando fatos de hipóteses."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta da demanda]"
---

# /copy-briefing-master — Briefing Master de Copy

> **Auto-Trigger:** pedido para criar, revisar ou consolidar o brief de uma campanha de copy
> **Keywords:** "brief de copy", "brief da campanha", "brief da campanha de copy", "cria um brief de copy", "criar um brief de copy", "consolidar o brief de copy", "fechar o brief de copy", "fechar o brief da campanha", "consolidar o brief da campanha"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Transforma uma demanda de copy em um brief operacional completo, testável e sem ambiguidade, com fatos confirmados separados de hipóteses, KPI primário único, estágio de consciência, restrições e critérios de aceite verificáveis; e consolida o brief com público, oferta e pesquisa para o gate G1.

## Quando ativar

- O usuário pede para criar, revisar ou fechar o briefing de uma campanha de copy.
- Existe um `demand-intake` validado e falta o brief da campanha.
- Chegaram `audience-voc`, `offer-canvas` e `research-packet` e o brief precisa ser consolidado para aprovação (G1).
- O usuário pergunta "o que falta saber para começar a copy".

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| `business` (slug da unidade) e `campaign_id` | Sim | usuário ou contexto da sessão |
| `demand-intake` e `execution-plan` | Sim para `create-brief` | `.data/copy-squad/{business}/{campaign_id}/00-intake/` |
| `audience-voc`, `offer-canvas`, `research-packet` | Sim para `consolidate-brief` | `01-strategy/` e `02-research/` |
| Respostas do solicitante a perguntas anteriores | Não | usuário |

## Procedimento

1. Ler `squads/copy-squad/agents/brief-master.md` e assumir o papel do Brief Master, ou delegar ao subagent `copy-squad--brief-master` via Agent tool, passando `business` e `campaign_id`.
2. Escolher a task: `squads/copy-squad/tasks/create-brief.md` (brief v1 ou revisão) ou `squads/copy-squad/tasks/consolidate-brief.md` (integração e G1).
3. Carregar os arquivos exigidos pelo comando no `command_loader` do agente: contrato `brief`, checklist `brief-quality-checklist` e template `campaign-brief-tmpl`.
4. Executar a task passo a passo: classificar fatos e hipóteses, definir KPI e estágio de consciência, listar restrições, escrever critérios de aceite e formular no máximo 5 perguntas.
5. Autoverificar com `squads/copy-squad/checklists/brief-quality-checklist.md` (score maior ou igual a 0.80). O QG-BRIEF é validado pelo `copy-chief` (executor); a autoverificação do brief-master não aprova o gate.
6. Persistir em `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` (nova versão, nunca sobrescrever) e renderizar `brief.md`.
7. Anexar o envelope `handoff-envelope` em `handoffs.jsonl` e registrar o evento no journey log.

## Saída

- Contrato `brief` (`squads/copy-squad/contracts/brief.schema.json`).
- Caminho: `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` (e `brief.md`).
- Envelope com `status` `ready`, `needs_input` ou `needs_approval` e `gate: G1` quando exigido.

## Gates humanos e risco

- **G1:** aprovação do brief consolidado, obrigatória para risco medium ou high; decisor: `approval-owner`. O pedido é montado pelo `copy-publisher` (`prepare-approval-package`) em `06-approval/_campaign/g1-r{n}/`; esta skill não monta pedido de aprovação.
- Claims de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças elevam o risco para high e exigem também G3; o G3 de oferta (preço, garantia, provas) entra no mesmo pacote do G1.
- Posicionamento, preço, promessa e segmento são decisões humanas: o brief as registra, não as inventa.
- Nada é publicado ou enviado por esta skill.

## Exemplo

Entrada (exemplo ilustrativo): `/copy-briefing-master camp-mentoria-gestao` com o pedido "aumentar inscrições da mentoria de gestão financeira para pequenas empresas, canal e-mail e página, prazo de duas semanas".

Resultado esperado: `brief.json` v1 com `status: needs_input`, KPI proposto "inscrições na lista de espera em 14 dias", preço em `hypotheses_to_validate` e 3 perguntas objetivas com motivo.

## Anti-padrões

- Preencher preço, garantia, prazo ou resultado por suposição.
- Aceitar KPI sem métrica e janela de tempo.
- Escrever headlines ou ângulos no brief.
- Sobrescrever versão anterior ou pular o G1 quando a política o exige.
- Fazer mais de 5 perguntas ou perguntas sem motivo.

## Quando NÃO Ativar

- O pedido é escrever copy final, hooks ou ângulos (use `/copy-hook-generator` ou o time de produção).
- O pedido é definir preço, garantia ou posicionamento (decisão humana).
- O pedido é pesquisar concorrentes (use `/copy-competitive-angle-finder`) ou extrair voz do cliente (use `/copy-voc-extractor`).
- Não há demanda de copy: conversa casual ou dúvida técnica sem relação com campanha.
