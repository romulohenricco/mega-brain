# Plano de Execução — {campaign_id}

> Template humano do contrato `execution-plan` (`contracts/execution-plan.schema.json`). Preenchido pelo `copy-chief`. O artefato oficial é o JSON em `.data/copy-squad/{business}/{campaign_id}/00-intake/execution-plan.json`; este documento é a versão legível para revisão.

## 1. Identificação

| Campo | Valor |
|---|---|
| artifact_id | pln-{campaign_id}-001 |
| campaign_id | camp-{slug} |
| business | {business} |
| demand_id | dmd-{campaign_id}-001 |
| produzido por | copy-chief |
| produzido em | AAAA-MM-DDTHH:MM:SSZ |
| versão | 1 |
| status | draft / ready / needs_input |
| confiança (0 a 1) | |

## 2. Demanda

| Campo | Valor |
|---|---|
| objective | (resultado de negócio esperado) |
| demand_type | conversion / content / crm / product_ux / video / brand / research |
| canais | |
| público (resumo) | |
| oferta (resumo) | |
| prazo | AAAA-MM-DD |
| prioridade operacional | urgent / high / normal / low (priority e priority_rationale do demand-intake) |

## 3. Risco

| Campo | Valor |
|---|---|
| risk_level | low (só uso interno) / medium (toda ação externa, no mínimo) / high |
| claims sensíveis presentes | price / guarantee / result / authority / testimonial / comparison / health / financial / nenhum (ainda: data_privacy e urgência/escassez também acionam G3) |
| política aplicada | (referência a `data/risk-policy.yaml`) |
| justificativa | (fatos com fonte; em caso de incerteza, tratado como high) |

## 4. Workflow escolhido

| Campo | Valor |
|---|---|
| workflow_id | wf-copy-production / wf-campaign-launch / wf-fast-variation / wf-performance-loop / wf-content-repurposing |
| motivo da escolha (1 frase; fast lane só para uso interno ou teste) | |
| alternativa descartada | |

## 5. Passos

| # | Agente | Task | Entradas | Contrato de saída | Aprovação humana | Gate | Critérios de sucesso |
|---|--------|------|----------|-------------------|------------------|------|----------------------|
| 1 | brief-master | tasks/create-brief.md | demand-intake | brief | não | — | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |

(Acrescente linhas conforme o workflow. Cada task deve existir em `squads/copy-squad/tasks/` e seguir o padrão `tasks/{id}.md`. Quem produz não valida o próprio artefato.)

## 6. Gates humanos

| Gate | Posição no plano | Obrigatório? | Responsável |
|---|---|---|---|
| G1 — brief | após consolidate-brief e prepare-approval-package | medium e high | approval-owner |
| G2 — ângulo | após generate-angles-hooks, QG-ANGLES (copy-chief) e prepare-approval-package (copy-publisher) | high ou campanha multi-ativo | approval-owner |
| G3 — claims | G3 de oferta junto do G1 (high ou claim sensível); G3 de texto após check-compliance / fact-check-claims e prepare-approval-package | claim sensível, data_privacy ou urgência/escassez | approval-owner |
| G4 — final | após prepare-approval-package; o preflight contra-assinado pelo copy-chief é pós-decisão, antes de o humano ou a sessão principal executar | toda ação externa (medium e high) | approval-owner |
| G5 — correção | quando houver correção humana (correct-agent-failure, sem approval-request) | sempre que ocorrer | approval-owner |

O pedido de G1 a G4 (e da amostragem de uso interno, gate SAMPLING) é sempre produzido pelo copy-publisher (prepare-approval-package); em G1, G2 e G3 de oferta, asset_id = campaign_id. Nenhum subagent executa ação externa: a execução é do humano ou da sessão principal. O QG-INTAKE deste plano é executado pelo brief-master; o copy-chief faz só a autochecagem.

## 7. Informação faltante e perguntas

| # | Pergunta (máx. 5) | Por que importa | Quem responde |
|---|-------------------|-----------------|---------------|
| 1 | | | |

missing_information: (lista)

## 8. Esforço e próximo passo

| Campo | Valor |
|---|---|
| estimated_effort | (faixa, ex.: 3 a 5 dias úteis) |
| SLA por fase | |
| next_action | (agente, task e entrada do próximo passo) |

## 9. Premissas e fontes

- assumptions: (suposições explícitas, nunca sobre preço, garantia, prazo ou resultado)
- sources: (título, locator, tipo: primary / official / customer / internal / secondary)

## 10. Verificação antes de emitir

- [ ] `workflow_id` entre os 5 do squad
- [ ] Todas as tasks existem e seguem `tasks/{id}.md`
- [ ] Gates exigidos pelo risco presentes, cada gate humano precedido de prepare-approval-package
- [ ] QG-INTAKE executado pelo brief-master (validador), não pelo copy-chief
- [ ] Nenhum passo viola AP05 (produtor diferente de validador)
- [ ] Perguntas pendentes ≤ 5
- [ ] Nenhum texto de copy no plano
- [ ] Validado em `contracts/execution-plan.schema.json`
