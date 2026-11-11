# Proposta de banco de dados — copy-squad

> **Status: NÃO APLICADO.** Este documento descreve uma proposta. Nenhum banco foi criado, migrado ou alterado. A fonte de verdade do squad é, hoje, o filesystem em `.data/copy-squad/`. O SQL proposto está em `docs/proposed-migration.sql` e começa com o aviso "PROPOSTA — NÃO APLICAR sem revisão do @data-engineer e aprovação humana". O modelo de aprovação segue o ADR-001 (`docs/governance-decisions.md`), que prevalece em caso de conflito.

## 1. Por que o filesystem é a fonte de verdade agora

| Motivo | Detalhe |
|---|---|
| Auditabilidade | Cada artefato é um arquivo JSON versionado (v1, v2, ...) que pode ser lido, comparado e arquivado |
| Contratos já validados | Os schemas em `contracts/*.schema.json` validam cada arquivo sem depender de banco |
| Isolamento simples | A pasta `{business}` separa unidades de negócio sem política de acesso adicional |
| Custo zero de infraestrutura | Nenhum serviço, credencial ou migração a operar na fase inicial |
| Imutabilidade natural | Drafts nunca são sobrescritos; logs são append-only |
| Alinhamento com a governança do repositório | O workspace é somente leitura para o squad; o runtime fica em `.data/` (gitignorado) |

O banco, quando existir, será um **espelho reativo** do filesystem para consulta, relatórios e escala. Ele não substitui a fonte de verdade sem decisão humana explícita.

## 2. Mapeamento tabela, contrato e caminho

| Tabela proposta (`copy_squad.*`) | Contrato JSON | Caminho em `.data/copy-squad/{business}/` |
|---|---|---|
| `campaigns` | `execution-plan`, `demand-intake` | `{campaign_id}/00-intake/` |
| `briefs` | `brief` | `{campaign_id}/01-strategy/brief.json` |
| `research_packets` | `research-packet` | `{campaign_id}/02-research/research-packet.json` |
| `angles` | `angles` | `{campaign_id}/03-angles/angles.json` |
| `copy_assets` | `conversion-copy`, `content-piece`, `ux-copy`, `video-script`, `email-journey` | `{campaign_id}/04-drafts/{asset_id}/` |
| `copy_versions` | os mesmos contratos de ativo, uma linha por versão | `{campaign_id}/04-drafts/{asset_id}/v{n}.json` |
| `approvals` | `approval-request` e `approval-decision`, para qualquer gate (G1 a G4 e `SAMPLING`) | `{campaign_id}/06-approval/_campaign/{gate}-r{n}/` (G1, G2, G3 de oferta; `asset_id = campaign_id`) e `{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/` (G3 de texto, G4) e `.../{asset_id}/sampling-r{n}/` (amostragem); `{gate}` sempre em minúsculas |
| `publish_receipts` | `publish-receipt` | `{campaign_id}/07-published/{asset_id}/publish-receipt.json` |
| `proofs` | `offer-canvas` (campo `proof_stack`) | `{campaign_id}/01-strategy/offer-canvas.json` |
| `performance_events` | dados de entrada de `performance-analysis` | `{campaign_id}/08-performance/` |
| `learning_records` | `learning-record` | `_library/learnings/{lrn-id}.json` |
| `handoffs` | `handoff-envelope` | `{campaign_id}/handoffs.jsonl` |
| `agent_runs` | `agent-run` | `.data/copy-squad/_telemetry/agent-runs.jsonl` |
| `agent_evaluations` | `agent-evaluation` | `.data/copy-squad/_telemetry/agent-evaluations.jsonl` |

Observações do mapeamento:

- A pesquisa original previa 11 tabelas. Esta proposta adiciona `publish_receipts`, `learning_records` e `handoffs` para refletir contratos que o squad já produz.
- Em cada tabela, a coluna `document` (jsonb) guarda o contrato completo como espelho; as colunas tipadas existem para filtro e relatório. Em `approvals`, o `payload` e as colunas da decisão espelham os dois contratos.
- `approvals` é genérica: o alvo é `asset_type` + `asset_ref` (brief, conjunto de ângulos, offer-canvas, compliance-review, ativo de copy ou amostra), sem FK obrigatória a `copy_assets`, para que G1, G2 e G3 também possam ser gravados. Cada pedido é uma rodada (`round_n`, equivalente a `{gate}-r{n}`, com o gate em minúsculas na pasta). Nos gates de campanha (G1, G2, G3 de oferta), `asset_id = campaign_id`. O pedido traz `channel` e a decisão traz `bound_to` (`bound_gate`, `bound_operation`, `bound_destination`, `bound_channel`).
- `learning_records.origin` inclui `customer_feedback`, e `copy_assets.format` segue os enums por contrato (VSL em `video-script`; `case_study`, `white_paper`, `manifesto` e `tagline` em `content-piece`).
- `business_id` aparece em todas as tabelas; no filesystem, equivale ao primeiro nível `{business}`.
- Telemetria guarda referências (`input_ref`, `output_ref`), nunca conteúdo bruto de clientes.

## 3. Quando migrar

Considerar a migração quando pelo menos um destes sinais aparecer de forma recorrente:

1. Mais de um operador precisa consultar o mesmo acervo ao mesmo tempo (concorrência).
2. Relatórios entre campanhas (por exemplo, desempenho de ângulos por canal) ficam lentos ou manuais.
3. A biblioteca (`_library/index.jsonl`) passa de poucos milhares de ativos e a busca por arquivo deixa de ser prática.
4. Há necessidade de aprovação em interface web com autenticação por usuário.
5. Existe exigência de retenção, backup ou auditoria que o filesystem não cobre.

