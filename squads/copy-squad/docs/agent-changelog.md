# Changelog de agentes — copy-squad

> Registro de versões dos agentes (prompt-base, escopo, contrato, heurísticas). Toda alteração em `agents/*.md` que mude comportamento incrementa a versão do agente e gera uma entrada aqui. O campo `prompt_version` dos contratos referencia estas versões.

## 1.0.2 — 2026-11-10

Rodada 3 de correção: emendas E1 a E7 do ADR-001 (`docs/governance-decisions.md`, seção "Emendas — rodada 3"), que prevalecem sobre as decisões originais. Nenhum agente muda de contrato principal; mudam campos de contrato, caminhos e regras operacionais.

### Resumo das mudanças

- **E1 (D1, D8, D21):** `approval-request` ganha `channel` obrigatório (`internal` para G1, G2, G3 de oferta e amostragem); `approval-decision` ganha `bound_to` = `{gate, operation, destination, channel}`, copiado do pedido pelo `decide`. `verify --for-execution` exige `gate == G4`, `operation` externa e `risk_level != low`; `--payload` compara o hash do conteúdo a executar. `--now` e `--config` só com `COPY_SQUAD_TEST_MODE=1`; o `copy-chief` reexecuta sem flags. Novo subcomando `content-hash` (único método de `content_sha256`).
- **E2 (D3, D4):** `verify` exige `decided_at <= now`, `expires_at == decided_at + 72h` (tolerância de 60 s) e `comments` não vazio em `human-chat-confirmed`; `meta.produced_by` e `meta.artifact_type` fixos na decisão; `edits[]` exige `section`, `before`, `after`, `reason`; mapeamento de `meta.status` (`approved_with_edits` → `needs_approval`). Em `human-chat-confirmed` quem transcreve é a sessão principal fora do papel de `copy-chief`.
- **E3 (D5, D14):** `asset_id = campaign_id` nos gates de campanha; pastas de rodada em minúsculas (`g1-r1`, `sampling-r1`); `idempotency_key = {campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 hex}`; `SAMPLING` aceito em `handoff-envelope` e `execution-plan`; G2 passa por `copy-chief` (QG-ANGLES) e `copy-publisher`; revisões sempre `*-v{n}.json`; `artifact_id = {asset_id}-v{n}` e `draft_id` no payload; `proof_id` com prefixo `prv-`.
- **E4 (D8, D18):** `QG-PUBLISH-PREFLIGHT` é pós-decisão; `publish-receipt.verification` com `{sha_match, approval_valid, not_expired, bound_match, verify_ok, counter_signed_by, counter_signed_at}`; nenhum subagent executa ação externa (`PUBLISH_EXECUTORS = [human, main_session]`); compra e veiculação de mídia são execução externa.
- **E5 (D11 a D13):** gatilho do G3 = claim sensível, `data_privacy` ou urgência/escassez; guard de publicação único em todos os workflows; herança de aprovação como checkpoint de entrada; `failure_correction` irrecuperável vai a `escalated_to_copy_chief`.
- **E6 (D17, D20, D22):** campos de `customer_phrases` (`anonymized`, `reuse`, `usage_rights`, `usage_basis`); `analysis_phase` em `performance-analysis`; MVP inclui `brand-voice-guardian`, com `QG-LEARNING` dispensado (`mvp_waivers`).
- **E7 (D23):** keywords `copy-*` com complemento de copy; limitação do router e proposta de melhoria documentadas no README.
- **Documentos de apoio:** README, base de conhecimento, arquitetura, primeiros passos e proposta de banco (`approvals.channel`, `bound_*`, `idempotency_key` com `CHECK`, janela `decided_at + 72h`; `publish_receipts` com `bound_match`, `verify_ok` e contra-assinatura) alinhados. A migração continua **não aplicada**.

## 1.0.1 — 2026-11-10

Alinhamento de todo o squad ao ADR-001 (`docs/governance-decisions.md`), resultado da revisão adversarial da versão 1.0.0 (121 achados). Nenhum agente muda de contrato principal; mudam regras operacionais e documentos de apoio.

### Resumo das mudanças

