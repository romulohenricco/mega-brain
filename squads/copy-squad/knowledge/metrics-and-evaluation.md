# Métricas e avaliação dos agentes

> Não avalie um agente apenas pelo texto. Avalie se ele cumpriu o contrato, usou as ferramentas corretas, respeitou restrições e contribuiu para o resultado. O indicador mais importante não é "quantos textos o squad produziu", mas **quantas decisões comerciais corretas ele acelerou com qualidade, segurança e retorno mensurável**.

## 1. As três camadas

| Camada | Pergunta | Exemplos |
|---|---|---|
| **Qualidade** | O output é bom e está correto? | Clareza, aderência à oferta, precisão factual, ausência de claims sem suporte |
| **Operacional** | O agente executou bem o trabalho? | Revisões necessárias, tempo, custo por peça, taxa de retrabalho, latência |
| **Negócio** | O output contribuiu para o resultado? | Conversão, CPL, CPA, receita por sessão, retenção |

Cada avaliação é registrada em `agent-evaluation` (campo `layer` = `quality`, `operational` ou `business`) e cada execução em `agent-run`. Metas por agente ficam em `data/agent-metrics.yaml`; a rubrica de nível, em `data/seniority-matrix.yaml`.

## 2. Métricas por agente

| Agente | Qualidade | Operacional | Negócio |
|---|---|---|---|
| `copy-chief` | Aderência ao fluxo, handoff correto, completude do plano | Taxa de retrabalho, latência de roteamento, escalonamentos | Tempo até a primeira entrega, throughput |
| `brief-master` | Completude do brief, perguntas relevantes, ausência de suposições | Idas e voltas, tempo até aprovação | Redução de retrabalho na produção |
| `audience-voc` | Fidelidade às evidências, cobertura de objeções, frases com fonte | Fontes analisadas, lacunas apontadas | Reuso das frases nos ativos aprovados |
| `offer-strategist` | Prova verificada por promessa, clareza do mecanismo | Claims enviados ao G3, retrabalho de oferta | Taxa de conversão da oferta |
| `brand-voice-guardian` | Precisão do guia, consistência entre peças | Tempo de revisão, issues por peça | Redução de desvios de marca |
| `research-analyst` | Precisão factual, cobertura de fontes, citações verificáveis | Fontes por brief, lacunas detectadas, tempo | Qualidade percebida pelos copywriters |
| `hook-angle-creator` | Originalidade, especificidade, diversidade (20 ou mais ângulos) | Ângulos aprovados, taxa de seleção | CTR inicial, engajamento |
| `conversion-copywriter` | Clareza, persuasão, aderência à oferta, CTA, ausência de claims sem suporte | Revisões necessárias, tempo, custo por peça | Conversão, CPL, CPA, receita por sessão |
| `content-copywriter` | Relevância, profundidade, originalidade, SEO, precisão | Tempo de produção, cobertura de tópicos | Tráfego orgânico, leads, tempo na página |
| `ux-writer` | Clareza, consistência, acessibilidade | Retrabalho com produto | Ativação, conclusão de onboarding, menos suporte |
| `video-social-scriptwriter` | Força do hook, retenção, aderência à plataforma | Retenção média, taxa de conclusão | CTR, leads, vendas atribuídas |
| `email-crm-copywriter` | Relevância por segmento, clareza, CTA, conformidade | Entrega, abertura, clique, descadastro | Conversão, receita por e-mail, retenção |
| `localization-specialist` | Naturalidade, fidelidade ao sentido e à persuasão | Notas de adaptação, rechecagens | Desempenho por mercado |
| `copy-editor` | Clareza, concisão, preservação de fatos | Redução de palavras, nº de alterações, tempo | Melhora de conversão pós-edição |
| `compliance-checker` | Cobertura de claims, precisão da detecção, falsos positivos e negativos | Tempo de revisão, bloqueios, exceções | Redução de risco, aprovações sem retrabalho |
| `cro-analyst` | Qualidade da hipótese, rigor estatístico, priorização | Testes lançados e concluídos, ciclos por semana | Lift de conversão, receita incremental |
| `knowledge-curator` | Relevância da recuperação, precisão, cobertura | Recuperação útil, lacunas, tempo de busca | Reuso de ativos, menor custo por campanha |
| `copy-publisher` | Hash sempre obtido de `approval_tools.py`; verificação correta de validade | Taxa de VETO por divergência, tempo de pacote | Entregas sem incidente |

## 3. Métricas autônomas (comuns a todos os agentes)

