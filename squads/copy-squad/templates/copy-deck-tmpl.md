# Copy Deck — {asset_title}

> Renderização humana do contrato `conversion-copy` (contracts/conversion-copy.schema.json).
> Produzido por: conversion-copywriter · Revisão obrigatória: copy-editor, brand-voice-guardian, compliance-checker · Aprovação: approval-owner (G3 claims, G4 final).
> Este documento não substitui o JSON persistido em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.

## 1. Identificação

| Campo | Valor |
|---|---|
| artifact_id | {asset_id}-v{n} |
| campaign_id | camp-{slug} |
| business | {business} |
| asset_id | {asset_id} |
| versão | v{n} |
| formato | landing_page / sales_page / ad / email / sequence |
| canal | {canal} |
| brief_id | brf-{slug} |
| angle_id | ang-{slug} |
| estágio de consciência | unaware / problem_aware / solution_aware / product_aware / most_aware |
| risk_level | low / medium / high |
| status | draft / ready / needs_approval |
| confidence | 0.00 |
| produzido em | {data} |

## 2. Contexto resumido

- **Objetivo de negócio e KPI primário:** {primary_kpi}
- **Público e dor central:** {segmento / dor}
- **Promessa (do offer canvas):** {promessa}
- **Mecanismo:** {mecanismo}
- **Ação desejada:** {ação}
- **Limites do canal (data/channel-specs.yaml):** {limites}

## 3. Seções

Repita o bloco abaixo para cada seção (hero, problema, mecanismo, prova, oferta, objeções, FAQ, risco, CTA).

### Seção: {section}

**Copy**

{texto da seção}

**CTA da seção:** {cta ou transição}

| Campo | Conteúdo |
|---|---|
| claims | {lista de afirmações verificáveis feitas nesta seção} |
| proof_used | {proof_ids do offer canvas / fontes do research packet} |
| needs_approval | {claims sem prova, preço ou garantia a confirmar} |

## 4. CTAs

| # | Texto | Intenção | Estágio do funil | Canal | Observação |
|---|---|---|---|---|---|
| 1 | {texto} | {intenção} | {estágio} | {canal} | {nota} |

## 5. Variações para teste

| variation_id | elemento | texto | hipótese | caracteres / limite |
|---|---|---|---|---|
| v-{id} | headline / corpo / cta | {texto} | {hipótese em uma frase} | {n}/{limite} |

Regras: uma variável por lote; controle (baseline) identificado; vencedor só declarado pelo cro-analyst.

## 6. Claims e aprovações pendentes

| Claim | Tipo (price, guarantee, result, authority, testimonial, comparison, health, financial) | Prova (proof_id) | Status (verified / unverified) | Ação necessária |
|---|---|---|---|---|
| {claim} | {tipo} | {proof_id ou nenhuma} | {status} | {ação} |

- **Urgência / escassez:** {não usada | usada, com motivo e prazo reais do offer canvas}
- **Gate necessário:** {G3 se houver claims sensíveis; G4 para publicação}

## 7. Suposições e riscos

- **Suposições (assumptions):** {lista}
- **Riscos remanescentes:** {lista}
- **Lacunas de prova:** {lista}

## 8. Autochecagem do produtor

Referência: `checklists/conversion-copy-checklist.md` (a pontuação oficial é do copy-chief, executor do QG-DRAFT; esta é só autochecagem, self_check_by: conversion-copywriter).

- [ ] Todo fato aponta para prova ou fonte
- [ ] Claims sensíveis tratados (proof_id ou needs_approval)
- [ ] Abertura coerente com o estágio de consciência
- [ ] CTA final específico (verbo + objeto + benefício)
- [ ] Limites de caracteres respeitados
- [ ] Sem urgência sem legitimate_urgency real
- [ ] Só claims pré-aprovados; claim novo marcado needs_approval (G3)
- [ ] Frases de clientes anonimizadas; citação literal só com usage_rights granted e G3

## 9. Handoff

| Campo | Valor |
|---|---|
| from_agent | conversion-copywriter |
| to_agent | copy-editor |
| envelope_id | env-{slug} |
| artifact_path | .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json |
| status | ready / needs_approval / needs_input |
| human_approval_required | true / false |
| gate | G3 / null |
| motivo | {resumo do que o copy-chief (QG-DRAFT) e o editor devem observar} |
