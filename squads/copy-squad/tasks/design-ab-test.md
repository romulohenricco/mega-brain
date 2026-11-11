---
task: design-ab-test
name: design-ab-test
task_name: "Desenhar teste A/B"
version: "1.0.0"
squad: copy-squad
task_id: design-ab-test
category: intelligence
difficulty: advanced
responsavel: '@cro-analyst'
responsavel_type: Agent
responsible_executor: cro-analyst
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 30-60min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: hypothesis
  tipo: contract:performance-analysis (item de hypotheses priorizado)
  obrigatorio: true
- campo: baseline_e_volume
  tipo: dados do solicitante (taxa atual, tráfego por período)
  obrigatorio: true
- campo: brief
  tipo: contract:brief
  obrigatorio: true
Saida:
- campo: test_design
  tipo: contract:performance-analysis (campo hypotheses[].test_design e next_actions)
  persistido_em: .data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json
input: [performance-analysis, brief, baseline_e_volume]
output: [performance-analysis]
action_items:
  - "Escolher a hipótese priorizada e confirmar variável única"
  - "Definir métrica primária e métricas de proteção"
  - "Definir MDE e calcular tamanho de amostra por variação"
  - "Estimar duração a partir do volume e cobrir ciclo semanal"
  - "Registrar critério de parada e de decisão antes de iniciar (padrão: AB_CONFIDENCE_LEVEL e AB_MIN_SAMPLE_PER_VARIANT)"
  - "Listar riscos, aprovações necessárias e plano de registro do aprendizado"
acceptance_criteria:
  - "Desenho com seis elementos: hipótese, variável única, métrica primária, MDE, tamanho de amostra e duração"
  - "Critério de parada e de decisão registrado antes do início do teste"
  - "Cálculo de amostra com premissas explícitas (baseline, poder, significância)"
  - "Duração cobre pelo menos um ciclo semanal completo"
  - "Métricas de proteção (guardrails) definidas"
  - "Execução em produção condicionada a approval-decision (G4)"
  - "Score do checklists/cro-test-checklist.md >= 0.80"
pre_condition: "Hipótese priorizada disponível; taxa atual e volume de tráfego informados; ferramenta de teste ou processo de divisão de tráfego conhecido"
post_condition: "Desenho de teste gravado no performance-analysis; pendências de aprovação e de dados registradas; teste pronto para o pacote de aprovação"
checklist: checklists/cro-test-checklist.md
quality_gate: null
human_gate: null
skill: null
workflows: [wf-performance-loop]
performance:
  error_handling: "needs_input se faltar baseline ou volume; teste com mais de uma variável é devolvido para divisão; nunca iniciar ou alterar página sem approval-decision"
---

# Task: Desenhar teste A/B

## Objetivo

Definir, antes da execução, um teste A/B que consiga responder à hipótese com rigor: uma variável, uma métrica primária, um efeito mínimo detectável (MDE), um tamanho de amostra, uma duração e um critério de parada. O objetivo é impedir vencedores falsos, testes eternos e conclusões tiradas depois do fato.

## Quando usar / quando não usar

**Usar quando:**
- Há hipótese priorizada (`build-cro-hypotheses`) e o squad vai testá-la.
- O `wf-performance-loop` chega à fase de teste.
- É preciso saber quanto tempo e quanto tráfego um teste exige antes de investir.

**Não usar quando:**
- Não há tráfego mínimo para detectar o MDE desejado (nesse caso, redefinir o MDE, usar métrica intermediária ou testar qualitativamente).
- A mudança é correção óbvia de erro (ortografia, link quebrado): corrigir, não testar.
- O pedido é interpretar resultado de teste já rodado (use `analyze-performance`).

## Entradas

| Campo | Contrato / formato | Obrigatório | Origem |
|---|---|---|---|
| hypothesis | item de `hypotheses` com `ice` e `priority` | Sim | `build-cro-hypotheses` |
| baseline_e_volume | taxa atual da métrica primária e volume por semana | Sim | Solicitante ou análise anterior |
| brief | `contract:brief` | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| restrições operacionais | ferramenta de teste, divisão de tráfego, janelas de campanha | Recomendado | Solicitante |
| risk-policy | `data/risk-policy.yaml` | Sim (leitura) | Squad |

## Passos

