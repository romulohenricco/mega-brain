---
task: prepare-approval-package
name: prepare-approval-package
task_name: "Preparar pacote de aprovação"
version: "1.0.0"
squad: copy-squad
task_id: prepare-approval-package
category: operations
difficulty: advanced
responsavel: '@copy-publisher'
responsavel_type: Agent
responsible_executor: copy-publisher
execution_type: Agent
atomic_layer: Molecule
elicit: false
estimated_time: 10-20min
model: haiku
status: pending
domain: tactical
Entrada:
- campo: artefato_final
  tipo: contract:brief, angles, offer-canvas (G1, G2, G3 de oferta), compliance-review (G3 de texto), conversion-copy, content-piece, ux-copy, video-script ou email-journey (G4 e amostragem)
  obrigatorio: true
- campo: revisoes
  tipo: contract:edit-report, brand-review, compliance-review (conforme o gate e o risco)
  obrigatorio: false
Saida:
- campo: approval_request
  tipo: contract:approval-request
  persistido_em: .data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-request.json (G3 de texto e G4; amostragem em sampling-r{n}) ou 06-approval/_campaign/{gate}-r{n}/approval-request.json (G1, G2 e G3 de oferta, com asset_id = campaign_id); {gate} em minúsculas; ao lado do pedido, payload.json na mesma pasta de rodada (E8)
input: [artefato, edit-report, brand-review, compliance-review]
output: [approval-request]
action_items:
  - "Identificar o gate (G1, G2, G3, G4 ou SAMPLING) e a pasta de rodada"
  - "Verificar revisões obrigatórias pelo risco"
  - "Congelar o payload sem alterações"
  - "Gravar payload.json na pasta da rodada (exatamente approval-request.payload, JSON canônico D1; é o arquivo que o humano aprova e que a execução usa, E8)"
  - "Calcular payload_sha256 com approval_tools.py hash (D1), nunca de cabeça"
  - "Definir channel, expires_at (prazo de resposta de 72h), idempotency_key derivada e audit_trail"
  - "Persistir o pedido e encaminhá-lo ao approval-owner"
acceptance_criteria:
  - "approval-request válido em contracts/approval-request.schema.json"
  - "payload_sha256 produzido pela saída de `python squads/copy-squad/scripts/approval_tools.py hash`, que cobre somente o payload (sort_keys, separators (',', ':'), ensure_ascii=False, UTF-8, sem NFC e sem destination)"
  - "expires_at do pedido igual a criação mais 72 horas, como prazo de resposta (silêncio nunca é aprovação); a janela de execução (decided_at mais 72 horas) fica na approval-decision"
  - "channel presente (internal em G1, G2, G3 de oferta e amostragem); asset_id = campaign_id nos gates de campanha"
  - "idempotency_key no formato {campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do payload_sha256}"
  - "revisões exigidas pelo risco referenciadas em reviews"
pre_condition: "para G4, ativo revisado pelo copy-editor, pelo brand-voice-guardian e pelo compliance-checker (completo em high; leve em medium); para G1, G2 e G3, o artefato do gate consolidado pelo produtor"
post_condition: "approval-request persistido na pasta da rodada e entregue ao approval-owner com status needs_approval"
checklist: checklists/publish-preflight-checklist.md
quality_gate: null
human_gate: [G1, G2, G3, G4]
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "revisão ausente = não montar o pacote; devolver ao copy-chief com a lista do que falta; nunca preencher revisão por conta própria"
---

# Task: Preparar pacote de aprovação

## Objetivo

