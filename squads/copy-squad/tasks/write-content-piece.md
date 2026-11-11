---
task: write-content-piece
name: write-content-piece
task_name: "Escrever peça de conteúdo"
version: "1.0.0"
squad: copy-squad
task_id: write-content-piece
category: production
difficulty: intermediate
responsavel: '@content-copywriter'
responsavel_type: Agent
responsible_executor: content-copywriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 45-90min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: research_packet
  tipo: contract:research-packet
  obrigatorio: true
- campo: angle
  tipo: contract:angles
  obrigatorio: false
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: false
Saida:
- campo: content_piece
  tipo: contract:content-piece
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, research-packet, angles, brand-voice-guide]
output: [content-piece]
action_items:
  - "Validar brief e research packet; parar com needs_input se faltar algo crítico"
  - "Consultar a biblioteca para evitar duplicação"
  - "Definir tese, intenção de busca e outline"
  - "Redigir o corpo com fontes citadas"
  - "Marcar afirmações que exigem revisão especializada"
  - "Preencher SEO e CTA"
  - "Autoverificar, persistir a versão e emitir envelope para o copy-editor"
acceptance_criteria:
  - "JSON válido contra contracts/content-piece.schema.json"
  - "100% das afirmações factuais com fonte em meta.sources ou marcadas em needs_expert_review"
  - "Tese declarada em até 30 palavras e respondida pelo corpo"
  - "Quando houver seo: meta_title com até 60 e meta_description com até 160 caracteres e search_intent declarada"
  - "Nenhuma sobreposição não justificada com peça existente da biblioteca"
  - "Score da autoverificação >= 0.80 em checklists/content-quality-checklist.md"
pre_condition: "Brief com status ready ou approved e research packet com fatos classificados como verified ou unverified"
post_condition: "Versão v{n} do content-piece persistida sem sobrescrever versões anteriores e envelope emitido para o copy-editor"
checklist: checklists/content-quality-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: null
workflows: [wf-copy-production]
performance:
  error_handling: "needs_input com até 5 perguntas; nunca inventar fonte, dado ou depoimento; claim sensível vira needs_expert_review"
---

# Task: Escrever peça de conteúdo

## Objetivo

Produzir uma peça editorial (artigo, newsletter, post, carrossel, guia, estudo de caso, white paper, manifesto ou tagline) que entrega valor real ao leitor, sustenta suas afirmações em fontes do research packet, atende à intenção de busca declarada e termina em um CTA honesto, pronta para edição pelo copy-editor.

## Quando usar / quando não usar

| Usar quando | Não usar quando |
|---|---|
| A demanda é educar, construir autoridade ou nutrir o público | A demanda é vender diretamente (página de vendas, anúncio, e-mail de venda): usar tasks do conversion-copywriter ou do email-crm-copywriter |
| Há brief aprovado e research packet disponível | Falta brief ou research packet: devolver needs_input ao copy-chief |
| O formato é article, newsletter, post, carousel, guide, case_study, white_paper, manifesto ou tagline | O formato é roteiro de vídeo ou VSL (write-video-script) ou microcopy (write-ux-microcopy) |
| `demand_type: brand` (manifesto, tagline, posicionamento verbal) | `demand_type: research`: o entregável é research packet (build-research-packet) |
| É preciso conteúdo original para um tema ainda não coberto | O objetivo é derivar de um ativo existente: usar repurpose-asset |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | contracts/brief.schema.json | Sim | brief-master, 01-strategy/brief.json |
| research_packet | contracts/research-packet.schema.json | Sim | research-analyst, 02-research/research-packet.json |
| angle | contracts/angles.schema.json | Não | hook-angle-creator, 03-angles/angles.json |
| brand_voice_guide | contracts/brand-voice-guide.schema.json | Não | brand-voice-guardian, _brand/brand-voice-guide.json |
| formato | enum (article, newsletter, post, carousel, guide, case_study, white_paper, manifesto, tagline) | Sim | pedido ou brief.formats |
| palavras-chave e intenção de busca | texto | Não | brief ou pedido |

## Passos

1. **Validar insumos.** Confirmar que o brief está em ready ou approved e que o research packet traz fatos com status. Se faltar objetivo, público, canal ou formato, devolver needs_input com no máximo 5 perguntas.
2. **Consultar a biblioteca.** Verificar em `.data/copy-squad/{business}/_library/index.jsonl` se já existe peça com tese semelhante. Havendo, escolher outro recorte ou registrar a adaptação em meta.assumptions (heurística CS-CT-004).
3. **Definir tese e intenção.** Escrever a tese em uma frase, o que o leitor leva em 30 segundos e a intenção de busca (informational, navigational, commercial ou transactional).
4. **Montar o outline.** Estruturar título, argumentos, exemplos e conclusão. Cada seção precisa responder a um item do objetivo ou da objeção do público no brief.
5. **Redigir o corpo.** Escrever na voz da marca, explicar todo jargão na primeira ocorrência e responder à intenção nas primeiras 100 palavras quando houver SEO. Respeitar os limites do formato em data/channel-specs.yaml.
6. **Citar fontes.** Para cada afirmação factual, registrar a fonte em meta.sources (título, locator, tipo) e indicá-la no texto. Sem fonte, reescrever como opinião ou remover.
7. **Marcar revisões especializadas.** Listar em needs_expert_review as afirmações técnicas, de saúde, finanças, jurídicas ou comparativas; ajustar meta.risk_level conforme data/risk-policy.yaml.
8. **Preencher SEO e CTA.** Definir palavra-chave principal e secundárias, meta_title (até 60) e meta_description (até 160); escrever CTA coerente com o brief, sem urgência falsa.
9. **Autoverificar.** Aplicar checklists/content-quality-checklist.md; corrigir itens bloqueantes até score >= 0.80.
10. **Formatos de fundo de funil e de marca.**
    - `case_study` (estudo de caso): só com caso real documentado e autorizado pelo cliente (`usage_rights: granted`); estrutura situação, desafio, solução, resultado. Todo número de resultado vira claim `result` ou `testimonial`: `needs_approval`, risco `high` e G3. Sem caso real autorizado, devolver needs_input; nunca inventar caso, cliente ou número.
    - `white_paper`: tese, método, evidências e referências; cada dado com fonte em meta.sources; tema técnico, de saúde, financeiro ou jurídico entra em needs_expert_review.
    - `manifesto` e `tagline`: `demand_type: brand`; escrever 3 a 5 alternativas, sem promessa de resultado nem superlativo não comprovável. Mantêm risco `medium` quando forem publicados e passam obrigatoriamente pela revisão do `brand-voice-guardian` (QG-BRAND) antes do G4.