Enquanto nenhum sinal aparecer, mantenha o filesystem.

## 4. Requisitos obrigatórios antes de qualquer aplicação

| Requisito | Detalhe |
|---|---|
| Revisão do `@data-engineer` | DDL, índices, constraints, políticas e estratégia de migração |
| Aprovação humana | Decisão explícita do responsável; sem aplicação automática |
| Banco oficial | O projeto de banco deve ser o autorizado pela governança da unidade; não usar bancos proibidos ou de terceiros |
| `business_id` em todas as tabelas | Isolamento por unidade de negócio (equivalente a tenant) |
| Row Level Security habilitada | Em todas as tabelas, com políticas por `business_id` |
| Papel com escopo mínimo | Papel dedicado para o runtime, apenas com os privilégios necessários |
| Sem bypass de RLS | Nenhum papel de runtime com `BYPASSRLS`; nunca usar o papel administrativo |
| Segredos fora do repositório | Credenciais em cofre ou variáveis de ambiente; nunca em arquivo versionado |
| Avisos de segurança e desempenho | Executar após aplicar e corrigir achados |
| Plano de backfill e de rollback | Importar o histórico a partir de `.data/copy-squad/` e saber desfazer |
| Teste de isolamento | Provar que um `business_id` não lê dados de outro |

## 5. Regras de negócio refletidas no schema

- **Versões imutáveis:** `copy_versions` aceita apenas INSERT.
- **Payload aprovado imutável:** gatilho congela `payload`, `payload_sha256`, `destination`, `operation`, `gate`, `round_n`, `risk_level`, o alvo (`asset_type`, `asset_ref`, `asset_id`), `request_expires_at`, `channel` e `idempotency_key` após a criação, e bloqueia qualquer mudança depois da decisão (mudar exige nova rodada). Uma restrição exige que o hash decidido seja igual ao hash solicitado. O hash é `sha256` do JSON canônico do `payload` com `ensure_ascii=False`, calculado por `scripts/approval_tools.py hash`, nunca pelo banco nem por um modelo.
- **Decisão só pelo papel aprovador:** o UPDATE da decisão é restrito por papel (`copy_squad_approver`), não apenas por `business_id`; o papel do runtime de IA (`copy_squad_app`) só faz INSERT e SELECT. A decisão exige `human_attested = true` e `recorded_via` (`human-cli` ou `human-chat-confirmed`).
- **Só `approved` autoriza execução:** `approved_with_edits` nunca libera publicação; abre a rodada seguinte com novo hash (D2). O recibo valida isso no banco.
- **Idempotência:** `idempotency_key` no formato `{campaign_id}:{asset_id}:{gate em minúsculas}:r{n}:{12 primeiros hex do payload_sha256}` (validado por `CHECK`); `UNIQUE (business_id, idempotency_key)` evita execução dupla; `UNIQUE (business_id, asset_id, gate, round_n)` identifica cada rodada.
- **Prazos em dois momentos (D3):** `request_expires_at` (criação + 72 horas) é o prazo de resposta e não gera veto por silêncio; `decision_expires_at` é gravado por gatilho como `decided_at` + 72 horas e é a janela de execução usada pelo recibo; uma restrição `CHECK` reverifica `decision_expires_at = decided_at + 72h` (tolerância de 60 s). O gatilho do recibo também confere `bound_*` contra o pedido.
- **Recibo verificado:** `publish_receipts` só admite sucesso quando `sha_match`, `approval_valid` e `not_expired` são verdadeiros; os três são derivados pelo banco a partir da aprovação (decisão `approved`, hash, destino e operação externa iguais, dentro da janela de execução), não autodeclarados.
- **Telemetria append-only:** `agent_runs`, `agent_evaluations` e `handoffs` aceitam apenas INSERT e SELECT.

## 6. Estratégia de migração sugerida (para quando aprovada)

1. **Fase 0, desenho:** revisão do SQL pelo `@data-engineer`; ajuste de nomes e tipos.
2. **Fase 1, ambiente de teste:** aplicar em ambiente descartável; rodar teste de isolamento.
3. **Fase 2, backfill:** importar os arquivos existentes, comparando contagens e hashes com o filesystem.
4. **Fase 3, dupla escrita:** o squad grava em filesystem e banco; o filesystem continua como fonte de verdade.
5. **Fase 4, reconciliação:** relatório periódico de divergências entre filesystem e banco.
6. **Fase 5, decisão humana:** só então avaliar se o banco passa a ser fonte de verdade para algum subconjunto.

## 7. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Vazamento entre negócios | RLS por `business_id` e teste de isolamento obrigatório |
| Divergência entre arquivo e banco | Dupla escrita com reconciliação; filesystem prevalece |
| Dados pessoais de clientes no banco | Minimização; classificar campos; seguir LGPD; telemetria sem conteúdo bruto |
| Alteração de payload após aprovação | Gatilho de imutabilidade e verificação de sha256 por `approval_tools.py verify` (`copy-publisher`, com contra-assinatura do `copy-chief`) |
| Decisão gravada por agente de IA | Papel aprovador separado, `human_attested` e `recorded_via` obrigatórios; endurecimento recomendado fora do banco: hook que bloqueie escrita de agentes em `approval-decision.json` |
| Uso de papel administrativo em runtime | Papel dedicado sem `BYPASSRLS`; revisão de permissões trimestral |

## 8. Decisão atual

| Item | Estado |
|---|---|
| Fonte de verdade | Filesystem (`.data/copy-squad/`) |
| SQL | Proposto em `docs/proposed-migration.sql` (termina em ROLLBACK de propósito) |
| Aplicação | **Não aplicada** |
| Próximo passo | Revisão do `@data-engineer` e aprovação humana, quando algum sinal da seção 3 ocorrer |
