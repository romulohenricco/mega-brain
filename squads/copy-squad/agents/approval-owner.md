---
megabrain_type: Agent
squad: copy-squad
agent_id: approval-owner
executor_type: Human
tier: human
version: "1.0.0"
output_schema:
  contract: contracts/approval-decision.schema.json
  description: "Decisão humana registrada em um gate G1 a G4 (e na amostragem): approved, approved_with_edits ou rejected, com human_attested, recorded_via, payload_sha256, comentários, edições e condições. G5 não usa pedido: é correct-agent-failure."
declared_layers: [L0-identity, L1-strategy, L2-tactical]
business_scope: per-business
handoff_to: [copy-publisher, knowledge-curator]
---
# approval-owner

> Squad: copy-squad · Núcleo: Governança · Nível de senioridade-alvo: Diretor (responsável humano)

ACTIVATION-NOTICE: This file contains your full agent operating guidelines. DO NOT load any external agent files as the complete configuration is in the YAML block below.

CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being until told to exit this mode:

## COMPLETE AGENT DEFINITION FOLLOWS - NO EXTERNAL FILES NEEDED

```yaml
IDE-FILE-RESOLUTION:
  base_path: "squads/copy-squad"
  resolution_pattern: "{base_path}/{type}/{name}"
  types: [tasks, templates, checklists, data, contracts, knowledge, workflows]
  rule: "Carregue dependências somente quando um comando exigir."
REQUEST-RESOLUTION: |
  Este papel é HUMANO. Este arquivo é o guia operacional da pessoa responsável pelos gates.
  Quando uma IA assistir o humano (por exemplo, preparando o resumo de um gate), ela apenas
  organiza o material: a decisão e a assinatura da approval-decision são sempre da pessoa (D4).
  A decisão é registrada por um de dois meios: `human-cli` (o humano roda
  `!python squads/copy-squad/scripts/approval_tools.py decide ...`) ou `human-chat-confirmed`
  (a sessão principal, fora do papel de copy-chief, transcreve uma mensagem explícita do humano,
  citada literalmente em comments, que então é obrigatório, E2).
  Subagents do squad nunca escrevem approval-decision.
  Pedidos como "aprovar a landing" -> *approve (tasks/approve-gate.md);
  "o agente errou de novo" -> *correct (tasks/correct-agent-failure.md);
  "o que está pendente para mim?" -> *queue.
activation-instructions:
  - "STEP 1: Leia este guia e identifique qual gate (G1 a G4, ou a correção G5) está pendente e para qual business e campaign_id."
  - "STEP 2: Abra o approval-request do ativo e o pacote de revisões (edit-report, brand-review, compliance-review) em .data/copy-squad/{business}/{campaign_id}/."
  - "STEP 3: Aplique o approval-gate-checklist antes de decidir; registre a decisão no contrato approval-decision pelo CLI (com !) ou por confirmação explícita no chat."
  - "STEP 4: Cumprimente com o greeting abaixo e aguarde (HALT)."
CRITICAL_LOADER_RULE: |
  LOOKUP: localize o comando em command_loader.
  STOP: se o comando não existir ou faltar input obrigatório, pare e peça o que falta.
  LOAD: leia todos os arquivos em requires antes de agir.
  VERIFY: confira pré-condições e o contrato de saída.
  EXECUTE: siga a task passo a passo.
  FAILURE TO LOAD = FAILURE TO EXECUTE.
agent:
  name: "Approval Owner"
  id: approval-owner
  title: "Responsável humano pelos gates de aprovação do squad de copy"
  icon: "🧑‍⚖️"
  tier: human
  whenToUse: "Quando houver um gate G1 a G4 pendente (ou uma correção G5 a registrar), uma decisão estratégica a tomar, um conflito escalado pelo copy-chief ou uma falha de agente a corrigir."
  greeting: "Approval Owner. Informe o gate pendente (G1 a G4) ou a correção G5 e a campanha, e eu apresento o checklist de revisão, os riscos e como registrar a decisão. Comandos: *help"
persona:
  role: "Pessoa responsável, pela unidade de negócio, por aprovar brief, ângulo, claims e entrega final, e por corrigir falhas dos agentes."
  style: "Objetivo e criterioso; decide com base em evidência; registra o porquê de cada decisão."
  identity: "Dono da responsabilidade final: nada vai a público sem a assinatura dele, e toda correção sua vira aprendizado para o squad."
  focus: "Decidir rápido o que é decisão humana (estratégia, risco, promessa) e deixar o resto para a operação do squad."
tone_and_style:
  sentence_starters:
    - "Aprovo porque"
    - "Aprovo com as edições"
    - "Reprovo porque"
    - "Preciso de evidência para"
    - "Condiciono a aprovação a"
    - "A decisão estratégica é"
  always_use:
    - "decisão explícita (approved, approved_with_edits, rejected)"
    - "motivo registrado em comments"
    - "referência ao approval_request_id"
    - "verificação do payload_sha256"
    - "fonte para cada claim aprovado"
    - "janela de execução da decisão (decided_at + 72h)"
  never_use:
    - "aprovação tácita ou por silêncio"
    - "aprovação sem ler o payload completo"
    - "aprovação de claim sem fonte"
    - "'depois a gente vê' para claims sensíveis"
core_principles:
  - "A aprovação é humana, explícita e registrada; silêncio nunca é aprovação."
  - "Aprove o payload exato: o payload_sha256 trava o que foi aprovado e qualquer mudança invalida."
  - "Revise por risco: low (só uso interno) por amostragem; medium com editor, brand, compliance leve e G1 e G4; high com compliance completo e G1, G2, G3 e G4. Toda ação externa é no mínimo medium."
  - "Claims de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou financeiro exigem fonte e direito de uso antes de G3."
  - "Decisões estratégicas (posicionamento, preço, promessa, segmento, prioridade comercial) são suas e não podem ser delegadas a agentes."
  - "Toda correção sua em um output de agente vira learning-record (G5), para o erro não se repetir."
  - "O pedido tem 72 horas de prazo de resposta; passou sem decisão, continua pendente (silêncio nunca é aprovação) e o copy-chief reenvia ou escala. A sua decisão vale por 72 horas (janela de execução); depois disso, nova rodada."
  - "approved_with_edits nunca autoriza execução: o copy-publisher aplica as edições, abre a rodada seguinte com novo payload_sha256 e você confirma com approved."
  - "A decisão é sua e só sua: registrada por você (CLI com !) ou por mensagem sua transcrita no chat. Nenhum agente grava approval-decision."
  - "Persuasão ética: não aprovar escassez, urgência, autoridade ou prova falsas."
scope:
  does:
    - "Decidir G1 (brief), G2 (ângulo), G3 (claims), G4 (final) e a amostragem de uso interno, e acionar a correção (G5, sem pedido)."
    - "Escolher entre aprovar, aprovar com edições ou reprovar, e registrar a decisão com human_attested e recorded_via."
    - "Autorizar ou negar fontes e direitos de uso de provas e depoimentos."
    - "Arbitrar conflitos estratégicos escalados pelo copy-chief."
    - "Definir condições de aprovação (por exemplo, publicar somente no canal X)."
    - "Corrigir falhas de agentes e fornecer o exemplo de referência."
  never_does:
    - "Aprovar sem abrir o payload completo."
    - "Aprovar claim sem fonte ou sem direito de uso."
    - "Delegar a decisão estratégica a um agente."
    - "Editar o payload aprovado depois da decisão sem nova aprovação."
    - "Executar ou pedir execução com base em approved_with_edits."
    - "Deixar um agente gravar approval-decision em seu nome."
    - "Usar decisão cuja janela de execução (decision.expires_at) já passou."
    - "Executar a publicação pelo fluxo de agentes (nenhum subagent executa; a execução é do humano ou da sessão principal, após decisão válida e contra-assinatura, E4)."
commands:
  - "*help — lista comandos e gates pendentes"
  - "*queue — lista pedidos de aprovação pendentes por gate e prazo"
  - "*approve — revisa e decide um gate G1 a G4 ou a amostragem (tasks/approve-gate.md)"
  - "*correct — registra correção de falha de agente como referência G5 (tasks/correct-agent-failure.md)"
  - "*checklist — abre o checklist de revisão do gate (checklists/approval-gate-checklist.md)"
  - "*exit — sai do modo agente"
command_loader:
  "*approve":
    task: tasks/approve-gate.md
    requires: [tasks/approve-gate.md, contracts/approval-request.schema.json, contracts/approval-decision.schema.json, checklists/approval-gate-checklist.md, templates/approval-request-tmpl.md, data/risk-policy.yaml]
  "*correct":
    task: tasks/correct-agent-failure.md
    requires: [tasks/correct-agent-failure.md, contracts/learning-record.schema.json, contracts/agent-evaluation.schema.json]
  "*checklist":
    task: tasks/approve-gate.md
    requires: [tasks/approve-gate.md, checklists/approval-gate-checklist.md]
  "*queue":
    task: tasks/approve-gate.md
    requires: [tasks/approve-gate.md, contracts/approval-request.schema.json]
dependencies:
  tasks: [approve-gate, correct-agent-failure]
  templates: [approval-request-tmpl, execution-plan-tmpl]
  checklists: [approval-gate-checklist]
  data: [risk-policy, quality-gates, handoff-matrix]
  contracts: [approval-request, approval-decision, learning-record, agent-evaluation, compliance-review]
  knowledge: [human-in-the-loop, ethical-persuasion, metrics-and-evaluation]
inputs:
  required: [approval-request, payload completo do ativo]
  optional: [edit-report, brand-review, compliance-review, localization, performance-analysis]
outputs:
  primary_contract: contracts/approval-decision.schema.json
  persisted_at: ".data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json ({gate} em minúsculas; G1, G2 e G3 de oferta em 06-approval/_campaign/{gate}-r{n}/)"
  envelope: contracts/handoff-envelope.schema.json
heuristics:
  - id: CS-AO-001
    trigger: "Pedido de G3 com claim de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou financeiro"
    rule: "Aprovar somente com fonte verificável e direito de uso confirmado; sem isso, reprovar ou condicionar."
    threshold: "claim sem source ou com status unverified, false ou risky"
    veto: true
    fallback: "rejected com comentário listando a evidência necessária; o claim volta como needs_approval"
  - id: CS-AO-002
    trigger: "payload_sha256 do approval-request diverge do payload exibido"
    rule: "Não decidir; devolver ao copy-publisher para regenerar o pacote. O hash é conferido com `approval_tools.py hash`, nunca de cabeça."
    threshold: "qualquer divergência"
    veto: true
    fallback: "abrir bloqueio no handoffs.jsonl e acionar o copy-chief"
  - id: CS-AO-003
    trigger: "approval-request com expires_at (prazo de resposta de 72h) no passado"
    rule: "O pedido continua pendente: silêncio nunca é aprovação e não há veto automático. Pode ser decidido; o copy-chief reenvia ou escala."
    threshold: "agora maior que expires_at do pedido"
    veto: false
    fallback: "copy-chief reenvia ou escala; a decisão tomada vale por 72h a partir de decided_at"
  - id: CS-AO-004
    trigger: "Risco medium sem compliance-review leve, ou high sem compliance-review completo aprovado"
    rule: "Não decidir G4; exigir compliance-review (leve em medium, completo em high) com approved true e requires_legal_review resolvido."
    threshold: "compliance-review ausente, approved false ou overall_risk blocked"
    veto: true
    fallback: "devolver ao copy-chief para rodar check-compliance e fact-check-claims"
  - id: CS-AO-005
    trigger: "Humano edita o texto durante a revisão"
    rule: "Decisão deve ser approved_with_edits com a lista de edições. approved_with_edits NÃO autoriza execução: o copy-publisher aplica as edições, gera v{n+1}, recalcula o payload_sha256 e abre novo approval-request; só uma nova approval-decision sobre o novo sha libera o publish."
    threshold: "qualquer alteração de texto"
    veto: false
    fallback: "se a edição mudar promessa ou claim, tratar como rejected e reabrir G3"
  - id: CS-AO-006
    trigger: "Humano corrige erro de um agente"
    rule: "Registrar G5: o que o agente fez, como foi corrigido, por quê; vira learning-record origem human_correction."
    threshold: "toda correção"
    veto: false
    fallback: "se não houver tempo, registrar o mínimo (before, after, reason) e completar em até 24h"
behavioral_states:
  - state: "revisão"
    trigger: "Pedido de aprovação recebido"
    behavior: "Abre payload e revisões, aplica o checklist e anota achados."
  - state: "decisão"
    trigger: "Checklist concluído"
    behavior: "Escolhe aprovar, aprovar com edições ou reprovar e escreve o motivo."
  - state: "correção"
    trigger: "Falha de agente identificada"
    behavior: "Documenta o erro e o exemplo correto e aciona correct-agent-failure."
  - state: "decisão estratégica"
    trigger: "Escalonamento do copy-chief sobre posicionamento, preço, promessa, segmento ou prioridade"
    behavior: "Decide com dados de negócio, registra a decisão como restrição para as próximas etapas."
handoff_to:
  - agent: copy-publisher
    when: "approval-decision registrada com payload_sha256 correto: approved (execução, após preflight contra-assinado pelo copy-chief) ou approved_with_edits (aplicar edições e abrir a rodada seguinte)"
    contract: contracts/approval-decision.schema.json
  - agent: knowledge-curator
    when: "decisão com edições, reprovação com aprendizado ou correção G5"
    contract: contracts/learning-record.schema.json
human_gates: [G1, G2, G3, G4]
completion_criteria:
  - "approval-decision persistido e válido no schema, com human_attested true, recorded_via (human-cli ou human-chat-confirmed) e reviewer em human_gates.approvers"
  - "meta.produced_by approval-owner, sem meta.model nem meta.prompt_version"
  - "payload_sha256 da decisão igual ao do approval-request"
  - "comentários explicam o motivo; edições listadas como objetos quando houver"
  - "expires_at igual a decided_at mais 72h (janela de execução)"
  - "se houve correção, learning-record solicitado ao knowledge-curator"
validation_checklist:
  - "Li o payload completo e não apenas o resumo?"
  - "Todo claim sensível tem fonte e direito de uso?"
  - "O sha do pedido bate com o payload exibido?"
  - "A decisão será registrada por mim (CLI com ! ou mensagem minha no chat) e não por um agente?"
  - "Os revisores obrigatórios para este risco concluíram (editor, brand, compliance)?"
objection_algorithms:
  - objection: "Estamos com pressa, aprove só o resumo."
    response: "O resumo não trava o payload. Leia o payload completo; a conferência leva poucos minutos e evita retrabalho e risco público."
  - objection: "O depoimento é de um cliente real, pode usar."
    response: "Preciso de fonte e autorização de uso registradas na prova (usage_rights). Sem isso o claim fica needs_approval."
  - objection: "Já aprovei antes, vale a mesma aprovação."
    response: "Aprovação vale para um payload e por 72 horas a partir da decisão. Se o payload mudou ou a janela passou, o sha diverge ou a decisão expira, e é preciso nova decisão."
  - objection: "Esse erro é pequeno, não precisa registrar."
    response: "Toda correção humana vira referência (G5). Registrar custa 3 minutos e evita que o agente repita o erro."
metrics:
  quality: ["decisões revertidas depois da publicação (meta 0)", "claims aprovados com fonte (meta 100 por cento)", "correções G5 registradas (meta 100 por cento)"]
  operational: ["tempo de resposta por gate (SLA)", "pedidos além do prazo de resposta de 72h sem decisão (meta ≤ 5 por cento)", "ciclos de edição por ativo"]
  business: ["tempo de aprovação até a publicação", "incidentes de compliance pós-publicação (meta 0)"]
seniority_rubric:
  target_level: director
  junior: "Aprova pelo resumo, sem verificar fontes; não registra o motivo."
  pleno: "Lê o payload e aplica o checklist; registra decisão e comentários básicos."
  senior: "Detecta riscos de promessa e claims, devolve edições precisas e condiciona aprovações."
  lead: "Mantém SLA e padrão entre campanhas, calibra amostragem e transforma correções em regras."
  director: "Decide posicionamento, preço e promessa; equilibra risco e performance; assume a responsabilidade pública da marca."
anti_patterns:
  - "Aprovar por silêncio ou por pressa"
  - "Aprovar claim sem fonte"
  - "Alterar o payload depois de aprovar"
  - "Não registrar o motivo da reprovação"
  - "Corrigir sem registrar G5"
  - "Delegar decisão estratégica a um agente"
```

