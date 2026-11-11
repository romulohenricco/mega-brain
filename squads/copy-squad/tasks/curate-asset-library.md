---
task: curate-asset-library
name: curate-asset-library
task_name: "Curar biblioteca de ativos"
version: "1.0.0"
squad: copy-squad
task_id: curate-asset-library
category: intelligence
difficulty: intermediate
responsavel: '@knowledge-curator'
responsavel_type: Worker
responsible_executor: knowledge-curator
execution_type: Worker
atomic_layer: Molecule
elicit: false
estimated_time: 15-30min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: ativos_novos_ou_alterados
  tipo: lista de caminhos em .data/copy-squad/{business}/{campaign_id}/
  obrigatorio: true
- campo: approval_decisions
  tipo: contract:approval-decision
  obrigatorio: false
Saida:
- campo: index_jsonl
  tipo: arquivo JSONL (uma linha por ativo)
  persistido_em: .data/copy-squad/{business}/_library/index.jsonl
input: [ativos, approval-decision, learning-record]
output: [index.jsonl]
action_items:
  - "Fixar o negócio e listar os ativos a curar"
  - "Verificar procedência (fonte, data, autor, versão, status)"
  - "Classificar por campanha, oferta, público, canal, formato e resultado"
  - "Definir asset_status a partir do approval-decision"
  - "Acrescentar ou versionar linhas em index.jsonl"
  - "Detectar duplicidades e arquivos órfãos"
  - "Relatar divergências e sugerir ingestão opcional no Mega Brain"
acceptance_criteria:
  - "Uma linha JSON válida por ativo, sem linhas quebradas"
  - "Campos obrigatórios presentes em 100% das linhas (veja Saída)"
  - "Nenhum ativo approved sem approval-decision com decision == approved e payload_sha256 conferido pelo script"
  - "Todas as linhas com source_path dentro de .data/copy-squad/{business}/"
  - "Nenhuma linha anterior removida ou sobrescrita; novas versões acrescentadas"
  - "Duplicidades e órfãos relatados"
  - "Score do checklists/knowledge-entry-checklist.md >= 0.80"
pre_condition: "Negócio definido; ativos finalizados em 04-drafts, 05-review ou 06-approval disponíveis; approval-decision lido quando houver"
post_condition: "index.jsonl atualizado, relatório de curadoria produzido, divergências listadas para o copy-chief"
checklist: checklists/knowledge-entry-checklist.md
quality_gate: null
human_gate: null
skill: null
workflows: [wf-copy-production, wf-campaign-launch]
performance:
  error_handling: "Ativo sem procedência completa entra como draft com campos ausentes listados; índice nunca é truncado; qualquer falha de escrita interrompe e preserva o arquivo anterior"
---

# Task: Curar biblioteca de ativos

## Objetivo

Manter a Asset Library de cada negócio organizada e pesquisável. A task classifica os ativos produzidos pelo squad (provas, ângulos vencedores, headlines, CTAs, e-mails, páginas, roteiros, textos de interface, aprendizados) em `index.jsonl`, preservando fonte, data, autor, versão e status, e separando aprovado, rascunho, reprovado e em teste. É a base do reuso e do `retrieve-knowledge`.

## Quando usar / quando não usar

**Usar quando:**
- Um ativo recebeu `approval-decision` e deve entrar (ou mudar de status) na biblioteca.
- Uma campanha terminou e é preciso consolidar os ativos finais.
- O índice está desatualizado ou inconsistente (use o comando `*reindex`).
- Um aprendizado novo foi gravado e precisa constar no índice.

**Não usar quando:**
- O item é um aprendizado a ser redigido (use `register-learning`).
- A tarefa é consultar (use `retrieve-knowledge`).
- O ativo ainda está em produção ativa e não foi submetido a revisão (aguarde, ou indexe como `draft` apenas se solicitado).
- O pedido cruza dois negócios.

## Entradas

| Campo | Contrato / formato | Obrigatório | Origem |
|---|---|---|---|
| ativos_novos_ou_alterados | caminhos de JSON de contratos de copy (`conversion-copy`, `content-piece`, `ux-copy`, `video-script`, `email-journey`, `angles`) | Sim | `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` |
| approval_decisions | `contract:approval-decision` | Recomendado | `.data/copy-squad/{business}/{campaign_id}/06-approval/{asset_id}/{gate}-r{n}/approval-decision.json` (minúsculas, ex.: `g4-r1`; `_campaign/` para G1, G2 e G3 de oferta) |
| publish_receipts | `contract:publish-receipt` | Não | `.data/copy-squad/{business}/{campaign_id}/07-published/{asset_id}/` |
| learnings | `contract:learning-record` | Não | `.data/copy-squad/{business}/_library/learnings/` |
| índice atual | JSONL | Sim (leitura, se existir) | `.data/copy-squad/{business}/_library/index.jsonl` |

