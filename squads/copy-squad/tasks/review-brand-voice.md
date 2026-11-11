---
task: review-brand-voice
name: review-brand-voice
task_name: "Revisar voz da marca em peça"
version: "1.0.0"
squad: copy-squad
task_id: review-brand-voice
category: quality
difficulty: intermediate
responsavel: '@brand-voice-guardian'
responsavel_type: Agent
responsible_executor: brand-voice-guardian
execution_type: Agent
atomic_layer: Molecule
elicit: false
estimated_time: 10-30min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: edit_report
  tipo: contract:edit-report
  obrigatorio: true
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: true
Saida:
- campo: brand_review
  tipo: contract:brand-review
  persistido_em: .data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/brand-review-v{n}.json
input: [edit-report, brand-voice-guide]
output: [brand-review]
action_items:
  - "Confirmar a existência do guia e da peça editada"
  - "Comparar a peça com personalidade, tom do contexto, vocabulário e formalidade"
  - "Registrar issues com trecho literal, severidade e reescrita mínima"
  - "Congelar fatos, preços, números e claims"
  - "Calcular brand_alignment_score e decidir approved_for_next_stage"
  - "Encaminhar ao compliance-checker (aprovada) ou ao copy-editor (reprovada)"
acceptance_criteria:
  - "brand-review.json valida em contracts/brand-review.schema.json"
  - "Cada issue traz excerpt literal, problem, severity e reason ligada a regra do guia"
  - "0 reescritas que alterem fato, preço, número, prazo ou claim"
  - "approved_for_next_stage true somente com brand_alignment_score >= 80 e zero issue critical"
  - "Lacunas do guia registradas sem reprovar a peça por elas"
pre_condition: "brand-voice-guide existente para o {business} (e aprovado em G1) e edit-report da peça disponível."
post_condition: "brand-review.json gravado, envelope emitido ao compliance-checker ou copy-editor, telemetria registrada."
checklist: checklists/brand-voice-review-checklist.md
quality_gate: QG-BRAND
human_gate: null
skill: copy-brand-voice-check
workflows: [wf-copy-production, wf-campaign-launch, wf-fast-variation, wf-performance-loop, wf-content-repurposing]
performance:
  error_handling: "Sem guia: parar e propor define-brand-voice; reescrita que tocaria fato é descartada e o fato é escalado ao compliance-checker"
---

# Task: Revisar voz da marca em peça

## Objetivo

Validar se uma peça já editada respeita o guia de voz do negócio e emitir um `brand-review` objetivo: score de alinhamento de 0 a 100, issues por severidade (critical, medium, low), reescritas mínimas e a decisão `approved_for_next_stage`. A revisão não altera fatos, preços, números nem claims e não cria argumentos novos. Peças aprovadas seguem ao `compliance-checker`; reprovadas voltam ao `copy-editor`.

## Quando usar / quando não usar

**Usar quando:**
- O `copy-editor` entregou um `edit-report` e a peça precisa de validação de tom antes do compliance.
- Uma variação de uso interno (risco low) precisa de checagem de voz: o QG-BRAND é obrigatório em todas as peças, sem amostragem (`wf-fast-variation`).
- O humano pediu para verificar se um texto "está na voz da marca" (skill `copy-brand-voice-check`).

**Não usar quando:**
- Não existe guia de voz (use `tasks/define-brand-voice.md` primeiro).
- A peça ainda é rascunho não editado: deve passar antes pelo `copy-editor`.
- O pedido é validar fatos ou conformidade (use `tasks/check-compliance.md` ou `tasks/fact-check-claims.md`).
- A peça foi escrita ou editada pelo próprio `brand-voice-guardian` (AP05: produtor não valida).

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| edit_report | contract:edit-report | Sim | copy-editor (`05-review/{asset_id}/edit-report-v{n}.json`) |
| brand_voice_guide | contract:brand-voice-guide | Sim | `.data/copy-squad/{business}/_brand/brand-voice-guide.json` |
| draft | conversion-copy, content-piece, ux-copy, video-script ou email-journey | Sim (referenciado no edit-report) | `04-drafts/{asset_id}/v{n}.json` |
| risk_level | low, medium ou high | Não | execution-plan / brief |

## Passos

1. **Verificar pré-condições.** Confirmar que o guia existe, que é do mesmo `{business}` e que o `edit-report` referencia o `original_copy_id` correto. Sem guia: `needs_input` e parar.
2. **Ler a peça por seção.** Usar `edited_sections` do edit-report; identificar o contexto (canal e formato) e localizar a linha correspondente em `tone_by_context`.
3. **Comparar com o guia.** Checar personalidade, tom do contexto, `vocabulary.preferred` e `forbidden`, glossário, `formality` e `style_rules`.
4. **Registrar issues.** Para cada desvio: `severity`, `excerpt` literal, `problem`, `suggested_revision` mínima e `reason` ligada a regra do guia.
5. **Congelar fatos.** Qualquer trecho que contenha preço, número, prazo, garantia, depoimento ou claim não pode ser reescrito; se parecer incorreto, escalar ao `compliance-checker` (issue medium com `suggested_revision` vazio).
6. **Calcular o score.** Partir de 100 e deduzir por issue (critical -20, medium -8, low -2, limite inferior 0), ajustando por aderência global ao tom; registrar o raciocínio em `tone_match`.
7. **Decidir.** `approved_for_next_stage = true` somente se score >= 80 e nenhum critical. Caso contrário `false`.
8. **Registrar lacunas do guia.** Se o contexto não existir em `tone_by_context`, avaliar pelo núcleo de personalidade e sugerir extensão do guia (sem reprovar por isso).
9. **Persistir.** Gravar `brand-review-v{n}.json` na pasta de revisão do ativo, com `n` igual à versão do draft revisado (`{asset_id}-v{n}`, ADR-001 D14); nunca sobrescrever revisões anteriores.
10. **Emitir handoff e telemetria.** Envelope ao `compliance-checker` (aprovada) ou `copy-editor` (reprovada, no máximo 2 ciclos); registrar `agent-run`.

