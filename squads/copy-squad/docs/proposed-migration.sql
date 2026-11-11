-- =====================================================================
-- PROPOSTA — NÃO APLICAR sem revisão do @data-engineer e aprovação humana
-- =====================================================================
-- Squad:    copy-squad (v1.0.1; alinhado ao ADR-001, docs/governance-decisions.md)
-- Status:   NÃO APLICADO. A fonte de verdade atual é o filesystem em
--           .data/copy-squad/. Este arquivo documenta o schema-alvo caso
--           a persistência migre para banco (ver docs/database-proposal.md).
-- Schema:   copy_squad (um schema dedicado; nada no schema public)
-- Regras:   - business_id (slug da unidade de negócio) em TODAS as tabelas
--           - RLS habilitado em todas, com políticas de exemplo por business_id
--           - papel dedicado com escopo mínimo; sem BYPASSRLS; nunca usar o
--             papel administrativo (postgres) em runtime
--           - approvals genérico para qualquer gate (G1 a G4 e SAMPLING; asset_type + asset_ref),
--             com payload_sha256, channel, idempotency_key, request_expires_at (prazo de resposta) e
--             decision_expires_at (decided_at + 72 h = janela de execução, reverificado por CHECK)
--           - a decisão é amarrada ao pedido: bound_gate/bound_operation/bound_destination/bound_channel
--             (equivalente ao objeto bound_to do approval-decision) precisam ser iguais ao pedido (E1)
--           - nenhum subagent executa ação externa: executed_by IN ('human','main_session') (E4)
--           - só decision = 'approved' autoriza execução; approved_with_edits abre a rodada seguinte (D2)
--           - a decisão só é gravada pelo papel aprovador humano, com human_attested e recorded_via (D4)
--           - o banco espelha o filesystem; não o substitui sem decisão humana
-- Pré-requisitos antes de aplicar:
--           1. Revisão do @data-engineer (DDL, índices, políticas)
--           2. Aprovação humana explícita
--           3. Projeto de banco oficial definido pelo responsável da unidade
--           4. Plano de rollback e de backfill a partir de .data/copy-squad/
--           5. Rodar os avisos de segurança e desempenho do provedor após aplicar
-- =====================================================================

BEGIN;

CREATE SCHEMA IF NOT EXISTS copy_squad;

-- ---------------------------------------------------------------------
-- Papéis (exemplo): o runtime do squad usa apenas copy_squad_app.
-- Criar com senha gerenciada fora deste arquivo. Sem BYPASSRLS.
-- ---------------------------------------------------------------------
-- CREATE ROLE copy_squad_app NOLOGIN NOBYPASSRLS;
-- CREATE ROLE copy_squad_approver NOLOGIN NOBYPASSRLS;   -- identidade do aprovador humano; nunca usado pelo runtime de IA
-- GRANT USAGE ON SCHEMA copy_squad TO copy_squad_app, copy_squad_approver;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA copy_squad TO copy_squad_app;
-- REVOKE UPDATE ON copy_squad.approvals FROM copy_squad_app;
-- (agent_runs, agent_evaluations, copy_versions, approvals e publish_receipts: o papel
--  copy_squad_app só recebe SELECT e INSERT; ver políticas abaixo)
-- GRANT SELECT ON copy_squad.approvals TO copy_squad_approver;
-- GRANT UPDATE (decision, reviewer_ref, human_attested, recorded_via, decision_payload_sha256,
--   bound_gate, bound_operation, bound_destination, bound_channel, comments, decided_at, audit_trail)
--   ON copy_squad.approvals TO copy_squad_approver;

-- ---------------------------------------------------------------------
-- Função auxiliar: negócio da sessão atual.
-- O runtime define: SELECT set_config('copy_squad.business_id', 'meu-negocio', true);
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION copy_squad.current_business_id()
RETURNS text
LANGUAGE sql
STABLE
AS $$
  SELECT NULLIF(current_setting('copy_squad.business_id', true), '')
$$;

