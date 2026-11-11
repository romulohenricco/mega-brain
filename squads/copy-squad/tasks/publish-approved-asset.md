---
task: publish-approved-asset
name: publish-approved-asset
task_name: "Publicar ativo aprovado"
version: "1.0.0"
squad: copy-squad
task_id: publish-approved-asset
category: operations
difficulty: advanced
responsavel: '@copy-publisher'
responsavel_type: Hybrid
responsible_executor: copy-publisher
execution_type: Hybrid
atomic_layer: Molecule
elicit: false
estimated_time: 15-30min
model: haiku
status: pending
domain: tactical
Entrada:
- campo: approval_request
  tipo: contract:approval-request
  obrigatorio: true
- campo: approval_decision
  tipo: contract:approval-decision
  obrigatorio: true
Saida:
- campo: publish_receipt
  tipo: contract:publish-receipt
  persistido_em: .data/copy-squad/{business}/{campaign_id}/07-published/{asset_id}/publish-receipt.json
input: [approval-request, approval-decision]
output: [publish-receipt]
action_items:
  - "Rodar approval_tools.py verify --for-execution --request/--decision/--payload da pasta da rodada do G4, com --payload apontando para o payload.json da rodada (gate G4, operation externa, risco acima de low, bound_to igual ao pedido, hash do conteúdo, decisão approved, validade, proveniência humana), sem --now nem --config"
  - "Preflight pós-decisão em dois passos (D8, E4): copy-publisher registra o resultado do verify, copy-chief reexecuta o verify sem flags e contra-assina"
  - "Emitir o pacote de execução para o humano ou a sessão principal (nenhum subagent executa)"
  - "Registrar o publish-receipt com verification completa, contra-assinatura e rollback_plan após a confirmação do executor"
  - "Notificar cro-analyst e knowledge-curator"
acceptance_criteria:
  - "execução somente com decision approved (approved_with_edits nunca autoriza, D2) e human_attested true"
  - "hash do payload.json da rodada (verify --payload, método D1/E1) igual ao payload_sha256 do pedido e da decisão (sha_match true, com a saída do script anexada)"
  - "bound_to da decisão igual a gate, operation, destination e channel do pedido (bound_match true); request.gate G4, operation externa e risk_level diferente de low"
  - "now menor que decision.expires_at (not_expired true); o expires_at do pedido não é reavaliado (D3)"
  - "destination, channel e operation do pacote de execução iguais ao aprovado; divergência é VETO"
  - "preflight contra-assinado pelo copy-chief (QG-PUBLISH-PREFLIGHT, que reexecutou verify --for-execution sem flags) antes de qualquer execução externa"
  - "execução feita pelo humano ou pela sessão principal, nunca por subagent (PUBLISH_EXECUTORS = [human, main_session])"
  - "publish-receipt válido, com verification {sha_match, approval_valid, not_expired, bound_match, verify_ok, counter_signed_by, counter_signed_at}, rollback_plan e outcome"
  - "idempotency_key executada no máximo uma vez"
pre_condition: "approval-decision existente para o approval-request, dentro de 72h contadas a partir de decided_at"
post_condition: "pacote de execução entregue e confirmado pelo executor (published, scheduled ou handed_off) ou bloqueado com motivo; recibo persistido"
checklist: checklists/publish-preflight-checklist.md
quality_gate: QG-PUBLISH-PREFLIGHT
human_gate: null
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "qualquer falha no preflight bloqueia a execução; subagent nunca executa ação externa, só emite o pacote de execução com checklist; nunca git push"
---

# Task: Publicar ativo aprovado

## Objetivo

