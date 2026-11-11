---
task: audit-ux-copy
name: audit-ux-copy
task_name: "Auditar microcopy existente"
version: "1.0.0"
squad: copy-squad
task_id: audit-ux-copy
category: quality
difficulty: intermediate
responsavel: '@ux-writer'
responsavel_type: Agent
responsible_executor: ux-writer
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 45-90min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: current_microcopy
  tipo: inventário de textos atuais da interface (capturas, planilha ou exportação)
  obrigatorio: true
- campo: product_flow
  tipo: fluxo e estados da interface com comportamento confirmado
  obrigatorio: true
- campo: glossary
  tipo: glossário do produto
  obrigatorio: false
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: false
Saida:
- campo: ux_copy_audit
  tipo: contract:ux-copy (copy reescrita; problemas e pendências em meta.assumptions e em perguntas abertas)
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [current-microcopy, product-flow, glossary, brand-voice-guide]
output: [ux-copy]
action_items:
  - "Inventariar os textos atuais por tela e estado"
  - "Classificar problemas por severidade e tipo"
  - "Detectar termos inconsistentes contra o glossário"
  - "Propor reescrita elemento a elemento"
  - "Registrar problemas, suposições e perguntas ao produto"
  - "Priorizar correções por impacto e esforço"
  - "Autoverificar, persistir e emitir envelope"
acceptance_criteria:
  - "Inventário cobre 100% dos textos fornecidos, sem omitir elementos"
  - "Cada problema classificado como critical, medium ou low, com o trecho original e o motivo"
  - "Cada problema critical ou medium com reescrita proposta no contrato ux-copy"
  - "Divergências de termo consolidadas com proposta de termo único"
  - "Lista de correções priorizada por impacto e esforço"
  - "Nenhuma reescrita afirma comportamento não confirmado"
  - "Score >= 0.80 em checklists/ux-copy-checklist.md aplicado à versão reescrita"
pre_condition: "Microcopy atual disponível e fluxo descrito; acesso ao glossário ou autorização para propor um"
post_condition: "Versão reescrita persistida, problemas e pendências registrados em meta.assumptions e envelope emitido ao copy-editor"
checklist: checklists/ux-copy-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: null
workflows: [wf-copy-production]
performance:
  error_handling: "needs_input se o inventário estiver incompleto; marcar como não auditável o texto sem contexto de tela; nunca presumir comportamento do sistema"
---

# Task: Auditar microcopy existente

## Objetivo

Revisar a microcopy já existente de um produto, identificar problemas de clareza, culpa, consistência de termos, acessibilidade, limites de espaço e comportamento afirmado sem confirmação, e entregar uma versão reescrita e priorizada. Esta tarefa não escreve copy de aquisição; avalia e melhora texto de uso do produto.

## Quando usar / quando não usar

| Usar quando | Não usar quando |
|---|---|
| O produto já tem textos e há queixas de confusão, erro ou chamados de suporte | Não existe texto atual: usar write-ux-microcopy |
| Será feito um redesenho ou padronização de voz de produto | O objetivo é revisar landing page ou campanha: usar edit-draft e tasks de conversão |
| É preciso unificar glossário e termos | O pedido é auditoria jurídica ou de privacidade: encaminhar a compliance e jurídico |
| Há métricas de erro ou abandono por etapa a melhorar | O inventário não pode ser obtido: devolver needs_input |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| current_microcopy | inventário de textos | Sim | produto, design ou engenharia |
| product_flow | fluxo e estados | Sim | produto |
| glossary | glossário do produto | Não | produto |
| brand_voice_guide | contracts/brand-voice-guide.schema.json | Não | brand-voice-guardian |
| métricas de erro e abandono | números fornecidos pelo solicitante | Não | analytics do produto |

## Passos