- **Hash do payload (D1, D21):** método único (`sha256` do JSON canônico do `payload`, com `ensure_ascii=False`), sempre calculado por `scripts/approval_tools.py`, nunca por um modelo. `destination`, `channel` e `operation` ficam fora do hash e são comparados por igualdade.
- **`approved_with_edits` (D2):** nunca autoriza execução; abre a rodada seguinte com novo hash e decisão `approved`.
- **Validade (D3):** pedido com 72 horas para resposta (silêncio nunca é aprovação); decisão com 72 horas de janela de execução a partir de `decided_at`.
- **Proveniência humana (D4):** decisão registrada somente pelo humano (`human-cli` ou `human-chat-confirmed`), com `human_attested` e `reviewer` em `human_gates.approvers`.
- **Produtor único de pedidos (D5):** o `copy-publisher` monta todos os `approval-request` (G1 a G4 e amostragem, gate `SAMPLING`).
- **Risco (D6):** toda ação externa é no mínimo médio; risco baixo só para uso interno; `wf-fast-variation` inclui `QG-COMPLIANCE` leve.
- **Executores dos gates (D7, D8):** tabela única produtor x executor; preflight em dois passos (`copy-publisher` roda, `copy-chief` contra-assina).
- **Ângulos (D9), G3 em dois momentos (D10), gates por risco e herança de aprovação (D11, D12), máquinas de estado (D13), versionamento de drafts (D14).**
- **Escopo de formatos (D15):** VSL é do `video-social-scriptwriter`; brand copywriting e conteúdo de fundo de funil são do `content-copywriter`.
- **Terceiros e voz do cliente (D16, D17), ferramentas dos subagents (D18), cadência (D19), A/B (D20), modo MVP com `copy-publisher` (D22), roteamento de skills (D23).**
- **Documentos de apoio:** README, base de conhecimento, arquitetura, primeiros passos e proposta de banco (`docs/proposed-migration.sql`, ainda **não aplicada**) alinhados ao ADR.

As versões individuais dos agentes na tabela da entrada 1.0.0 não foram alteradas por esta entrada; mudanças futuras de comportamento por agente seguem a convenção de versionamento abaixo.

## 1.0.0 — 2026-11-10

Entrada inicial do squad, criada a partir da pesquisa de domínio sobre a profissão de copywriter e o modelo de squad agêntico.

### Agentes (19: 18 IA e 1 humano)

| Agente | Tier | Tipo | Núcleo | Contrato principal | Versão |
|---|---|---|---|---|---|
| `copy-chief` | orchestrator | Agent | Comando | `execution-plan` | 1.0.0 |
| `brief-master` | tier_0 | Agent | Estratégia | `brief` | 1.0.0 |
| `audience-voc` | tier_0 | Agent | Estratégia | `audience-voc` | 1.0.0 |
| `offer-strategist` | tier_0 | Agent | Estratégia | `offer-canvas` | 1.0.0 |
| `brand-voice-guardian` | tier_0 (define) e tier_2 (revisa) | Agent | Estratégia e Qualidade | `brand-voice-guide`, `brand-review` | 1.0.0 |
| `research-analyst` | tier_0 | Agent | Produção (pesquisa) | `research-packet` | 1.0.0 |
| `hook-angle-creator` | tier_1 | Agent | Produção | `angles` | 1.0.0 |
| `conversion-copywriter` | tier_1 | Agent | Produção | `conversion-copy` | 1.0.0 |
| `content-copywriter` | tier_1 | Agent | Produção | `content-piece` | 1.0.0 |
| `ux-writer` | tier_1 | Agent | Produção | `ux-copy` | 1.0.0 |
| `video-social-scriptwriter` | tier_1 | Agent | Produção | `video-script` | 1.0.0 |
| `email-crm-copywriter` | tier_1 | Agent | Produção | `email-journey` | 1.0.0 |
| `localization-specialist` | tier_1 | Agent | Produção | `localization` | 1.0.0 |
| `copy-editor` | tier_2 | Agent | Qualidade | `edit-report` | 1.0.0 |
| `compliance-checker` | tier_2 | Agent | Qualidade e Inteligência | `compliance-review` | 1.0.0 |
| `cro-analyst` | tier_3 | Agent | Inteligência | `performance-analysis` | 1.0.0 |
| `knowledge-curator` | tier_3 | Agent | Inteligência | `knowledge-query-result`, `learning-record` | 1.0.0 |
| `copy-publisher` | tier_3 | Agent | Operação | `approval-request`, `publish-receipt` | 1.0.0 |
| `approval-owner` | human | Human | Governança | `approval-decision` | 1.0.0 |

### Decisões de projeto

- Consolidação de papéis: Brief Intake em `brief-master` (perguntas de intake ficam no `copy-chief`); Project Manager em `copy-chief`; Version Control em `copy-publisher`; Asset Library em `knowledge-curator`; Audience e Voice-of-Customer em `audience-voc`; Positioning e Offer em `offer-strategist`; Analytics e CRO em `cro-analyst`.
- Regra AP05: produtor diferente de validador.
- Nenhum agente executa ação externa sem `approval-decision` válido e `payload_sha256` igual.
- Persistência em filesystem (`.data/copy-squad`); proposta de banco registrada, não aplicada.

### Convenções de versionamento

| Mudança | Incremento | Exemplo |
|---|---|---|
| Correção de texto sem efeito de comportamento | patch | 1.0.1 |
| Nova heurística, comando ou campo opcional | minor | 1.1.0 |
| Mudança de contrato, de escopo ou de gate | major | 2.0.0 |

Cada entrada futura deve indicar: agente, versão anterior e nova, motivo, contrato afetado e evidência (avaliação ou learning-record que motivou a mudança).

### Modelo de entrada futura

```text
## x.y.z — AAAA-MM-DD
- agente: nome
  de: versão anterior
  para: nova versão
  motivo: ...
  contratos afetados: ...
  evidência: learning-record ou agent-evaluation de referência
```