1. **Selecionar e validar a hipótese.** Confirme que há variável única e métrica primária. Se houver duas variáveis, devolva para divisão em `build-cro-hypotheses`.
2. **Definir a métrica primária.** Uma só, ligada ao KPI do brief (por exemplo, taxa de conversão do formulário, clique no CTA, taxa de resposta). Defina numerador, denominador e janela de atribuição.
3. **Definir métricas de proteção.** Indicadores que não podem piorar (por exemplo, taxa de descadastro, taxa de reembolso, qualidade do lead). Defina o limite de tolerância.
4. **Definir o MDE.** O menor efeito que justifica a mudança (absoluto ou relativo). Registre a justificativa de negócio (por exemplo, o que compensa o custo de implementação).
5. **Calcular o tamanho de amostra por variação.** Aproximação de planejamento com poder de 80% e significância de 5% bilateral: `n ≈ 16 × p × (1 − p) / δ²`, em que `p` é a taxa de baseline e `δ` é o MDE absoluto. Exemplo ilustrativo: `p = 0,03` e `δ = 0,006` (20% relativo) dá `n ≈ 16 × 0,03 × 0,97 / 0,000036 ≈ 12.900` visitantes por variação. Registre as premissas.
6. **Estimar a duração.** Duração = amostra total necessária / tráfego diário disponível. Arredonde para cima até ciclos semanais completos e não encerre antes do mínimo planejado.
7. **Definir a alocação.** Divisão de tráfego (por exemplo, 50/50), unidade de aleatorização (visitante, usuário, envio) e critérios de exclusão. Garanta que as variações rodem no mesmo período.
8. **Registrar critério de parada e de decisão antes de iniciar.** Escreva: amostra mínima, duração mínima, limite de significância, métricas de proteção e regra de empate. O padrão é `AB_CONFIDENCE_LEVEL` (0,95, equivalente a p < 0,05) e amostra por variante >= `AB_MIN_SAMPLE_PER_VARIANT` (1000 sessões ou destinatários), usando o maior entre esse mínimo e o tamanho calculado no passo 5. Critério diferente só é aceito se registrado aqui, antes do início, com justificativa; depois do início ele não pode ser alterado (`analyze-performance` aplica o critério registrado) ("sem diferença detectável: manter a versão atual"). Proíba a regra de parar no primeiro pico.
9. **Mapear dependências e riscos.** Claims envolvidos (G3), execução em produção (G4), dependência de outro agente (por exemplo, `conversion-copywriter` para a variação B), risco de sobreposição com outros testes (efeito de interação).
10. **Definir o registro do aprendizado.** Indique que, ao final, `analyze-performance` interpreta o resultado e `register-learning` grava o `learning-record`, também em caso de empate ou resultado negativo.
11. **Montar bloco epistêmico.** FATOS (baseline e volume fornecidos, com fonte), RECOMENDAÇÃO (desenho, com confiança) e HIPÓTESE (efeito esperado).
12. **Validar e persistir.** Aplique o checklist, grave no `performance-analysis`, registre `agent-run` e emita o envelope; encaminhe ao `copy-chief`. Quando o teste for para produção, o `copy-chief` aciona o `copy-publisher` para montar o pacote de aprovação do G4 (`prepare-approval-package`); o G4 é humano e o `copy-chief` apenas contra-assina o preflight depois da decisão. Nada é executado antes disso.

## Saída