## Saída

- **Contrato:** `contracts/brand-review.schema.json`.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/05-review/{asset_id}/brand-review-v{n}.json`.
- **Envelope** (`handoff-envelope`): `from_agent: brand-voice-guardian`; `to_agent: compliance-checker` ou `copy-editor`; `input_ids`: `edt-...` e `bvg-...`; `output_id: bvr-...`; `artifact_type: brand-review`; `status: ready` (ou `blocked` se houver critical); `gate: null`.

## Acceptance Criteria (Critérios de aceite)

- Schema válido; `meta.artifact_id` com prefixo `bvr-`; `brand_guide_id` com o id do guia usado.
- Cada issue com os campos obrigatórios e trecho literal.
- Nenhuma sugestão toca em fato, preço, número, prazo ou claim.
- Decisão coerente com a regra objetiva (score >= 80 e zero critical).
- Reescritas mínimas: cada `suggested_revision` altera apenas o trecho necessário.

## Quality gate e checklist

- **Checklist:** `checklists/brand-voice-review-checklist.md` (seção da revisão).
- **Quality gate:** `QG-BRAND` (produtor: `copy-editor`, versão editada; executor: `brand-voice-guardian`; ADR-001 D7). Obrigatório em todas as peças, inclusive de risco low: a amostragem (`SAMPLING_RATE_LOW`) vale só para a revisão humana, nunca para este gate. APPROVE >= 0.80; REVIEW 0.60-0.79 (rework com o `copy-editor`, máx. 2 ciclos); VETO < 0.60 ou veto condition (revisão sem guia, alteração de fato).
- **Gate humano:** nenhum direto; o `brand-review` compõe o pacote do G4 para risco medium/high.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Guia ausente | `needs_input`; acionar `tasks/define-brand-voice.md` via `copy-chief` |
| `edit-report` sem `original_copy_id` válido | `needs_input`; devolver ao `copy-editor` |
| Peça em idioma diferente do guia | Registrar limitação; encaminhar ao `localization-specialist` se for transcreação |
| Conflito entre guia e instrução do brief | Registrar o conflito; seguir o guia e escalar ao `copy-chief` |
| Terceiro ciclo reprovado | Escalar ao `copy-chief` e ao `approval-owner` com o histórico de issues |
| Trecho possivelmente factual incorreto | Não reescrever; issue medium com escalonamento ao `compliance-checker` |

## Handoff

- **compliance-checker:** `brand-review` aprovado junto com o edit-report.
- **copy-editor:** `brand-review` reprovado com issues acionáveis e reescritas mínimas.
- **copy-chief:** escalonamento após o 3º ciclo ou conflito entre guia e brief.
- **knowledge-curator:** exemplos aprovados de voz para a biblioteca (quando houver G5).

## Exemplo

**Entrada resumida (exemplo ilustrativo):** e-mail de nutrição editado; guia prevê tom informal e proíbe jargão sem explicação.

**Saída (trecho, exemplo ilustrativo):**

```json
{
  "meta": {"artifact_id": "bvr-email-nutricao-v1", "artifact_type": "brand-review", "produced_by": "brand-voice-guardian", "version": 1, "status": "ready"},
  "text_id": "eml-nutricao-v2",
  "brand_guide_id": "bvg-negocio-exemplo-v1",
  "brand_alignment_score": 74,
  "tone_match": "Parcial: início próximo, meio técnico demais",
  "issues": [
    {"severity": "critical", "excerpt": "otimize seu EBITDA", "problem": "Jargão proibido sem definição", "suggested_revision": "melhore o resultado antes de juros e impostos (EBITDA)", "reason": "vocabulary.forbidden: jargão sem explicação"},
    {"severity": "low", "excerpt": "Prezado cliente", "problem": "Formalidade acima do guia", "suggested_revision": "Olá", "reason": "formality: informal"}
  ],
  "approved_for_next_stage": false
}
```

## Anti-padrões

- Revisar sem guia, usando tom presumido.
- Reescrever a peça inteira em vez de ajustar trechos.
- Alterar preço, número, prazo ou claim por motivo de tom.
- Aprovar com issue critical aberta.
- Criticar por gosto sem citar a regra do guia.
- Reprovar por contexto não coberto pelo guia em vez de propor extensão.
- Revisar peça escrita ou editada por si mesmo.
