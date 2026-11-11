# Brief de Campanha: {campaign_id}

> Template do artefato humano do contrato `brief` (`contracts/brief.schema.json`). Renderizado como `brief.md` ao lado de `brief.json` em `.data/copy-squad/{business}/{campaign_id}/01-strategy/`. O JSON é a fonte de verdade; este documento é a visão legível usada no gate G1. Preencha cada campo com informação confirmada ou rotule como hipótese. Não escreva copy aqui.

## Identificação

| Campo | Valor |
|---|---|
| Brief (artifact_id) | `brf-{slug}` |
| Versão | {version} |
| Negócio (business) | {business} |
| Campanha (campaign_id) | {campaign_id} |
| Produzido por | brief-master |
| Data (produced_at) | {data-hora ISO 8601} |
| Status | draft / needs_input / needs_approval / ready |
| Nível de risco | low / medium / high |
| Confiança (0 a 1) | {valor} |
| Prazo (deadline) | {AAAA-MM-DD} |

## 1. Objetivo de negócio e KPI

- **Objetivo de negócio (`business_objective`):** {uma frase com o resultado de negócio esperado}
- **KPI primário (`primary_kpi`):** {métrica, unidade e janela de tempo; exatamente um}
- **KPIs secundários (`secondary_kpis`):**
  - {métrica de apoio 1}
  - {métrica de apoio 2}

## 2. Público (`audience`)

| Campo | Conteúdo |
|---|---|
| Segmento (`segment`) | {recorte do público; decisão humana registrada: quem decidiu e quando} |
| Dores (`pain_points`) | {lista; indicar fonte ou "hipótese"} |
| Desejos (`desires`) | {lista} |
| Objeções (`objections`) | {lista com categoria: price, trust, complexity, risk, time, compatibility, need, other} |
| Estágio de consciência (`awareness_stage`) | unaware / problem_aware / solution_aware / product_aware / most_aware |
| Evidência do estágio | {fonte ou "hipótese a validar"} |

## 3. Oferta (`offer`)

| Campo | Conteúdo |
|---|---|
| Promessa (`promise`) | {promessa da oferta, sem adjetivos de venda} |
| Mecanismo (`mechanism`) | {como a oferta entrega a promessa} |
| Provas (`proof`) | {lista de proof_id do offer-canvas; indicar verificado ou não} |
| Preço (`price`) | {valor oficial com fonte, ou vazio se não confirmado} |
| Garantia (`guarantee`) | {termos oficiais com fonte, ou vazio se não confirmado} |
| Restrições (`constraints`) | {limites legais, de produto e de promessa} |

## 4. Canal, formatos e tom

| Campo | Conteúdo |
|---|---|
| Canal (`channel`) | {canal principal} |
| Formatos (`formats`) | {ex.: página de captura, 3 e-mails, 5 variações de anúncio} |
| Tom de voz (`tone_of_voice`) | {descrição ou referência ao brand-voice-guide} |

## 5. Obrigatórios e proibições

**Deve incluir (`must_include`):**
- {item com fonte ou decisão humana}

**Deve evitar (`must_avoid`):**
- {restrição legal, de marca, de canal ou de produto}

## 6. Critérios de aceite (`acceptance_criteria`)

Cada critério deve ser verificável por um revisor que não participou da conversa.

1. {ex.: cada peça tem exatamente um CTA, específico}
2. {ex.: zero claims de preço, garantia ou resultado sem fonte e aprovação G3}
3. {ex.: tom conforme o brand-voice-guide da unidade}
4. {ex.: limites de caracteres do canal respeitados}
5. {ex.: toda prova citada referencia um proof_id}

## 7. Fatos confirmados e hipóteses

**Fatos confirmados (`confirmed_facts`)**

| # | Fato | Fonte |
|---|---|---|
| 1 | {afirmação} | {artifact_id, URL pública ou caminho repo-relativo} |

**Hipóteses a validar (`hypotheses_to_validate`)**

| # | Hipótese | Como validar | Responsável |
|---|---|---|---|
| 1 | {afirmação sem fonte} | {ação ou fonte necessária} | {papel} |

## 8. Perguntas em aberto (`open_questions`)

No máximo 5. Cada pergunta com o motivo.

1. {pergunta} — Motivo: {o que ela destrava}

## 9. Premissas e fontes (`meta.assumptions`, `meta.sources`)

- **Premissas:** {inferências rotuladas}
- **Fontes:** {título, localizador e tipo: primary, official, customer, internal ou secondary}

## 10. Pacote de decisão G1 (preencher no brief consolidado)

| Item | Resposta |
|---|---|
| Decisões humanas pendentes | {lista curta} |
| Contradições entre artefatos | {itens com as duas fontes} |
| Claims sensíveis que exigem G3 | {preço, garantia, resultado, autoridade, depoimento, comparativo, saúde, finanças} |
| Risco e política aplicada | {risk_level e motivo} |
| Decisão do approval-owner (registrada só pelo humano) | aprovado / aprovado com edições / reprovado |
| Comentários e condições | {texto} |
| Efeito da decisão | só `aprovado` libera a produção; `aprovado com edições` abre nova rodada (`g1-r{n+1}`) com novo hash; `reprovado` encerra a rodada |
| Prazo de resposta do pedido | 72 horas a partir da criação; sem resposta, o pedido segue pendente (silêncio nunca é aprovação) |
| Janela de execução da decisão | 72 horas a partir de `decided_at` |
| Pacote montado por | copy-publisher (`payload_sha256` calculado por `approval_tools.py hash`) |

## Rastreabilidade

- Brief anterior: {artifact_id da versão anterior ou "nenhum"}
- Artefatos integrados: {aud-..., ofr-..., rsp-...}
- Envelope de handoff: `handoffs.jsonl`, entrada `env-{slug}`
