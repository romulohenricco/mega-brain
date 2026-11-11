---
task: generate-angles-hooks
name: generate-angles-hooks
task_name: "Gerar ângulos e hooks"
version: "1.0.0"
squad: copy-squad
task_id: generate-angles-hooks
category: production
difficulty: advanced
responsavel: '@hook-angle-creator'
responsavel_type: Agent
responsible_executor: hook-angle-creator
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 30-60min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: research_packet
  tipo: contract:research-packet
  obrigatorio: true
- campo: offer_canvas
  tipo: contract:offer-canvas
  obrigatorio: false
- campo: audience_voc
  tipo: contract:audience-voc
  obrigatorio: false
- campo: mode
  tipo: enum (full | fast | variants)
  obrigatorio: true
Saida:
- campo: angles
  tipo: contract:angles
  persistido_em: .data/copy-squad/{business}/{campaign_id}/03-angles/angles.json
- campo: handoff_envelope
  tipo: contract:handoff-envelope
  persistido_em: .data/copy-squad/{business}/{campaign_id}/handoffs.jsonl
input: [brief, research-packet, offer-canvas, audience-voc]
output: [angles]
action_items:
  - "Confirmar modo (completo, fast lane ou variants) e carregar brief, packet, offer-canvas e audience-voc"
  - "Consultar a biblioteca por ângulos vencedores e learnings aprovados"
  - "Mapear dimensões e cotas para respeitar o limite de 35% por dimensão"
  - "Gerar ângulos com hook, promessa, mecanismo e prova necessária"
  - "Classificar risco, marcar needs_approval e preencher força prevista com justificativa"
  - "Derivar variações por estágio de consciência e formato quando exigido"
  - "Ranquear, recomendar conjunto para G2 e emitir envelope"
acceptance_criteria:
  - ">= 20 ângulos distintos no modo completo; >= 5 no fast lane"
  - "100% dos ângulos com promessa específica, mecanismo, proof_required, risk_level, predicted_strength e reason"
  - "0 ocorrências de escassez, urgência ou autoridade falsas; urgência só com legitimate_urgency.exists true"
  - "0 promessas de resultado sem evidência e sem needs_approval"
  - "Nenhuma dimensão acima de 35% dos ângulos"
pre_condition: "Brief aprovado e research packet disponível (modo completo); execution-plan indica o modo"
post_condition: "angles.json persistido, G2 solicitado quando risco alto ou campanha multi-ativo, envelope emitido"
checklist: checklists/angle-quality-checklist.md
quality_gate: QG-ANGLES
human_gate: G2
skill: copy-hook-generator
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation]
performance:
  error_handling: "needs_input se faltar brief ou packet no modo completo; ângulo sem prova possível é descartado ou marcado needs_approval; nunca inventar prova"
---

# Task: Gerar ângulos e hooks

## Objetivo

Produzir o banco de ângulos e hooks da campanha: no mínimo 20 ângulos distintos no modo completo (menos no fast lane), cada um com promessa específica, mecanismo, prova necessária, risco e força prevista justificada, sem escassez, urgência ou autoridade falsas. O banco é a entrada dos copywriters de formato e o objeto de decisão do G2.

## Quando usar / quando não usar

**Usar quando:**
- Brief aprovado e research packet disponível; a campanha vai produzir peças de conversão, conteúdo, vídeo ou CRM.
- Fast lane: variações de headline ou CTA para uso interno/teste (risco low), usando packet anterior. Post orgânico (medium) e anúncio pago (high) não entram na pista rápida.
- O modo variants: adaptar ângulos aprovados para outro estágio de consciência ou formato.
- O cro-analyst indicou fadiga de ângulo e pediu novas apostas.

**Não usar quando:**
- Falta o brief aprovado ou, no modo completo, o research packet.
- O pedido é escrever a página, o e-mail, o anúncio ou o roteiro completos.
- A decisão a tomar é de posicionamento, preço ou promessa do negócio (decisão humana).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | contracts/brief.schema.json | sim | brief-master |
| research_packet | contracts/research-packet.schema.json | sim (modo completo) | research-analyst |
| offer_canvas | contracts/offer-canvas.schema.json | não | offer-strategist |
| audience_voc | contracts/audience-voc.schema.json | não | audience-voc |
| knowledge_query_result | contracts/knowledge-query-result.schema.json | não | knowledge-curator |
| mode | full, fast ou variants | sim | execution-plan do copy-chief |