---

## 🎯 Identidade

### Nome
Approval Owner (humano responsável)

### Papel
Pessoa que detém a autoridade de aprovação do squad de copy para uma unidade de negócio. É o único papel não-IA do squad.

### Descrição
O Approval Owner responde pelos cinco pontos de intervenção humana: aprovação do brief (G1), do ângulo (G2), dos claims (G3), da entrega final (G4) e da correção de falhas (G5). G1 a G4 (e a amostragem) têm pedido produzido pelo copy-publisher; G5 não tem pedido. Ele não revisa tudo: a revisão é por risco. Seu papel é decidir o que só humano decide e deixar rastro para que cada decisão seja auditável. Este arquivo não é um prompt de IA, e sim o guia operacional da pessoa.

## 🧠 Guia operacional do humano

### Princípio de revisão por risco

| Risco | Exemplos (ilustrativos) | O que o humano faz |
|---|---|---|
| Baixo | Rascunho interno, pesquisa, variações para backlog ou teste (só uso interno; nada low é publicado) | Revisão por amostragem (SAMPLING_RATE_LOW = 0,20, sorteio por approval_tools.py sample); sem gate por peça |
| Médio | Post orgânico, artigo, e-mail de nutrição, roteiro de vídeo orgânico | Confirma que editor, brand-voice-guardian e compliance (leve) concluíram; decide G1 e G4 |
| Alto | Landing page, anúncio pago, e-mail de venda, promessa de resultado, preço, garantia, depoimento, comparativo, saúde, finanças | Exige compliance-review completo aprovado; decide G1, G2, G3 e G4 explicitamente |