## Passos

1. **Fixar o negócio.** Confirme `business` e que todos os caminhos estão dentro de `.data/copy-squad/{business}/`. Caso contrário, recuse (CS-KC-001).
2. **Carregar o índice.** Leia `index.jsonl` (se não existir, será criado). Valide que cada linha é JSON bem formado; reporte linhas corrompidas sem apagá-las.
3. **Listar os ativos.** Para cada caminho da entrada, abra o arquivo e extraia `meta` (artifact_id, tipo, versão, produzido por, data, campanha, sources).
4. **Verificar procedência.** Exija fonte (`sources` ou origem do dado), data (`produced_at`), autor (`produced_by`), versão (`version`) e status. Falta de qualquer campo rebaixa o item para `draft` com a lista de campos ausentes.
5. **Definir `asset_status`.** `approved` somente se existir `approval-decision` com `decision == approved` (nunca `approved_with_edits`: com edições há nova rodada) e `payload_sha256` igual ao do `approval-request` e ao hash recalculado pelo script (`python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>`; nunca calculado de cabeça). O TTL de 72 h limita a execução externa, não a permanência do ativo `approved` na biblioteca; novo uso externo após o prazo exige nova rodada; `testing` se estiver em teste A/B registrado; `rejected` se `decision = rejected` ou veto de revisão; `draft` nos demais casos.
6. **Classificar.** Preencha `campaign_id`, oferta, público, canal, formato, tipo (`proof`, `angle`, `email`, `landing`, `script`, `insight`, `learning`, `voice`, `ux`, `content`; headline, CTA e anúncio entram como `content`, `ux` ou `landing` conforme a origem, com o detalhe no campo `format`) e resultado conhecido (resumo da performance quando houver `performance-analysis`).
7. **Calcular o hash do conteúdo.** Registre `content_sha256` calculado por `python squads/copy-squad/scripts/approval_tools.py content-hash <arquivo.json>` (sha256 do JSON canônico, mesma serialização do D1; único método de `content_sha256`, nunca calculado de cabeça) para detectar alterações posteriores e duplicidades. Não confunda com `payload_sha256` da aprovação.
8. **Montar a linha do índice.** Um objeto JSON por linha com os campos abaixo.
9. **Versionar, não sobrescrever.** Se o `asset_id` já existir, acrescente nova linha com versão maior e marque a anterior como `superseded: true` em nova linha de atualização (append-only); o consumidor sempre lê a última linha por `asset_id`.
10. **Detectar duplicidades e órfãos.** Mesmo `content_sha256` com `asset_id` diferente indica duplicidade; arquivo da biblioteca sem linha no índice, ou linha apontando para arquivo inexistente, indica órfão. Relate; não apague.
11. **Aplicar o checklist.** Use `checklists/knowledge-entry-checklist.md` (procedência, isolamento, status, formato do índice).
12. **Relatar.** Produza resumo: ativos indexados por status, itens rebaixados com motivo, duplicidades, órfãos e sugestões. Se o humano pediu, inclua a sugestão de ingestão: "Para levar ao conhecimento de negócio do Mega Brain, execute /ingest-empresa com o ativo `{caminho}` do negócio `{business}`." Não execute.

## Saída

Formato de cada linha de `.data/copy-squad/{business}/_library/index.jsonl` (campos mínimos):

```json
{
  "asset_id": "cvc-exemplo-headline-a",
  "title": "Título descritivo do ativo",
  "type": "content",
  "asset_status": "approved",
  "campaign_id": "camp-exemplo",
  "offer": "oferta resumida",
  "audience": "público resumido",
  "channel": "canal",
  "format": "formato",
  "result": "resumo do resultado conhecido ou 'sem dados'",
  "source_path": ".data/copy-squad/{business}/camp-exemplo/04-drafts/cvc-exemplo-headline-a/v2.json",
  "sources": ["origem do dado, quando houver"],
  "author": "conversion-copywriter",
  "date": "2026-11-10",
  "version": 2,
  "content_sha256": "64 caracteres hexadecimais",
  "approval_decision_id": "apd-exemplo",
  "missing_fields": [],
  "updated_at": "2026-11-10T12:00:00Z"
}
```

