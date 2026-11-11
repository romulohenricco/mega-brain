# Scripts do copy-squad

Três ferramentas determinísticas, sem rede e sem LLM:

| Script | Papel |
|---|---|
| `validate_copy_squad.py` | Valida estrutura, config, agentes, tasks, workflows, contratos, skills, wrappers, independência e consistência com o ADR-001 |
| `approval_tools.py` | Hash do payload, preflight de execução, amostragem e registro de decisão humana (D21) |
| `guard_approval_decision.py` | Hook PreToolUse opcional (E8): impede o Claude de rodar `approval_tools.py decide` e de escrever `approval-decision.json`. Não vem ligado |

Dependências em `scripts/requirements.txt` (`PyYAML` e `jsonschema>=4.18`). O
`approval_tools.py` usa só a biblioteca padrão (lê o `config.yaml` com PyYAML quando
existe e com um leitor mínimo quando não existe); com `jsonschema` instalado, o `verify`
também valida o pedido e a decisão contra os schemas do squad.

```bash
python -m pip install -r squads/copy-squad/scripts/requirements.txt
```

## validate_copy_squad.py

A partir da raiz do repositório:

```bash
python squads/copy-squad/scripts/validate_copy_squad.py          # saída em texto
python squads/copy-squad/scripts/validate_copy_squad.py --json   # saída em JSON
python squads/copy-squad/scripts/validate_copy_squad.py --repo <raiz-do-repo>
python squads/copy-squad/scripts/validate_copy_squad.py --allow-missing-jsonschema   # só diagnóstico parcial
python -m pytest tests/test_copy_squad.py tests/test_copy_squad_approval_tools.py -q
```

Sem `--repo`, a raiz é deduzida do próprio arquivo (a pasta `scripts` fica três
níveis abaixo da raiz). O validador nunca contém caminhos absolutos.

### Severidades e exit codes

- **ERROR** viola o contrato do squad e reprova (exit 1).
- **WARN** não reprova. Hoje só: skill fora de 80 a 160 linhas, ou `jsonschema`
  ausente com `--allow-missing-jsonschema`.
- Exit 2: PyYAML ausente.

`jsonschema` ausente é ERROR por padrão: sem ele, contratos e fixtures não seriam
validados e a suíte passaria trivialmente.

### O que cada checagem cobre

| Checagem | Cobertura |
|---|---|
| structure | Diretórios e arquivos obrigatórios; nenhum `CLAUDE.md` dentro do squad |
| config | Campos obrigatórios, `metadata.score`, nível de workspace, `components.*` igual ao disco nos dois sentidos (arquivo em disco fora de `components` é ERROR), `agents[].file`, `entry_agent` |
| registry | `agent-registry.yaml` contra o `config.yaml`: ids, `total_agents`, `ai_agents`, `human_roles`, `entry_agent` |
| syntax | Sintaxe de todo `.yaml`, `.yml` e `.json` do squad |
| handoff-matrix | Agentes citados em `data/handoff-matrix.yaml` existem |
| checklists | Mínimo de linhas (`checklist_min_lines`), `knowledge/INDEX` e README exigidos; `executor` no metadata do checklist de cada gate igual ao `executor` de `data/quality-gates.yaml` (D7), incluindo os cinco checklists de formato do QG-DRAFT |
| agents | Frontmatter, ACTIVATION-NOTICE, mínimo de linhas, `agent.id`, `*help` e `*exit`, `handoff_to`, `command_loader.requires` e `dependencies.*` (não resolvida é ERROR) |
| tasks | Frontmatter e chaves obrigatórias; `task`, `task_id` e `name` iguais ao nome do arquivo; `quality_gate` em `data/quality-gates.yaml` ou `null`; `human_gate` em G1 a G5 ou `null`; responsável, checklist, skill, workflows, mínimo de linhas e ausência de tasks órfãs |
| workflows | State machine coerente, fases com checkpoint, agente da fase igual ao responsável da task, conjunto de `gate_id` igual a `gate_sequence_by_workflow`, `executor` de cada gate igual ao de `data/quality-gates.yaml`, mínimo de linhas |
| refs | Referências em texto livre a `tasks/*.md`, `contracts/*.schema.json`, `checklists/*.md`, `data/*.(yaml\|md)`, `templates/*-tmpl.md`, `workflows/wf-*.yaml` e `knowledge/*.md` precisam existir |
| contracts | JSON válido, draft 2020-12, `$id` do squad, fixture `.valid.json` e exemplo em `templates/json/` validam, com verificação própria de `date` e `date-time` |
| approval-fixtures | `payload_sha256` do approval-request de fixture e de exemplo igual ao hash D1 do payload; a decision repete o mesmo hash e o mesmo `approval_request_id` |
| approval-verify | Reproduz o fluxo E8 numa pasta de rodada temporária (`06-approval/<asset>/g4-r1/`): grava o `payload.json` (igual a `request.payload`) ao lado do pedido e da decisão da fixture (`approval-request.valid.json` + `approval-decision.valid.json`) e executa `approval_tools.py verify --for-execution --payload` em modo de teste (`COPY_SQUAD_TEST_MODE=1`, `--now` derivado de `decided_at`, `--config` temporário em que só o `business` do pedido lista o reviewer) esperando `ok=true`; e exige falha nos casos negativos: `bound_to` divergente ou ausente, `approved_with_edits`, decisão expirada, hash alterado, `expires_at` fora de 72 h, gate diferente de G4, `payload.json` divergente do aprovado, `decision.meta.business` ou `campaign_id` trocados (e aprovadores lidos do business do pedido, não da decisão), `meta.artifact_type` trocado, `destination` vazio, `channel` ausente e `--now` sem modo de teste (exit 2) |
| conventions | Caminhos `05-review/...` de revisão sem `-v{n}` (`edit-report`, `brand-review`, `compliance-review`, `localization`) e pastas de rodada com gate em maiúsculas (use `g4-r1`, `sampling-r1`, nunca a forma maiúscula) em qualquer texto do squad, das skills e dos wrappers |
| skills | `SKILL.md`, frontmatter, marcadores, seção de não ativação, registro com a mesma versão, `copy-*` em disco igual a `components.skills`, 80 a 160 linhas (WARN) |
| wrappers | Um wrapper por agente `Agent`, campos obrigatórios, linha `tools:` presente, nenhuma ferramenta `mcp__`, `Bash` só para quem roda scripts do squad e busca web só para research-analyst e compliance-checker (D18); nenhum wrapper para o approval-owner |
| independence | Padrões proibidos em `squads/copy-squad/` (inclusive `scripts/`), nas skills `copy-*` e nos wrappers: outro squad de copy, engines externas, nome de empresa, caminhos absolutos e qualquer letra de unidade de disco, placeholders de chaves duplas, CRLF e segredos com formato conhecido |

