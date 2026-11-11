# Checklist: Revisão Humana nos Gates G1 a G4 e Correção G5

## Metadata
```yaml
id: approval-gate-checklist
name: "Checklist de revisão humana dos gates G1 a G4 e da correção G5"
version: 1.0.0
executor: approval-owner        # humano decisor do gate; não é executor de nenhum QG-*
related_task: approve-gate
quality_gate: null             # o QG-PUBLISH-PREFLIGHT é do copy-publisher (produtor) com contra-assinatura do copy-chief (executor)
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Dar ao `approval-owner` (pessoa responsável) um roteiro objetivo para decidir os gates de aprovação do squad de copy. O checklist garante que a decisão seja tomada sobre o payload exato, com claims verificados e com o risco compatível com a revisão feita. A decisão é do humano, distinto de quem produziu o artefato, e é registrada em `approval-decision` por ele (D4: `human-cli` ou `human-chat-confirmed`, com `human_attested: true`). O pedido de G1 a G4 vem sempre do `copy-publisher`; `approved_with_edits` nunca autoriza execução (D2). Este checklist não reivindica o QG-PUBLISH-PREFLIGHT, que é aplicado depois, em `publish-approved-asset`. A fase 6 cobre a correção de falhas de agentes (G5, sem pedido) para que o erro vire referência.

## Fase 1: Integridade do pedido (todos os gates)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | Abri o payload completo (não apenas o resumo ou o título) | blocking | [ ] | |
| 2 | `payload_sha256` do pedido é a saída de `approval_tools.py hash` sobre o payload exibido (nunca conferido de cabeça) | blocking | [ ] | |
| 3 | Sei o prazo de resposta (`expires_at` do pedido, 72h): passou, o pedido segue pendente; silêncio nunca é aprovação | recommended | [ ] | |
| 4 | `gate`, `operation` e `destination` correspondem ao que será decidido (esses campos ficam fora do hash e serão comparados na execução) | blocking | [ ] | |
| 5 | `risk_level` e `policy_applied` fazem sentido para o conteúdo | recommended | [ ] | |
| 6 | `audit_trail` mostra a sequência esperada de revisões | recommended | [ ] | |

**Score Fase 1:** ___/6

## Fase 2: G1 — Aprovação do brief

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 7 | Objetivo de negócio e KPI primário claros e mensuráveis | blocking | [ ] | |
| 8 | Oferta (promessa, mecanismo, preço, garantia) correta e autorizada | blocking | [ ] | |
| 9 | Público e estágio de consciência coerentes com a estratégia | blocking | [ ] | |
| 10 | `must_include` e `must_avoid` refletem limites de marca e legais | recommended | [ ] | |
| 11 | Fatos confirmados separados de hipóteses a validar | blocking | [ ] | |
| 12 | `open_questions` resolvidas ou aceitas conscientemente | recommended | [ ] | |

**Score Fase 2:** ___/6

## Fase 3: G2 — Aprovação de ângulo

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 13 | Ângulos escolhidos têm promessa específica e mecanismo plausível | blocking | [ ] | |
| 14 | Prova exigida (`proof_required`) existe ou está planejada | blocking | [ ] | |
| 15 | Nenhum ângulo usa escassez, urgência, autoridade ou prova falsas | blocking | [ ] | |
| 16 | Ângulos selecionados são coerentes com o posicionamento | recommended | [ ] | |
| 17 | Ângulos com `needs_approval` tiveram decisão registrada | blocking | [ ] | |

**Score Fase 3:** ___/5

## Fase 4: G3 — Aprovação de claims

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 18 | Cada claim de preço, garantia, resultado, autoridade, depoimento, comparativo, saúde ou financeiro tem `status: verified` | blocking | [ ] | |
| 19 | Cada claim tem fonte aberta e conferida por mim | blocking | [ ] | |
| 20 | Depoimentos e dados de cliente têm direito de uso (`usage_rights`) confirmado e dados pessoais anonimizados ou autorizados | blocking | [ ] | |
| 21 | Comparações com concorrentes são verdadeiras, justas e documentadas | blocking | [ ] | |
| 22 | Sinalizações de LGPD e de políticas da plataforma estão resolvidas | blocking | [ ] | |
| 23 | `requires_legal_review` resolvido quando verdadeiro | blocking | [ ] | |

**Score Fase 4:** ___/6

## Fase 5: G4 — Aprovação final

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 24 | `edit-report` presente e sem riscos remanescentes não tratados (medium e high) | blocking | [ ] | |
| 25 | `brand-review` com `approved_for_next_stage: true` (medium e high) | blocking | [ ] | |
| 26 | `compliance-review` com `approved: true` (leve em medium; completo em high) | blocking | [ ] | |
| 27 | Destino, canal e janela de publicação corretos | blocking | [ ] | |
| 28 | O texto atende aos critérios de aceite do brief | recommended | [ ] | |
| 29 | Plano de rollback conhecido | recommended | [ ] | |

**Score Fase 5:** ___/6

## Fase 6: G5 — Correção de falha de agente (sem approval-request)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 30 | Registrei o agente, a execução e a regra violada | blocking | [ ] | |
| 31 | Registrei `before`, `after` e `reason` do exemplo de referência | blocking | [ ] | |
| 32 | Dados pessoais foram anonimizados no exemplo | blocking | [ ] | |
| 33 | Definida a ação de prevenção (prompt, heurística, checklist ou gate) | recommended | [ ] | |
| 34 | Acionei o `knowledge-curator` para o `learning-record` | blocking | [ ] | |

**Score Fase 6:** ___/5

## Fase 7: Registro da decisão (todos os gates com pedido)

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 35 | A decisão é minha e será registrada por mim: `!python squads/copy-squad/scripts/approval_tools.py decide ...` (`human-cli`) ou mensagem minha no chat, transcrita pela sessão principal fora do papel de copy-chief e citada literalmente em `comments` (`human-chat-confirmed`; `comments` não pode ficar vazio) | blocking | [ ] | |
| 36 | `human_attested: true`, `reviewer` em `human_gates.approvers`, `meta.produced_by: approval-owner`, `meta.artifact_type: approval-decision`, `meta.status` coerente (approved -> approved, rejected -> rejected, approved_with_edits -> needs_approval) e sem `meta.model` nem `meta.prompt_version` | blocking | [ ] | |
| 37 | `payload_sha256` da decisão idêntico ao do pedido; `bound_to` = `{gate, operation, destination, channel}` copiado do pedido; `decided_at` não futuro e `expires_at` = `decided_at` + 72h (janela de execução); decisão gravada na pasta da rodada do pedido (`{gate}-r{n}` em minúsculas) | blocking | [ ] | |
| 38 | Se `approved_with_edits`: `edits` como objetos com `section`, `before`, `after` e `reason` (todos obrigatórios) e ciência de que a execução só ocorre após nova rodada `approved` sobre o novo hash | blocking | [ ] | |

**Score Fase 7:** ___/4

## Veto conditions

A decisão `approved` está vetada (e `approved_with_edits` só vale como pedido de edições) quando houver:

1. `payload_sha256` divergente do hash calculado pelo script.
2. Claim sensível sem fonte, com status diferente de verified ou sem direito de uso.
3. Risco medium sem compliance leve, ou high sem `compliance-review` completo aprovado.
4. Escassez, urgência, autoridade ou prova falsas no conteúdo.
5. Revisores obrigatórios do nível de risco não concluíram.
6. Destino diferente do pedido ou conteúdo alterado depois do hash.
7. Dado pessoal de cliente exposto sem autorização.
8. Decisão que seria registrada por agente em vez do humano (D4).

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| sha divergente | Devolver ao `copy-publisher` para regenerar o pacote |
| Pedido além de 72h sem decisão | Segue pendente; `copy-chief` reenvia ou escala (sem veto automático) |
| Decisão com janela de execução vencida | Nova rodada via `prepare-approval-package` |
| Claim sem fonte | `rejected` com a lista de evidências; claim volta como `needs_approval` |
| Revisão ausente | Devolver ao `copy-chief` para acionar o revisor |
| Texto precisa de ajuste pequeno | `approved_with_edits` com lista de edições; `copy-publisher` abre a rodada seguinte com novo sha e você confirma com `approved` |
| Risco estratégico (posicionamento, preço, promessa) | Decisão do `approval-owner` registrada como restrição; reabrir o brief se necessário |
| Erro de agente identificado | Registrar G5 (`correct-agent-failure`, sem pedido) |

## Edge cases

- **Aprovação parcial:** se parte das seções está ok, use `approved_with_edits` removendo o trecho problemático; nunca aprove "o resto" sem nova rodada e novo sha.
- **Mais de uma aprovação pendente para o mesmo ativo:** valide qual é a mais recente pelo `artifact_id` e `version`; invalide as demais.
- **Aprovador ausente:** designar substituto formalmente; nunca aprovação tácita.
- **Peça com janela curta (ex.: evento):** usar SLA de 4 horas úteis para G4 e manter o rito.
- **Baixo risco por amostragem (uso interno):** o sorteio sai de `approval_tools.py sample` (SAMPLING_RATE_LOW = 0.20) e o pedido é `gate: SAMPLING`, `internal_use`; se encontrar erro, ampliar a revisão do lote.
- **Mudança de oferta durante a revisão:** invalidar o pedido, voltar ao G1.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

Aplique apenas as fases do gate em decisão (Fase 1, a do gate e a Fase 7). O total é a soma dos itens das fases aplicadas. Item bloqueante reprovado implica VETO.

**Score final:** ___/___ = ___ → [ ] APPROVE  [ ] REVIEW  [ ] VETO
