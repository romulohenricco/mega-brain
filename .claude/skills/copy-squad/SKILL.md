---
name: copy-squad
description: "Porta de entrada do squad de copy: ativa o copy-chief, qualifica a demanda, escolhe o workflow e conduz a produção com gates humanos."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[demanda de copy ou campaign_id]"
---

# /copy-squad — Porta de Entrada do Squad de Copy

> **Auto-Trigger:** pedido para acionar o time de copy, planejar uma campanha de copy ou iniciar uma demanda do time de copy
> **Keywords:** "squad de copy para", "copy squad", "time de copy para", "time de copywriting", "chama o copy chief", "escrever copy de", "escreva uma copy de", "escreva a copy da", "preciso de uma copy para", "preciso de um headline de copy para", "revisar a copy da", "campanha de copy para", "campanha completa de copy", "pedido de copy para", "traduzir a copy da", "microcopy de produto", "microcopy da campanha", "copy de newsletter", "escreva um e-mail de vendas", "escreva um email de vendas", "copy do anúncio", "copy do anuncio", "landing page e uma sequência de e-mails", "landing page e uma sequencia de e-mails", "landing page e uma sequência de e-mail", "landing page e uma sequencia de e-mail", "landing page e e-mails de venda", "sequência de e-mails e uma landing page", "sequencia de e-mails e uma landing page"
> **Prioridade:** ALTA
> **Tools:** Read, Write, Glob, Grep, Agent

## Propósito

Ativa o `copy-chief` (Copy Command Center), qualifica a demanda de copy, avalia o risco, escolhe o workflow entre os cinco do squad e conduz a execução delegando cada passo ao agente certo, sempre com aprovação humana nos gates devidos. Esta skill roda na sessão principal: a sessão assume o papel do `copy-chief` e delega cada etapa aos subagents `copy-squad--{agente}`. Um subagent não cria subagent nem conversa com o humano, por isso a condução do workflow e as paradas nos gates acontecem na conversa da sessão principal.

## Quando ativar

- O usuário quer produzir copy (landing page, anúncio, e-mails, roteiro, conteúdo, microcopy) com um time estruturado.
- O usuário menciona o squad, o time ou o chief de copy.
- Há uma campanha de copy em andamento e é preciso planejar, monitorar ou escalar uma decisão.
- Há dados de performance de copy e a intenção é abrir um ciclo de otimização.
- Há um ativo longo a reaproveitar em vários formatos.
- O pedido é multi-ativo (por exemplo, "uma landing page e uma sequência de e-mails"): é a porta de entrada que calcula risco, workflow e G2; as skills de formato único não substituem esta entrada.
- O pedido cai em tasks sem skill própria, alcançáveis só por esta entrada: `localize-copy`, `write-ux-microcopy`, `write-content-piece`, `write-crm-message`, `design-offer`, `define-brand-voice`, `analyze-performance`, `check-compliance`.

## Entradas

| Entrada | Obrigatória | Observação |
|---|---|---|
| Demanda bruta (texto livre) | sim | Objetivo, público, canal, oferta, prazo e restrições, quando houver |
| `business` (slug) | sim | Unidade de negócio; define o isolamento de dados |
| `campaign_id` | não | Para retomar campanha existente; novo é gerado como `camp-{slug}` |
| Contexto do workspace | não | Leitura somente de `workspace/businesses/{business}/L0-identity/`, `L1-strategy/`, `L2-tactical/` |

## Procedimento

1. Ler `squads/copy-squad/agents/copy-chief.md` e assumir o papel na sessão principal: quem conduz os passos 5 a 8 (despachar os subagents e parar nos gates humanos) é a sessão principal. O subagent `copy-squad--copy-chief` não conduz o workflow; no máximo prepara intake e plano e devolve `demand-intake`, `execution-plan` e o envelope à sessão principal.
2. Carregar `squads/copy-squad/tasks/intake-demand.md`; qualificar a demanda e gerar o `demand-intake` (até 5 perguntas, com `priority`; se houver `needs_input`, parar e perguntar). O QG-INTAKE é aplicado pelo `brief-master` (subagent `copy-squad--brief-master`), nunca pelo `copy-chief`.
3. Carregar `squads/copy-squad/tasks/plan-execution.md`; calcular o risco (`squads/copy-squad/data/risk-policy.yaml`), escolher o workflow e gerar o `execution-plan`.
4. Apresentar ao usuário o resumo do plano (workflow, risco, passos principais, gates) e confirmar antes de produzir.
5. Conduzir o workflow escolhido (`squads/copy-squad/workflows/wf-copy-production.yaml`, `wf-campaign-launch.yaml`, `wf-fast-variation.yaml`, `wf-performance-loop.yaml` ou `wf-content-repurposing.yaml`), delegando cada passo ao subagent `copy-squad--{agente}` (ex.: `copy-squad--brief-master`, `copy-squad--conversion-copywriter`).
6. Antes de cada gate humano (G1, G2, G3 e G4, e a amostragem de uso interno), delegar ao subagent `copy-squad--copy-publisher` a task `prepare-approval-package` (produtor único do `approval-request`, hash por `approval_tools.py hash`). Em seguida, parar na conversa: apresentar o pedido ao `approval-owner` (papel humano, sem subagent) e aguardar a decisão dele. A decisão é registrada só pelo humano (CLI com `!`, ou mensagem dele transcrita no chat pela sessão principal fora do papel de copy-chief, citada literalmente em `comments`); subagents nunca gravam `approval-decision`, e `approved_with_edits` nunca autoriza execução (a rodada seguinte exige nova decisão `approved`). G5 não usa pedido: é `correct-agent-failure`.
7. Persistir os artefatos em `.data/copy-squad/{business}/{campaign_id}/`, registrar os envelopes em `handoffs.jsonl` e o journey log em `.data/logs/journey/lifecycle-events.jsonl`.
8. Para publicar (pós-decisão do G4), o `copy-publisher` roda `approval_tools.py verify --for-execution --request <rodada>/approval-request.json --decision <rodada>/approval-decision.json --payload <rodada>/payload.json` (o `payload.json` gravado por `prepare-approval-package` na pasta da rodada do G4, que é o que se executa, não o draft) sem `--now` nem `--config` (só valem em teste) e a sessão (no papel de `copy-chief`) reexecuta o comando sem flags e contra-assina o preflight. Nenhum subagent executa ação externa: o `copy-publisher` emite o pacote de execução e registra o `publish-receipt`, e a execução é do humano ou da própria sessão principal. Monitorar com `squads/copy-squad/tasks/monitor-pipeline.md` (cadências diária, semanal, mensal e trimestral) e fechar a campanha ao receber `publish-receipt` e `learning-record`.

