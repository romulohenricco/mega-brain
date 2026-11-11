# Offer Canvas — {campaign_name}

> Renderização humana do contrato `contracts/offer-canvas.schema.json`.
> Persistência do JSON: `.data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json`
> Preencha SOMENTE com fatos fornecidos ou documentados. O que faltar fica em "Pendências para aprovação (G3 de oferta)". Exemplos devem ser marcados como "exemplo ilustrativo".

## 0. Metadados

| Campo | Valor |
|---|---|
| artifact_id | `ofr-{slug}` |
| business | `{business}` |
| campaign_id | `{campaign_id}` |
| versão | {n} |
| produzido por | offer-strategist |
| status | draft / needs_input / needs_approval / ready |
| risk_level | low / medium / high |
| confiança (0 a 1) | {valor} |
| data | {YYYY-MM-DD} |

**Premissas (assumptions):**
- {hipótese 1}
- {hipótese 2}

**Fontes (sources):**
| Título | Localizador (URL pública ou caminho repo-relativo/.data) | Tipo (primary/official/customer/internal/secondary) | Acessado em |
|---|---|---|---|
| {título} | {locator} | {tipo} | {YYYY-MM-DD} |

## 1. Promessa

**Promessa (uma frase, proporcional à melhor prova verificada):**
> {promise}

**Força da prova que a sustenta:** afirmação / demonstração / dado / caso verificado
**Versão ambiciosa (se existir, só com aprovação):** {texto ou "n/a"}

## 2. Mecanismo

**Como a promessa se realiza (1 a 2 frases):**
> {mechanism}

**Lacunas do mecanismo:** {o que ainda não está documentado}

## 3. Pilha de provas

| proof_id | Tipo | Resumo fiel | Fonte | Verificada? | Direito de uso | Claim que sustenta |
|---|---|---|---|---|---|---|
| prv-{slug} | testimonial / case / data / demo / guarantee / certification / media | {summary} | {source} | sim / não | granted / pending / unknown | {claim} |

**Regra:** só provas `verified: sim` com `usage_rights: granted` podem aparecer na copy.
**Lacunas de prova e plano de coleta:**
| Claim sem prova | Ação de coleta | Responsável | Prazo |
|---|---|---|---|
| {claim} | {ação} | {responsável} | {data} |

## 4. Condições comerciais (somente dados fornecidos)

| Item | Valor | Fonte do dado | Status |
|---|---|---|---|
| Preço (valor e moeda) | {amount} {currency} | {fonte} | fornecido / pendente |
| Condições de pagamento | {payment_terms} | {fonte} | fornecido / pendente |
| Garantia (tipo e termos literais) | {type}; {terms} | {fonte} | fornecido / pendente |
| Bônus | {lista} | {fonte} | fornecido / pendente / n/a |
| Risco reverso | {risk_reversal} | {fonte} | fornecido / pendente / n/a |

## 5. Urgência legítima

| Campo | Valor |
|---|---|
| Existe urgência real? (`exists`) | sim / não |
| Motivo real (`reason`) | {motivo verificável ou "n/a"} |
| Prazo (`deadline`) | {YYYY-MM-DD ou "n/a"} |

> `exists: sim` exige motivo real **e** prazo (o contrato rejeita só um deles). Sem os dois, mantenha "não". É proibido criar escassez ou urgência artificial.

## 6. Posicionamento

| Campo | Conteúdo |
|---|---|
| Categoria em que competimos | {category} |
| Diferenciais verificáveis | 1) {diferencial} 2) {diferencial} |
| Referências competitivas (com fonte datada) | {nome, posicionamento, fonte} |

**Messaging house** (`positioning.messaging_house`)
| Elemento | Conteúdo |
|---|---|
| Mensagem central (`central_message`) | {texto} |
| Pilar 1 / provas (`pillars[].pillar` / `proof_ids`) | {pilar} / {proof_ids} |
| Pilar 2 / provas | {pilar} / {proof_ids} |
| Pilar 3 / provas | {pilar} / {proof_ids} |

> No máximo 3 pilares; cada `proof_id` precisa existir na pilha de provas.

## 7. Objeções e respostas

| Objeção (linguagem do cliente) | Categoria | Frequência | Evidência | Resposta | proof_ids | Mecanismo |
|---|---|---|---|---|---|---|
| {objection} | price / trust / complexity / risk / time / compatibility / need / other | high / medium / low | {evidência} | {response} | {ids} | {mecanismo} |

**Respostas marcadas como hipótese:** {lista}

## 8. Ângulos de venda sugeridos

| # | Ângulo | Ligado a (objeção/prova) | Risco | Observação |
|---|---|---|---|---|
| 1 | {sale_angle} | {referência} | low / medium / high | {nota} |

## 9. Pendências para aprovação (G3 de oferta)

> No JSON, cada pendência é uma string `<claim_type>: <pergunta>`. O G3 de oferta é decidido antes da produção; só "aprovado" libera, "aprovado com edições" abre nova rodada.

| # | Claim | Tipo (price / guarantee / result / authority / testimonial / comparison / health / financial / other) | Pergunta objetiva ao approval-owner | Decisão (registrada só pelo humano) |
|---|---|---|---|---|
| 1 | {claim} | {claim_type} | {pergunta} | aprovado / aprovado com edições / reprovado |

## 10. Perguntas abertas (máx. 5)

1. {pergunta}

## 11. Revisão e aprovação

| Etapa | Responsável | Resultado | Data |
|---|---|---|---|
| Autoverificação (`offer-quality-checklist`) | offer-strategist | score {x} | {data} |
| Validação do brief (QG-BRIEF) | copy-chief | APPROVE / REVIEW / VETO | {data} |
| Checagem de claims | compliance-checker | {resultado} | {data} |
| Aprovação G3 de oferta (pacote do copy-publisher) | approval-owner | {decisão} | {data} |