### Autodenúncia

O validador se varre como qualquer outro arquivo do squad. Os padrões proibidos são
montados por concatenação; a única exceção é uma linha com o comentário
`# forbidden-pattern-def`, que é ignorada. Use a marcação só para definição de padrão.

## approval_tools.py

Resolve o `config.yaml` pela posição do script (pasta acima de `scripts/`). Subcomandos
(D21, E1, E2, E8):

```bash
python squads/copy-squad/scripts/approval_tools.py hash <approval-request.json>
python squads/copy-squad/scripts/approval_tools.py content-hash <arquivo.json>
python squads/copy-squad/scripts/approval_tools.py verify --request R --decision D [--for-execution] [--payload payload.json]
python squads/copy-squad/scripts/approval_tools.py sample <asset_id> [--rate 0.20]
python squads/copy-squad/scripts/approval_tools.py decide --request R --decision approved --reviewer ID --confirm <12 hex> [--comments "..."]
```

| Subcomando | Quem usa | Saída |
|---|---|---|
| `hash` | copy-publisher, copy-chief | `payload_sha256` em stdout, pelo método D1: `sha256(json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))`. Sem NFC e sem normalização de quebra de linha |
| `content-hash` | copy-publisher, knowledge-curator | `content_sha256`: o mesmo método do D1 aplicado ao JSON inteiro do arquivo (changelog, biblioteca, checklists). É o único método de `content_sha256` |
| `verify` | copy-publisher (roda), copy-chief (reexecuta sem flags de teste e contra-assina) | JSON `{ok, checks[]}`; exit 0 se tudo passa, 1 se algo falha. Preflight (E8): `verify --for-execution --request <rodada>/approval-request.json --decision <rodada>/approval-decision.json --payload <rodada>/payload.json` |
| `sample` | copy-publisher | `true` ou `false`: `int(sha256(asset_id)[:8], 16) / 0xFFFFFFFF < rate` |
| `decide` | **somente o humano** (no Claude Code, com o prefixo `!`) | Grava `approval-decision.json` ao lado do request, na pasta da rodada, com `recorded_via: human-cli`, `human_attested: true`, `meta.produced_by: approval-owner`, `meta.status` mapeado (approved, rejected, approved_with_edits vira needs_approval), hash recalculado, `bound_to` copiado do pedido e `expires_at = decided_at + 72 h`. Exige `--confirm` igual aos 12 primeiros hex do hash, reviewer listado em `approvers` e não sobrescreve decisão existente |