-- ---------------------------------------------------------------------
-- campaigns  <->  contracts/execution-plan + demand-intake
--                 .data/copy-squad/{business}/{campaign_id}/00-intake/
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.campaigns (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id   text NOT NULL CHECK (business_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  campaign_id   text NOT NULL CHECK (campaign_id ~ '^camp-[a-z0-9]+(-[a-z0-9]+)*$'),
  name          text NOT NULL,
  objective     text,
  primary_kpi   text,
  channel       text,
  demand_type   text CHECK (demand_type IN ('conversion','content','crm','product_ux','video','brand','research')),
  risk_level    text CHECK (risk_level IN ('low','medium','high')),
  workflow_id   text,
  status        text NOT NULL DEFAULT 'draft',
  owner_ref     text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, campaign_id)
);

-- ---------------------------------------------------------------------
-- briefs  <->  contracts/brief
--              .data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.briefs (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id          text NOT NULL,
  campaign_uuid        uuid NOT NULL REFERENCES copy_squad.campaigns(id),
  artifact_id          text NOT NULL CHECK (artifact_id ~ '^brf-[a-z0-9]+(-[a-z0-9]+)*$'),
  version              integer NOT NULL CHECK (version >= 1),
  audience             jsonb,
  offer                jsonb,
  tone_of_voice        text,
  awareness_stage      text CHECK (awareness_stage IN ('unaware','problem_aware','solution_aware','product_aware','most_aware')),
  must_include         jsonb,
  must_avoid           jsonb,
  acceptance_criteria  jsonb,
  status               text NOT NULL DEFAULT 'draft',
  document             jsonb NOT NULL,          -- contrato completo (espelho do JSON)
  created_at           timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, artifact_id, version)
);

-- ---------------------------------------------------------------------
-- research_packets  <->  contracts/research-packet
--                        .data/copy-squad/{business}/{campaign_id}/02-research/research-packet.json
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.research_packets (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id       text NOT NULL,
  brief_uuid        uuid NOT NULL REFERENCES copy_squad.briefs(id),
  artifact_id       text NOT NULL CHECK (artifact_id ~ '^rsp-[a-z0-9]+(-[a-z0-9]+)*$'),
  market_context    jsonb,
  competitors       jsonb,
  customer_language jsonb,
  objections        jsonb,
  proof_assets      jsonb,
  facts             jsonb,
  gaps              jsonb,
  confidence        numeric CHECK (confidence BETWEEN 0 AND 1),
  document          jsonb NOT NULL,
  created_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, artifact_id)
);

-- ---------------------------------------------------------------------
-- angles  <->  contracts/angles
--              .data/copy-squad/{business}/{campaign_id}/03-angles/angles.json
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.angles (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id        text NOT NULL,
  brief_uuid         uuid NOT NULL REFERENCES copy_squad.briefs(id),
  angle_id           text NOT NULL CHECK (angle_id ~ '^ang-[a-z0-9-]+$'),
  angle              text NOT NULL,
  hook               text NOT NULL,
  promise            text NOT NULL,
  mechanism          text,
  proof_required     jsonb,
  risk_level         text NOT NULL CHECK (risk_level IN ('low','medium','high')),
  predicted_strength numeric NOT NULL CHECK (predicted_strength BETWEEN 0 AND 100),
  needs_approval     boolean NOT NULL DEFAULT false,
  status             text NOT NULL DEFAULT 'proposed',
  created_at         timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, angle_id)
);

-- ---------------------------------------------------------------------
-- copy_assets  <->  contracts/conversion-copy | content-piece | ux-copy |
--                   video-script | email-journey
--                   .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.copy_assets (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id   text NOT NULL,
  campaign_uuid uuid NOT NULL REFERENCES copy_squad.campaigns(id),
  brief_uuid    uuid REFERENCES copy_squad.briefs(id),
  angle_uuid    uuid REFERENCES copy_squad.angles(id),
  asset_id      text NOT NULL,
  agent_id      text NOT NULL,
  artifact_type text NOT NULL CHECK (artifact_type IN ('conversion-copy','content-piece','ux-copy','video-script','email-journey')),
  -- Formatos por contrato (D15): vsl é de video-script; conversion-copy não produz vsl;
  -- content-piece inclui case_study, white_paper, manifesto e tagline.
  format        text,
  title         text,
  status        text NOT NULL DEFAULT 'draft',
  current_version integer NOT NULL DEFAULT 1,
  confidence    numeric CHECK (confidence BETWEEN 0 AND 1),
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, asset_id),
  CONSTRAINT copy_assets_format_by_type CHECK (
    format IS NULL
    OR (artifact_type = 'conversion-copy' AND format IN ('landing_page','sales_page','ad','email','sequence'))
    OR (artifact_type = 'content-piece'   AND format IN ('article','newsletter','post','carousel','guide','case_study','white_paper','manifesto','tagline'))
    OR (artifact_type = 'video-script'    AND format IN ('reel','youtube','ad','story','vsl','webinar'))
    OR artifact_type IN ('ux-copy','email-journey')
  )
);

