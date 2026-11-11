---
task: approve-gate
name: approve-gate
task_name: "Decidir gate de aprovação humana"
version: "1.0.0"
squad: copy-squad
task_id: approve-gate
category: governance
difficulty: advanced
responsavel: '@approval-owner'
responsavel_type: Human
responsible_executor: approval-owner
execution_type: Human
atomic_layer: Molecule
elicit: true
estimated_time: 15-45min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: approval_request
  tipo: contract:approval-request
  obrigatorio: true
- campo: revisoes
  tipo: contract:edit-report, brand-review, compliance-review
  obrigatorio: true
Saida:
- campo: approval_decision
  tipo: contract:approval-decision
  persistido_em: .data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json (ou 06-approval/_campaign/{gate}-r{n}/ em G1, G2 e G3 de oferta, com asset_id = campaign_id), na mesma pasta da rodada do pedido; {gate} em minúsculas (g1 a g4, sampling)
input: [approval-request, edit-report, brand-review, compliance-review]
output: [approval-decision]
action_items:
  - "Abrir o pedido e o payload completo"
  - "Conferir sha (saída de approval_tools.py hash), prazo de resposta e revisões exigidas pelo risco"
  - "Aplicar o checklist do gate (G1 a G4 e amostragem)"
  - "Decidir: approved, approved_with_edits ou rejected"
  - "Registrar approval-decision pelo humano (CLI com ! ou confirmação no chat), com motivo, edições e condições"
acceptance_criteria:
  - "approval-decision válido em contracts/approval-decision.schema.json"
  - "payload_sha256 da decisão idêntico ao do approval-request"
  - "bound_to da decisão = {gate, operation, destination, channel} copiado do pedido (o decide faz a cópia)"
  - "human_attested true, recorded_via (human-cli ou human-chat-confirmed) e reviewer presente em human_gates.approvers; meta.produced_by approval-owner e meta.artifact_type approval-decision, sem meta.model nem meta.prompt_version; meta.status: approved -> approved, rejected -> rejected, approved_with_edits -> needs_approval"
  - "decided_at e expires_at preenchidos, com expires_at = decided_at + 72h (janela de execução)"
  - "comentário com motivo registrado em toda decisão"
  - "claims sensíveis aprovados somente com fonte verificada"
pre_condition: "approval-request produzido pelo copy-publisher (prepare-approval-package), pendente, com payload_sha256 conferido"
post_condition: "approval-decision persistido e enviado ao copy-publisher (aprovado) ou ao produtor via copy-chief (reprovado ou approved_with_edits)"
checklist: checklists/approval-gate-checklist.md
quality_gate: null
human_gate: [G1, G2, G3, G4]
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-performance-loop, wf-content-repurposing, wf-fast-variation]
performance:
  error_handling: "sha divergente impede a decisão; devolver ao copy-publisher para reemitir; pedido além de 72h sem resposta continua pendente (o copy-chief reenvia ou escala); nunca aprovar por exceção"
---

# Task: Decidir gate de aprovação humana

## Objetivo

Registrar a decisão humana em um dos gates G1 (brief), G2 (ângulo), G3 (claims) e G4 (final). A task é executada pelo `approval-owner`, pessoa responsável; os agentes apenas preparam o material, e o pedido de G1 a G4 é sempre produzido pelo `copy-publisher` (`prepare-approval-package`, D5). O `approval-decision` é escrito somente pelo humano (D4), por um de dois meios registrados em `recorded_via`: `human-cli` (o humano roda `approval_tools.py decide ...`, no Claude Code com o prefixo `!`) ou `human-chat-confirmed` (a sessão principal, fora do papel de copy-chief, transcreve uma mensagem explícita do humano, citada literalmente em `comments`, que é obrigatório e não vazio neste meio). Subagents do squad nunca escrevem a decisão. O resultado trava o payload aprovado por `payload_sha256` e define o que o `copy-publisher` pode executar, e só `approved` autoriza execução (D2). Em baixo risco (`wf-fast-variation`), a revisão por amostragem (`SAMPLING_RATE_LOW = 0.20`, sorteio determinístico por `approval_tools.py sample`) usa a mesma task, com pedido `gate: SAMPLING` e operação `internal_use`. G5 não passa por esta task: não há pedido, e a correção segue `correct-agent-failure`.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Brief consolidado precisa de G1 (risco medium ou high) | Para corrigir falha de agente (use `correct-agent-failure`, G5) |
| Ângulos prontos para G2 (risco high ou campanha multi-ativo) | Para editar a copy em lugar do agente |
| Claims sensíveis precisam de G3 | Quando o pedido expirou ou o sha não confere |
| Ativo final precisa de G4 antes de publicar, enviar ou veicular | Para tomar decisão de publicação por fora do fluxo |
| Amostragem em baixo risco (uso interno, `SAMPLING`) | Quando falta revisão obrigatória do nível de risco |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| approval_request | `approval-request` | sim | `copy-publisher` (único produtor do `approval-request` em G1, G2, G3, G4 e amostragem, via `prepare-approval-package`; para G1 e G2 o pacote reúne o brief consolidado ou os ângulos, entregues pelo `copy-chief`) |
| payload completo | no próprio pedido | sim | `payload` |
| edit-report | `edit-report` | G4 em medium e high | `copy-editor` |
| brand-review | `brand-review` | G4 em medium e high | `brand-voice-guardian` |
| compliance-review | `compliance-review` | G3; G4 em medium (modo leve) e high (completo) | `compliance-checker` |
| política de risco | `data/risk-policy.yaml` | sim | squad |