| Métrica | Como medir |
|---|---|
| Taxa de conclusão | `agent-run.status = success` dividido pelo total de execuções |
| Aderência ao contrato | Saída valida no schema do contrato sem correção manual |
| Precisão de uso de ferramentas | Ferramentas e arquivos corretos por passo da task |
| Aderência ao plano | Passos executados contra passos do `execution-plan` |
| Tempo até a conclusão | `finished_at` menos `started_at` |
| Custo por tarefa | `cost_usd`, `tokens_in` e `tokens_out` |
| Taxa de recuperação de erro | Falhas resolvidas em até 2 ciclos de retrabalho |
| Segurança | Zero claims inventados, zero ação externa sem aprovação |

## 4. Quality gates automáticos

Escala de 0 a 1: **APPROVE ≥ 0.80**, **REVIEW 0.60 a 0.79**, **VETO < 0.60** ou qualquer veto_condition. Em REVIEW, o retrabalho tem no máximo 2 ciclos (`REWORK_MAX_CYCLES`); esgotado, o fluxo vai para `escalated_to_copy_chief`, nunca direto a `vetoed`. No VETO, escala-se ao `copy-chief` e, se necessário, ao `approval-owner`. O executor de cada gate (distinto do produtor) está em `data/quality-gates.yaml` e na tabela de `knowledge/squad-operating-model.md`. Gates: `QG-INTAKE`, `QG-BRIEF`, `QG-RESEARCH`, `QG-ANGLES`, `QG-DRAFT`, `QG-EDIT`, `QG-BRAND`, `QG-COMPLIANCE`, `QG-LOCALIZATION`, `QG-PUBLISH-PREFLIGHT`, `QG-LEARNING` (`data/quality-gates.yaml`).

O scorecard de avaliação está em `checklists/agent-evaluation-scorecard.md`.

## 5. Rigor estatístico (cro-analyst)

- Comparar sempre com baseline, meta e período anterior.
- Não atribuir causalidade sem isolamento adequado de variáveis.
- Considerar o tamanho da amostra antes de declarar vencedor.
- **Critério padrão de vencedor (D20):** `AB_CONFIDENCE_LEVEL = 0.95` e `AB_MIN_SAMPLE_PER_VARIANT` (token em `data/token-registry.yaml`). Sem atingir **os dois**, `winner_declared = false`.
- `significance.confidence_level` é um **número** (por exemplo, `0.95`), nunca texto como "93%" ou "não atingido". Sem teste, o campo é omitido.
- Critério diferente do padrão só vale se estiver **pré-registrado** no `design-ab-test` antes do teste; o `cro-analyst` não define o critério depois de ver o resultado.
- **Nunca declarar que uma variação venceu** sem significância ou critério definido; o campo `winner_declared` só é `true` com `significance` preenchido e o critério atendido.
- Priorizar hipóteses por ICE (impacto, confiança, facilidade).
- Separar FATOS com fonte, RECOMENDAÇÃO com confiança e HIPÓTESE com validação requerida (campo `epistemic`).

## 6. Cadência

| Frequência | O que revisar |
|---|---|
| Diário | Fila de aprovação e aprovações pendentes (pedidos vencidos permanecem pendentes e são reenviados ou escalados), bloqueios, falhas |
| Semanal | Performance por campanha, canal e agente; amostragem de baixo risco |
| Mensal | Atualização de voz da marca, provas, objeções, prompts e rubricas (delegada aos donos de cada item) |
| Trimestral | Arquitetura, modelos, custos, permissões e riscos |

As quatro cadências são cobertas por `tasks/monitor-pipeline.md` (D19); o dono é o `copy-chief`. Como o `copy-chief` não avalia a si mesmo (AP05), as avaliações das métricas do próprio `copy-chief` são registradas pelo `approval-owner` ou por script.

## 7. Telemetria

- `.data/copy-squad/_telemetry/agent-runs.jsonl`: uma linha por execução (`agent-run`).
- `.data/copy-squad/_telemetry/agent-evaluations.jsonl`: uma linha por avaliação (`agent-evaluation`).
- Ambos são append-only. Não gravar conteúdo bruto de clientes na telemetria; use referências (`input_ref`, `output_ref`).

## 8. Indicador principal

**Decisões comerciais corretas aceleradas, com qualidade, segurança e retorno mensurável.** Volume de texto é indicador de custo, não de valor. Um squad que produz menos peças, mas com menos retrabalho, zero claim inventado e aprendizado registrado, está performando melhor.
