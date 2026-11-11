---
task: manage-versions
name: manage-versions
task_name: "Gerenciar versões e changelog de ativos"
version: "1.0.0"
squad: copy-squad
task_id: manage-versions
category: operations
difficulty: basic
responsavel: '@copy-publisher'
responsavel_type: Worker
responsible_executor: copy-publisher
execution_type: Worker
atomic_layer: Molecule
elicit: false
estimated_time: 5-10min
model: haiku
status: pending
domain: tactical
Entrada:
- campo: asset_id
  tipo: string
  obrigatorio: true
- campo: nova_versao
  tipo: artefato de contrato de produção ou edição
  obrigatorio: true
- campo: motivo_da_mudanca
  tipo: texto
  obrigatorio: true
Saida:
- campo: changelog
  tipo: arquivo changelog.jsonl (append-only)
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/changelog.jsonl
input: [asset_id, nova versão, motivo]
output: [changelog.jsonl]
action_items:
  - "Descobrir a versão corrente"
  - "Gravar v{n+1} sem sobrescrever"
  - "Registrar changelog com autor, motivo e hash"
  - "Marcar versões superadas e a versão em aprovação"
  - "Gerar diff resumido quando solicitado"
acceptance_criteria:
  - "nenhuma versão anterior sobrescrita ou removida"
  - "numeração sequencial sem lacunas (v1, v2, v3)"
  - "cada linha do changelog tem version, changed_by, change_reason, content_sha256 e at"
  - "versão em aprovação identificada e imutável"
  - "changelog append-only"
pre_condition: "existe um artefato a versionar com asset_id definido"
post_condition: "nova versão gravada, changelog atualizado e versão corrente identificada"
checklist: checklists/publish-preflight-checklist.md
quality_gate: QG-PUBLISH-PREFLIGHT
human_gate: null
skill: null
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "se a versão corrente estiver em aprovação, gravar como nova versão sem alterar a aprovada; se o arquivo existir, nunca sobrescrever e abortar com erro"
---

# Task: Gerenciar versões e changelog de ativos

## Objetivo

Garantir histórico auditável de cada ativo de copy. Toda alteração de um rascunho cria uma nova versão (`v1`, `v2`, `v3`...), nunca sobrescreve a anterior, e deixa uma linha de changelog com autor, motivo e hash do conteúdo. A task é determinística (Worker) e consolida o papel de Version Control do organograma original. Ela garante que a versão em aprovação seja a mesma que será entregue, apoiando a regra de imutabilidade do payload aprovado.

## Quando usar / quando não usar

| Usar | Não usar |
|---|---|
| Um agente produz uma nova versão de um ativo (draft, edição, localização) | Para decidir qual versão publicar (decisão humana, com o sha) |
| Após `approved_with_edits`, antes de reemitir o pedido | Para apagar versões antigas (proibido) |
| Pedido de diff ou histórico de um ativo | Para editar o conteúdo |
| Rework por veto de quality gate | Para versionar arquivos de código do repositório (git é do @devops) |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| asset_id | string estável entre versões, sem sufixo de versão (ex.: `cvc-camp-x-001`) | sim | agente produtor |
| nova versão | `conversion-copy`, `content-piece`, `ux-copy`, `video-script` ou `email-journey` | sim | agente produtor ou `copy-editor` |
| motivo da mudança | texto | sim | quem gerou a versão |
| changed_by | id do agente ou do humano | sim | contexto |
| estado de aprovação | `approval-request`/`approval-decision` | não | `06-approval/{asset_id}/{gate}-r{n}/` (`{gate}` em minúsculas) |

## Passos

1. **Descobrir a versão corrente**: liste `04-drafts/{asset_id}/` e identifique o maior `v{n}`; se não houver, a nova será `v1`.
2. **Checar estado de aprovação**: se existir `approval-request` pendente ou decisão `approved` (maior rodada) para a versão corrente, marque-a como `locked` no changelog; ela não pode ser alterada.
3. **Gravar a nova versão**: crie `v{n+1}.json` com o conteúdo recebido, `meta.version = n+1` e `meta.artifact_id = {asset_id}-v{n+1}` (D14: o `asset_id` é estável; as revisões referenciam a versão exata); se o arquivo já existir, aborte (jamais sobrescreva).
4. **Calcular `content_sha256`**: rode o comando, nunca de cabeça: `python squads/copy-squad/scripts/approval_tools.py content-hash <v{n}.json>` (E1: sha256 do JSON canônico do arquivo, mesma serialização do D1). É o único método de `content_sha256`, usado também pela biblioteca (`curate-asset-library`) e pelos checklists. Este hash identifica a versão no changelog; o `payload_sha256` da aprovação é calculado à parte por `approval_tools.py hash`.
5. **Registrar o changelog**: acrescente uma linha em `changelog.jsonl` com `version`, `changed_by`, `change_reason`, `content_sha256`, `parent_version`, `locked_versions` e `at`.
6. **Marcar superação**: a versão anterior fica como `superseded` no changelog (não por alteração do arquivo, mas por nova linha).
7. **Gerar diff (sob demanda)**: compare `v{n}` e `v{n+1}` por seção e liste adições, cortes e reordenações com contagem de palavras antes e depois.
8. **Atualizar o ponteiro de corrente**: registre no envelope de handoff qual é a versão corrente e qual está em aprovação (se houver).
9. **Registrar no journey log** a criação da versão e, se for o caso, o rework (ciclo 1 ou 2).