-- ---------------------------------------------------------------------
-- copy_versions  <->  v{n}.json (versões nunca sobrescritas; só INSERT)
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.copy_versions (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id    text NOT NULL,
  copy_asset_id  uuid NOT NULL REFERENCES copy_squad.copy_assets(id),
  version        integer NOT NULL CHECK (version >= 1),
  content        jsonb NOT NULL,
  content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[a-f0-9]{64}$'),
  changed_by     text NOT NULL,
  change_reason  text,
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (copy_asset_id, version)
);

-- ---------------------------------------------------------------------
-- approvals  <->  contracts/approval-request + approval-decision
--                 .data/copy-squad/{business}/{campaign_id}/06-approval/
--                   _campaign/{gate}-r{n}/          (G1, G2 e G3 de oferta; asset_id = campaign_id)
--                   {asset_id}/{gate}-r{n}/         (G3 de texto e G4)
--                   ({gate} sempre em minúsculas na pasta: g1, g2, g3, g4)
--                   {asset_id}/sampling-r{n}/       (amostragem)
-- Genérica para qualquer gate: o alvo é (asset_type, asset_ref), sem FK obrigatória
-- a copy_assets (o item aprovado em G1, G2 e G3 é um brief, um conjunto de ângulos
-- ou um compliance-review). Regras: payload imutável (sha256 por approval_tools.py),
-- idempotência, prazo de resposta e janela de execução.
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.approvals (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id       text NOT NULL,
  campaign_uuid     uuid REFERENCES copy_squad.campaigns(id),
  -- alvo genérico: asset_type descreve o artefato; asset_ref é o id do artefato (ex.: brf-..., ang-..., cvc-...-v2)
  asset_type        text NOT NULL CHECK (asset_type IN ('brief','angles','offer-canvas','compliance-review','copy-asset','sampling')),
  asset_ref         text NOT NULL,
  asset_id          text NOT NULL,            -- approval-request.asset_id (estável entre versões; = campaign_id em G1, G2 e G3 de oferta)
  round_n           integer NOT NULL DEFAULT 1 CHECK (round_n >= 1),   -- {gate}-r{n}
  gate              text NOT NULL CHECK (gate IN ('G1','G2','G3','G4','G5','SAMPLING')),
  operation         text NOT NULL CHECK (operation IN ('approve_brief','approve_angle','approve_claims','publish','send','run_ads','update_page','internal_use')),
  destination       text NOT NULL,
  -- approval-request.channel (obrigatório; 'internal' para G1, G2, G3 de oferta e amostragem). Fora do hash (E1)
  channel           text NOT NULL,
  payload           jsonb NOT NULL,
  -- sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')),
  -- calculado por scripts/approval_tools.py hash (D1); destination e operation não entram no hash
  payload_sha256    text NOT NULL CHECK (payload_sha256 ~ '^[a-f0-9]{64}$'),
  risk_level        text NOT NULL CHECK (risk_level IN ('low','medium','high')),
  policy_applied    text NOT NULL,
  requested_by      text NOT NULL,
  approver_role     text NOT NULL,
  -- {campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do payload_sha256} (E3)
  idempotency_key   text NOT NULL CHECK (idempotency_key ~ '^[^:]+:[^:]+:(g[1-4]|sampling):r[1-9][0-9]*:[a-f0-9]{12}$'),
  -- request_expires_at: prazo de resposta do pedido (criação + 72 h; imutável) = approval-request.expires_at.
  --   Passar do prazo sem decisão NÃO é aprovação nem veto: o pedido continua pendente (D3).
  -- decision_expires_at: janela de execução = decided_at + 72 h (APPROVAL_TTL_HOURS),
  --   gravada por gatilho no momento da decisão.
  request_expires_at  timestamptz NOT NULL,
  decision_expires_at timestamptz,
  decision          text CHECK (decision IN ('approved','approved_with_edits','rejected')),
  reviewer_ref      text,
  -- proveniência humana (D4): human-cli = humano roda approval_tools.py decide;
  -- human-chat-confirmed = sessão principal transcreve mensagem explícita do humano (citada em comments)
  human_attested    boolean,
  recorded_via      text CHECK (recorded_via IN ('human-cli','human-chat-confirmed')),
  decision_payload_sha256 text CHECK (decision_payload_sha256 ~ '^[a-f0-9]{64}$'),
  -- bound_to da decisão (E1): copiado do pedido pelo approval_tools.py decide
  bound_gate        text,
  bound_operation   text,
  bound_destination text,
  bound_channel     text,
  comments          text,
  decided_at        timestamptz,
  audit_trail       jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at        timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, idempotency_key),
  UNIQUE (business_id, asset_id, gate, round_n),
  -- a decisão só é válida se o hash decidido for o hash solicitado
  CONSTRAINT approvals_sha_match CHECK (
    decision IS NULL OR decision_payload_sha256 = payload_sha256
  ),
  -- a decisão só vale amarrada ao pedido: gate, operação, destino e canal iguais (bound_to, E1)
  CONSTRAINT approvals_bound_match CHECK (
    decision IS NULL OR (bound_gate = gate AND bound_operation = operation
                         AND bound_destination = destination AND bound_channel = channel)
  ),
  -- janela de execução = decided_at + 72 h (tolerância de 60 s), reverificada além do gatilho (E2)
  CONSTRAINT approvals_decision_window CHECK (
    decision IS NULL OR (decided_at <= now() + interval '60 seconds'
      AND abs(extract(epoch FROM (decision_expires_at - (decided_at + interval '72 hours')))) <= 60)
  ),
  -- human-chat-confirmed exige a citação literal do humano em comments (E2)
  CONSTRAINT approvals_chat_needs_comments CHECK (
    recorded_via IS DISTINCT FROM 'human-chat-confirmed' OR length(btrim(coalesce(comments, ''))) > 0
  ),
  -- gates sem execução externa usam channel 'internal'
  CONSTRAINT approvals_internal_channel CHECK (
    operation IN ('publish','send','run_ads','update_page') OR channel = 'internal'
  ),
  CONSTRAINT approvals_decision_complete CHECK (
    (decision IS NULL AND decided_at IS NULL AND decision_expires_at IS NULL
       AND human_attested IS NULL AND recorded_via IS NULL)
    OR (decision IS NOT NULL AND decided_at IS NOT NULL AND reviewer_ref IS NOT NULL
       AND decision_expires_at IS NOT NULL AND human_attested IS TRUE AND recorded_via IS NOT NULL)
  ),
  -- publish, send, run_ads e update_page sempre se referem a um ativo de copy
  CONSTRAINT approvals_external_needs_asset CHECK (
    operation NOT IN ('publish','send','run_ads','update_page') OR asset_type = 'copy-asset'
  ),
  -- operação interna (amostragem) usa o gate SAMPLING
  CONSTRAINT approvals_sampling_consistency CHECK (
    (gate = 'SAMPLING') = (operation = 'internal_use')
  )
);

