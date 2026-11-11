---
task: write-video-script
name: write-video-script
task_name: "Escrever roteiro de vídeo"
version: "1.0.0"
squad: copy-squad
task_id: write-video-script
category: production
difficulty: intermediate
responsavel: '@video-social-scriptwriter'
responsavel_type: Agent
responsible_executor: video-social-scriptwriter
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
- campo: angle
  tipo: contract:angles
  obrigatorio: true
- campo: format_platform_duration
  tipo: formato (reel|youtube|ad|story|vsl|webinar), plataforma e duração em segundos
  obrigatorio: true
- campo: offer_canvas
  tipo: contract:offer-canvas
  obrigatorio: false
- campo: research_packet
  tipo: contract:research-packet
  obrigatorio: false
Saida:
- campo: video_script
  tipo: contract:video-script
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, angles, offer-canvas, research-packet]
output: [video-script]
action_items:
  - "Confirmar formato, plataforma, duração e CTA"
  - "Listar provas utilizáveis e seus direitos de uso"
  - "Escrever hook de até 3 segundos"
  - "Distribuir beats de retenção, tensão, prova e CTA"
  - "Redigir locução, texto em tela e direção visual por beat"
  - "Calibrar a duração e gerar variações de hook e CTA"
  - "Autoverificar e emitir envelope para o copy-editor"
acceptance_criteria:
  - "JSON válido contra contracts/video-script.schema.json"
  - "Hook com no máximo 3 segundos de locução, específico para o público"
  - "Beat de retenção no intervalo exigido pelo formato (5 a 8s em curtos; 30 a 60s em longos)"
  - "Soma da locução dentro de 10% de duration_seconds"
  - "CTA único; pelo menos 2 variações de hook e 1 de CTA com hipótese"
  - "Todo claim ou prova marcado em claims; nenhum depoimento ou resultado inventado"
  - "Score >= 0.80 em checklists/video-script-checklist.md"
pre_condition: "Brief ready ou approved e ângulo aprovado (G2 quando exigido); formato, plataforma e duração definidos"
post_condition: "Roteiro persistido como nova versão sem sobrescrever e envelope emitido para o copy-editor"
checklist: checklists/video-script-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: copy-script-writer
workflows: [wf-copy-production, wf-campaign-launch, wf-content-repurposing]
performance:
  error_handling: "needs_input com até 5 perguntas; prova não verificada vira claim unverified e cena alternativa; nunca prometer resultado garantido"
---

# Task: Escrever roteiro de vídeo

## Objetivo

Produzir um roteiro cronometrado para Reels, YouTube, story, anúncio em vídeo, VSL ou webinar, com hook nos primeiros 3 segundos, retenção, tensão, prova e CTA único, direção visual e variações para teste, pronto para a produção humana e para a edição do copy-editor.

## Quando usar / quando não usar

| Usar quando | Não usar quando |
|---|---|
| Há ângulo aprovado e a demanda é vídeo (curto, longo, anúncio, VSL, webinar); VSL (`format: vsl`) é exclusivamente desta task e do video-social-scriptwriter, nunca do conversion-copywriter | Só legendas e captions: usar write-social-captions |
| O brief traz plataforma, duração e objetivo | Faltam plataforma ou duração: devolver needs_input |
| É preciso adaptar um ativo longo em roteiro (wf-content-repurposing) | O pedido é edição, captação ou publicação de vídeo (fora do escopo) |
| A peça terá variações de teste | Copy de página ou e-mail: usar tasks do conversion-copywriter ou do email-crm-copywriter |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | contracts/brief.schema.json | Sim | brief-master |
| angle | contracts/angles.schema.json | Sim | hook-angle-creator |
| formato, plataforma, duração | texto e inteiro | Sim | pedido ou brief.formats |
| offer_canvas | contracts/offer-canvas.schema.json | Não | offer-strategist (provas, direitos de uso, urgência legítima) |
| research_packet | contracts/research-packet.schema.json | Não | research-analyst |
| brand_voice_guide | contracts/brand-voice-guide.schema.json | Não | brand-voice-guardian |

## Passos

