# Checklist: Qualidade da Oferta

## Metadata
```yaml
id: offer-quality-checklist
name: "Checklist de Qualidade da Oferta e do Posicionamento"
version: 1.0.0
executor: copy-chief                # validador do QG-BRIEF (checklist de apoio; ADR-001 D7)
self_check_by: offer-strategist     # produtor: a autoverificação não aprova o gate
related_task: design-offer
quality_gate: QG-BRIEF
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que o `offer-canvas` esteja completo, sustentado por prova verificada, honesto quanto a preço, garantia e urgência, e pronto para alimentar a produção de copy sem criar passivo factual ou jurídico. Aplica-se também às tasks `map-objections` e `build-proof-stack`, que atualizam campos do mesmo canvas.

Tipos de item: `blocking` (falha = veto) e `quality` (falha reduz o score). Marque `[x]` quando o item for atendido com evidência no JSON.

---

## Fase 1: Fundamentos da oferta

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | `promise` presente, específica (quem, o quê, em quanto tempo quando houver base) e em uma frase | blocking | [ ] | |
| 2 | `mechanism` explica o "como" em 1 a 2 frases (ou a lacuna está registrada em `assumptions`) | blocking | [ ] | |
| 3 | A promessa não excede a melhor prova `verified: true` disponível | blocking | [ ] | |
| 4 | `meta` completo (`artifact_id` com prefixo `ofr-`, `produced_by: offer-strategist`, `version` incrementada) | quality | [ ] | |
| 5 | Fatos, hipóteses e pendências separados (hipóteses em `assumptions`) | quality | [ ] | |
| 6 | Promessa compatível com o `awareness_stage` e o objetivo do brief | quality | [ ] | |

**Score Fase 1:** ___/6

---

## Fase 2: Provas e claims

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 7 | Cada item de `proof_stack` tem `proof_id`, `type`, `summary`, `source`, `verified`; `testimonial` e `case` têm `usage_rights`, e `verified: true` neles só com `usage_rights: granted` | blocking | [ ] | |
| 8 | Nenhuma prova inventada, arredondada ou parafraseada como literal | blocking | [ ] | |
| 9 | Provas liberadas para copy têm `verified: true` e `usage_rights: granted` | blocking | [ ] | |
| 10 | Cada claim da promessa está ligado a pelo menos uma prova ou registrado como lacuna | quality | [ ] | |
| 11 | Dado de cliente identificável sinalizado para revisão LGPD | quality | [ ] | |
| 12 | Todo claim de price, guarantee, result, authority, testimonial, comparison, health ou financial consta em `needs_approval`, que é array de strings `<claim_type>: <pergunta>` (nunca objetos) | blocking | [ ] | |

**Score Fase 2:** ___/6

---

## Fase 3: Condições comerciais e urgência

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 13 | `price`, `guarantee`, `bonuses` e `risk_reversal` aparecem somente se foram fornecidos por fonte humana ou documento | blocking | [ ] | |
| 14 | `price.currency` no padrão `^[A-Z]{3}$` quando houver preço | quality | [ ] | |
| 15 | `legitimate_urgency.exists = true` apenas com `reason` e `deadline` reais e futuros (o contrato exige os dois) | blocking | [ ] | |
| 16 | Nenhuma escassez, urgência ou autoridade falsa implícita nas descrições | blocking | [ ] | |
| 17 | Pendências comerciais viraram perguntas objetivas (máx. 5) ao approval-owner | quality | [ ] | |

**Score Fase 3:** ___/5

---

## Fase 4: Posicionamento e objeções

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 18 | `positioning.category` definida, `differentiators` com >= 2 itens verificáveis e `positioning.messaging_house` com `central_message` e até 3 `pillars` (`proof_ids` existentes no `proof_stack`) | blocking | [ ] | |
| 19 | Comparativos nominais têm fonte pública datada e estão em `needs_approval` | blocking | [ ] | |
| 20 | `objection_responses` cobre as objeções high/medium do audience-voc (>= 90%) | quality | [ ] | |
| 21 | Cada resposta está ancorada em `proof_ids` ou `mechanism`; as demais marcadas como hipótese | quality | [ ] | |
| 22 | `sale_angles` ligados a objeções e provas, com nível de risco | quality | [ ] | |

**Score Fase 4:** ___/5

---

## Fase 5: Governança e entrega

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 23 | `risk_level` coerente com a risk-policy (claim sensível = high) | blocking | [ ] | |
| 24 | JSON valida em `contracts/offer-canvas.schema.json` | blocking | [ ] | |
| 25 | Versão nova gravada (sem sobrescrever) em `01-strategy/offer-canvas.json` | quality | [ ] | |
| 26 | Envelope de handoff emitido com `gate: G3` quando houver claim sensível; o G3 de oferta (antes da produção) é pedido ao `copy-publisher`, nunca montado pelo produtor (ADR-001 D5, D10) | quality | [ ] | |
| 27 | Nenhum dado de outro negócio e nenhum caminho absoluto no conteúdo | blocking | [ ] | |

**Score Fase 5:** ___/5

---

## Veto conditions

Qualquer uma abaixo força `VETO` independentemente do score:

1. Preço, garantia, bônus ou prazo preenchido sem fonte.
2. Prova inventada, ou prova não verificada / sem direito de uso liberada para a copy.
3. Promessa mais forte que a melhor prova disponível, sem registro em `needs_approval`.
4. `legitimate_urgency.exists = true` sem motivo e prazo reais documentados.
5. Claim sensível ausente de `needs_approval`.
6. Comparativo nominal sem fonte pública datada.
7. Mistura de dados de dois negócios no mesmo canvas.
8. JSON inválido no schema.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Promessa acima da prova | Reduzir ao nível sustentável; mover a versão ambiciosa para `needs_approval` |
| Campo comercial sem fonte | Remover o valor, registrar a pergunta e marcar `status: needs_input` |
| Prova sem verificação | Manter com `verified: false`, retirar do uso em copy, propor coleta de fonte |
| Objeção sem âncora | Marcar como hipótese e solicitar novo recorte ao `audience-voc` |
| Urgência sem motivo | Definir `exists: false`; sugerir reforço de ação sem pressão artificial |
| Claim sensível não listado | Adicionar a `needs_approval` como string `<claim_type>: <pergunta>`; elevar risco |
| JSON inválido | Corrigir tipos, enums e `additionalProperties`; reexecutar a validação |

Limite: 2 ciclos de rework; no terceiro, escalar ao `copy-chief`.

## Edge cases

- **Oferta gratuita (isca digital):** preço é `0`; mesmo assim, registrar condições de dados pessoais coletados e consentimento (sinalizar LGPD).
- **Oferta sem nenhuma prova:** a promessa deve ser reduzida a afirmação com mecanismo; registrar plano de coleta; risco não inferior a medium.
- **Preço variável ou sob consulta:** registrar o fato como "sob consulta" em `payment_terms`; nunca estimar faixa.
- **Garantia condicional:** `guarantee.terms` deve reproduzir as condições literais fornecidas; condições omitidas = veto.
- **Vários públicos:** um canvas por segmento/campanha; não misturar objeções.
- **Mercado regulado (saúde, finanças):** todo resultado e comparativo vai para `compliance-checker` e G3 independentemente do score.
- **Oferta com bônus expirável:** o prazo precisa ser real; guardar o motivo no `reason`.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Total de itens: 27. Fórmula: `score = itens_OK / 27`. Item `blocking` reprovado equivale a veto mesmo com score alto.

| Faixa | Decisão | Ação |
|---|---|---|
| >= 0.80 sem veto | APPROVE | Emitir handoff ao `brief-master` / `hook-angle-creator` |
| 0.60 a 0.79 | REVIEW | Rework (máx. 2 ciclos) |
| < 0.60 ou veto | VETO | Escalar ao `copy-chief`; solicitar decisão ao `approval-owner` se envolver claim |

**Score final:** ___/27 = ___ → ______
