# Registro de Aprendizado — {lrn-id}

> Template humano do contrato `learning-record` (`contracts/learning-record.schema.json`).
> Preenchido pelo `knowledge-curator` a partir de CRO, correção humana (G5), debrief de campanha ou falha de qualidade.
> Persistência do JSON: `.data/copy-squad/{business}/_library/learnings/{lrn-id}.json`.
> Regra: nunca inventar resultado, métrica, fonte ou número. Resultado inconclusivo é `testing` ou `draft`, nunca `approved`.

## 1. Identificação

| Campo | Valor |
|---|---|
| Negócio (`business`) | {business} |
| Campanha (`campaign_id`, se houver) | {campaign_id} |
| Registro (`meta.artifact_id`) | lrn-{slug} |
| Versão (`meta.version`) | {versão} |
| Produzido por | knowledge-curator |
| Data (`meta.produced_at`) | {data-hora} |
| Fontes (`meta.sources`) | {performance-analysis, approval-decision, audience-voc (feedback de cliente), debrief ou relatório de falha, com caminho} |

## 2. Origem

- **Origem (`origin`):** cro | human_correction | campaign_debrief | qa_failure | customer_feedback
- **Artefato de origem:** {caminho em .data/copy-squad/{business}/...}
- **Gate relacionado:** {G5 para correção humana; nenhum nos demais; QG-LEARNING validado pelo cro-analyst}

## 3. Aprendizado

| Campo | Conteúdo |
|---|---|
| Hipótese (`hypothesis`) | {o que se acreditava antes} |
| Variação (`variation`) | {o que mudou} |
| Métrica (`metric`) | {como foi medido} |
| Resultado (`result`) | {o que aconteceu, com números e amostra; se inconclusivo, escrever "Inconclusivo" e a razão} |
| Decisão (`decision`) | {o que o squad passa a fazer} |
| Próxima ação (`next_action`) | {ação concreta, responsável e prazo} |

## 4. A que se aplica (`applies_to`)

| Dimensão | Valor |
|---|---|
| Oferta (`offer`) | {oferta} |
| Público (`audience`) | {público} |
| Canal (`channel`) | {canal} |
| Formato (`format`) | {formato} |

Limites de generalização: {quando este aprendizado NÃO deve ser aplicado}

## 5. Exemplo de referência (`reference_example`)

Obrigatório quando `origin = human_correction`.

| Campo | Texto |
|---|---|
| Antes (`before`) | {texto original, literal} |
| Depois (`after`) | {texto corrigido, literal} |
| Razão (`reason`) | {por que a correção foi feita} |

## 6. Status e revisão

| Campo | Valor |
|---|---|
| Status do aprendizado (`learning_status`) | approved / draft / rejected / testing |
| Justificativa do status | {por que este status} |
| Revisar depois de (`review_after`) | {YYYY-MM-DD} |
| Contradições ou duplicidades | {ids de registros relacionados, se houver} |

Guia de status:
- `approved`: resultado conclusivo, confirmado pelo humano ou por critério pré-registrado.
- `testing`: teste em andamento ou resultado ainda inconclusivo.
- `draft`: falta confirmação, razão ou evidência.
- `rejected`: descobriu-se que o aprendizado está errado ou não se aplica.

## 7. Registro no índice

| Campo | Valor |
|---|---|
| Linha em `index.jsonl` | asset_id `{lrn-id}`, type `learning`, asset_status `{status}` |
| Caminho (`source_path`) | `.data/copy-squad/{business}/_library/learnings/{lrn-id}.json` |
| Sugestão de ingestão (opcional, apenas se o humano pedir) | Para levar ao conhecimento de negócio do Mega Brain, execute /ingest-empresa com o caminho acima e o negócio {business}. Não executar automaticamente. |

## 8. Revisão de qualidade

| Item | Resultado |
|---|---|
| Checklist `checklists/knowledge-entry-checklist.md` (QG-LEARNING) | score {0-1} · {APPROVE / REVIEW / VETO} |
| Revisor | {copy-chief ou approval-owner} |
| Observações | {texto} |