1. **Confirmar o enquadramento.** Validar brief e ângulo; fixar formato, plataforma, duração e o único CTA. Se algo faltar, needs_input com até 5 perguntas.
2. **Ler os limites da plataforma.** Consultar data/channel-specs.yaml (duração máxima, proporção, legendas, limites de caption).
3. **Selecionar provas utilizáveis.** Da offer-canvas e do research packet, listar apenas provas verificadas ou marcá-las como unverified; confirmar usage_rights para depoimento e imagem.
4. **Escrever o hook.** Criar hook de até 3 segundos, específico para o público, sem saudação; escrever ao menos 2 alternativas.
5. **Desenhar a espinha dorsal.** Estruturar problema, tensão, virada, prova ou demonstração e CTA; para VSL e webinar, acrescentar abertura de loop, história, mecanismo, oferta e resposta a objeções, respeitando a offer-canvas.
6. **Redigir os beats.** Para cada beat registrar time, voiceover, on_screen_text e visual_direction, com uma ideia por beat e intervalos conforme o formato.
7. **Calibrar a duração.** Contar palavras da locução (cerca de 2,5 por segundo) e ajustar para ficar dentro de 10% de duration_seconds.
8. **Marcar claims e risco.** Registrar em claims qualquer promessa de resultado, número, depoimento, preço, garantia ou autoridade e sinalizar G3. Definir `meta.risk_level`: vídeo orgânico publicado é no mínimo `medium` (G4); anúncio em vídeo pago e VSL de venda são `high` (compliance-checker, G3 quando houver claim sensível e G4); `low` só para rascunho ou variação de uso interno, que nunca é veiculada.
9. **Variações e caption.** Gerar variações de hook e de CTA com hipótese; escrever caption para a plataforma.
10. **Autoverificar e persistir.** Aplicar checklists/video-script-checklist.md, corrigir até 0.80, gravar `04-drafts/{asset_id}/v{n}.json` (com `meta.artifact_id = {asset_id}-v{n}`) e emitir o envelope.

## Saída

- **Contrato:** `contracts/video-script.schema.json` (meta com artifact_id de prefixo `vid-`).
- **Template humano:** `templates/video-script-tmpl.md` para renderizar o roteiro para a equipe de produção.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope:** from_agent `video-social-scriptwriter`, to_agent `copy-editor`, artifact_type `video-script`, status `ready`, gate `G3` se houver claim sensível, `data_privacy` ou urgência/escassez, `human_approval_required` true para medium ou high.

## Acceptance Criteria (Critérios de aceite)

- Roteiro válido e persistido como nova versão.
- Hook, retenção, tensão, prova e CTA presentes e identificáveis.
- Duração compatível com a locução.
- Variações de hook e CTA com hipótese.
- Claims e provas marcados; direitos de uso verificados.
- Autoverificação >= 0.80.

## Quality gate e checklist

- **Gate:** QG-DRAFT; produtor video-social-scriptwriter, executor (validador) copy-chief com `checklists/video-script-checklist.md`. Edição, voz, compliance e aprovação humana ocorrem depois, com validadores diferentes do produtor.
- **Checklist:** `checklists/video-script-checklist.md` (escala 0 a 1; APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60 ou veto condition).
- Retrabalho máximo de 2 ciclos.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Plataforma ou duração ausentes | needs_input; propor opções padrão (ex.: 30s para Reels) para confirmação |
| Prova não verificada | Marcar unverified, trocar a cena por demonstração do processo |
| Depoimento sem direito de uso | Excluir a cena e marcar needs_approval |
| Texto não cabe na duração | Cortar para o essencial ou propor versão mais longa |
| Ângulo exige promessa de resultado | Escalar para G3 e escrever alternativa sem a promessa |
| Schema inválido | Corrigir e revalidar antes de entregar |

## Handoff

Para `copy-editor` (edit-draft). Anúncios pagos em vídeo e VSL de venda são risco `high`, exigindo compliance-checker, G3 (quando houver claim sensível, `data_privacy` ou urgência/escassez) e G4 antes de qualquer veiculação, conduzidos pelo copy-chief e pelo copy-publisher via `prepare-approval-package`. Execução só com `approval-decision` `approved` e `payload_sha256` igual; `approved_with_edits` abre nova rodada.

## Exemplo

Entrada resumida (exemplo ilustrativo): Reel de 30 segundos para SaaS de fluxo de caixa, ângulo "o dinheiro some no fim do mês".

```json
{
  "format": "reel",
  "platform": "instagram",
  "duration_seconds": 30,
  "hook": "Seu caixa fecha o mês no vermelho e você não sabe por quê?",
  "script": [
    {"time": "0-3s", "voiceover": "Seu caixa fecha o mês no vermelho e você não sabe por quê?", "on_screen_text": "Para onde foi o dinheiro?", "visual_direction": "Close no rosto, corte seco para extrato rabiscado"},
    {"time": "3-12s", "voiceover": "Quase sempre é a conta que vence antes de o cliente pagar.", "on_screen_text": "Vence antes de entrar", "visual_direction": "Linha do tempo com dois eventos fora de ordem"}
  ],
  "cta": "Baixe o modelo de projeção no link da bio",
  "variations": ["Hook B: Você sabe quanto terá em caixa daqui a 30 dias?", "CTA B: Comente MODELO para receber o passo a passo"],
  "claims": []
}
```

## Anti-padrões

- Abrir com saudação ou logo antes do hook.
- Roteiro sem tempo ou sem direção visual.
- Vários CTAs concorrentes.
- Prometer resultado garantido ou usar depoimento sem autorização.
- Ignorar a gramática da plataforma.
- Publicar ou editar o vídeo.