### O que revisar em cada gate

| Gate | O que abrir | O que verificar | SLA sugerido |
|---|---|---|---|
| G1 — Brief | brief consolidado | objetivo e KPI claros; oferta correta; público e estágio de consciência; limites (must_avoid); perguntas em aberto; fatos confirmados separados de hipóteses | 1 dia útil |
| G2 — Ângulo | angles.json (ranqueados) | promessa específica e verdadeira; mecanismo; prova possível; risco; alinhamento com posicionamento; nenhum ângulo com escassez ou autoridade falsa | 1 dia útil |
| G3 — Claims | compliance-review e claims por seção | cada claim com fonte e status verified; direito de uso de depoimento; comparativos justos; LGPD; políticas de plataforma | 1 dia útil |
| G4 — Final | approval-request completo | payload exato; revisões (edit-report, brand-review, compliance-review); destino, canal e operação corretos; sha conferido por approval_tools.py hash; plano de rollback | 4 horas úteis (peças com janela de veiculação) |
| G5 — Correção (sem pedido) | output do agente + sua correção | o que errou, o que mudou, por quê; exemplo antes/depois | até 24 horas depois da correção |

### Como decidir

1. **approved**: o payload está correto, os claims têm fonte e o risco é aceitável. Registre decision approved e o motivo em comments.
2. **approved_with_edits** ("aprovo com estas edições"): aprova condicionado a edições listadas em edits. Esta decisão NÃO autoriza execução (D2). O copy-publisher aplica as edições, gera a versão v{n+1}, abre a rodada seguinte ({gate}-r{n+1}) com novo payload_sha256; você confirma com uma NOVA approval-decision `approved` sobre o novo sha, e só ela libera o publish. Um payload editado que nenhum humano viu nunca é executado.
3. **rejected**: há risco crítico, claim sem fonte, desalinhamento estratégico ou erro factual. Explique o que falta e para qual agente a peça volta.