11. **Persistir e entregar.** Gravar `04-drafts/{asset_id}/v{n}.json` (nova versão, com `meta.artifact_id = {asset_id}-v{n}`), anexar o envelope em `handoffs.jsonl` e registrar o evento no journey log.

## Saída

- **Contrato:** `contracts/content-piece.schema.json` (meta com artifact_id de prefixo `cnt-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope de handoff:** `contracts/handoff-envelope.schema.json` com from_agent `content-copywriter`, to_agent `copy-editor`, artifact_type `content-piece`, status `ready`, gate `G3` quando houver claim sensível, `data_privacy` ou urgência/escassez, e `human_approval_required` true para risco medium ou high.

## Acceptance Criteria (Critérios de aceite)

- Peça válida contra o schema e persistida como nova versão.
- Zero afirmação factual sem fonte ou marcação.
- Tese única de até 30 palavras, coerente com o objetivo do brief.
- Meta title até 60 e meta description até 160 caracteres quando houver seo.
- Autoverificação com score >= 0.80.
- Envelope emitido com contagem de fontes e lista de revisões pendentes no campo reason.

## Quality gate e checklist

- **Gate:** QG-DRAFT; produtor content-copywriter, executor (validador) copy-chief com `checklists/content-quality-checklist.md`. A autoverificação do produtor não aprova o gate; edição, voz e compliance aplicam depois seus próprios gates.
- **Checklist:** `checklists/content-quality-checklist.md`. Escala 0 a 1: APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60 ou veto condition.
- Retrabalho máximo de 2 ciclos; persistindo a falha, escalar ao copy-chief.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Brief ausente ou não aprovado | Parar, status needs_input, pedir ao copy-chief |
| Research packet sem fontes para a tese | Reduzir o escopo da tese ou devolver ao research-analyst via copy-chief |
| Fonte inacessível ou sem data | Marcar como unverified e não usar a informação factual |
| Tema já coberto na biblioteca | Mudar recorte, atualizar com fonte nova ou propor atualização da peça existente |
| Claim sensível (preço, resultado, saúde, finanças) | Remover do corpo, listar em needs_expert_review, sinalizar G3 |
| Schema inválido | Corrigir e revalidar; não entregar JSON inválido |

## Handoff

Para `copy-editor` (edit-draft). Se a peça tiver claim sensível, o copy-chief aciona o compliance-checker após edição e voz. Nenhuma publicação sem `approval-decision` com `decision: approved` e `payload_sha256` igual ao do pedido; `approved_with_edits` abre nova rodada e nunca autoriza execução. Para `demand_type: brand`, o copy-chief aciona também o brand-voice-guardian.

## Exemplo

Entrada resumida (exemplo ilustrativo): brief de SaaS de fluxo de caixa para pequenas empresas, formato article, estágio problem_aware, palavra-chave "como organizar o fluxo de caixa".

```json
{
  "brief_id": "brf-fluxo-caixa-q1",
  "format": "article",
  "title": "Como organizar o fluxo de caixa da sua pequena empresa em 4 passos",
  "thesis": "Fluxo de caixa organizado nasce de um calendário de entradas e saídas, não de uma planilha mais bonita.",
  "outline": ["O que é fluxo de caixa", "Passo 1: liste entradas e saídas", "Passo 2: projete 90 dias", "Passo 3: revise semanalmente", "Passo 4: reserve margem"],
  "cta": "Baixe o modelo gratuito de projeção de 90 dias",
  "seo": {"primary_keyword": "como organizar o fluxo de caixa", "search_intent": "informational", "meta_title": "Como organizar o fluxo de caixa em 4 passos"},
  "needs_expert_review": []
}
```

## Anti-padrões

- Inventar cliente, caso, depoimento ou número de resultado em estudo de caso.
- Escrever o corpo antes de definir a tese e a intenção.
- Citar dados "de memória" sem fonte registrada.
- Disfarçar venda de conteúdo educativo.
- Duplicar peça existente trocando só o título.
- Entupir de palavra-chave e ignorar a intenção de busca.
- Entregar sem autoverificação ou sobrescrever versão anterior.