1. **Inventariar.** Organizar os textos por tela, estado e elemento, preservando o texto original exato e o contexto; registrar o que não pôde ser contextualizado.
2. **Confirmar o comportamento.** Cruzar cada texto com o fluxo para identificar afirmações sobre o sistema; marcar as não confirmadas.
3. **Avaliar dimensões.** Para cada elemento verificar clareza, estrutura de erro, culpa, tom, tamanho, termos, acessibilidade e consistência entre telas.
4. **Classificar problemas.** Atribuir severidade (critical, medium, low), tipo e motivo; critical inclui culpa ao usuário, informação enganosa, erro sem ação e risco de acessibilidade grave.
5. **Consolidar termos.** Listar sinônimos concorrentes para o mesmo conceito e propor o termo do glossário (ou novo termo proposto).
6. **Reescrever.** Propor texto novo para todo problema critical ou medium e, quando barato, também para low, respeitando limite de caracteres.
7. **Registrar acessibilidade.** Incluir accessibility_note nos elementos reescritos que tenham risco.
8. **Priorizar.** Ordenar correções por impacto no usuário (erro, abandono, suporte) e esforço de implementação; indicar o conjunto de primeira onda.
9. **Registrar pendências.** Colocar em meta.assumptions os problemas encontrados, as suposições e as perguntas abertas ao produto; não afirmar o que não foi confirmado.
10. **Autoverificar e persistir.** Aplicar checklists/ux-copy-checklist.md à versão reescrita, corrigir até 0.80, gravar a nova versão e emitir envelope.

## Saída

- **Contrato:** `contracts/ux-copy.schema.json` com a copy reescrita; o relatório de problemas (severidade, trecho original, motivo) e as perguntas abertas ficam em `meta.assumptions` e em campo `reason` do envelope, pois o contrato não tem campo próprio de issues.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope:** from_agent `ux-writer`, to_agent `copy-editor`, artifact_type `ux-copy`, status `ready` ou `needs_input`; reason resume número de problemas por severidade e ondas de implementação.

## Acceptance Criteria (Critérios de aceite)

- Inventário completo e rastreável.
- Problemas classificados e justificados.
- Reescritas dentro dos limites, com glossário consistente.
- Priorização por impacto e esforço registrada.
- Perguntas ao produto explícitas.
- Score >= 0.80 na versão reescrita.

## Quality gate e checklist

- **Gate:** QG-DRAFT sobre a versão reescrita; produtor ux-writer, executor (validador) copy-chief com `checklists/ux-copy-checklist.md`. O copy-editor revisa depois. Aplicar a reescrita na interface é ação externa (`update_page`): risco mínimo `medium` e G4.
- **Checklist:** `checklists/ux-copy-checklist.md` (escala 0 a 1; APPROVE >= 0.80).
- Retrabalho máximo de 2 ciclos.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Inventário parcial | Auditar o que existe e listar as telas não cobertas em meta.assumptions |
| Texto sem contexto de tela | Marcar como não auditável e pedir captura ao produto |
| Conflito com glossário vigente | Respeitar o glossário e registrar proposta de mudança para decisão humana |
| Descoberta de problema legal ou de privacidade | Sinalizar ao compliance-checker via copy-chief; não reescrever termos legais |
| Volume muito grande | Priorizar fluxos críticos (cadastro, pagamento, erro) e planejar ondas |

## Handoff

Para `copy-editor`. O relatório priorizado segue ao copy-chief para decisão de produto. Mudanças de glossário voltam ao approval-owner. A aplicação do texto na interface é feita por produto e engenharia somente após `approval-decision` `approved` com `payload_sha256` igual (`approved_with_edits` abre nova rodada).

## Exemplo

Entrada resumida (exemplo ilustrativo): auditoria de três mensagens de um SaaS de fluxo de caixa.

```json
{
  "surface": "error",
  "context": "Auditoria de mensagens de erro do cadastro e da importação",
  "copy": [
    {"element": "erro_importacao", "text": "Não conseguimos ler o arquivo. Use o formato CSV com as colunas data, descrição e valor, e tente importar de novo.", "character_limit": 140, "accessibility_note": "Anunciar via aria-live assertive"},
    {"element": "erro_senha", "text": "A senha precisa de ao menos 8 caracteres. Você pode usar letras, números e símbolos.", "character_limit": 100, "accessibility_note": "Mostrar a regra antes do erro, não depender de cor"}
  ],
  "glossary_terms_used": ["importação", "senha"],
  "meta": {
    "assumptions": [
      "Problema critical: 'Você digitou a senha errada' culpava o usuário (reescrito).",
      "Problema medium: 'Entrada inválida' sem ação (reescrito).",
      "Pergunta ao produto: o formato CSV é o único aceito hoje?"
    ]
  }
}
```

## Anti-padrões

- Reescrever sem entender o comportamento do sistema.
- Auditar apenas o tom e ignorar acessibilidade e consistência.
- Trocar termos sem consultar o glossário.
- Entregar lista longa de problemas sem priorização.
- Tratar a auditoria como oportunidade de colocar copy promocional no produto.
- Aplicar mudanças diretamente na interface.
