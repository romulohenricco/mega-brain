# Guia de Voz da Marca — {business}

> Renderização humana do contrato `contracts/brand-voice-guide.schema.json`.
> Persistência do JSON: `.data/copy-squad/{business}/_brand/brand-voice-guide.json`
> Baseie cada item em materiais reais da marca. O que for inferência deve ser marcado como hipótese. Exemplos criados para ilustrar devem ser marcados como "exemplo ilustrativo".

## 0. Metadados

| Campo | Valor |
|---|---|
| artifact_id | `bvg-{slug}` |
| business | `{business}` |
| versão | {n} |
| produzido por | brand-voice-guardian |
| status | draft / needs_approval / approved |
| confiança (0 a 1) | {valor} (menos de 3 materiais reais = até 0,6) |
| aprovação G1 | pendente / aprovado por {revisor} em {YYYY-MM-DD} |
| data | {YYYY-MM-DD} |

**Materiais analisados (fontes):**
| # | Material | Canal | Localizador | Data | Aprovado pelo negócio? |
|---|---|---|---|---|---|
| 1 | {título} | {canal} | {locator} | {YYYY-MM-DD} | sim / não |

**Premissas (assumptions):**
- {hipótese sobre a voz, a validar}

## 1. Personalidade

| Traço | Em uma frase, como aparece no texto | Evidência (trecho real) | Evidência ou hipótese? |
|---|---|---|---|
| {traço 1} | {descrição} | "{trecho}" | evidência / hipótese |
| {traço 2} | {descrição} | "{trecho}" | evidência / hipótese |
| {traço 3} | {descrição} | "{trecho}" | evidência / hipótese |

## 2. Tom por contexto

| Contexto (canal / formato) | Tom esperado | Energia | Comprimento típico de frase | Observações |
|---|---|---|---|---|
| anúncio | {tom} | baixa / média / alta | {curta / média} | {nota} |
| página de vendas | {tom} | | | |
| e-mail de nutrição | {tom} | | | |
| e-mail de venda | {tom} | | | |
| post / social | {tom} | | | |
| roteiro de vídeo | {tom} | | | |
| microcopy de produto (UX) | {tom} | | | |

## 3. Vocabulário

| Preferido (usar) | Motivo |
|---|---|
| {termo} | {motivo} |

| Proibido (nunca usar) | Motivo | Alternativa |
|---|---|---|
| {termo} | {motivo} | {alternativa} |

> Inclua superlativos sem prova, promessas absolutas e jargões sem definição entre os proibidos quando fizer sentido para o negócio.

## 4. Glossário

| Termo | Definição aprovada para uso | Contexto |
|---|---|---|
| {termo} | {definition} | {contexto} |

## 5. Formalidade e regras de estilo

| Item | Regra |
|---|---|
| Formalidade (`formality`) | formal / neutral / informal |
| Tratamento ao leitor | {você / senhor(a) / nome} |
| Pessoa verbal | {primeira pessoa do plural / singular / impessoal} |
| Emojis | {permitidos em ... / proibidos} |
| Caixa alta e pontuação enfática | {regra} |
| Números, moedas e datas | {formato} |
| Frases e parágrafos | {limites} |
| Outras regras (`style_rules`) | {lista} |

## 6. Exemplos do e don't

| # | DO (exemplo na voz) | Por quê | Origem |
|---|---|---|---|
| 1 | "{texto}" | {motivo} | real / exemplo ilustrativo |
| 2 | "{texto}" | | |
| 3 | "{texto}" | | |

| # | DON'T (fora da voz) | Por quê | Reescrita na voz |
|---|---|---|---|
| 1 | "{texto}" | {motivo} | "{texto}" |
| 2 | "{texto}" | | |
| 3 | "{texto}" | | |

## 7. Lacunas e evolução do guia

| Lacuna / contexto sem tom definido | Proposta | Decisão |
|---|---|---|
| {contexto} | {nova linha de tone_by_context} | aprovada / rejeitada |

**Correções humanas incorporadas (G5):**
| Data | Peça | Correção | Regra ou exemplo gerado |
|---|---|---|---|
| {YYYY-MM-DD} | {asset_id} | {descrição} | {regra} |

## 8. Aprovação

| Etapa | Responsável | Resultado | Data |
|---|---|---|---|
| Autoverificação (`brand-voice-review-checklist`, Fase 1) | brand-voice-guardian | score {x} | {data} |
| Conferência de coerência (versões seguintes; sem QG-BRAND) | copy-chief | ok / ajustar | {data} |
| Aprovação G1 (primeira versão; só `approved` libera, `approved_with_edits` abre nova rodada) | approval-owner | aprovado / aprovado com edições / reprovado | {data} |

> O guia não passa por QG-BRAND (ADR-001 D7): o `brand-voice-guardian` produziria e validaria o mesmo artefato. O QG-BRAND revisa as peças contra este guia.

**Regra de uso:** peça só avança para o compliance se a revisão der `brand_alignment_score >= 80` e nenhuma issue critical. Fatos, preços e claims nunca são alterados por motivo de tom.