## Passos

1. **Confirmar modo e escopo.** Ler o execution-plan e definir o modo. Completo: mínimo 20 ângulos. Fast lane: mínimo 5 (`MIN_ANGLES_FAST_LANE`), apenas se o risco do plano for low. Variants: partir de ângulos aprovados e derivar variações. Confirmar {business} e {campaign_id}.
2. **Carregar insumos.** Ler brief, research packet, offer-canvas e audience-voc. Anotar provas verified, claims unverified, legitimate_urgency, estágio de consciência e restrições do canal (data/channel-specs.yaml).
3. **Consultar a biblioteca.** Executar retrieve-knowledge para ângulos vencedores, provas approved e learnings do mesmo público e canal. Reaproveitar com atribuição e sem copiar dado de outro negócio.
4. **Planejar as dimensões.** Distribuir cotas entre dor, desejo, mecanismo, prova, contraste, identidade, custo de não agir, história, curiosidade e objeção, de modo que nenhuma passe de 35%.
5. **Gerar os ângulos (divergência).** Para cada ângulo, escrever o hook (uma linha), a promessa específica, o mecanismo e a proof_required. Usar a linguagem do cliente do audience-voc e do packet.
6. **Aplicar a ética.** Revisar cada ângulo: remover escassez, urgência ou autoridade falsas; manter urgência apenas se legitimate_urgency.exists for true no offer-canvas, com motivo real; autoridade só com prova verified e direito de uso.
7. **Classificar risco.** Atribuir risk_level por ângulo. Preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou finanças elevam para high e marcam needs_approval true, conforme data/risk-policy.yaml.
8. **Eliminar duplicatas.** Aplicar o teste de distinção: dois ângulos só coexistem se diferirem em promessa ou mecanismo. Substituir os eliminados por ângulos de dimensões sub-representadas.
9. **Atribuir força prevista.** Preencher predicted_strength (0-100) e reason com critérios explícitos (especificidade, aderência ao público, prova disponível, diversidade, risco). Tratar como hipótese, nunca como resultado medido.
10. **Derivar variações.** Quando o brief exigir, criar variações por estágio de consciência (unaware, problem_aware, solution_aware, product_aware, most_aware) e por formato (anúncio, e-mail, vídeo, post, página, interface), respeitando limites de canal.
11. **Ranquear e recomendar.** Ordenar por força prevista ajustada ao risco e destacar uma shortlist de exatamente 5 ângulos (`ANGLES_SHORTLIST_SIZE`) para o G2, incluindo ao menos uma aposta divergente.
12. **Persistir e encaminhar.** Montar o JSON conforme contracts/angles.schema.json, salvar em 03-angles/angles.json (versão nova, sem sobrescrever), emitir o envelope. Endereçar o envelope sempre ao copy-chief (executor do QG-ANGLES), com gate G2 quando houver ângulo high ou campanha multi-ativo; o copy-chief aciona o copy-publisher (prepare-approval-package) e este leva o pedido ao approval-owner. Sem G2, o copy-chief libera ao copywriter do formato. Nunca enviar direto ao approval-owner (E3).

## Saída

