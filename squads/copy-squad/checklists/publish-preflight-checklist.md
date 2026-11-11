# Checklist: Preflight de Publicação

## Metadata
```yaml
id: publish-preflight-checklist
name: "Checklist de preflight de publicação e entrega"
version: 1.0.0
executor: copy-chief           # contra-assina o QG-PUBLISH-PREFLIGHT (D7, D8)
self_check_by: copy-publisher # produtor do pacote e do resultado do verify; a autochecagem não aprova o gate
related_task: publish-approved-asset
quality_gate: QG-PUBLISH-PREFLIGHT
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que nada seja publicado, enviado, veiculado ou alterado em canal externo sem uma aprovação humana válida e que o conteúdo entregue seja exatamente o aprovado. O preflight é em dois passos (D8) e acontece **depois** da decisão do G4: não é pré-requisito do G4 (E4). O `copy-publisher` (produtor) aplica as fases 1 e 2 ao montar o pacote (`prepare-approval-package`) e as fases 3 e 4 depois da decisão (`publish-approved-asset`), rodando `approval_tools.py verify --for-execution --request <rodada>/approval-request.json --decision <rodada>/approval-decision.json --payload <rodada>/payload.json` (payload.json da rodada, E8) e registrando o resultado. O `copy-chief` (executor do QG-PUBLISH-PREFLIGHT) reexecuta o mesmo comando sem flags e contra-assina na fase 6; sem a contra-assinatura nenhuma ação externa é executada. `--now` e `--config` só existem para teste (`COPY_SQUAD_TEST_MODE=1`); um resultado obtido com eles não vale. Nenhum subagent executa a ação externa: a execução é do humano ou da sessão principal. Também cobre o versionamento (`manage-versions`).

## Fase 1: Revisões e rito de risco

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | `risk_level` do ativo identificado (low, medium, high) | blocking | [ ] | |
| 2 | Medium e high: `edit-report` presente e `quality_score` registrado | blocking | [ ] | |
| 3 | Medium e high: `brand-review` com `approved_for_next_stage: true` | blocking | [ ] | |
| 4 | Medium: `compliance-review` em modo leve; high: completo, com `approved: true` e `overall_risk` diferente de blocked | blocking | [ ] | |
| 5 | Claims sensíveis tiveram G3 registrado | blocking | [ ] | |
| 6 | Versão localizada (se houver) passou por recheck de compliance | recommended | [ ] | |

**Score Fase 1:** ___/6

## Fase 2: Integridade do payload e do pacote

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 7 | O payload é idêntico à versão `v{n}` revisada (sem edição) e o `payload.json` da rodada é idêntico a `approval-request.payload` (E8) | blocking | [ ] | |
| 8 | `payload_sha256` é a saída de `approval_tools.py hash` (D1: só o payload, `ensure_ascii=False`, UTF-8, sem NFC e sem `destination`); nunca calculado de cabeça; `channel` presente no pedido | blocking | [ ] | |
| 9 | Rodar `approval_tools.py hash` de novo reproduz o valor registrado | blocking | [ ] | |
| 10 | `expires_at` do pedido igual à criação mais 72 horas (prazo de resposta) | blocking | [ ] | |
| 11 | `idempotency_key` no formato `{campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do hash}` (nos gates de campanha, `asset_id = campaign_id`) e única na campanha | blocking | [ ] | |
| 12 | `audit_trail` com pelo menos 3 entradas (congelamento, hash, emissão) | recommended | [ ] | |
| 13 | Versões anteriores preservadas e changelog atualizado | recommended | [ ] | |

**Score Fase 2:** ___/7

## Fase 3: Validade da aprovação

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 14 | Existe `approval-decision` para o `approval_request_id` | blocking | [ ] | |
| 15 | `decision` é `approved` (D2: `approved_with_edits` nunca autoriza execução) | blocking | [ ] | |
| 16 | `payload_sha256` da decisão igual ao do pedido e ao hash do `payload.json` da rodada, recalculado agora por `approval_tools.py verify --for-execution --request/--decision/--payload` da rodada (com a saída anexada); `request.gate == G4`, `operation` externa e `risk_level` diferente de `low` | blocking | [ ] | |
| 17 | Agora é anterior a `decision.expires_at`; `decided_at` não está no futuro e `expires_at == decided_at + 72h` (tolerância de 60 s); o `expires_at` do pedido não é reavaliado (D3) | blocking | [ ] | |
| 18 | `conditions` da decisão (canal, data, segmento) atendidas | blocking | [ ] | |
| 19 | `human_attested: true`, `recorded_via` (`human-cli` ou `human-chat-confirmed`, este com `comments` não vazio) e `reviewer` em `human_gates.approvers` (D4); decisão da maior rodada do gate | blocking | [ ] | |

**Score Fase 3:** ___/6

## Fase 4: Destino e execução

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 20 | `bound_to` da decisão igual a `gate`, `operation`, `destination` e `channel` do pedido, e `destination`, `channel` e `operation` a executar iguais aos do pedido (ficam fora do hash); divergência é VETO | blocking | [ ] | |
| 21 | Pacote de execução emitido para o humano ou a sessão principal (nenhum subagent executa; `PUBLISH_EXECUTORS = [human, main_session]`) | blocking | [ ] | |
| 22 | Nenhuma credencial gravada em arquivo do repositório ou do `.data` | blocking | [ ] | |
| 23 | Janela de agendamento coerente com a decisão | recommended | [ ] | |
| 24 | `rollback_plan` específico definido antes da execução | blocking | [ ] | |
| 25 | `idempotency_key` ainda sem `publish-receipt` | blocking | [ ] | |

**Score Fase 4:** ___/6

## Fase 5: Recibo e registro

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 26 | `publish-receipt` válido no schema | blocking | [ ] | |
| 27 | `verification` completo: sha_match, approval_valid, not_expired, bound_match e verify_ok verdadeiros, `counter_signed_by: copy-chief` e `counter_signed_at` preenchido | blocking | [ ] | |
| 28 | `outcome` coerente (published, scheduled, handed_off, failed) com `executed_by` (`human` ou `main_session`) | blocking | [ ] | |
| 29 | `external_reference` registrada quando houver | recommended | [ ] | |
| 30 | Envelopes para `cro-analyst` e `knowledge-curator` registrados | recommended | [ ] | |
| 31 | Evento no journey log | recommended | [ ] | |

**Score Fase 5:** ___/6

## Fase 6: Contra-assinatura do copy-chief (D8)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 32 | O resultado do `approval_tools.py verify --for-execution` (`{ok, checks[]}`), sem `--now` nem `--config`, foi enviado ao `copy-chief` em envelope `preflight-result` | blocking | [ ] | |
| 33 | O `copy-chief` conferiu os itens das fases 1 a 4, reexecutou o mesmo `verify --for-execution --request/--decision/--payload` da rodada sem flags e contra-assinou (ou vetou) em envelope de volta, antes de qualquer execução | blocking | [ ] | |

**Score Fase 6:** ___/2

## Veto conditions

A execução é vetada (envelope `blocked`, sem ação externa) quando houver:

1. `approval-decision` ausente, `rejected`, `approved_with_edits` ou de outro payload.
2. `payload_sha256` recalculado diferente do aprovado, mesmo por um caractere, ou `bound_to` diferente do pedido.
3. Decisão expirada (`now` maior ou igual a `decision.expires_at`, `decided_at` + 72h).
4. Revisão obrigatória do nível de risco ausente ou reprovada.
5. Destino, canal ou operação diferentes do aprovado.
6. `idempotency_key` já executada.
7. Qualquer tentativa de `git push`, PR ou deploy de código (fora do escopo; exclusivo do @devops).
8. Ausência da contra-assinatura do `copy-chief` ou decisão sem `human_attested`.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Revisão ausente | Devolver ao `copy-chief` com a lista do que falta |
| Hash não reproduz | Descartar o pacote, reconstruir da versão revisada, recalcular |
| Hash diverge da decisão | Abrir a rodada seguinte sobre o payload atual; não executar |
| Decisão expirada | `prepare-approval-package` na rodada seguinte e nova decisão |
| `approved_with_edits` | Aplicar as edições, gerar `v{n+1}` e abrir a rodada seguinte; só `approved` sobre o novo hash libera |
| Sem contra-assinatura do `copy-chief` | Não executar; corrigir o apontado e repetir o preflight (máximo 2 ciclos) |
| Executor humano ou sessão principal indisponível | Manter o pacote de execução com checklist (`outcome: handed_off`); subagent nunca executa no lugar |
| Chave de idempotência repetida | Devolver o recibo existente |
| Condição da decisão não atendida | Pedir ajuste ao `approval-owner`; não executar |

## Edge cases

- **Aprovação com condição de data:** executar somente dentro da janela; fora dela, nova rodada.
- **Falha parcial na execução:** o executor aplica o `rollback_plan`; registrar `failed` e abrir bloqueio.
- **Várias versões aprovadas no mesmo dia:** usar somente a decisão cujo sha coincide com o payload atual.
- **Ativo em vários canais:** um `publish-receipt` por destino, cada um com sua `idempotency_key`.
- **Execução humana:** exigir confirmação do executor e `external_reference` antes de marcar `handed_off` como concluído.
- **Mudança de plataforma ou política entre aprovação e execução:** pausar e reencaminhar ao `compliance-checker`.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 33 (Fase 1: 6, Fase 2: 7, Fase 3: 6, Fase 4: 6, Fase 5: 6, Fase 6: 2). Item bloqueante reprovado implica VETO independentemente do score.

**Score final:** ___/33 = ___ → [ ] APPROVE  [ ] REVIEW  [ ] VETO