Liberar, e somente depois da verificação, a entrega do ativo exatamente como foi aprovado. A task é Hybrid: o `copy-publisher` verifica, emite o pacote de execução e registra o recibo; **nenhum subagent executa a ação externa** (E4): quem executa é o humano ou a sessão principal (`PUBLISH_EXECUTORS = [human, main_session]`), depois da contra-assinatura do `copy-chief`, a partir do checklist do pacote (outcome `handed_off` até a confirmação). Compra, configuração e veiculação de mídia também são execução externa (G4 mais humano ou sessão principal); a copy do anúncio é escopo do squad. O resultado é um `publish-receipt` com prova de que o hash, a aprovação, a validade, o `bound_to` e a contra-assinatura foram conferidos, e com plano de rollback. O squad nunca publica sem `approval-decision` válido, e nunca executa `git push` (exclusivo do @devops, fora do escopo).

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Existe `approval-decision` `approved` válida (dentro do `expires_at` da decisão) sobre o hash atual | Sem decisão, com `rejected`, `approved_with_edits` ou expirada |
| Preflight de publicação a executar | Para montar o pacote (use `prepare-approval-package`) |
| Entrega do pacote de execução ao humano ou à sessão principal | Para alterar o texto antes de entregar |
| Reexecução segura após falha (nova tentativa idempotente) | Para publicar de repositório de código (git push é do @devops) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| approval_request | `approval-request` | sim | `06-approval/{asset_id}/g4-r{n}/approval-request.json` (rodada do G4, pasta em minúsculas) |
| approval_decision | `approval-decision` | sim | `06-approval/{asset_id}/g4-r{n}/approval-decision.json` (mesma rodada) |
| payload.json da rodada | `approval-request.payload` em JSON canônico (E8) | sim | `06-approval/{asset_id}/g4-r{n}/payload.json` (mesma rodada; passado ao verify por `--payload`; é o que se executa, nunca o draft `04-drafts/.../v{n}.json`) |
| executor | humano ou sessão principal | sim | quem executa depois da contra-assinatura; subagent não executa e não recebe credencial |
| janela de agendamento | data e hora | não | pedido ou `conditions` da decisão |

## Passos

1. **Carregar pedido e decisão**: leia `approval-request.json` e `approval-decision.json` da maior rodada do G4 do `asset_id`; confira `approval_request_id` e `payload_sha256` declarados.
2. **Verificar a decisão (D2, D4)**: aceite somente `approved` (a decisão da maior rodada do G4, para respeitar revogação) com `human_attested: true`, `recorded_via` válido e `reviewer` em `human_gates.approvers`. `approved_with_edits` NÃO autoriza execução: o `copy-publisher` aplica as edições, abre a rodada seguinte com novo `payload_sha256` e só uma decisão `approved` sobre o novo hash libera a publicação. Qualquer outra decisão ou ausência resulta em VETO (CS-PB-001).
3. **Verificar validade (D3)**: `now` deve ser menor que `decision.expires_at` (`decided_at` + 72h, a janela de execução). O `expires_at` do pedido é só o prazo de resposta do humano e não é reavaliado aqui; decisão expirada = VETO e nova rodada (CS-PB-003).
4. **Rodar o verify e recalcular o hash (D1, D21, E1)**: execute `python squads/copy-squad/scripts/approval_tools.py verify --for-execution --request <approval-request.json> --decision <approval-decision.json> --payload <06-approval/{asset_id}/g4-r{n}/payload.json>` (todos os três arquivos da mesma pasta de rodada; E8). O script usa os aprovadores do negócio do pedido (`request.meta.business`), exige `decision.meta.business` e `decision.meta.campaign_id` iguais aos do pedido e, em `--for-execution`, `destination`, `channel` e as quatro chaves de `bound_to` como strings não vazias. O script exige `request.gate == G4`, `operation` em {publish, send, run_ads, update_page} e `risk_level` diferente de `low`; confere `bound_to` da decisão igual a gate, operation, destination e channel do pedido; recalcula o hash do `payload.json` que será executado (JSON canônico, `ensure_ascii=False`, sem NFC e sem destino) contra o `payload_sha256` do pedido e da decisão; e checa `decision == approved`, `decided_at <= now`, `expires_at == decided_at + 72h`, `now < decision.expires_at`, `human_attested`, `recorded_via`, `comments` não vazio em `human-chat-confirmed` e `reviewer`. **Nunca passe `--now` nem `--config`**: só valem em teste (`COPY_SQUAD_TEST_MODE=1`); fora dele o script recusa com exit 2, e um resultado obtido com esses flags é inválido. Anexe a saída JSON (`{ok, checks[]}`) ao preflight; um `sha_match: true` sem a saída do script é inválido, e o hash nunca é calculado de cabeça. Depois compare `destination`, `channel` e `operation` do pacote de execução com os do pedido, um a um; divergência = VETO (CS-PB-002).
5. **Preflight pós-decisão em dois passos (D8, E4)**: o `QG-PUBLISH-PREFLIGHT` acontece depois da decisão do G4 e não é pré-requisito dele. (a) O `copy-publisher` executa `checklists/publish-preflight-checklist.md` (revisões, destino igual ao aprovado, `conditions` atendidas, `idempotency_key` inédita, rollback definido), registra o resultado do `verify` e emite o resultado em `handoff-envelope` (`artifact_type: preflight-result`, `to_agent: copy-chief`); (b) o `copy-chief` **reexecuta** o mesmo `verify --for-execution --request/--decision/--payload` da rodada, sem flags de teste, e contra-assina como executor de `QG-PUBLISH-PREFLIGHT`, aprovando ou vetando em envelope de volta (`copy-chief` -> `copy-publisher`, liberado); a contra-assinatura vira `counter_signed_by` e `counter_signed_at` do recibo. Sem ela, nenhuma ação externa é executada (o produtor não valida o próprio artefato, AP05).
6. **Idempotência**: se a `idempotency_key` já tiver `publish-receipt`, devolva o recibo existente sem executar (CS-PB-006).
7. **Emitir o pacote de execução (E4)**: nenhum subagent executa a operação externa. Com a contra-assinatura, gere o pacote para o humano ou a sessão principal (checklist passo a passo, conteúdo exato do `payload.json` da rodada aprovada, `operation` (`publish`, `send`, `run_ads` ou `update_page`), `destination`, `channel`, janela, pontos de conferência e rollback). Quem executar registra `executed_by: human` ou `main_session`; o `outcome` fica `handed_off` até a confirmação.
8. **Confirmar o resultado**: receba do executor o `external_reference` (id, URL pública ou protocolo) quando houver; defina `outcome`: `published`, `scheduled`, `handed_off` ou `failed`.
9. **Emitir o recibo**: `publish-receipt` com `verification` {sha_match, approval_valid, not_expired, bound_match, verify_ok, counter_signed_by (`copy-chief`), counter_signed_at}, `rollback_plan` específico, `executed_by` e `executed_at`. Um veto antes da execução gera apenas o envelope `blocked`; recibo com `outcome: failed` só existe se uma execução tiver sido tentada.
10. **Notificar e registrar**: envelopes para `cro-analyst` (monitorar) e `knowledge-curator` (registrar ativo aprovado); evento no journey log; atualizar `status` do ativo para `published` ou `blocked`.

