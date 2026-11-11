---
name: copy-concision-editor
description: "Corta 20% a 40% de um texto de copy sem perder o argumento, preservando claims, números, fontes e CTA, com log de mudanças e relatório de edição."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[asset_id ou campaign_id, e meta de redução opcional, ex.: 30%]"
---

# /copy-concision-editor — Editor de Concisão

> **Auto-Trigger:** pedido para enxugar, cortar ou encurtar um texto de copy mantendo o argumento
> **Keywords:** "enxugar a copy da", "enxugar a copy do", "enxugar essa copy de", "enxuga a copy da", "enxuga a copy do", "encurtar a copy da", "encurtar a copy do", "encurta a copy da", "cortar a copy da", "cortar a copy do", "corta a copy da", "corta a copy do", "enxugar o texto de venda", "enxugar a página de vendas", "enxugar a pagina de vendas", "cortar o roteiro de venda", "corta o roteiro de venda", "cortar o roteiro de anúncio", "corta o roteiro de anúncio", "corta esse roteiro de anúncio", "corta esse roteiro de anuncio", "deixar a copy mais enxuta", "deixar a copy mais concisa", "editor de concisão de copy", "editor de concisao de copy"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Reduzir um rascunho de copy em 20% a 40% sem perder problema, mecanismo, prova, oferta, objeção e CTA, e entregar um `edit-report` auditável com cada corte justificado.

Esta skill é a porta do Editor de Concisão do squad `copy-squad`: ela ativa o agente `copy-editor` no modo concisão e executa a task `tasks/edit-for-concision.md`. O texto melhora, mas não é aprovado: depois vêm a revisão de voz, a conformidade e os gates humanos.

## Quando ativar

- O usuário pede para "cortar", "enxugar", "deixar mais conciso" ou "reduzir" um texto de copy já escrito por outro agente.
- Um anúncio, e-mail, roteiro curto ou página excede o limite do canal.
- A fast lane (`wf-fast-variation`) precisa de versões curtas, para uso interno ou teste, de uma peça aprovada.
- Há feedback de que um texto está repetitivo ou longo demais.

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| Draft de outro agente (conversion-copy, content-piece, video-script ou email-journey) | Sim | `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` |
| brief aprovado | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| Limite do canal | Não | `squads/copy-squad/data/channel-specs.yaml` |
| Meta de redução | Não (padrão 20 a 40%) | Argumento da skill |
| Guia de voz | Não | `.data/copy-squad/{business}/_brand/brand-voice-guide.json` |

Se faltar `business`, `campaign_id` ou `asset_id`, peça ao usuário antes de agir.

## Procedimento

1. Ler `squads/copy-squad/agents/copy-editor.md` e assumir o papel de Copy Editor, OU delegar ao subagent `copy-squad--copy-editor` via Agent tool com o `asset_id` e o caminho do draft.
2. Carregar `squads/copy-squad/tasks/edit-for-concision.md` e o checklist `squads/copy-squad/checklists/edit-quality-checklist.md`.
3. Confirmar que o draft foi escrito por outro agente; se foi o próprio editor, parar e pedir reatribuição ao `copy-chief` (AP05).
4. Medir as palavras do original e extrair o inventário intocável: claims, números, fontes, depoimentos citados, texto obrigatório e CTA.
5. Cortar em passes (repetição, preenchimento, jargão e rodeios, compressão estrutural) e testar o argumento após cada passe.
6. Recontar, calcular `reduction_pct` e verificar a banda de 20 a 40; justificar qualquer desvio.
7. Conferir a preservação item a item e o limite do canal.
8. Persistir o `edit-report` (QG-EDIT: produtor copy-editor, executor `copy-chief`; a autoverificação não aprova o gate) e emitir o envelope de handoff para o `brand-voice-guardian`; registrar o evento no journey log (`.data/logs/journey/lifecycle-events.jsonl`).

## Saída

- Contrato: `squads/copy-squad/contracts/edit-report.schema.json`.
- Caminho: `.data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/edit-report-v{n}.json` (nova versão; nunca sobrescreve).
- Envelope: `contracts/handoff-envelope.schema.json`, em `.data/copy-squad/{business}/{campaign_id}/handoffs.jsonl`, de `copy-editor` para `brand-voice-guardian`.
- Resumo ao usuário: palavras antes e depois, `reduction_pct`, principais cortes e o que foi escalado.

## Gates humanos e risco

- Nenhum gate humano próprio. O edit-report é insumo para G3 (claims) e G4 (aprovação final).
- O editor não aprova: o status máximo é `ready` para revisão.
- Se a edição revelar claim sem fonte, promessa absoluta ou dado pessoal, o item vai para `remaining_risks` (compliance-checker) ou `escalations` (copy-chief).

## Exemplo

Pedido: "Corta esse roteiro de anúncio, está longo demais para 45 segundos" (roteiro de 180 palavras).

Resultado resumido (exemplo ilustrativo): 180 para 118 palavras (`reduction_pct` 34.4), claims preservados, abertura expositiva removida e duas frases de repetição eliminadas; uma afirmação sem número marcada para o compliance-checker.

## Anti-padrões

- Bater o percentual cortando prova, garantia ou CTA.
- Alterar números, preços ou fontes para "soar melhor".
- Reescrever o texto com outra tese e chamar de concisão.
- Declarar o texto aprovado ou pronto para publicar.
- Forçar 20% em um texto que já era enxuto.
- Editar texto que o próprio agente escreveu.

## Quando NÃO Ativar

- Quando o pedido é escrever um texto novo ou criar variações de conteúdo (use o redator do squad).
- Quando o usuário quer validar claims, fontes ou riscos legais (use `/copy-fact-checker`).
- Quando o texto é um disclaimer, termo legal ou aviso obrigatório (intocável).
- Quando a tarefa é revisar tom de voz (use `/copy-brand-voice-check`).
- Quando o pedido é traduzir ou localizar (acione o `localization-specialist` via `/copy-squad`).
- Quando não existe brief nem draft de outro agente.