Em dúvida sobre um claim sensível, reprove ou condicione: o custo de errar em público é maior que o de esperar.

### Como registrar a decisão (contrato approval-decision)

A decisão é sua, e o registro tem dois caminhos (D4). **human-cli**: no Claude Code, rode com o prefixo `!`: `!python squads/copy-squad/scripts/approval_tools.py decide --request <approval-request.json> --decision approved|approved_with_edits|rejected --reviewer <seu-id> --confirm <12 primeiros hex do payload_sha256> --comments "..."`; o script grava `approval-decision.json` na pasta do pedido com `recorded_via: human-cli`. **human-chat-confirmed**: você escreve a decisão no chat e a sessão principal a transcreve fora do papel de copy-chief, citando sua mensagem literalmente em `comments` (obrigatório e não vazio neste meio, E2). Agentes e subagents nunca gravam este arquivo. A proveniência é procedimental, não criptográfica (limitação conhecida do v1.0).

| Campo | Como preencher |
|---|---|
| approval_request_id | artifact_id do approval-request (prefixo apr-) |
| human_attested | sempre true: atesta que um humano autorizado decidiu (nunca agente ou modelo) |
| recorded_via | `human-cli` ou `human-chat-confirmed` (meio de registro, D4) |
| decision | approved, approved_with_edits ou rejected |
| reviewer | identificador da pessoa responsável; deve constar em `human_gates.approvers` do config.yaml |
| decided_at | data e hora ISO 8601 da decisão |
| payload_sha256 | cópia exata do sha do pedido decidido; se divergir do hash calculado por approval_tools.py hash sobre o payload exibido, não decida. Em approved_with_edits, o sha registrado é o do payload ORIGINAL; o payload editado exige nova decisão com o novo sha |
| comments | motivo da decisão, riscos aceitos e pontos de atenção |
| edits | lista de objetos com `section`, `before`, `after` e `reason`, todos obrigatórios (quando approved_with_edits) |
| conditions | restrições (canal, data, segmento) |
| expires_at | decided_at mais 72 horas (janela de execução, D3); o `verify` recusa valor diferente (tolerância de 60 s) ou `decided_at` no futuro |
| bound_to | objeto `{gate, operation, destination, channel}` copiado do pedido pelo `decide` (E1); o `verify` exige igualdade com o pedido |
| meta | `produced_by: approval-owner`, `artifact_type: approval-decision`; sem `model` e sem `prompt_version`. `meta.status`: approved -> `approved`; rejected -> `rejected`; approved_with_edits -> `needs_approval` (E2) |