## Saída

- **Contrato:** sem contrato JSON Schema próprio; o artefato versionado preserva o seu contrato original (`meta.version` incrementado). O changelog é um arquivo JSONL append-only.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` e `changelog.jsonl` (minúsculas) na mesma pasta.
- **Envelope de handoff:** `from_agent: copy-publisher`, `to_agent` o agente solicitante, `artifact_type` do ativo, `status: ready`, `human_approval_required: false`, `gate: null`.

## Acceptance Criteria (Critérios de aceite)

- A listagem da pasta mostra versões sequenciais sem lacunas e sem alterações em versões antigas.
- Cada linha do changelog é JSON válido e contém os campos obrigatórios.
- A versão com pedido de aprovação aparece como `locked`.
- `content_sha256` reproduzível a partir do arquivo da versão, por `approval_tools.py content-hash` (passo 4).
- Diffs (quando pedidos) apontam seções e contagens de palavras corretas.
- Nenhuma operação de git foi executada.

## Quality gate e checklist

- **Gate:** `QG-PUBLISH-PREFLIGHT` (item de rastreabilidade de versões).
- **Checklist:** `checklists/publish-preflight-checklist.md`, fase de integridade e versões.
- **Veto:** tentativa de sobrescrever versão existente, lacuna de numeração ou changelog editado retroativamente.

## Tratamento de erro e fallback

| Situação | Tratamento |
|---|---|
| Arquivo `v{n+1}` já existe | Abortar e registrar a anomalia; usar o próximo número livre apenas se for um conflito de concorrência, e registrar |
| Duas versões simultâneas do mesmo ativo | Preservar ambas (`v{n+1}` e `v{n+2}`), registrar `parent_version` e pedir ao `copy-chief` para decidir qual segue |
| Changelog corrompido | Reconstruir a partir dos arquivos `v{n}.json` em novo arquivo e preservar o antigo; registrar anomalia |
| Versão em aprovação alterada | Bloquear; criar nova versão e abrir a rodada seguinte de aprovação |
| Falta de motivo | Pedir o motivo; sem motivo registrar `change_reason: "não informado"` e sinalizar ao `copy-chief` |
| Conteúdo inválido no contrato | Rejeitar a gravação e devolver ao produtor com o erro de schema |

## Handoff

| Condição | Próximo | Contrato | Gate |
|---|---|---|---|
| Nova versão gravada | Agente solicitante (ex.: `copy-editor`) | contrato do ativo | null |
| Versão pronta para aprovação | `copy-publisher` (`prepare-approval-package`) | contrato do ativo | G4 |
| `approved_with_edits` aplicado (D2) | `copy-publisher` abre a rodada seguinte (`prepare-approval-package`) | contrato do ativo | G1 a G4 |
| Conflito de versões | `copy-chief` | `handoff-envelope` | null |

## Exemplo

Entrada resumida (exemplo ilustrativo): o `copy-editor` entrega a edição de `cvc-camp-mentoria-lp-001`, que passa de v2 para v3.

```json
{"version": 3, "parent_version": 2, "changed_by": "copy-editor", "change_reason": "Corte de 28 por cento de redundância e clareza no hero", "content_sha256": "5555555555555555555555555555555555555555555555555555555555555555", "locked_versions": [], "state": "current", "at": "2026-11-10T11:40:00Z"}
```

Linha complementar registrada no mesmo changelog para a versão anterior:

```json
{"version": 2, "state": "superseded", "superseded_by": 3, "at": "2026-11-10T11:40:00Z"}
```

## Anti-padrões

- Sobrescrever `v1` para "manter a pasta limpa".
- Editar o changelog depois de gravado.
- Pular número de versão.
- Alterar a versão que está em aprovação.
- Usar o git do repositório como substituto do versionamento do ativo.
- Gravar versão sem motivo ou sem hash.
- Apagar versões reprovadas (elas alimentam aprendizado).