Montar o pedido de aprovação humana com tudo que o `approval-owner` precisa para decidir e que o `copy-publisher` precisa para executar com segurança: payload completo e imutável, hash (`payload_sha256`) calculado pelo script `approval_tools.py hash`, política de risco aplicada, revisões anexadas, prazo de resposta de 72 horas (a janela de execução conta a partir de `decided_at`, na `approval-decision`), chave de idempotência e trilha de auditoria. Esta task é o **produtor único** de `approval-request` (D5) para todos os gates com pedido: G1 (`approve_brief`), G2 (`approve_angle`), G3 (`approve_claims`), G4 (`publish`, `send`, `run_ads`, `update_page`) e amostragem (`internal_use`, campo `gate: SAMPLING`). O pacote evita que o agente altere a peça depois do aceite humano. G5 não usa pedido: é `correct-agent-failure`.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Brief consolidado pronto para G1, ângulos prontos para G2, claims prontos para G3 | Artefato ainda em edição ou sem revisões obrigatórias |
| Ativo final revisado e pronto para G4 | Para aprovar (decisão é humana) |
| Rodada seguinte após `approved_with_edits` (D2), decisão expirada ou payload alterado | Para publicar (use `publish-approved-asset`) |
| Amostragem de baixo risco que precise de registro formal (`SAMPLING`) | Para corrigir falha de agente (G5, use `correct-agent-failure`) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| artefato do gate | `brief`, `angles`, `offer-canvas` (G1, G2, G3 de oferta); `compliance-review` e a copy (G3 de texto); `conversion-copy`, `content-piece`, `ux-copy`, `video-script` ou `email-journey` (G4, amostragem) | sim | `01-strategy/`, `03-angles/`, `05-review/`, `04-drafts/{asset_id}/v{n}.json` |
| edit-report | `edit-report` | G4 em medium e high | `copy-editor` |
| brand-review | `brand-review` | G4 em medium e high | `brand-voice-guardian` |
| compliance-review | `compliance-review` | G3; G4 em medium (modo leve) e high (completo) | `compliance-checker` |
| script | `scripts/approval_tools.py` | sim | squad (D21) |
| localization | `localization` | quando houver versão localizada | `localization-specialist` |
| política | `data/risk-policy.yaml` | sim | squad |
| destino, canal e operação | texto | sim | `execution-plan` (canal `internal` em G1, G2, G3 de oferta e amostragem) |

## Passos

1. **Identificar ativo e versão**: confirme `asset_id`, versão (`v{n}`) e o contrato do artefato; use sempre a versão mais recente aprovada pelas revisões.
2. **Checar o rito de risco** (`data/risk-policy.yaml`): low (uso interno) não exige revisões de G4, mas registre a amostragem; medium exige `edit-report`, `brand-review` com `approved_for_next_stage: true` e `compliance-review` em modo leve; high exige também `compliance-review` completo com `approved: true` e `requires_legal_review` resolvido. Toda ação externa é no mínimo medium (D6). Para G1, G2 e G3, confira que o artefato está consolidado pelo produtor e que o `risk_level` do `execution-plan` pede o gate (G1 em medium e high; G2 em high ou campanha multi-ativo; G3 com claim sensível).
3. **Definir `gate`, `operation` e a pasta da rodada**: `G1` com `approve_brief`, `G2` com `approve_angle`, `G3` com `approve_claims`, `G4` com `publish`, `send`, `run_ads` ou `update_page`, e `SAMPLING` com `internal_use` (amostragem determinística: `approval_tools.py sample`). Pastas (D5, E3): `06-approval/_campaign/{gate}-r{n}/` para G1, G2 e G3 de oferta, com `asset_id = campaign_id`; `06-approval/{asset_id}/{gate}-r{n}/` para G3 de texto e G4; `06-approval/{asset_id}/sampling-r{n}/` para amostragem. `{gate}` é sempre `lower(approval-request.gate)` (ex.: `g4-r1`, `sampling-r1`); o campo `gate` do JSON continua `G4` ou `SAMPLING`; `n` é a rodada seguinte à maior existente do gate. Em G2, o pacote só é montado depois que o `copy-chief` executou o QG-ANGLES sobre os ângulos: nenhum produtor envia direto ao `approval-owner`.
4. **Congelar o payload**: copie o artefato no campo `payload` sem qualquer edição, tradução ou formatação nova. Em G3 de texto, G4 e amostragem o payload inclui `draft_id = {asset_id}-v{n}` (igual ao `meta.artifact_id` do draft), pois `asset_id` é estável entre versões (D14, E3).
5. **Calcular o hash (D1)**: grave o `approval-request.json` com `payload_sha256` provisório de 64 zeros, rode `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>` e copie a saída para `payload_sha256`; rode o comando de novo e confirme que a saída é idêntica. A fórmula do script é `sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))`, em hexadecimal minúsculo de 64 caracteres; cobre **somente** `payload` (sem NFC, sem normalização de quebra de linha). `destination`, `channel` e `operation` não entram no hash: o `decide` os copia para `bound_to` da decisão e o preflight de `publish-approved-asset` (`verify --for-execution`) os compara por igualdade com o pedido e com o que será executado, e divergência é VETO. O hash nunca é calculado "de cabeça" por um modelo; sem a saída do script, o pacote é inválido. Registre o comando e a saída no `audit_trail`.
6. **Definir os metadados**: `risk_level`, `policy_applied` (ex.: `risk-policy: high -> compliance + G3 + G4`), `requested_by: copy-publisher`, `approver_role: approval-owner`, `destination`, `channel`, `expires_at` (criação mais 72h = **prazo de resposta**, D3: passou sem decisão, o pedido continua pendente e o `copy-chief` reenvia ou escala; silêncio nunca é aprovação; a janela de execução é o `expires_at` da `approval-decision`, igual a `decided_at` mais 72h) e `idempotency_key` derivada: `{campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do payload_sha256}` (ex.: `camp-mentoria:cvc-landing-mentoria-01:g4:r1:3f9a1c2b7d40`, exemplo ilustrativo; em G1, G2 e G3 de oferta `asset_id = campaign_id`, então o segmento se repete: `camp-mentoria:camp-mentoria:g1:r1:...`). O schema impõe esse formato por `pattern`. A mesma chave identifica a mesma operação sobre o mesmo payload; payload ou rodada nova gera chave nova.
7. **Preencher `reviews`**: ids de `edit_report_id`, `brand_review_id` e `compliance_review_id` correspondentes.
8. **Gravar o `payload.json` da rodada (E8)**: na mesma pasta do pedido, grave `payload.json` com exatamente o conteúdo de `approval-request.payload`, serializado como JSON canônico do D1 (`sort_keys`, separadores `(',', ':')`, `ensure_ascii=False`, UTF-8). Rode `python squads/copy-squad/scripts/approval_tools.py content-hash <rodada>/payload.json` e confirme que a saída é igual a `payload_sha256`. É esse arquivo, e não o draft `04-drafts/{asset_id}/v{n}.json`, que o humano aprova e que `publish-approved-asset` passa ao `verify --payload`.
9. **Registrar a trilha**: `audit_trail` com entradas (`at`, `actor`, `action`): payload congelado, hash calculado, revisões anexadas, pedido emitido.
10. **Validar, persistir e emitir**: valide no schema, aplique o `publish-preflight-checklist` (itens de pacote), grave `approval-request.json` e registre envelope ao `approval-owner`.

