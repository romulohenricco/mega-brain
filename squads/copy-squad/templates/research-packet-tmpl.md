# Research Packet — {campaign_id}

> Template do artefato humano do contrato `contracts/research-packet.schema.json`.
> Preencha cada campo com informação rastreável. O que não foi verificado fica como `unverified`.
> Este documento é a versão legível; a versão canônica é o JSON em
> `.data/copy-squad/{business}/{campaign_id}/02-research/research-packet.json`.

## 1. Identificação (meta)

| Campo | Valor |
|---|---|
| artifact_id | rsp-{slug} |
| artifact_type | research-packet |
| business | {business} |
| campaign_id | {campaign_id} |
| brief_id | brf-{slug} |
| produced_by | research-analyst |
| produced_at | {data-hora ISO-8601} |
| version | {n} |
| prompt_version | research-analyst@1.0.0 |
| model | {modelo} |
| status | {draft, ready, needs_input, needs_approval ou blocked} |
| risk_level | {low, medium ou high} |
| confidence | {0 a 1} |
| modo | {completo ou enxuto} |

**Premissas (assumptions):**
- {premissa 1, incluindo limitações de ferramenta, ex.: busca web indisponível}
- {premissa 2}

**Justificativa da confiança:** {proporção de fatos verified, cobertura de fontes primárias, peso das lacunas}

## 2. Perguntas de pesquisa

| # | Pergunta | Prioridade | Respondida? | Onde está a resposta |
|---|---|---|---|---|
| 1 | {pergunta derivada do brief} | alta, média ou baixa | sim, parcial ou não | {seção ou item} |
| 2 | | | | |

## 3. Contexto de mercado (market_context)

Cada item indica se é fato, inferência ou hipótese.

| # | Item | Tipo | Fonte (ref. da seção 8) |
|---|---|---|---|
| 1 | {afirmação sobre o mercado} | fato, inferência ou hipótese | {S1} |
| 2 | | | |

## 4. Concorrentes e ângulos de mercado (competitors)

| Nome | Posicionamento | Claims declarados por ele | source_url | Data de acesso | Diferencial |
|---|---|---|---|---|---|
| {concorrente ou substituto} | {resumo próprio} | {claim, sempre unverified para uso do negócio} | {URL} | {AAAA-MM-DD} | {diferencial} |

**Mapa de ângulos de mercado**

| Ângulo de mercado | Concorrentes que o usam | Saturação | Justificativa |
|---|---|---|---|
| {nome descritivo} | {lista} | alta, média ou baixa | {motivo} |

**Espaços livres (direções, sem headline):**
1. {oportunidade 1}
2. {oportunidade 2}
3. {oportunidade 3}

## 5. Linguagem do cliente (customer_language)

Somente temas e paráfrases anonimizadas, sem dado pessoal e sem citação literal. A frase literal de cliente vem exclusivamente do audience-voc (D17/E6).

| # | Tema ou paráfrase | Origem (tipo de fonte) | Contexto | Frequência |
|---|---|---|---|---|
| 1 | {tema ou paráfrase anonimizada} | {atendimento, vendas, comentários, entrevista} | {situação} | {alta, média ou baixa} |

## 6. Objeções (objections)

| # | Objeção | Categoria | Evidência | response_angle (direção, não texto final) |
|---|---|---|---|---|
| 1 | {objeção} | preço, confiança, complexidade, risco, tempo, compatibilidade, necessidade ou outra | {paráfrase ou dado, com fonte} | {direção da resposta} |

## 7. Ativos de prova (proof_assets)

| # | Prova | Tipo | Fonte | Status de verificação | Direito de uso |
|---|---|---|---|---|---|
| 1 | {depoimento, caso, dado, demonstração, garantia, certificação ou mídia} | | {referência} | verified ou unverified | concedido, pendente ou desconhecido |

## 8. Fatos e fontes (facts)

| # | Afirmação (statement) | Tipo | Status | Título da fonte | Localizador (URL ou caminho) | Tipo de fonte | Acesso em | Resumo da fonte |
|---|---|---|---|---|---|---|---|---|
| S1 | {fato} | fato, inferência ou hipótese | verified ou unverified | {título} | {URL ou caminho} | primary, official, customer, internal ou secondary | {AAAA-MM-DD} | {resumo} |

Regra: fato `verified` sem fonte completa não é aceito; rebaixe para `unverified`.

## 9. Lacunas (gaps)

| # | O que falta | Impacto na copy | Responsável sugerido | Como fechar | Prazo |
|---|---|---|---|---|---|
| 1 | {lacuna} | alto, médio ou baixo | {cliente, jurídico, dados, solicitante, approval-owner} | {entrevista, documento, teste} | {data} |

Pesquisas esgotadas em 3 rodadas: escreva `insufficient data`, o que foi buscado e o que seria necessário.

## 10. Riscos e itens para aprovação

- Claims de concorrentes que não podem ser usados em comparativo sem G3: {lista}
- Provas sem direito de uso confirmado: {lista}
- Itens que exigem revisão do compliance-checker: {lista}

## 11. Validação e handoff

| Campo | Valor |
|---|---|
| Gate de qualidade | QG-RESEARCH |
| Checklist aplicada | checklists/research-quality-checklist.md |
| Validador (executor do QG-RESEARCH) | compliance-checker |
| Score | {0 a 1} |
| Decisão | {APPROVE, REVIEW ou VETO} |
| Próximo agente | {hook-angle-creator ou brief-master} |
| Envelope | env-{slug}, registrado em handoffs.jsonl |
