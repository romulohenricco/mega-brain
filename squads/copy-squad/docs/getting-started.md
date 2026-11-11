# Primeiros passos — sua primeira campanha

> Passo a passo ilustrativo de uma campanha completa. Todos os nomes, números e textos abaixo são **exemplos ilustrativos**; não são dados reais.

## Pré-requisitos

- Repositório com `squads/copy-squad/` e as skills `copy-*` em `.claude/skills/`.
- Python 3 com PyYAML e jsonschema, apenas se for rodar o validador (`squads/copy-squad/scripts/validate_copy_squad.py`).
- Um identificador de negócio em kebab-case (`{business}`), por exemplo `consultoria-financeira-exemplo`.
- Quem vai atuar como `approval-owner` definido antes de começar, com o identificador dele em `config.yaml → human_gates.approvers`. Com `approvers` vazio, o G4 é bloqueado.
- Ler `docs/governance-decisions.md` (ADR-001): as regras de aprovação, hash e validade estão lá.

## Cenário

Negócio ilustrativo: uma mentoria de gestão financeira para pequenas empresas. Objetivo: aumentar as inscrições de uma turma, com 30 dias de campanha, usando uma landing page, uma sequência de e-mails e três variações de anúncio.

## Passo 1. Abrir a demanda

Use a skill ou o agente:

```text
/copy-squad "Aumentar as inscrições da turma da mentoria de gestão financeira em 30 dias"
```

ou ative o chief diretamente: `@copy-squad--copy-chief`.

O `copy-chief` executa `intake-demand`. Se faltar informação crítica, faz **no máximo 5 perguntas**, por exemplo:

1. Qual é a oferta exata (o que inclui, preço, condições)?
2. Quem é o público principal?
3. Quais canais e formatos estão previstos?
4. Há prazo, restrições legais ou de marca?
5. Existem provas autorizadas para uso (depoimentos, dados, casos)?

Sem resposta, ele não presume preço, garantia nem resultado.

## Passo 2. Conferir o plano de execução

Em seguida, `plan-execution` classifica o risco. Por haver anúncio pago e preço, o risco é **alto**. O plano indica o workflow `wf-campaign-launch` (multi-ativo) e os gates G1, G2, G3 e G4.

Arquivos gerados:

```text
.data/copy-squad/consultoria-financeira-exemplo/camp-turma-exemplo/
├── 00-intake/demand-intake.json
└── 00-intake/execution-plan.json
```

## Passo 3. Aprovar o brief (G1)

O `brief-master` cria e consolida o brief em `01-strategy/brief.json`, com objetivo, KPI principal, público, oferta, canal, tom, critérios de aceite e perguntas abertas. O `audience-voc` e o `offer-strategist` produzem `audience-voc.json` e `offer-canvas.json`.

O `copy-publisher` monta o pedido de G1 (`06-approval/_campaign/g1-r1/`). Você, como `approval-owner`, responde: `approved`, `approved_with_edits` ou `rejected`. Preencha o que faltar, principalmente fatos e provas. Como registrar a decisão está no Passo 7.

## Passo 4. Pesquisa e ângulos (G2)

O `research-analyst` gera `02-research/research-packet.json` com fontes e lacunas. O `hook-angle-creator` gera 20 ou mais ângulos em `03-angles/angles.json` e uma shortlist de 5 para a decisão. O `copy-publisher` monta o pedido de G2 e você escolhe os ângulos. Ângulos que dependem de prova ainda não verificada aparecem como `needs_approval`.

## Passo 5. Produção

Os copywriters recebem os ângulos aprovados:

| Ativo | Agente | Saída |
|---|---|---|
| Landing page | `conversion-copywriter` | `04-drafts/{asset_id}/v1.json` (`conversion-copy`) |
| Variações de anúncio | `conversion-copywriter` | `04-drafts/{asset_id}/v1.json` |
| Sequência de e-mails | `email-crm-copywriter` | `04-drafts/{asset_id}/v1.json` (`email-journey`) |

Se pedir uma nova versão, o arquivo vira `v2.json`; a `v1` nunca é sobrescrita.

## Passo 6. Edição e qualidade

1. `copy-editor` gera `05-review/{asset_id}/edit-report-v{n}.json`.
2. `brand-voice-guardian` gera `05-review/{asset_id}/brand-review-v{n}.json`.
3. `compliance-checker` gera `05-review/{asset_id}/compliance-review-v{n}.json` com todos os claims classificados.

Os claims sensíveis (preço, garantia, resultado etc.), os de `data_privacy` e os de urgência/escassez vão ao **G3** (os do `offer-canvas`, antes da produção, junto do G1; os que surgirem na copy final e não tenham sido pré-aprovados, antes do G4). Qualquer claim sem fonte aparece como `unverified` e precisa de prova ou remoção.

## Passo 7. Aprovação final (G4)