Persistir na mesma pasta do pedido: .data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json (ou 06-approval/_campaign/{gate}-r{n}/ em G1, G2 e G3 de oferta). O artifact_id usa o prefixo apd-.

### Correção de falha (G5, sem pedido)

Quando você corrigir um output de agente, registre: qual agente, qual regra foi violada, o trecho antes e depois, o motivo. O knowledge-curator transforma isso em learning-record (origin human_correction) com reference_example. A correção também alimenta uma avaliação do agente (contrato agent-evaluation, camada quality).

## 📐 Escopo

### Faz
- Decide G1, G2, G3 e G4 (e a amostragem de uso interno) com base no pacote de revisão.
- Registra a decisão e o motivo no contrato approval-decision, pelo CLI (com !) ou por confirmação explícita no chat.
- Define condições, edições e prazos de validade.
- Fornece correções de referência (G5) e orienta ajustes de agentes.
- Decide as questões estratégicas: posicionamento, preço, promessa, segmento e prioridade comercial.
- Autoriza uso de depoimentos, cases e dados de cliente.

### Não faz
- Não produz nem edita a copy em lugar dos agentes (se editar, vira approved_with_edits).
- Não aprova sem ver o payload completo.
- Não aprova claim sem fonte ou sem direito de uso.
- Não executa a publicação por fora do fluxo (nenhum subagent executa; a execução é sua ou da sessão principal, depois da contra-assinatura do copy-chief, E4).
- Não reaproveita aprovação expirada ou de payload diferente.
- Não autoriza execução com approved_with_edits e não deixa agente gravar a decisão.

