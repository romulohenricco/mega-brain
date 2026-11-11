---
name: copy-cro-hypothesis-builder
description: "Transforma resultados de performance de copy em hipóteses de CRO testáveis, de variável única, priorizadas por ICE, sem declarar vencedor sem critério."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id ou descrição curta do resultado a otimizar]"
---

# /copy-cro-hypothesis-builder — Construtor de Hipóteses de CRO

> **Auto-Trigger:** pedido para transformar resultados de campanha em hipóteses de teste, priorizar o que testar ou montar um teste A/B de copy
> **Keywords:** "hipóteses de cro da campanha", "hipoteses de cro da campanha", "hipótese de cro da campanha", "hipotese de cro da campanha", "hipóteses de teste a/b de copy", "hipoteses de teste a/b de copy", "hipótese de teste a/b de copy", "hipotese de teste a/b de copy", "teste a/b de copy", "teste ab de copy", "backlog de testes a/b de copy", "cro de copy"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

---

## Propósito

Converter achados de performance de peças de copy em hipóteses testáveis, de variável única, priorizadas por impacto, confiança e facilidade (ICE), com desenho preliminar de teste, para que o squad saiba o que testar primeiro e por quê.

## Quando ativar

- O usuário traz resultados de campanha (métricas, período, canal) e quer saber o que testar.
- O usuário pede um backlog de testes A/B para uma landing page, anúncio, e-mail ou roteiro.
- O `wf-performance-loop` chega à fase de hipóteses.
- Um teste terminou e é preciso planejar o próximo.

## Entradas

| Entrada | Obrigatória | Observação |
|---|---|---|
| `business` (slug) e `campaign_id` | Sim | Um único negócio por execução |
| Métricas do período (export, planilha ou colagem) | Sim | Fornecidas pelo usuário; o squad não acessa GA4, Ads ou CRM sem credencial e aprovação |
| Baseline, meta e período anterior | Recomendado | Se faltarem, a lacuna é declarada e a confiança reduzida |
| `performance-analysis` existente | Se houver | Em `.data/copy-squad/{business}/{campaign_id}/08-performance/` |
| Aprendizados anteriores | Opcional | Via `retrieve-knowledge` do `knowledge-curator` |

## Procedimento

1. Leia `squads/copy-squad/agents/cro-analyst.md` e assuma o papel, **ou** delegue ao subagent `copy-squad--cro-analyst` pelo Agent tool.
2. Se não existir `performance-analysis` para a campanha, carregue `squads/copy-squad/tasks/analyze-performance.md` e execute-a primeiro com os dados fornecidos.
3. Carregue `squads/copy-squad/tasks/build-cro-hypotheses.md` e siga os passos: ler achados, consultar aprendizados, escrever hipóteses no formato "Se mudarmos {variável} de A para B, então {métrica} deve {efeito}, porque {razão}", garantir variável única, pontuar ICE com justificativa e ordenar a fila.
4. Se o usuário quiser o desenho do teste, carregue `squads/copy-squad/tasks/design-ab-test.md` (variável única, métrica primária, MDE, amostra, duração, critério de parada definido antes).
5. Aplique `squads/copy-squad/checklists/cro-test-checklist.md`; abaixo de 0.80, corrija (máximo 2 ciclos).
6. Persista em `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}.json` (nova versão, sem sobrescrever) e emita o envelope de handoff em `handoffs.jsonl`.
7. Encaminhe ao `knowledge-curator` para registrar o aprendizado e ao `copy-chief` para decidir o próximo ciclo.

## Saída

- Contrato: `squads/copy-squad/contracts/performance-analysis.schema.json` (campo `hypotheses`, com `priority` e `ice`).
- Caminho: `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}.json`.
- Versão legível: `squads/copy-squad/templates/performance-report-tmpl.md`.

## Gates humanos e risco

- Executar qualquer teste em produção exige G4: `approval-decision` com `decision == approved` (nunca `approved_with_edits`), dentro de 72 h e com `payload_sha256` verificado por `squads/copy-squad/scripts/approval_tools.py hash`, pedido montado pelo `copy-publisher`; esta skill apenas recomenda e desenha.
- Hipóteses que dependem de novo claim (preço, garantia, resultado, autoridade, depoimento, comparativo, saúde, financeiro) ficam `needs_approval` e exigem G3.
- Decisões de posicionamento, preço, promessa e segmento permanecem humanas.
- Critério padrão de vencedor (D20): `AB_CONFIDENCE_LEVEL = 0.95` e `AB_MIN_SAMPLE_PER_VARIANT` (tokens de `data/token-registry.yaml`). Sem atingir os dois, `winner_declared = false`; `significance.confidence_level` é número (ex.: `0.95`), nunca texto. Critério diferente só se pré-registrado no `design-ab-test` antes do teste.
- Nunca atribuir causalidade sem isolamento de variáveis.

## Exemplo

Pedido (ilustrativo): "O CTA de preço da página de vendas do SaaS de fluxo de caixa tem 3,0% de clique e 62% de queda de scroll antes do preço. O que testamos?"

Resposta resumida: hipótese 1, mover a garantia para acima do CTA de preço (variável: posição da garantia; efeito esperado: +10% a +20% relativo no clique; ICE 8/6/9); hipótese 2, trocar o título do hero pela dor específica (ICE 7/5/8). Teste prioritário: A/B 50/50, métrica primária clique no CTA, MDE 0,6 p.p., amostra por variação calculada com baseline de 3,0%, critério de parada registrado antes do início.

## Anti-padrões

- Hipótese vaga ou com várias variáveis.
- ICE sem justificativa.
- Declarar que uma variação "venceu" com poucos dados.
- Atribuir causalidade a correlação de período.
- Acessar contas de mídia sem credencial e aprovação.
- Misturar dados de negócios diferentes.

## Quando NÃO Ativar

- Para escrever a copy das variações (use as skills de produção, como `/copy-hook-generator` ou `/copy-ad-variation-generator`).
- Para revisar tom de voz ou checar claims (use `/copy-brand-voice-check` ou `/copy-fact-checker`).
- Quando não há nenhum dado de performance nem tráfego para testar.
- Para decidir estratégia, preço ou promessa (decisão humana).
- Para publicar ou alterar páginas, anúncios ou e-mails.