## Passos

1. **Triagem**: identifique o gate (G1 a G4 ou amostragem), o `asset_id`, o `risk_level` e o `expires_at` do pedido (prazo de resposta); ordene a fila por vencimento.
2. **Conferir integridade**: confirme que `payload_sha256` do pedido é a saída de `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>` sobre o payload exibido (nunca de cabeça); se divergir, interrompa e devolva ao `copy-publisher` (CS-AO-002). Se o prazo de resposta passou, o pedido continua pendente e pode ser decidido; o silêncio nunca é aprovação e quem reenvia ou escala é o `copy-chief` (CS-AO-003).
3. **Conferir o rito de risco**: low (uso interno) não exige revisões; medium exige `edit-report`, `brand-review` aprovados e `compliance-review` em modo leve; high exige `compliance-review` completo com `approved: true`.
4. **Ler o payload completo** e aplicar o `checklists/approval-gate-checklist.md` correspondente ao gate.
5. **Verificar claims**: para cada claim de price, guarantee, result, authority, testimonial, comparison, health ou financial, abra a fonte, confirme `status: verified` e o direito de uso; sem isso, não aprove.
6. **Avaliar riscos de persuasão**: rejeite escassez, urgência, autoridade ou prova falsas; urgência só com `legitimate_urgency.exists` verdadeiro e motivo real.
7. **Decidir** entre `approved`, `approved_with_edits` (D2: significa "aprovo com estas edições"; liste `edits` como objetos com `section`, `before`, `after` e `reason`, todos obrigatórios; **não autoriza execução**, o `copy-publisher` aplica as edições e abre a rodada seguinte com novo `payload_sha256`, e você confirma com `approved`) e `rejected` (encerra a rodada; explique o que falta e para qual fase volta).
8. **Registrar o `approval-decision` (D4)**: o registro é feito pelo humano. Opção 1, `human-cli`: `!python squads/copy-squad/scripts/approval_tools.py decide --request <approval-request.json> --decision approved|approved_with_edits|rejected --reviewer <id> --confirm <12 primeiros hex do hash> --comments "..."`. Opção 2, `human-chat-confirmed`: o humano escreve a decisão no chat e a sessão principal, fora do papel de copy-chief, a transcreve citando a mensagem literalmente em `comments` (o `verify` recusa `comments` vazio neste meio). Campos: `approval_request_id`, `decision`, `reviewer` (presente em `human_gates.approvers`), `human_attested: true`, `recorded_via`, `decided_at` (não pode estar no futuro), `payload_sha256` (cópia exata do pedido), `bound_to` (`{gate, operation, destination, channel}` copiado do pedido pelo `decide`), `comments`, `edits`, `conditions`, `expires_at` = `decided_at` + 72h (D3; tolerância de 60 s no `verify`). Sem `meta.model` nem `meta.prompt_version`; `meta.status` segue o mapeamento approved -> `approved`, rejected -> `rejected`, approved_with_edits -> `needs_approval`.
9. **Disparar desdobramentos**: `approved` -> envelope ao `copy-publisher`; `approved_with_edits` -> envelope ao `copy-publisher` para aplicar as edições e abrir a rodada seguinte; `rejected` -> envelope ao `copy-chief`, que devolve ao produtor; houve correção humana -> acione `correct-agent-failure` (G5, sem pedido).

## Saída

- **Contrato:** `contracts/approval-decision.schema.json` (`artifact_id` prefixo `apd-`).
- **Persistência:** na pasta da rodada do pedido, `.data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json` (ex.: `06-approval/cvc-camp-x-lp-001/g4-r1/`); G1, G2 e G3 de oferta em `06-approval/_campaign/{gate}-r{n}/` (ex.: `_campaign/g1-r1/`), com `asset_id = campaign_id`; amostragem em `06-approval/{asset_id}/sampling-r{n}/`. `{gate}` é sempre `lower(approval-request.gate)`. O preflight lê a decisão da maior rodada do gate.
- **Envelope de handoff:** `from_agent: approval-owner`, `to_agent: copy-publisher` (aprovado) ou `copy-chief` (reprovado), `artifact_type: approval-decision`, `status: ready` ou `blocked`, `human_approval_required: false`, `gate` igual ao decidido, `reason` com o motivo.

## Acceptance Criteria (Critérios de aceite)