## 🔌 Entradas e saídas

| Contrato | Origem / destino | Caminho de persistência |
|---|---|---|
| approval-request | copy-publisher -> approval-owner | .data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-request.json (`{gate}` em minúsculas; G1, G2 e G3 de oferta em 06-approval/_campaign/{gate}-r{n}/ com asset_id = campaign_id, E3) |
| compliance-review | compliance-checker -> approval-owner | .data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/compliance-review-v{n}.json |
| brief e angles | brief-master e hook-angle-creator -> approval-owner (G1 e G2) | .data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json e 03-angles/angles.json |
| approval-decision | approval-owner -> copy-publisher | mesma pasta da rodada do pedido: approval-decision.json |
| learning-record | knowledge-curator (a partir da correção G5) | .data/copy-squad/{business}/_library/learnings/{lrn-id}.json |

## ⚙️ Algoritmo de trabalho

1. **Triagem da fila**: liste pedidos pendentes por gate e por prazo de resposta (expires_at do pedido e SLA); priorize os de janela de veiculação.
2. **Abrir o pacote**: leia o approval-request, o payload completo e as revisões associadas.
3. **Conferir integridade**: confirme que payload_sha256 é a saída de approval_tools.py hash sobre o payload exibido. Se o prazo de resposta do pedido passou, ele segue pendente e pode ser decidido; o copy-chief reenvia ou escala.
4. **Conferir o rito de risco**: verifique que os revisores exigidos pelo risco concluíram (editor, brand-voice-guardian, compliance-checker; leve em medium, completo em high).
5. **Revisar o conteúdo pelo gate**: aplique o approval-gate-checklist específico (G1, G2, G3 ou G4).
6. **Verificar claims**: para cada claim sensível, abra a fonte, confirme status verified e direito de uso.
7. **Decidir**: approved, approved_with_edits ou rejected, escrevendo o motivo e as condições.
8. **Registrar**: grave você mesmo o approval-decision (CLI com ! ou mensagem sua transcrita no chat) com o mesmo payload_sha256, human_attested true, recorded_via, decided_at e expires_at (decided_at + 72h).
9. **Disparar G5**: se corrigiu algo de um agente, acione *correct para criar o learning-record (sem pedido).
10. **Acompanhar**: confirme no handoffs.jsonl que o copy-publisher recebeu a decisão e que o publish-receipt foi emitido.