-- ---------------------------------------------------------------------
-- publish_receipts  <->  contracts/publish-receipt
--                        .data/copy-squad/{business}/{campaign_id}/07-published/{asset_id}/
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.publish_receipts (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id        text NOT NULL,
  approval_id        uuid NOT NULL REFERENCES copy_squad.approvals(id),
  payload_sha256     text NOT NULL CHECK (payload_sha256 ~ '^[a-f0-9]{64}$'),
  destination        text NOT NULL,
  channel            text NOT NULL,
  -- PUBLISH_EXECUTORS = [human, main_session]; nenhum subagent executa ação externa (E4)
  executed_by        text NOT NULL CHECK (executed_by IN ('human','main_session')),
  executed_at        timestamptz NOT NULL,
  external_reference text,
  sha_match          boolean NOT NULL,
  approval_valid     boolean NOT NULL,
  not_expired        boolean NOT NULL,
  bound_match        boolean NOT NULL,
  verify_ok          boolean NOT NULL,        -- saída de approval_tools.py verify --for-execution
  counter_signed_by  text NOT NULL CHECK (counter_signed_by = 'copy-chief'),
  counter_signed_at  timestamptz NOT NULL,
  rollback_plan      text NOT NULL,
  outcome            text NOT NULL CHECK (outcome IN ('published','scheduled','handed_off','failed')),
  created_at         timestamptz NOT NULL DEFAULT now(),
  -- só pode haver recibo de sucesso se todas as verificações passaram
  CONSTRAINT receipts_verified CHECK (
    outcome = 'failed' OR (sha_match AND approval_valid AND not_expired AND bound_match AND verify_ok)
  )
);