## Saída

- `demand-intake` em `.data/copy-squad/{business}/{campaign_id}/00-intake/demand-intake.json` (contrato `squads/copy-squad/contracts/demand-intake.schema.json`).
- `execution-plan` em `.data/copy-squad/{business}/{campaign_id}/00-intake/execution-plan.json` (contrato `squads/copy-squad/contracts/execution-plan.schema.json`).
- Resumo ao usuário: workflow, risco, passos, gates e próxima ação.
- Envelope de handoff para o `brief-master` (`squads/copy-squad/contracts/handoff-envelope.schema.json`).

## Gates humanos e risco

| Risco | Exemplos | Regra |
|---|---|---|
| low | Somente uso interno: rascunho, pesquisa, variações para backlog ou teste, ideias. Nada low é publicado, enviado ou veiculado | Avança com log; compliance leve; revisão humana por amostragem de 20 por cento |
| medium | Post orgânico, artigo, e-mail de nutrição, roteiro orgânico (piso de toda ação externa) | Editor, voz da marca, compliance leve, G1 e G4 (G2 se multi-ativo) |
| high | Landing page, anúncio pago, e-mail de venda, preço, garantia, resultado, depoimento, comparativo, saúde, finanças | Compliance completo, G1, G2, G3 e G4 explícitos (fonte canônica: `squads/copy-squad/data/risk-policy.yaml`) |

Gates: G1 (brief), G2 (ângulo), G3 (claims), G4 (final), G5 (correção de falha, sem pedido). Claim sensível sobe o risco para high e exige G3. Nada é publicado, enviado ou veiculado sem `approval-decision` `approved` válido (janela de 72 horas a partir da decisão), `payload_sha256` igual ao recalculado pelo script e preflight contra-assinado. Silêncio nunca é aprovação. Git push e PR estão fora do escopo do squad.

## Exemplo

Pedido (exemplo ilustrativo): "Quero uma landing page e uma sequência de e-mails para vender a mentoria de gestão financeira para pequenas empresas."

Resultado: `demand_type: conversion`; garantia citada no pedido eleva o risco para `high`; workflow `wf-campaign-launch` (dois ativos); plano com G1, G2, G3 e G4; `next_action: brief-master executa create-brief`; perguntas pendentes sobre preço e provas autorizadas (máx. 5).

## Anti-padrões

- Escrever a copy final no lugar dos agentes especialistas.
- Pular a qualificação da demanda ou o cálculo de risco.
- Fazer mais de 5 perguntas ao usuário.
- Publicar, enviar ou agendar sem aprovação humana registrada.
- Calcular o hash de cabeça, executar com `approved_with_edits` ou registrar `approval-decision` em nome do humano (a transcrição de `human-chat-confirmed` é da sessão principal fora do papel de copy-chief, com a mensagem literal em `comments`).
- Pedir a um subagent que publique, envie ou veicule, ou passar `--now` ou `--config` ao `approval_tools.py` fora de teste.
- Tentar que um subagent conduza o workflow ou converse com o humano nos gates.
- Inventar preço, garantia, depoimento, número ou prova.
- Usar o mesmo agente para produzir e validar o mesmo artefato.
- Gravar dados fora de `.data/copy-squad/` ou escrever no workspace.

## Quando NÃO Ativar

- O pedido é de uma tarefa pontual já coberta por uma skill específica do squad (ex.: apenas gerar hooks, só revisar o tom de voz, só checar claims): use a skill correspondente.
- O pedido é de design, edição de vídeo ou desenvolvimento de código: fora do escopo do squad. Compra, configuração e veiculação de mídia são execução externa (G4 mais humano ou sessão principal, nunca subagent); a copy do anúncio é escopo do squad.
- O usuário quer apenas uma resposta rápida sobre conceitos de copy, sem produzir artefatos.
- O pedido é de publicação ou deploy de código (push, PR, release): exclusivo do @devops.