- Decisão registrada de forma explícita; silêncio nunca vale como aprovação.
- `payload_sha256` da decisão igual ao do pedido e ao hash recalculado por `approval_tools.py hash`.
- `human_attested: true`, `recorded_via` válido e `reviewer` na lista de aprovadores; `bound_to` igual ao pedido.
- Todo claim sensível aprovado tem `source` e `usage_rights` quando for depoimento ou dado de cliente.
- `expires_at` = `decided_at` mais 72h (janela de execução).
- Em `approved_with_edits`, lista de `edits` (objetos com section, before, after e reason) completa, `meta.status: needs_approval` e instrução de que a execução só ocorre após nova rodada `approved`.
- Em `rejected`, motivo e destino do retorno descritos.

## Quality gate e checklist

- **Gate:** esta task não reivindica o `QG-PUBLISH-PREFLIGHT`: o preflight pertence ao `copy-publisher` (produtor) com contra-assinatura do `copy-chief` (executor) e roda depois da decisão, em `publish-approved-asset`.
- **Checklist:** `checklists/approval-gate-checklist.md` (aplicado pelo `approval-owner`).
- **Limite de ciclos:** no máximo 2 rodadas de `approved_with_edits` por ativo (`REWORK_MAX_CYCLES`); depois, escalar ao `copy-chief` e reabrir o brief ou o ângulo.
- **Veto:** risco high sem compliance aprovado, sha divergente ou claim sem fonte.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| sha divergente | Não decidir; `copy-publisher` regenera o pacote |
| Pedido além de 72h sem decisão | Continua pendente; `copy-chief` reenvia ou escala. Não há veto nem aprovação por silêncio |
| Compliance ausente em risco high | Devolver ao `copy-chief` para rodar `check-compliance` e `fact-check-claims` |
| Aprovador indisponível dentro do SLA | `copy-chief` alerta; escalar a um substituto designado; nunca auto-aprovar |
| Dúvida sobre direito de uso | `rejected` com a lista do que provar; claim volta como `needs_approval` |
| Humano altera o texto durante a revisão | `approved_with_edits` (nunca autoriza execução); `copy-publisher` abre a rodada seguinte com novo sha e nova decisão `approved` |
| Tentativa de agente gravar `approval-decision` | Recusar: só o humano grava (D4); registrar a ocorrência e acionar o `copy-chief` |

## Handoff

| Decisão | Próximo | Contrato | Gate |
|---|---|---|---|
| `approved` | `copy-publisher` (`publish-approved-asset` em G4; em G1 a G3 a fase seguinte do workflow) | `approval-decision` | G1 a G4 |
| `approved_with_edits` | `copy-publisher` (aplica as edições e executa `prepare-approval-package` na rodada seguinte) | `approval-decision` | G1 a G4 |
| `rejected` | `copy-chief` encaminha ao agente produtor | `approval-decision` | G1 a G4 |
| Correção de agente | `correct-agent-failure` e depois `knowledge-curator` (`register-learning`), sem pedido | `learning-record` | G5 |

## Exemplo

Entrada resumida (exemplo ilustrativo): G4 da landing page; compliance sinalizou "garantia de 30 dias" como `unverified`. O `reviewer` do exemplo é um papel ilustrativo; em uso real é um id presente em `human_gates.approvers`, e o `payload_sha256` é o do pedido.

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "apd-camp-mentoria-lp-001",
    "artifact_type": "approval-decision",
    "campaign_id": "camp-mentoria-gestao",
    "business": "{business}",
    "produced_by": "approval-owner",
    "produced_at": "2026-11-10T15:00:00Z",
    "version": 1,
    "status": "rejected"
  },
  "human_attested": true,
  "recorded_via": "human-cli",
  "bound_to": {"gate": "G4", "operation": "publish", "destination": "pagina-de-vendas-mentoria", "channel": "landing_page"},
  "approval_request_id": "apr-camp-mentoria-lp-001",
  "decision": "rejected",
  "reviewer": "responsável-negócio",
  "decided_at": "2026-11-10T15:00:00Z",
  "payload_sha256": "2222222222222222222222222222222222222222222222222222222222222222",
  "comments": "Garantia de 30 dias sem política aprovada. Definir os termos e reenviar para G3.",
  "conditions": [],
  "expires_at": "2026-11-13T15:00:00Z"
}
```

## Anti-padrões

- Aprovar pelo resumo sem abrir o payload.
- Aprovar claim "porque o cliente confirmou" sem registro.
- Reaproveitar aprovação de payload anterior.
- Editar o texto e não abrir a rodada seguinte.
- Executar ou pedir execução com base em `approved_with_edits`.
- Deixar um agente gravar o `approval-decision` em nome do humano.
- Aprovar por silêncio ou tratar o fim do prazo de resposta como aprovação.
- Deixar o motivo da decisão em branco.
- Usar a decisão G4 para resolver pendência estratégica que deveria ter sido tratada em G1.