## Saída

- **Contrato:** `contracts/approval-request.schema.json` (`artifact_id` prefixo `apr-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-request.json` (G3 de texto, G4; amostragem em `sampling-r{n}`) ou `06-approval/_campaign/{gate}-r{n}/approval-request.json` (G1, G2, G3 de oferta, com `asset_id = campaign_id`); `{gate}` sempre em minúsculas.
- **Envelope de handoff:** `from_agent: copy-publisher`, `to_agent: approval-owner`, `artifact_type: approval-request`, `status: needs_approval`, `human_approval_required: true`, `gate` do pedido (`G1`, `G2`, `G3`, `G4` ou `SAMPLING`), `risk_level` do ativo.

## Acceptance Criteria (Critérios de aceite)

- `approval_tools.py hash` sobre o arquivo gera exatamente `payload_sha256`, e a saída do comando consta no `audit_trail`.
- `expires_at` está a 72h da criação (prazo de resposta do humano); `idempotency_key` segue o formato `{campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 hex do hash}` e não aparece em pedido com payload ou rodada diferente.
- A pasta da rodada segue D5 e nenhuma rodada anterior foi sobrescrita.
- `reviews` referencia todos os ids exigidos pelo risco.
- `audit_trail` tem pelo menos 3 entradas com ator e ação.
- O payload é idêntico ao da versão do rascunho (sem edição) e o `payload.json` da rodada é idêntico ao `approval-request.payload` (`content-hash` do arquivo = `payload_sha256`).
- Pedido persistido e envelope registrado.

## Quality gate e checklist

- **Gate:** esta task não reivindica o `QG-PUBLISH-PREFLIGHT`: ele é pós-decisão (E4) e não é pré-requisito do G4; roda em `publish-approved-asset`. Aqui o `copy-publisher` aplica só os itens de pacote do checklist.
- **Checklist:** `checklists/publish-preflight-checklist.md`, fases de revisões e integridade.
- **Produtor:** `copy-publisher`. O QG-PUBLISH-PREFLIGHT (executor `copy-chief`, contra-assinatura, D7, D8) acontece depois da decisão, em `publish-approved-asset`, com `approval_tools.py verify --for-execution --request/--decision/--payload` da rodada (payload = `payload.json`).
- **Veto:** revisão obrigatória ausente, payload alterado, hash não reproduzível, `idempotency_key` duplicada.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Revisão obrigatória ausente | Status `needs_input` ao `copy-chief` com a lista do que falta |
| `compliance-review` com `approved: false` | Não empacotar; devolver ao fluxo de rework |
| Payload diferente da versão revisada | Descartar o pacote; reconstruir da versão com revisões |
| Mesma `idempotency_key` já executada (mesmo payload e rodada) | Não reemitir execução; o `publish-receipt` existente é devolvido. Reenvio legítimo abre a rodada seguinte e muda a chave; registrar em `audit_trail` |
| Humano decidiu `approved_with_edits` (D2) | Não executar. Aplicar as edições, gerar `v{n+1}` do rascunho, abrir a rodada `{gate}-r{n+1}` com novo `payload_sha256` (via script) e pedir nova decisão `approved` |
| Pedido sem resposta além de 72h | Continua pendente (silêncio nunca é aprovação); avisar o `copy-chief` para reenviar ou escalar |
| Decisão `approved` expirada (`now` ≥ `decision.expires_at`) | Nova rodada; manter a anterior no histórico |
| `approval_tools.py` indisponível | Parar e sinalizar ao `copy-chief`; nunca calcular o hash de cabeça |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Pacote pronto | `approval-owner` (`approve-gate`) | `approval-request` | G1, G2, G3 ou G4 |
| Revisão ausente | `copy-chief` | `handoff-envelope` | null |
| Após decisão `approved` | `copy-publisher` (`publish-approved-asset`) | `approval-decision` | G4 |

## Exemplo

Entrada resumida (exemplo ilustrativo): landing page `cvc-camp-mentoria-lp-001`, risco high, com as três revisões. O valor de `payload_sha256` abaixo é um marcador ilustrativo; em uso real vem sempre da saída de `approval_tools.py hash`.

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "apr-camp-mentoria-lp-001",
    "artifact_type": "approval-request",
    "campaign_id": "camp-mentoria-gestao",
    "business": "{business}",
    "produced_by": "copy-publisher",
    "produced_at": "2026-11-10T12:30:00Z",
    "version": 1,
    "status": "needs_approval",
    "risk_level": "high"
  },
  "asset_id": "cvc-camp-mentoria-lp-001",
  "gate": "G4",
  "operation": "publish",
  "destination": "página de vendas da mentoria",
  "channel": "landing_page",
  "payload": {"draft_id": "cvc-camp-mentoria-lp-001-v3", "format": "landing_page", "sections": ["..."]},
  "payload_sha256": "3333333333333333333333333333333333333333333333333333333333333333",
  "risk_level": "high",
  "policy_applied": "risk-policy: high exige compliance, G3 e G4",
  "reviews": {"edit_report_id": "edt-camp-mentoria-lp-001", "brand_review_id": "bvr-camp-mentoria-lp-001", "compliance_review_id": "cpl-camp-mentoria-lp-001"},
  "requested_by": "copy-publisher",
  "approver_role": "approval-owner",
  "expires_at": "2026-11-13T12:30:00Z",
  "idempotency_key": "camp-mentoria-gestao:cvc-camp-mentoria-lp-001:g4:r1:333333333333",
  "audit_trail": [
    {"at": "2026-11-10T12:20:00Z", "actor": "copy-publisher", "action": "payload congelado da v3"},
    {"at": "2026-11-10T12:25:00Z", "actor": "copy-publisher", "action": "payload_sha256 calculado com approval_tools.py hash (saída conferida em duas execuções)"},
    {"at": "2026-11-10T12:30:00Z", "actor": "copy-publisher", "action": "pedido G4 emitido ao approval-owner"}
  ]
}
```

## Anti-padrões

- Calcular o hash "de cabeça" ou com código improvisado em vez de `approval_tools.py hash`.
- Incluir `destination` ou `operation` no objeto hasheado, ou aplicar NFC (o método é D1: só o payload).
- Empacotar sem compliance em risco high.
- "Ajeitar" o payload antes de congelar.
- Reutilizar `idempotency_key` para payload ou destino diferente.
- Esquecer que `destination`, `channel` e `operation` ficam fora do hash: sem o `bound_to` da decisão e a comparação por igualdade no `verify`, o pedido poderia ser trocado depois do aceite.
- Definir `expires_at` do pedido maior que 72h.
- Tratar o `expires_at` do pedido como janela de execução (ela conta a partir de `decided_at`) ou tratar pedido vencido como veto automático ou como aprovação.
- Deixar G1, G2 ou G3 sem pedido produzido por esta task, ou o `copy-chief` montar o `approval-request`.
- Gravar o pedido de uma nova rodada por cima da pasta da rodada anterior.
- Omitir a trilha de auditoria.
- Pular o pacote em risco medium ou high "porque o cliente já viu".