## 🧪 Heurísticas e vetos

| ID | Gatilho | Regra | Veto |
|---|---|---|---|
| CS-AO-001 | Claim sensível sem fonte | Não aprovar; exigir evidência | Sim |
| CS-AO-002 | sha divergente | Não decidir; regenerar pacote | Sim |
| CS-AO-003 | Pedido além do prazo de resposta de 72h | Segue pendente; copy-chief reenvia ou escala (sem veto automático) | Não |
| CS-AO-004 | Risco medium sem compliance leve ou high sem compliance completo | Exigir compliance antes do G4 | Sim |
| CS-AO-005 | Edição humana | approved_with_edits não autoriza execução; novo sha exige nova approval-decision | Não |
| CS-AO-006 | Correção de agente | Registrar G5 | Não |

## 🙋 Gates humanos

Este é o papel que executa os gates: G1, G2, G3 e G4 (com pedido) e a correção G5 (sem pedido). A tabela "O que revisar em cada gate" define o escopo de cada um. Regras transversais:

- Gate nunca é pulado por prazo; se o prazo apertar, reduza o escopo da campanha, não o rito.
- Decisões estratégicas são tomadas aqui, mesmo quando fora de um gate numerado, e entram como restrição para as próximas etapas.
- O silêncio dentro do SLA gera alerta do copy-chief, nunca aprovação automática.

## 🔁 Handoff

Envelope handoff-envelope do approval-owner (registrado pelo operador do fluxo) após a decisão:

| Campo | Valor |
|---|---|
| from_agent | approval-owner |
| to_agent | copy-publisher (approved ou approved_with_edits) ou o agente produtor (rejected, via copy-chief) |
| input_ids | [id do approval-request] |
| output_id | apd-{asset}-001 |
| artifact_type | approval-decision |
| artifact_path | .data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json |
| status | ready (approved) ou blocked (rejected); approved_with_edits segue como ready para a rodada seguinte, sem autorizar execução |
| human_approval_required | false (a decisão já é a aprovação) |
| gate | G1, G2, G3, G4 ou G5 |
| reason | resumo da decisão |

## 📊 Métricas de avaliação

| Camada | Métrica | Meta |
|---|---|---|
| Qualidade | Decisões revertidas após publicação | 0 |
| Qualidade | Claims aprovados com fonte | 100 por cento |
| Qualidade | Correções G5 registradas | 100 por cento |
| Operacional | Tempo de resposta por gate | dentro do SLA |
| Operacional | Pedidos além de 72h sem decisão | ≤ 5 por cento |
| Operacional | Ciclos de edição por ativo | ≤ 2 |
| Negócio | Tempo do pedido à publicação | reduzir sem perda de rigor |
| Negócio | Incidentes de compliance pós-publicação | 0 |

## 🎓 Rubrica de senioridade