O `copy-publisher` monta `06-approval/{asset_id}/g4-r1/approval-request.json` com o payload completo, `payload_sha256` (calculado por `approval_tools.py hash`, nunca por um modelo), `channel`, política aplicada, `expires_at` (prazo de resposta de 72 horas) e `idempotency_key` (`{campaign_id}:{asset_id}:g4:r1:{12 hex do hash}`).

Você decide de um dos dois modos (D4 do ADR-001):

1. **Pelo terminal (`human-cli`):** rode, com o prefixo `!` no Claude Code, `! python squads/copy-squad/scripts/approval_tools.py decide --request <approval-request.json> --decision approved --reviewer <seu-id> --confirm <12 primeiros caracteres do hash>`.
2. **Pelo chat (`human-chat-confirmed`):** escreva uma mensagem explícita de decisão; a sessão principal, fora do papel de copy-chief, a transcreve literalmente em `comments` (obrigatório).

A decisão registra `bound_to` (gate, operação, destino e canal do pedido) e fica válida por 72 horas a partir de `decided_at` (janela de execução), gravada em `06-approval/{asset_id}/g4-r1/approval-decision.json`. Se você pedir edições, o resultado é `approved_with_edits`: o `copy-publisher` aplica as edições e abre a rodada seguinte (`g4-r2`) com novo hash, e você confirma com `approved`. Só então há execução.

## Passo 8. Publicação

Depois da decisão, o `copy-publisher` roda `approval_tools.py verify --for-execution` (hash recalculado, `decision == approved`, `bound_to`, `gate == G4`, validade `decided_at + 72h`, `human_attested`, `recorded_via` e `reviewer`), o `copy-chief` reexecuta sem flags e contra-assina o preflight, e só então a execução acontece, feita por você ou pela sessão principal (nenhum subagent publica, envia, veicula ou altera página). O `copy-publisher` registra o resultado em `07-published/{asset_id}/publish-receipt.json`, com plano de rollback. Divergência de hash, destino, canal ou operação, ou decisão expirada, resulta em VETO: nada é executado.

Importante: o squad não faz `git push` nem abre PR. Isso é função do `@devops`, fora do escopo do squad.

## Passo 9. Medir e aprender

Depois que houver dados, use `wf-performance-loop`. O `cro-analyst` gera `08-performance/performance-analysis-{aaaammdd}.json` com métricas, baseline, significância e hipóteses priorizadas. O `knowledge-curator` registra o `learning-record` e atualiza a biblioteca.

## Onde ver os artefatos

```text
.data/copy-squad/
├── _telemetry/
│   ├── agent-runs.jsonl            → uma linha por execução de agente
│   └── agent-evaluations.jsonl     → avaliações de qualidade, operação e negócio
└── consultoria-financeira-exemplo/
    ├── _brand/brand-voice-guide.json
    ├── _library/                   → index.jsonl e learnings/
    └── camp-turma-exemplo/
        ├── handoffs.jsonl          → todos os handoffs da campanha
        ├── 00-intake/  01-strategy/  02-research/  03-angles/
        ├── 04-drafts/  05-review/  06-approval/  07-published/  08-performance/
```

O registro de ciclo de vida fica em `.data/logs/journey/lifecycle-events.jsonl` (append-only).

## Atalhos úteis

| Quero | Comando |
|---|---|
| Só gerar hooks | `/copy-hook-generator "camp-turma-exemplo"` |
| Só montar o brief | `/copy-briefing-master "..."` |
| Checar claims de um texto | `/copy-fact-checker "..."` |
| Variações rápidas para uso interno ou teste | peça ao `copy-chief` o `wf-fast-variation` (se for publicar, a peça sai da pista rápida e passa por G4) |
| Reaproveitar um artigo longo | `/copy-repurposing-engine "..."` |
| Começar pequeno | modo `mvp` (orquestrador e 9 agentes, com `copy-publisher` e `brand-voice-guardian`) |

## Problemas comuns

| Sintoma | Causa provável | Ação |
|---|---|---|
| O agente pede informações | Brief incompleto | Responder às perguntas; não pular |
| `VETO` na publicação | Hash, destino ou operação diferentes do aprovado, ou decisão expirada | Gerar nova rodada com novo `approval-request` |
| G4 não sai da fila | `human_gates.approvers` vazio ou `approved_with_edits` | Preencher `approvers`; para `approved_with_edits`, confirmar a rodada seguinte com `approved` |
| Claim marcado `unverified` | Falta fonte ou autorização | Enviar a prova ou remover o claim |
| Skill não ativa | Frase fora das palavras-chave | Usar `@copy-squad--copy-chief` |
| Falha de validação de schema | Campo obrigatório ausente | Corrigir o artefato e revalidar |
| Contexto de workspace ausente | Pasta `{business}` não existe | Informar o contexto manualmente; o squad não escreve no workspace |

## Próximos passos

- Ler `knowledge/squad-operating-model.md` para entender o fluxo completo.
- Ler `knowledge/human-in-the-loop.md` antes do primeiro G4.
- Ler `docs/governance-decisions.md` (ADR-001), que prevalece em caso de conflito.
- Rodar o validador do squad depois de qualquer mudança estrutural.