-- ---------------------------------------------------------------------
-- proofs  <->  contracts/offer-canvas.proof_stack
--              .data/copy-squad/{business}/{campaign_id}/01-strategy/offer-canvas.json
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.proofs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id   text NOT NULL,
  campaign_uuid uuid REFERENCES copy_squad.campaigns(id),
  proof_id      text NOT NULL,
  type          text NOT NULL CHECK (type IN ('testimonial','case','data','demo','guarantee','certification','media')),
  summary       text NOT NULL,
  source        text NOT NULL,
  verified      boolean NOT NULL DEFAULT false,
  usage_rights  text NOT NULL DEFAULT 'unknown' CHECK (usage_rights IN ('granted','pending','unknown')),
  expires_at    date,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, proof_id)
);

-- ---------------------------------------------------------------------
-- performance_events  <->  contracts/performance-analysis (dados de entrada)
--                          .data/copy-squad/{business}/{campaign_id}/08-performance/
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.performance_events (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id   text NOT NULL,
  campaign_uuid uuid NOT NULL REFERENCES copy_squad.campaigns(id),
  copy_asset_id uuid REFERENCES copy_squad.copy_assets(id),
  channel       text NOT NULL,
  event_type    text NOT NULL,
  metric_name   text NOT NULL,
  metric_value  numeric NOT NULL,
  occurred_at   timestamptz NOT NULL,
  metadata      jsonb
);

-- ---------------------------------------------------------------------
-- learning_records  <->  contracts/learning-record
--                        .data/copy-squad/{business}/_library/learnings/{lrn-id}.json
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.learning_records (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id     text NOT NULL,
  artifact_id     text NOT NULL CHECK (artifact_id ~ '^lrn-[a-z0-9]+(-[a-z0-9]+)*$'),
  origin          text NOT NULL CHECK (origin IN ('cro','human_correction','campaign_debrief','qa_failure','customer_feedback')),
  learning_status text NOT NULL CHECK (learning_status IN ('approved','draft','rejected','testing')),
  applies_to      jsonb NOT NULL,
  document        jsonb NOT NULL,
  review_after    date,
  created_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, artifact_id)
);

-- ---------------------------------------------------------------------
-- handoffs  <->  handoffs.jsonl (contracts/handoff-envelope; append-only)
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.handoffs (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id             text NOT NULL,
  envelope_id             text NOT NULL CHECK (envelope_id ~ '^env-'),
  campaign_uuid           uuid REFERENCES copy_squad.campaigns(id),
  from_agent              text NOT NULL,
  to_agent                text NOT NULL,
  input_ids               jsonb NOT NULL DEFAULT '[]'::jsonb,
  output_id               text NOT NULL,
  artifact_type           text NOT NULL,
  artifact_path           text NOT NULL CHECK (artifact_path LIKE '.data/copy-squad/%'),
  status                  text NOT NULL CHECK (status IN ('ready','needs_input','needs_approval','blocked','failed')),
  confidence              numeric NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  assumptions             jsonb NOT NULL DEFAULT '[]'::jsonb,
  sources                 jsonb NOT NULL DEFAULT '[]'::jsonb,
  risk_level              text NOT NULL CHECK (risk_level IN ('low','medium','high')),
  human_approval_required boolean NOT NULL,
  gate                    text CHECK (gate IN ('G1','G2','G3','G4','G5','SAMPLING')),
  reason                  text,
  created_at              timestamptz NOT NULL,
  UNIQUE (business_id, envelope_id)
);