## Saída

- **Contrato:** `contracts/publish-receipt.schema.json` (`artifact_id` prefixo `pub-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/07-published/{asset_id}/publish-receipt.json`.
- **Envelope de handoff:** `from_agent: copy-publisher`, `to_agent: cro-analyst` e `knowledge-curator`, `artifact_type: publish-receipt`, `status: ready` (ou `blocked`/`failed` em caso de veto), `human_approval_required: false`, `gate: null`.

## Acceptance Criteria (Critérios de aceite)

- Nenhuma ação externa foi feita antes da verificação completa.
- `verification` completo, com `sha_match`, `approval_valid`, `not_expired`, `bound_match` e `verify_ok` verdadeiros e `counter_signed_by: copy-chief` com `counter_signed_at`, em toda execução bem-sucedida.
- `rollback_plan` descreve como desfazer (ex.: despublicar, pausar envio, restaurar versão `v{n-1}`).
- `outcome` coerente com `executed_by` (`human` ou `main_session`).
- Destino, canal e operação executados iguais ao aprovado.
- Nenhum subagent executou a ação externa.
- Nenhuma credencial gravada em arquivo do repositório ou do `.data`.

## Quality gate e checklist

- **Gate:** `QG-PUBLISH-PREFLIGHT` (APPROVE ≥ 0,80 e todos os itens bloqueantes cumpridos).
- **Checklist:** `checklists/publish-preflight-checklist.md`.
- **Executor:** `copy-chief` contra-assina o preflight (conforme `data/quality-gates.yaml`, D7) reexecutando `verify --for-execution` sem flags; o `copy-publisher` é o produtor (roda o `verify`) e não valida a si mesmo.
- **Arestas de handoff (D8):** `copy-publisher` -> `copy-chief` (preflight) e `copy-chief` -> `copy-publisher` (liberado).
- **Veto:** sha divergente, decisão expirada, decisão sem proveniência humana, `approved_with_edits` sem nova decisão `approved`, destino, canal ou operação diferentes do aprovado, `idempotency_key` repetida.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| sha divergente | VETO sem execução (envelope `blocked`); reemitir pacote sobre o payload atual |
| Decisão expirada (`now` ≥ `decision.expires_at`) | VETO; nova rodada de aprovação ao `approval-owner` |
| `copy-chief` veta ou não contra-assina o preflight | Não executar; corrigir o apontado e repetir o preflight (máx. 2 ciclos) |
| Decisão `approved_with_edits` | Não executar; abrir nova versão, novo hash e novo `approval-request` (via `prepare-approval-package`) e aguardar `approved` |
| Executor humano ou sessão principal indisponível | Manter o pacote de execução pendente com checklist (`outcome: handed_off`); subagent nunca executa no lugar |
| Falha parcial na execução | `outcome: failed`; o executor aplica o `rollback_plan`; abrir bloqueio ao `copy-chief` |
| Condição da decisão não atendida (ex.: canal ou data) | Não executar; pedir ajuste ao `approval-owner` |
| Repetição acidental | Devolver recibo existente pela `idempotency_key` |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Entregue | `cro-analyst` (`analyze-performance`) | `publish-receipt` | null |
| Entregue | `knowledge-curator` (`curate-asset-library`) | `publish-receipt` | null |
| Preflight pronto para contra-assinatura | `copy-chief` | `handoff-envelope` | null |
| Veto ou falha | `copy-chief` | `handoff-envelope` | null |
| Reaprovação necessária | `copy-publisher` abre a rodada seguinte (`prepare-approval-package`) para o `approval-owner` | `approval-request` | G4 |

## Exemplo

Entrada resumida (exemplo ilustrativo): e-mail de nutrição aprovado e contra-assinado; o humano agenda o envio na ferramenta de e-mail. O hash do exemplo é um marcador; em uso real é o do pedido, conferido pelo `verify`.

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "pub-camp-mentoria-eml-001",
    "artifact_type": "publish-receipt",
    "campaign_id": "camp-mentoria-gestao",
    "business": "{business}",
    "produced_by": "copy-publisher",
    "produced_at": "2026-11-11T09:00:00Z",
    "version": 1,
    "status": "published"
  },
  "asset_id": "eml-camp-mentoria-001",
  "approval_decision_id": "apd-camp-mentoria-eml-001",
  "payload_sha256": "4444444444444444444444444444444444444444444444444444444444444444",
  "destination": "ferramenta de e-mail marketing",
  "channel": "email",
  "executed_by": "human",
  "executed_at": "2026-11-11T09:00:00Z",
  "external_reference": "campanha-agendada-123 (exemplo ilustrativo)",
  "verification": {"sha_match": true, "approval_valid": true, "not_expired": true, "bound_match": true, "verify_ok": true, "counter_signed_by": "copy-chief", "counter_signed_at": "2026-11-11T08:50:00Z"},
  "rollback_plan": "Cancelar o agendamento na ferramenta antes do disparo; restaurar a versão v2 como rascunho.",
  "outcome": "handed_off"
}
```

## Anti-padrões

- Executar antes de rodar `approval_tools.py verify --for-execution`, ou registrar `sha_match: true` sem a saída do script.
- Passar `--now` ou `--config` ao verify fora de teste, ou aceitar um preflight obtido com eles.
- Deixar um subagent executar a ação externa, ou usar curl com credencial do ambiente para contornar a regra.
- Executar com base em `approved_with_edits`.
- Reavaliar o `expires_at` do pedido como validade da aprovação (vale só `decision.expires_at`).
- Aceitar "o humano falou que aprovou" sem `approval-decision`.
- Publicar em destino diferente do aprovado.
- Fazer pequenas correções "de última hora" no texto.
- Guardar token ou senha de ferramenta externa no repositório.
- Ignorar `conditions` da decisão.
- Reutilizar a mesma `idempotency_key` para nova tentativa após alteração do payload.