### O que o `verify` confere

- Hash do request e da decision iguais ao hash recalculado do `payload`; com `--payload`, o hash D1 do `payload.json` da rodada (o conteúdo que será executado, E8) também é igual ao `payload_sha256` do pedido.
- Identidade (E8): `meta.artifact_type` do pedido é `approval-request` e o da decisão é `approval-decision`; `decision.meta.business` e `decision.meta.campaign_id` são iguais aos do pedido.
- Schema (E8, só com `jsonschema` instalado): pedido e decisão validam contra `contracts/approval-request.schema.json` e `contracts/approval-decision.schema.json` (checagens `request_valido_no_schema` e `decision_valido_no_schema`). Sem `jsonschema`, essas duas checagens não existem.
- Decision refere ao request (`approval_request_id`) e `decision == approved` (`approved_with_edits` nunca autoriza execução, D2).
- `bound_to` da decision é igual a `gate`, `operation`, `destination` e `channel` do pedido, sem campos extras (E1).
- `--for-execution` (preflight): `request.gate == G4`, `operation` em `publish`, `send`, `run_ads`, `update_page`, `risk_level != low`, `destination` e `channel` do pedido como strings não vazias e as quatro chaves de `bound_to` (`gate`, `operation`, `destination`, `channel`) como strings não vazias.
- Validade (E2): `decided_at <= now`, `now < expires_at` e `expires_at == decided_at + 72 h` com tolerância de 60 s.
- Proveniência: `human_attested`, `recorded_via` válido, `comments` não vazio quando `recorded_via == human-chat-confirmed`, `meta.produced_by == approval-owner`, sem `meta.model` nem `meta.prompt_version`, `meta.status` coerente com a decisão e `reviewer` em `human_gates.approvers` do **business do pedido** (`request.meta.business`, E8), nunca do business declarado pela decisão.

### Modo de teste

`--now` e `--config` (em `verify` e `decide`) só são aceitos com a variável de ambiente
`COPY_SQUAD_TEST_MODE=1`; sem ela o script recusa com exit 2. No uso real o relógio é o
do sistema e a lista de aprovadores é a do `config.yaml` do squad, então quem executa o
preflight não consegue mudar a janela de 72 h nem a lista de aprovadores. O copy-chief
reexecuta `verify --for-execution` sem flags ao contra-assinar. Só os testes e o
validador (`approval-verify`) usam o modo de teste.

Limitação conhecida (D4): a proveniência humana é procedimental, não criptográfica.

## guard_approval_decision.py (hook opcional, E8)

Endurecimento da D4: um hook PreToolUse que lê o JSON da chamada no stdin (como os demais
hooks de `.claude/hooks/`) e bloqueia com exit 2 e mensagem em português:

- `Bash` cujo comando contém `approval_tools.py decide`;
- `Bash` que grava `approval-decision.json` em `06-approval/` por redirecionamento (`>`, `>>`), `tee`, `cp`, `mv`, `install`, `ln` ou `sed -i` (heurística: código arbitrário, como `python -c`, não é coberto);
- `Write`, `Edit` e `MultiEdit` cujo `file_path` case com `06-approval/**/approval-decision.json`.

Vale para a sessão principal e para subagents. Qualquer outra chamada passa em silêncio
(exit 0); entrada ilegível também passa (fail-open, como os outros hooks do repositório).

**Não vem ligado.** Ligar é decisão do responsável pelo repositório, porque altera o
`.claude/settings.json`. Trecho para adicionar em `hooks.PreToolUse`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/squads/copy-squad/scripts/guard_approval_decision.py\""
          }
        ]
      }
    ]
  }
}
```

Efeito de ligar o hook:

- O humano continua decidindo: comandos digitados com o prefixo `!` no Claude Code não passam
  por hooks, então `!python squads/copy-squad/scripts/approval_tools.py decide ...` grava
  `approval-decision.json` com `recorded_via: human-cli`.
- `human-chat-confirmed` deixa de existir na prática: a sessão principal não consegue mais
  transcrever a mensagem do humano para o arquivo. O único meio de registrar a decisão passa a
  ser `human-cli`.
- O `verify` não muda: continua aceitando os dois valores de `recorded_via`, para que decisões
  antigas e fixtures continuem verificáveis.
- Limitação: o hook barra o Claude, não o sistema de arquivos. Quem tem um terminal próprio
  continua podendo escrever o arquivo; a proveniência segue procedimental (D4).

Teste manual:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"python squads/copy-squad/scripts/approval_tools.py decide"}}' \
  | python squads/copy-squad/scripts/guard_approval_decision.py; echo "exit $?"   # exit 2
```
