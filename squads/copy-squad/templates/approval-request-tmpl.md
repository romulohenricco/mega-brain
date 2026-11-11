# Pedido de Aprovação — {asset_id}

> Template humano do contrato `approval-request` (`contracts/approval-request.schema.json`). Preenchido pelo `copy-publisher` e lido pelo `approval-owner`. O artefato oficial é o JSON em `.data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-request.json` (G1, G2 e G3 de oferta em `06-approval/_campaign/{gate}-r{n}/`; amostragem em `06-approval/{asset_id}/sampling-r{n}/`). O payload aprovado é imutável: qualquer mudança gera novo hash e a rodada seguinte de aprovação.

## 1. Identificação

| Campo | Valor |
|---|---|
| artifact_id | apr-{campaign_id}-{n} |
| rodada | {gate}-r{n} (pasta da rodada; `{gate}` = `lower(gate)`, ex.: g4-r1, sampling-r1) |
| campaign_id | camp-{slug} |
| business | {business} |
| asset_id | (id estável do ativo, sem versão, ex.: cvc-camp-x-001; em G1, G2 e G3 de oferta = campaign_id, pasta `06-approval/_campaign/`) |
| versão do ativo | v{n} (meta.artifact_id do draft = {asset_id}-v{n}; a versão vai dentro do payload) |
| solicitado por | copy-publisher |
| aprovador | approval-owner |
| criado em | AAAA-MM-DDTHH:MM:SSZ |

## 2. Decisão solicitada

| Campo | Valor |
|---|---|
| gate | G1 / G2 / G3 / G4 / SAMPLING (G5 não usa pedido) |
| operation | approve_brief / approve_angle / approve_claims / publish / send / run_ads / update_page / internal_use |
| destination | (local de destino exato; fora do hash, copiado para o `bound_to` da decisão e comparado por igualdade no preflight) |
| channel | (canal exato, ex.: landing_page, email, paid_ads, organic_social; `internal` em G1, G2, G3 de oferta e amostragem; fora do hash, vai para o `bound_to`) |
| risk_level | low / medium / high |
| policy_applied | (regra de `data/risk-policy.yaml` aplicada) |

## 3. Integridade e validade

| Campo | Valor |
|---|---|
| payload_sha256 | (saída de `python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; 64 caracteres hexadecimais minúsculos) |
| método do hash (D1) | sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')); só o payload; sem NFC; nunca calculado de cabeça |
| expires_at | criação + 72 horas = prazo de resposta (pedido vencido segue pendente; silêncio nunca é aprovação). A janela de execução é o expires_at da approval-decision (decided_at + 72h) |
| idempotency_key | {campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do payload_sha256} (ex.: camp-x:cvc-camp-x-001:g4:r1:3f9a1c2b7d40; em gates de campanha asset_id = campaign_id) |

## 4. Revisões anexadas

| Revisão | ID | Resultado | Obrigatória por |
|---|---|---|---|
| edit-report | edt-... | quality_score: ___ | medium e high |
| brand-review | bvr-... | brand_alignment_score: ___ / aprovado: sim/não | medium e high |
| compliance-review | cpl-... | overall_risk: ___ / aprovado: sim/não | G3; G4 em medium (modo leve) e high (completo) |

## 5. Claims para decisão (G3)

| Claim | Tipo | Status | Fonte | Ação requerida |
|---|---|---|---|---|
| (texto literal) | price / guarantee / result / authority / testimonial / comparison / health / financial / other | verified / unverified / false / risky | | |

Regra: claim sem fonte verificável não é aprovado; volta como `needs_approval`.

## 6. Payload completo

(Copie o artefato final inalterado. O JSON completo está no campo `payload` do arquivo persistido. Este bloco serve para leitura humana; em caso de divergência, vale o JSON e o hash.)

```text
{conteúdo completo do ativo, seção por seção}
```

## 7. Trilha de auditoria

| Em | Ator | Ação |
|---|---|---|
| AAAA-MM-DDTHH:MM:SSZ | copy-publisher | payload congelado da versão v{n} |
| AAAA-MM-DDTHH:MM:SSZ | copy-publisher | payload_sha256 calculado |
| AAAA-MM-DDTHH:MM:SSZ | copy-publisher | pedido emitido ao approval-owner |

## 8. Orientação ao aprovador (resumo)

- Abra o payload completo e confira o hash.
- Decida: **approved**, **approved_with_edits** (liste as edições; não autoriza execução: o copy-publisher abre a rodada seguinte com novo hash e você confirma com `approved`) ou **rejected** (explique o motivo).
- Registre a decisão você mesmo, em `approval-decision` com o mesmo `payload_sha256`: `!python squads/copy-squad/scripts/approval_tools.py decide ...` (`human-cli`) ou mensagem sua no chat transcrita pela sessão principal fora do papel de copy-chief, com a mensagem literal em `comments` (`human-chat-confirmed`). Agentes não gravam a decisão.
- A decisão vale por 72 horas a partir de `decided_at` (janela de execução).
- Corrigiu algo de um agente? Registre G5 (`correct-agent-failure`, sem pedido).

## 9. Plano de rollback

(Como desfazer a ação se algo der errado: despublicar, pausar envio, restaurar versão anterior.)

## 10. Verificação do pacote

- [ ] Revisões do nível de risco anexadas
- [ ] Payload idêntico à versão revisada
- [ ] Hash reproduzível com `approval_tools.py hash` (saída anexada ao audit_trail)
- [ ] expires_at em 72h (prazo de resposta)
- [ ] channel preenchido e idempotency_key derivada ({campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 hex do hash}) e única
- [ ] Pasta da rodada conforme D5
- [ ] Trilha de auditoria preenchida
- [ ] Validado em `contracts/approval-request.schema.json`