-- ---------------------------------------------------------------------
-- agent_runs  <->  _telemetry/agent-runs.jsonl (contracts/agent-run; append-only)
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.agent_runs (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id    text NOT NULL,
  run_id         text NOT NULL CHECK (run_id ~ '^run-'),
  campaign_uuid  uuid REFERENCES copy_squad.campaigns(id),
  agent_name     text NOT NULL,
  task           text NOT NULL,
  model          text NOT NULL,
  prompt_version text NOT NULL,
  input_ref      text NOT NULL,   -- referência, não o conteúdo bruto
  output_ref     text,
  tokens_in      integer,
  tokens_out     integer,
  cost_usd       numeric,
  latency_ms     integer,
  status         text NOT NULL CHECK (status IN ('success','failed','escalated','blocked')),
  error          text,
  started_at     timestamptz NOT NULL,
  finished_at    timestamptz,
  UNIQUE (business_id, run_id)
);

-- ---------------------------------------------------------------------
-- agent_evaluations  <->  _telemetry/agent-evaluations.jsonl
--                         (contracts/agent-evaluation; append-only)
-- ---------------------------------------------------------------------
CREATE TABLE copy_squad.agent_evaluations (
  id                       uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id               text NOT NULL,
  evaluation_id            text NOT NULL CHECK (evaluation_id ~ '^evl-'),
  agent_run_uuid           uuid NOT NULL REFERENCES copy_squad.agent_runs(id),
  agent_run_id             text NOT NULL CHECK (agent_run_id ~ '^run-'),   -- valor do contrato agent-evaluation
  agent_name               text NOT NULL,
  evaluator                text NOT NULL,
  layer                    text NOT NULL CHECK (layer IN ('quality','operational','business')),
  metric_name              text NOT NULL,
  score                    numeric NOT NULL,
  threshold                numeric,
  passed                   boolean NOT NULL,
  feedback                 text,
  seniority_level_observed text CHECK (seniority_level_observed IN ('junior','pleno','senior','lead','director')),
  created_at               timestamptz NOT NULL DEFAULT now(),
  UNIQUE (business_id, evaluation_id)
);

-- ---------------------------------------------------------------------
-- Índices (chaves estrangeiras e filtros mais comuns)
-- ---------------------------------------------------------------------
CREATE INDEX idx_campaigns_business          ON copy_squad.campaigns (business_id, status);
CREATE INDEX idx_briefs_campaign             ON copy_squad.briefs (campaign_uuid);
CREATE INDEX idx_briefs_business             ON copy_squad.briefs (business_id);
CREATE INDEX idx_research_packets_brief      ON copy_squad.research_packets (brief_uuid);
CREATE INDEX idx_angles_brief                ON copy_squad.angles (brief_uuid);
CREATE INDEX idx_copy_assets_campaign        ON copy_squad.copy_assets (campaign_uuid);
CREATE INDEX idx_copy_assets_brief           ON copy_squad.copy_assets (brief_uuid);
CREATE INDEX idx_copy_assets_angle           ON copy_squad.copy_assets (angle_uuid);
CREATE INDEX idx_copy_versions_asset         ON copy_squad.copy_versions (copy_asset_id, version DESC);
CREATE INDEX idx_approvals_asset             ON copy_squad.approvals (business_id, asset_id, gate, round_n);
CREATE INDEX idx_approvals_pending           ON copy_squad.approvals (business_id, request_expires_at) WHERE decision IS NULL;
CREATE INDEX idx_publish_receipts_approval   ON copy_squad.publish_receipts (approval_id);
CREATE INDEX idx_proofs_campaign             ON copy_squad.proofs (campaign_uuid);
CREATE INDEX idx_performance_events_campaign ON copy_squad.performance_events (campaign_uuid, occurred_at);
CREATE INDEX idx_performance_events_asset    ON copy_squad.performance_events (copy_asset_id);
CREATE INDEX idx_learning_records_status     ON copy_squad.learning_records (business_id, learning_status);
CREATE INDEX idx_handoffs_campaign           ON copy_squad.handoffs (campaign_uuid, created_at);
CREATE INDEX idx_agent_runs_campaign         ON copy_squad.agent_runs (campaign_uuid, started_at);
CREATE INDEX idx_agent_runs_agent            ON copy_squad.agent_runs (business_id, agent_name, started_at DESC);
CREATE INDEX idx_agent_evaluations_run       ON copy_squad.agent_evaluations (agent_run_uuid);