- **Contrato:** `contracts/performance-analysis.schema.json`: o desenho aparece em `hypotheses[].test_design` e as ações em `next_actions`; premissas em `meta.assumptions`.
- **Fase pré-teste (E6):** esta task entrega `performance-analysis` com `analysis_phase: "planning"`. Nessa fase só `hypotheses` e `next_actions` são obrigatórios, além de `meta` e `epistemic`. Os campos de resultado (`period`, `metrics`, `sample_size`, `findings`, `winner_declared`) ficam ausentes: não preencha valores neutros nem estime números antes do teste. Eles só se tornam obrigatórios na fase `result`, produzida por `analyze-performance`.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/08-performance/performance-analysis-{yyyymmdd}-{n}.json`.
- **Template humano:** `templates/performance-report-tmpl.md` (seção Plano de teste).
- **Envelope de handoff:**
  - `from_agent: cro-analyst`; `to_agent: copy-chief`
  - `artifact_type: performance-analysis`; `status: ready` ou `needs_approval`
  - `human_approval_required: true` quando o teste for executado em produção; `gate: null` (o envelope para o `copy-chief` não carrega gate G4: o pedido de G4 é montado só pelo `copy-publisher`)

## Acceptance Criteria (Critérios de aceite)

- Seis elementos do desenho presentes e coerentes (hipótese, variável única, métrica primária, MDE, amostra e duração).
- Premissas do cálculo explícitas e reproduzíveis.
- Critério de parada e de decisão escrito antes do início, incluindo regra de empate; o padrão é `AB_CONFIDENCE_LEVEL` (0,95) e `AB_MIN_SAMPLE_PER_VARIANT`, e qualquer desvio está pré-registrado com justificativa.
- Métricas de proteção com limite definido.
- Duração em ciclos semanais completos.
- Dependências, aprovações (G3 e G4) e riscos listados.
- Nenhuma execução iniciada pelo analista.

## Quality gate e checklist

- **Checklist:** `checklists/cro-test-checklist.md`.
- **Quality gate:** sem QG próprio; verificação pelo checklist (APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60).
- **Veto automático:** teste com mais de uma variável, sem critério de parada ou sem métrica primária.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Faltam baseline ou volume | `needs_input`; não calcular amostra com número inventado |
| Tráfego insuficiente para o MDE | Aumentar o MDE, estender a duração, usar métrica intermediária ou combinar com teste qualitativo; registrar o trade-off |
| Duas variáveis na hipótese | Devolver para divisão ou propor testes sequenciais |
| Testes concorrentes na mesma página | Registrar risco de interação e recomendar sequenciamento |
| Pedido para encerrar antes do critério | Recusar e explicar; permitir somente com justificativa registrada e resultado rotulado como não conclusivo |
| Claim novo na variação | Marcar `needs_approval` e acionar G3 antes de produzir a variação |

## Handoff

- **Para `copy-chief`:** desenho completo, para solicitar a produção da variação ao copywriter adequado e o pacote de aprovação ao `copy-publisher` (G4).
- **Para `knowledge-curator`:** hipótese e desenho, para registro como `testing` quando o teste iniciar.
- Após o término, o ciclo volta para `analyze-performance`.

## Exemplo

Entrada resumida (exemplo ilustrativo): hipótese de mover o bloco de garantia para acima do CTA de preço em uma página de vendas de um SaaS de fluxo de caixa; baseline do clique no CTA de 3,0%; tráfego de 4.500 visitantes por semana.

Trecho da saída:

```json
{
  "analysis_phase": "planning",
  "meta": {
    "schema_version": "1.0.0",
    "artifact_id": "prf-lp-saas-teste-garantia-20261110",
    "artifact_type": "performance-analysis",
    "campaign_id": "camp-exemplo",
    "business": "exemplo-negocio",
    "produced_by": "cro-analyst",
    "produced_at": "2026-11-10T14:30:00-03:00",
    "version": 1,
    "prompt_version": "1.0.0",
    "model": "sonnet",
    "status": "ready",
    "confidence": 0.6,
    "risk_level": "medium",
    "assumptions": ["Exemplo ilustrativo; dados não são resultados reais."]
  },
  "hypotheses": [
    {
      "hypothesis": "Se movermos a garantia para acima do CTA de preço, então o clique no CTA deve aumentar.",
      "variable": "posição do bloco de garantia",
      "expected_effect": "aumento relativo de 20% (de 3,0% para 3,6%)",
      "test_design": "A/B 50/50 por visitante. Métrica primária: clique no CTA de preço. Proteção: taxa de reembolso e envios de formulário não podem cair mais de 5% relativo. MDE: 0,6 ponto percentual. Amostra: cerca de 12.900 visitantes por variação (premissas: baseline 3,0%, poder 80%, significância 5% bilateral). Duração: tráfego de 4.500/semana implica cerca de 6 semanas; mínimo 6 semanas completas. Critério de parada: amostra atingida (maior entre o cálculo e `AB_MIN_SAMPLE_PER_VARIANT`) e confiança >= 0,95 (p < 0,05); empate mantém a versão atual. Proibido encerrar antes.",
      "priority": "high",
      "ice": {"impact": 8, "confidence": 6, "ease": 9}
    }
  ],
  "epistemic": {
    "facts": ["Baseline do clique no CTA de 3,0% e tráfego de 4.500 visitantes por semana [FONTE: dados fornecidos, exemplo ilustrativo]."],
    "recommendations": ["Posição: teste A/B 50/50 de variável única. Justificativa: tráfego sustenta o MDE em cerca de 6 semanas. Confiança: MEDIA."],
    "hypotheses": ["Garantia acima do CTA aumenta o clique em 20% relativo (sem evidência direta; validação requerida: o próprio teste)."]
  },
  "next_actions": [
    "Solicitar variação B ao conversion-copywriter (sem alterar texto da garantia).",
    "Pedir ao copy-chief que acione o copy-publisher para o pacote de aprovação G4 antes de executar em produção.",
    "Ao fim, executar analyze-performance e register-learning."
  ]
}
```

Observação: se o tráfego for considerado insuficiente para 6 semanas, o analista propõe aumentar o MDE ou usar métrica intermediária e registra o trade-off, sem reduzir o rigor em silêncio.

## Anti-padrões

- Teste com várias variáveis alteradas ao mesmo tempo.
- Definir o critério de decisão depois de ver os dados.
- Encerrar no primeiro pico de significância.
- Amostra calculada com baseline inventado.
- Ignorar ciclos semanais e sazonalidade.
- Ausência de métricas de proteção.
- Executar ou alterar página sem approval-decision.
- Não registrar aprendizado de testes empatados ou negativos.