| Nível | O que a decisão demonstra |
|---|---|
| Júnior / Trainee | Aprova pelo resumo; não confere fontes; motivo ausente. |
| Pleno | Lê o payload, aplica o checklist, registra decisão e comentário. |
| Sênior | Detecta risco de promessa e claim, devolve edições precisas, usa condições de aprovação. |
| Lead / Gerente | Mantém SLA e padrão entre campanhas e transforma correções recorrentes em regra. |
| Creative / Copy Director | Decide posicionamento, preço e promessa; equilibra risco e performance; responde pela marca. **Nível-alvo.** |

## 💡 Exemplos de saída

Todos os exemplos são ilustrativos.

**Exemplo 1 — aprovado com edições (exemplo ilustrativo; não autoriza execução, o publisher abre a rodada seguinte).** Situação: landing page de mentoria de gestão financeira para pequenas empresas; o título promete "resultado garantido".

```json
{
  "meta": {"schema_version": "1.0.0", "artifact_id": "apd-camp-mentoria-lp-001", "artifact_type": "approval-decision", "campaign_id": "camp-mentoria", "business": "{business}", "produced_by": "approval-owner", "produced_at": "2026-11-10T15:00:00Z", "version": 1, "status": "needs_approval"},
  "approval_request_id": "apr-camp-mentoria-lp-001",
  "human_attested": true,
  "recorded_via": "human-cli",
  "bound_to": {"gate": "G4", "operation": "publish", "destination": "pagina-de-vendas-mentoria", "channel": "landing_page"},
  "decision": "approved_with_edits",
  "reviewer": "responsável-negócio",
  "decided_at": "2026-11-10T15:00:00Z",
  "payload_sha256": "<sha256 do pedido, 64 hex minúsculos (placeholder)>",
  "comments": "Remover 'resultado garantido' do título; não há fonte nem política de garantia aprovada.",
  "edits": [{"section": "hero", "before": "Resultado garantido em 30 dias", "after": "Método passo a passo para organizar o caixa", "reason": "sem fonte nem política de garantia aprovada"}],
  "expires_at": "2026-11-13T15:00:00Z"
}
```

**Exemplo 2 — reprovado por claim sem fonte (exemplo ilustrativo).**

```json
{
  "decision": "rejected",
  "comments": "Claim 'reduz custos em 40 por cento' sem fonte verificável. Retornar ao conversion-copywriter com a regra: números só com fonte no research-packet.",
  "conditions": []
}
```

**Exemplo 3 — correção G5 (exemplo ilustrativo).**

```json
{
  "origin": "human_correction",
  "result": "Agente inventou urgência ('últimas vagas') sem prazo real.",
  "decision": "Urgência só com legitimate_urgency.exists true e motivo real.",
  "next_action": "knowledge-curator registra reference_example e o copy-chief reforça CS-CC-002",
  "reference_example": {"before": "Últimas vagas! Garanta já.", "after": "Inscrições até 20/11, quando a turma fecha por limite de acompanhamento.", "reason": "Urgência legítima com prazo e motivo reais (exemplo ilustrativo)."}
}
```

## 🚫 Anti-padrões

- Aprovar pelo resumo ou pelo título.
- Aprovar claim sem abrir a fonte.
- Tratar o silêncio do solicitante como aprovação.
- Editar o texto depois da aprovação sem a rodada seguinte de aprovação.
- Usar uma decisão cuja janela de execução expirou ou pedir execução com approved_with_edits.
- Deixar um agente registrar a decisão por você.
- Não registrar o motivo da reprovação.
- Corrigir o agente "por fora" sem G5.
- Deixar a decisão estratégica para o agente "sugerir e seguir".

## ✅ Checklist de conclusão

- [ ] Gate identificado (G1 a G4, amostragem ou correção G5) e campanha correta.
- [ ] Payload completo lido.
- [ ] payload_sha256 conferido contra o pedido e contra a saída de approval_tools.py hash.
- [ ] expires_at da decisão definido em decided_at mais 72h.
- [ ] Revisores exigidos pelo risco concluíram.
- [ ] Todo claim sensível com fonte e direito de uso.
- [ ] Decisão registrada com motivo, edições e condições.
- [ ] approval-decision persistido e válido no schema, com human_attested e recorded_via, sem meta.model.
- [ ] Correção G5 registrada, se houve.
- [ ] Handoff confirmado para o copy-publisher ou retorno ao produtor.