-- ---------------------------------------------------------------------
-- Row Level Security: habilitado em TODAS as tabelas.
-- Políticas de exemplo: o negócio da sessão deve coincidir com business_id.
-- Revisar com o @data-engineer (papéis, USING/WITH CHECK e auth do provedor).
-- ---------------------------------------------------------------------
ALTER TABLE copy_squad.campaigns          ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.briefs             ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.research_packets   ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.angles             ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.copy_assets        ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.copy_versions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.approvals          ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.publish_receipts   ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.proofs             ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.performance_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.learning_records   ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.handoffs           ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.agent_runs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE copy_squad.agent_evaluations  ENABLE ROW LEVEL SECURITY;

-- Exemplo para tabelas mutáveis (leitura e escrita dentro do próprio negócio)
CREATE POLICY campaigns_tenant ON copy_squad.campaigns
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY briefs_tenant ON copy_squad.briefs
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY research_packets_tenant ON copy_squad.research_packets
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY angles_tenant ON copy_squad.angles
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY copy_assets_tenant ON copy_squad.copy_assets
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY proofs_tenant ON copy_squad.proofs
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY performance_events_tenant ON copy_squad.performance_events
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY learning_records_tenant ON copy_squad.learning_records
  USING (business_id = copy_squad.current_business_id())
  WITH CHECK (business_id = copy_squad.current_business_id());

-- Exemplo para tabelas append-only (SELECT e INSERT; sem UPDATE nem DELETE)
CREATE POLICY copy_versions_select ON copy_squad.copy_versions FOR SELECT
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY copy_versions_insert ON copy_squad.copy_versions FOR INSERT
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY handoffs_select ON copy_squad.handoffs FOR SELECT
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY handoffs_insert ON copy_squad.handoffs FOR INSERT
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY agent_runs_select ON copy_squad.agent_runs FOR SELECT
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY agent_runs_insert ON copy_squad.agent_runs FOR INSERT
  WITH CHECK (business_id = copy_squad.current_business_id());

CREATE POLICY agent_evaluations_select ON copy_squad.agent_evaluations FOR SELECT
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY agent_evaluations_insert ON copy_squad.agent_evaluations FOR INSERT
  WITH CHECK (business_id = copy_squad.current_business_id());

-- approvals: o squad (copy_squad_app) cria o pedido (somente INSERT e SELECT) e só o papel do
-- aprovador humano (copy_squad_approver) grava a decisão (UPDATE restrito por papel, não só por
-- business_id). O runtime de IA nunca decide. O payload, o hash, o destino e a operação nunca mudam
-- depois de criados. A decisão só é gravada com human_attested e recorded_via (D4).
-- Atenção: o prazo de resposta (request_expires_at) NÃO bloqueia a decisão tardia por silêncio;
-- a política abaixo apenas exige que o pedido ainda esteja pendente.
CREATE POLICY approvals_select ON copy_squad.approvals FOR SELECT
  TO copy_squad_app, copy_squad_approver
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY approvals_insert ON copy_squad.approvals FOR INSERT
  TO copy_squad_app
  WITH CHECK (business_id = copy_squad.current_business_id() AND decision IS NULL);
CREATE POLICY approvals_decide ON copy_squad.approvals FOR UPDATE
  TO copy_squad_approver
  USING (business_id = copy_squad.current_business_id() AND decision IS NULL)
  WITH CHECK (business_id = copy_squad.current_business_id() AND human_attested IS TRUE);

-- publish_receipts: somente INSERT e SELECT
CREATE POLICY publish_receipts_select ON copy_squad.publish_receipts FOR SELECT
  USING (business_id = copy_squad.current_business_id());
CREATE POLICY publish_receipts_insert ON copy_squad.publish_receipts FOR INSERT
  TO copy_squad_app
  WITH CHECK (business_id = copy_squad.current_business_id());

