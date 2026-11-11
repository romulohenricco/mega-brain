# Checklist: Qualidade de Copy de Conversão

## Metadata
```yaml
id: conversion-copy-checklist
name: "Checklist de copy de conversão (landing page, anúncio, CTA, e-mail de venda)"
version: 1.0.0
executor: copy-chief           # validador do gate QG-DRAFT (D7)
self_check_by: conversion-copywriter  # produtor; a autochecagem não aprova o gate
related_task: write-landing-page
related_tasks: [write-landing-page, write-ad-variations, optimize-ctas]
quality_gate: QG-DRAFT
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Verificar, com itens mensuráveis, se um draft de copy de conversão está pronto para seguir à edição, à revisão de voz e ao compliance: ancorado em fatos e provas, estruturado pelo estágio de consciência, com CTA específico, variações testáveis e claims tratados. Validador diferente do produtor (AP05).

---

## Fase 1: Insumos e rastreabilidade

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | Draft valida no schema `conversion-copy` e traz meta completo (artifact_id `{asset_id}-v{n}`, versão, status, risk_level)? | blocking | [ ] | |
| 2 | `brief_id` e `angle_id` apontam para artefatos existentes e aprovados (G1 em medium ou high; G2 só em high ou campanha multi-ativo)? | blocking | [ ] | |
| 3 | Todo fato, número ou prova citado existe no research packet ou no offer canvas? | blocking | [ ] | |
| 4 | A versão anterior foi preservada (nova versão v+1, sem sobrescrever)? | blocking | [ ] | |
| 5 | `assumptions` registra cada suposição (estágio de consciência, canal, limites)? | quality | [ ] | |

**Score Fase 1:** ___/5

---

## Fase 2: Estrutura e persuasão

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 6 | A abertura corresponde ao `awareness_stage` do brief? | blocking | [ ] | |
| 7 | Seções mínimas presentes: atenção/hero, problema, mecanismo, prova, oferta, objeções/FAQ, risco, CTA? | quality | [ ] | |
| 8 | Cada seção termina em CTA ou transição clara? | quality | [ ] | |
| 9 | A promessa é específica e coerente com o ângulo aprovado? | quality | [ ] | |
| 10 | As principais objeções do audience-voc/offer canvas têm resposta com prova ou mecanismo? | quality | [ ] | |
| 11 | A linguagem usa termos do cliente como inspiração (customer_phrases anonimizadas; citação literal só com usage_rights granted e G3) e sem jargão não explicado? | quality | [ ] | |

**Score Fase 2:** ___/6

---

## Fase 3: Claims, provas e ética

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 12 | Todo claim de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou financeiro tem `proof_id` verificado ou está em `needs_approval`? | blocking | [ ] | |
| 13 | Nenhum depoimento, número, prêmio ou autoridade foi inventado? | blocking | [ ] | |
| 14 | Urgência/escassez só existe com `legitimate_urgency.exists == true`, com motivo e prazo? | blocking | [ ] | |
| 15 | Prova usada tem `usage_rights` concedido ou está sinalizada como pendente? | blocking | [ ] | |
| 16 | `risk_level` foi escalado para high quando há claim sensível? | blocking | [ ] | |
| 17 | Itens `needs_approval` estão consolidados no envelope e G3 está sinalizado? | quality | [ ] | |

**Score Fase 3:** ___/6

---

## Fase 4: CTAs, variações e canal

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 18 | CTA final segue verbo + objeto + benefício e corresponde à ação do brief? | quality | [ ] | |
| 19 | Nenhum CTA promete algo que o destino não entrega? | blocking | [ ] | |
| 20 | Variações mudam uma única variável cada e trazem `hypothesis`? | quality | [ ] | |
| 21 | Anúncios têm pelo menos 5 variações por elemento testado? | quality | [ ] | |
| 22 | Nenhum texto excede os limites de `data/channel-specs.yaml`? | blocking | [ ] | |
| 23 | Tom e vocabulário respeitam o brand-voice-guide quando existe? | quality | [ ] | |

**Score Fase 4:** ___/6

---

## Veto conditions

Qualquer item abaixo leva a VETO imediato (score final tratado como < 0.60), independentemente da pontuação:

1. Depoimento, número, prêmio ou resultado sem fonte apresentado como fato (itens 3, 13).
2. Urgência ou escassez sem `legitimate_urgency.exists == true` (item 14).
3. Claim sensível sem `proof_id` e sem registro em `needs_approval` (item 12).
4. Draft produzido sem brief, ângulo aprovado ou research packet (item 2).
5. CTA que promete algo que o destino não entrega (item 19).
6. Versão anterior sobrescrita (item 4).

## Auto-correção (o que fazer quando falha)

| Item que falhou | Ação |
|---|---|
| 3, 12, 13 | Remover a afirmação ou movê-la para `needs_approval`; pedir prova ao offer-strategist via copy-chief |
| 6 | Reescrever a abertura conforme o estágio de consciência |
| 14 | Remover urgência; reescrever com custo de esperar verificável |
| 18, 19 | Executar `tasks/optimize-ctas.md` para o CTA |
| 20, 21 | Refazer o lote com uma variável e hipótese |
| 22 | Reescrever (não cortar) até caber no limite |
| 4 | Restaurar a versão anterior e criar v+1 |

Máximo de 2 ciclos de retrabalho; depois escalar ao copy-chief.

## Edge cases

- **Sem provas verificadas disponíveis:** o draft segue com as seções de prova marcadas `needs_approval` e confidence reduzida; não é motivo para inventar.
- **Público most_aware:** a abertura direta pela oferta é correta; não penalizar a ausência de seção de problema extensa.
- **Anúncio com limite muito curto:** priorizar clareza do benefício e do CTA; registrar em assumptions o que foi omitido.
- **Reescrita a partir de dados de performance:** nova versão com mudança isolada e hipótese; não declarar vencedor sem o cro-analyst.
- **Preço ou garantia a confirmar:** marcador explícito e needs_approval; nunca valor estimado.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 23. Itens blocking não atendidos rebaixam o resultado para no máximo REVIEW; qualquer veto condition leva a VETO.