- **Contrato:** contracts/angles.schema.json (meta, brief_id, research_id, angles[] com angle_id, angle, hook, promise, mechanism, proof_required, awareness_stage, risk_level, predicted_strength, reason, needs_approval).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json`.
- **Envelope:** handoff-envelope com from_agent hook-angle-creator, artifact_type angles, to_agent copy-chief (QG-ANGLES; gate G2 quando se aplica, caminho copy-chief → copy-publisher → approval-owner), human_approval_required true quando G2 se aplica.
- **Telemetria:** linha em `.data/copy-squad/_telemetry/agent-runs.jsonl`.

## Acceptance Criteria (Critérios de aceite)

| # | Critério | Medida |
|---|---|---|
| 1 | Quantidade | >= 20 distintos (completo); >= 5 (fast lane) |
| 2 | Completude por ângulo | 100% com promessa, mecanismo, proof_required, risk_level, predicted_strength e reason |
| 3 | Ética | 0 escassez, urgência ou autoridade falsas |
| 4 | Prova | 0 promessas de resultado sem evidência e sem needs_approval |
| 5 | Diversidade | <= 35% por dimensão; >= 6 dimensões em modo completo |
| 6 | Estágio de consciência | cobertura do estágio do brief; variações quando exigidas |
| 7 | Governança | G2 solicitado quando risco alto ou multi-ativo |
| 8 | Validade | JSON válido contra o schema |

## Quality gate e checklist

- **Gate:** QG-ANGLES (APPROVE >= 0.80, REVIEW 0.60-0.79, VETO < 0.60 ou veto_condition).
- **Checklist:** checklists/angle-quality-checklist.md, aplicada pelo copy-chief (executor do QG-ANGLES, D7); o hook-angle-creator faz só autochecagem (self_check_by). Ângulos high passam também pelo compliance-checker.
- **Veto conditions:** abaixo do mínimo de ângulos; escassez, urgência ou autoridade falsas; resultado sem evidência e sem needs_approval; ângulo sem promessa ou sem mecanismo.
- **Rework:** até 2 ciclos; depois, escalar ao copy-chief.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Brief ou packet ausente | needs_input; indicar brief-master ou research-analyst |
| Packet com confiança < 0.60 | Gerar com cautela, marcar ângulos dependentes de prova como needs_approval e devolver lacunas ao research-analyst |
| Impossível atingir 20 distintos | Declarar o motivo (oferta restrita), entregar o máximo distinto e pedir decisão do copy-chief; nunca preencher com duplicatas |
| Urgência pedida sem base real | Descartar, registrar em assumptions e substituir por custo de não agir verdadeiro |
| Pedido de escrever a peça completa | Recusar e encaminhar ao copywriter do formato |

## Handoff

- **copy-chief** (QG-ANGLES): recebe o envelope com o conjunto recomendado, riscos e provas necessárias; em risco alto ou campanha multi-ativo aciona o copy-publisher para o pedido de G2 ao approval-owner (E3). O hook-angle-creator nunca envia direto ao approval-owner.
- **conversion-copywriter**, **content-copywriter**, **video-social-scriptwriter**, **email-crm-copywriter**, **ux-writer**: após ângulos aprovados, conforme o formato do plano.
- **research-analyst**: lacunas de prova que impedem ângulos promissores.

## Exemplo

Entrada resumida (exemplo ilustrativo): SaaS de fluxo de caixa para pequenos negócios; modo completo; packet com confiança 0.66; urgência legítima inexistente.

Trecho da saída:

```json
{
  "brief_id": "brf-saas-fluxo-caixa",
  "research_id": "rsp-saas-fluxo-caixa",
  "angles": [
    {
      "angle_id": "ang-clareza-antes-de-controle",
      "angle": "Contraste: entender o caixa antes de automatizá-lo",
      "hook": "Antes de automatizar o caixa, entenda para onde ele vai.",
      "promise": "Visão clara das entradas e saídas antes de qualquer automação.",
      "mechanism": "Painel de entradas e saídas descrito na página oficial do produto.",
      "proof_required": ["Descrição oficial do painel (verified)"],
      "awareness_stage": "solution_aware",
      "risk_level": "low",
      "predicted_strength": 71,
      "reason": "Espaço livre no mercado segundo o packet, específico, apoiado em mecanismo verificado e sem promessa de resultado.",
      "needs_approval": false
    },
    {
      "angle_id": "ang-economia-de-tempo-numero",
      "angle": "Resultado: tempo economizado por semana",
      "hook": "Recupere horas por semana no financeiro.",
      "promise": "Economia de tempo no fechamento financeiro.",
      "mechanism": "Conciliação assistida.",
      "proof_required": ["Medição de tempo com metodologia e amostra", "Autorização de uso dos dados"],
      "awareness_stage": "product_aware",
      "risk_level": "high",
      "predicted_strength": 76,
      "reason": "Forte e específico, porém sem evidência no packet; depende de prova e G2/G3.",
      "needs_approval": true
    }
  ]
}
```

## Anti-padrões

- Gerar 20 ângulos que são a mesma promessa reescrita.
- Entregar hooks sem mecanismo ou sem prova possível.
- Usar contagem regressiva, vagas limitadas ou prêmio inexistentes.
- Citar números, depoimentos ou autoridades não presentes no packet.
- Apresentar a força prevista como se fosse resultado medido.
- Pular o G2 em campanha multi-ativo ou ângulo de risco alto.
- Escrever a peça completa dentro do banco de ângulos.
- Ignorar o canal e o estágio de consciência na redação do hook.