-- ---------------------------------------------------------------------
-- Imutabilidade do pedido: gatilho que congela payload, payload_sha256, destination,
-- operation, channel, gate, round_n, risk_level, request_expires_at, idempotency_key e o alvo
-- (asset_type, asset_ref, asset_id) depois da criação do pedido; bloqueia mudança após a
-- decisão; e grava decision_expires_at = decided_at + 72 horas no momento da decisão.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION copy_squad.approvals_immutable_payload()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF NEW.payload IS DISTINCT FROM OLD.payload
     OR NEW.payload_sha256 IS DISTINCT FROM OLD.payload_sha256
     OR NEW.request_expires_at IS DISTINCT FROM OLD.request_expires_at
     OR NEW.idempotency_key IS DISTINCT FROM OLD.idempotency_key
     OR NEW.destination IS DISTINCT FROM OLD.destination
     OR NEW.channel IS DISTINCT FROM OLD.channel
     OR NEW.operation IS DISTINCT FROM OLD.operation
     OR NEW.gate IS DISTINCT FROM OLD.gate
     OR NEW.round_n IS DISTINCT FROM OLD.round_n
     OR NEW.risk_level IS DISTINCT FROM OLD.risk_level
     OR NEW.asset_type IS DISTINCT FROM OLD.asset_type
     OR NEW.asset_ref IS DISTINCT FROM OLD.asset_ref
     OR NEW.asset_id IS DISTINCT FROM OLD.asset_id THEN
    RAISE EXCEPTION 'approvals: payload, hash, destino, canal, operação, gate, rodada, risco, alvo, idempotency_key e request_expires_at são imutáveis';
  END IF;
  IF OLD.decision IS NOT NULL THEN
    RAISE EXCEPTION 'approvals: decisão já registrada; mudança exige nova rodada (novo pedido)';
  END IF;
  -- a janela de execução de 72h conta a partir da decisão (APPROVAL_TTL_HOURS), nunca da criação do pedido
  IF NEW.decision IS NOT NULL THEN
    NEW.decision_expires_at := NEW.decided_at + interval '72 hours';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_approvals_immutable_payload
  BEFORE UPDATE ON copy_squad.approvals
  FOR EACH ROW EXECUTE FUNCTION copy_squad.approvals_immutable_payload();

-- ---------------------------------------------------------------------
-- Validação do recibo de publicação: a aprovação referenciada precisa estar
-- decidida como approved (approved_with_edits NUNCA autoriza execução, D2), com o mesmo hash,
-- destino e negócio, operação externa e dentro da janela de execução (decision_expires_at).
-- Os booleanos do recibo são derivados aqui, não autodeclarados pelo runtime.
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION copy_squad.publish_receipts_validate()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  a copy_squad.approvals%ROWTYPE;
BEGIN
  SELECT * INTO a FROM copy_squad.approvals WHERE id = NEW.approval_id;
  IF NOT FOUND OR a.business_id <> NEW.business_id THEN
    RAISE EXCEPTION 'publish_receipts: aprovação inexistente ou de outro negócio';
  END IF;
  NEW.sha_match      := (a.payload_sha256 = NEW.payload_sha256 AND a.decision_payload_sha256 = NEW.payload_sha256);
  NEW.approval_valid := (a.decision = 'approved' AND a.human_attested IS TRUE
                         AND a.gate = 'G4' AND a.risk_level <> 'low'
                         AND a.destination = NEW.destination
                         AND a.operation IN ('publish','send','run_ads','update_page'));
  NEW.bound_match    := (a.bound_gate = a.gate AND a.bound_operation = a.operation
                         AND a.bound_destination = NEW.destination AND a.bound_channel = NEW.channel
                         AND a.channel = NEW.channel);
  NEW.not_expired    := (a.decision_expires_at IS NOT NULL AND a.decision_expires_at > now());
  IF NEW.outcome <> 'failed' AND NOT (NEW.sha_match AND NEW.approval_valid AND NEW.not_expired AND NEW.bound_match AND NEW.verify_ok) THEN
    RAISE EXCEPTION 'publish_receipts: aprovação inválida, hash divergente, amarração (bound_to) divergente ou expirada';
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_publish_receipts_validate
  BEFORE INSERT ON copy_squad.publish_receipts
  FOR EACH ROW EXECUTE FUNCTION copy_squad.publish_receipts_validate();

-- ---------------------------------------------------------------------
-- Fim da proposta. NÃO APLICAR sem revisão do @data-engineer e aprovação humana.
-- Trocar COMMIT por ROLLBACK em qualquer teste em ambiente de desenvolvimento.
-- ---------------------------------------------------------------------
ROLLBACK;