- **Persistência:** `.data/copy-squad/{business}/_library/index.jsonl` (append-only).
- **Relatório:** devolvido ao solicitante e, se houver campanha, registrado via envelope.
- **Envelope de handoff:** `from_agent: knowledge-curator`; `to_agent: copy-chief`; `artifact_type: knowledge-query-result` (relatório de índice) ou o resumo textual; `status: ready`; `human_approval_required: false`.

## Acceptance Criteria (Critérios de aceite)

- Todas as linhas são JSON válidos e contêm os campos mínimos.
- `asset_status = approved` sempre com `approval_decision_id` válido.
- Nenhuma linha anterior alterada ou removida.
- Itens com procedência incompleta rebaixados e listados.
- Duplicidades, órfãos e linhas corrompidas relatados.
- Todos os caminhos dentro do diretório do negócio.

## Quality gate e checklist

- **Checklist:** `checklists/knowledge-entry-checklist.md`.
- **Quality gate:** sem QG próprio; a verificação é pelo checklist (APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60).
- **Veto:** ativo approved sem decisão; mistura de negócios; sobrescrita de linhas.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| `index.jsonl` inexistente | Criar com a primeira linha e relatar a criação |
| Linha corrompida no índice | Preservar, relatar e continuar com as demais |
| `approval-decision` expirado (janela de execução de 72 horas, `expires_at`) | Manter o ativo no índice e sinalizar que novo uso externo exige nova rodada de aprovação |
| `payload_sha256` da decisão diferente do request ou do hash recalculado pelo script | Marcar divergência, não promover a approved, escalar ao `copy-chief` |
| Ativo de outro negócio na lista | Recusar o item e relatar |
| Falha de escrita | Interromper, preservar o arquivo anterior e reportar |

## Handoff

- **Para `copy-chief`:** relatório de curadoria e divergências que exigem decisão.
- **Para consumidores:** a biblioteca atualizada passa a responder em `retrieve-knowledge`.
- Sugestão opcional de ingestão no Mega Brain via `/ingest-empresa`, apenas como texto.

## Exemplo

Entrada resumida (exemplo ilustrativo): campanha de captação encerrada; três ativos finalizados: uma landing page com `approval-decision` aprovado, um e-mail em teste A/B e um anúncio reprovado no compliance.

Trecho do resultado:

```json
{"asset_id":"cvc-lp-captacao","title":"Landing de captação da mentoria (exemplo ilustrativo)","type":"landing","asset_status":"approved","campaign_id":"camp-captacao-q4","offer":"mentoria de gestão financeira","audience":"donos de pequenas empresas","channel":"página","format":"landing_page","result":"sem dados","source_path":".data/copy-squad/exemplo-negocio/camp-captacao-q4/04-drafts/cvc-lp-captacao/v3.json","author":"conversion-copywriter","date":"2026-11-08","version":3,"approval_decision_id":"apd-lp-captacao","missing_fields":[]}
{"asset_id":"eml-nutricao-02","title":"E-mail de nutrição 2 (exemplo ilustrativo)","type":"email","asset_status":"testing","campaign_id":"camp-captacao-q4","offer":"mentoria de gestão financeira","audience":"leads frios","channel":"e-mail","format":"e-mail de nutrição","result":"teste A/B em andamento","source_path":".data/copy-squad/exemplo-negocio/camp-captacao-q4/04-drafts/eml-nutricao-02/v2.json","author":"email-crm-copywriter","date":"2026-11-09","version":2,"approval_decision_id":"apd-eml-02","missing_fields":[]}
{"asset_id":"cvc-ad-promessa","title":"Anúncio com promessa de resultado (exemplo ilustrativo)","type":"content","asset_status":"rejected","campaign_id":"camp-captacao-q4","offer":"mentoria de gestão financeira","audience":"donos de pequenas empresas","channel":"anúncio pago","format":"ad","result":"reprovado por claim não verificado","source_path":".data/copy-squad/exemplo-negocio/camp-captacao-q4/04-drafts/cvc-ad-promessa/v1.json","author":"conversion-copywriter","date":"2026-11-07","version":1,"approval_decision_id":null,"missing_fields":[]}
```

## Anti-padrões

- Indexar sem verificar `approval-decision`.
- Sobrescrever ou apagar linhas existentes.
- Misturar ativos de negócios diferentes.
- Ignorar ativos reprovados (eles evitam repetição de erros).
- Deixar de relatar duplicidades e órfãos.
- Classificar sem oferta, público, canal e formato.
- Executar ingestão em outro sistema sem pedido humano.
