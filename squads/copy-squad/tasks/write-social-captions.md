---
task: write-social-captions
name: write-social-captions
task_name: "Escrever legendas e captions sociais"
version: "1.0.0"
squad: copy-squad
task_id: write-social-captions
category: production
difficulty: basic
responsavel: '@video-social-scriptwriter'
responsavel_type: Agent
responsible_executor: video-social-scriptwriter
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 20-45min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: brief
  tipo: contract:brief
  obrigatorio: true
- campo: angle
  tipo: contract:angles
  obrigatorio: false
- campo: video_script_or_asset
  tipo: contract:video-script ou contract:content-piece (ativo a legendar)
  obrigatorio: false
- campo: platforms
  tipo: lista de plataformas de destino
  obrigatorio: true
Saida:
- campo: captions
  tipo: contract:video-script (caption e variations) ou contract:content-piece (format post)
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [brief, angles, video-script, content-piece]
output: [video-script, content-piece]
action_items:
  - "Identificar o ativo e as plataformas de destino"
  - "Ler os limites de caption e hashtag de cada plataforma"
  - "Escrever uma legenda por plataforma com hook na primeira linha"
  - "Gerar variações para teste"
  - "Marcar claims e conferir consistência com o ativo"
  - "Autoverificar, persistir e emitir envelope"
acceptance_criteria:
  - "Uma legenda por plataforma solicitada, dentro do limite de caracteres de data/channel-specs.yaml"
  - "Primeira linha funciona como hook (visível antes do corte de leitura)"
  - "Pelo menos 2 variações de legenda ou de CTA por ativo, com hipótese declarada"
  - "Nenhum claim, número ou promessa que não esteja no ativo ou no research packet"
  - "CTA único por legenda, coerente com o brief"
  - "Score >= 0.80 em checklists/video-script-checklist.md"
pre_condition: "Brief ready ou approved e ativo a legendar identificado (ou brief de post independente)"
post_condition: "Legendas persistidas como nova versão e envelope emitido para o copy-editor"
checklist: checklists/video-script-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: null
workflows: [wf-copy-production, wf-fast-variation, wf-content-repurposing]
performance:
  error_handling: "needs_input com até 5 perguntas; plataforma sem especificação usa limite conservador registrado em assumptions; nunca criar claim novo na legenda"
---

# Task: Escrever legendas e captions sociais

## Objetivo

Escrever legendas e captions por plataforma (por exemplo Instagram, LinkedIn, YouTube, TikTok) e variações para teste, coerentes com o ativo e com o brief, respeitando limites, gramática de cada rede e as regras de persuasão ética.

## Quando usar / quando não usar

| Usar quando | Não usar quando |
|---|---|
| Há vídeo, carrossel ou imagem que precisa de legenda | Falta o ativo e o brief também: devolver needs_input |
| O pedido é post social independente: variações para backlog ou teste interno seguem wf-fast-variation (`low`); post publicado é `medium` e vai a G4 em wf-copy-production | O texto é artigo, newsletter ou guia: usar write-content-piece |
| É preciso adaptar a mesma peça para várias redes | O pedido é roteiro: usar write-video-script |
| Variações de legenda para teste | Anúncio pago de venda: usar write-ad-variations do conversion-copywriter |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| brief | contracts/brief.schema.json | Sim | brief-master |
| angle | contracts/angles.schema.json | Não | hook-angle-creator |
| ativo a legendar | contracts/video-script.schema.json ou contracts/content-piece.schema.json | Não | 04-drafts |
| plataformas | lista | Sim | pedido ou brief.channel |
| brand_voice_guide | contracts/brand-voice-guide.schema.json | Não | _brand/brand-voice-guide.json |

## Passos

1. **Identificar ativo e destinos.** Confirmar qual ativo recebe a legenda e para quais plataformas; ler o brief para objetivo e CTA.
2. **Ler limites.** Consultar data/channel-specs.yaml para limite de caracteres, corte de leitura ("ver mais"), uso de hashtags, menções e links.
3. **Extrair a essência.** Resumir a tese e a prova do ativo em uma frase; checar que não surgem claims novos.
4. **Escrever a primeira linha.** Criar hook que funciona antes do corte e que antecipe o benefício ou a pergunta central.
5. **Desenvolver o corpo.** Uma ideia por parágrafo curto, voz da marca, linguagem natural da plataforma; evitar copiar a mesma legenda entre redes.
6. **Definir CTA e hashtags.** Um CTA único; hashtags somente quando a plataforma as usa e dentro do limite recomendado em channel-specs.
7. **Gerar variações.** Criar ao menos 2 variações (hook, tom ou CTA) com hipótese e métrica esperada.
8. **Marcar riscos.** Registrar claims, menções a pessoas e uso de depoimento; `meta.risk_level` é `low` só para uso interno, `medium` para post orgânico publicado e `high` para anúncio pago ou claim sensível (sinalizar G3).
9. **Autoverificar.** Aplicar checklists/video-script-checklist.md (itens de caption e variações); corrigir até 0.80.
10. **Persistir e entregar.** Gravar como video-script (campos caption e variations) quando acompanhar vídeo, ou como content-piece com format `post` quando for post independente; emitir envelope ao copy-editor.

## Saída

- **Contrato:** `contracts/video-script.schema.json` (caption, variations) para legendas de vídeo, ou `contracts/content-piece.schema.json` com `format: post` para posts independentes.
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope:** from_agent `video-social-scriptwriter`, to_agent `copy-editor`, status `ready`, artifact_type `video-script` ou `content-piece`; gate `G3` se houver claim sensível, `data_privacy` ou urgência/escassez.

## Acceptance Criteria (Critérios de aceite)

- Todas as plataformas pedidas atendidas dentro do limite.
- Primeira linha com função de hook.
- Variações com hipótese.
- Nenhuma informação nova em relação ao ativo.
- Hashtags e menções conforme a plataforma.
- Autoverificação >= 0.80.

## Quality gate e checklist

- **Gate:** QG-DRAFT; produtor video-social-scriptwriter, executor (validador) copy-chief com `checklists/video-script-checklist.md`. Variações para uso interno ou teste (`low`) seguem na fast lane com log, `QG-COMPLIANCE` em modo leve e amostragem humana de 20% (`internal_use`). Legenda ou post que será publicado, enviado ou agendado nunca é `low`: o risco mínimo é `medium` (post orgânico) e exige G4; anúncio pago é `high` e exige G3 e G4.
- **Checklist:** `checklists/video-script-checklist.md`.
- Retrabalho máximo de 2 ciclos.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Plataforma sem especificação | Usar limite conservador (por exemplo 125 caracteres antes do corte) e registrar em assumptions |
| Ativo ainda não aprovado | Escrever mas marcar status needs_approval; não encaminhar à publicação |
| Legenda pedida com promessa que não está no ativo | Recusar a promessa e propor reescrita fiel ao ativo |
| Marca de terceiros ou pessoa real citada | Marcar para compliance e G3 |
| Conflito entre limite e CTA | Priorizar hook e CTA; cortar texto intermediário |

## Handoff

Para `copy-editor`. Em wf-fast-variation (uso interno), o fluxo segue edição, voz, compliance leve e amostragem humana. Se a legenda for publicada, ela sai da pista rápida: `prepare-approval-package` e G4. Publicação ou agendamento é do copy-publisher após `approval-decision` com `decision: approved` e `payload_sha256` igual; `approved_with_edits` abre nova rodada.

## Exemplo

Entrada resumida (exemplo ilustrativo): Reel de fluxo de caixa para Instagram e LinkedIn.

```json
{
  "format": "reel",
  "platform": "multi",
  "caption": "Instagram: Seu caixa está pedindo um calendário. Modelo gratuito no link da bio. | LinkedIn: Três hábitos de fluxo de caixa que pequenas empresas deixam passar, e como organizá-los em uma tarde.",
  "variations": [
    "Variação A (pergunta): Você sabe quanto terá em caixa daqui a 30 dias? Hipótese: pergunta aumenta comentários",
    "Variação B (lista): 3 hábitos para organizar o caixa hoje. Hipótese: promessa de lista aumenta salvamentos"
  ],
  "claims": []
}
```

## Anti-padrões

- Mesma legenda em todas as plataformas.
- Hashtags em excesso ou irrelevantes.
- Criar promessa nova que o ativo não sustenta.
- Esconder o CTA no fim do texto cortado.
- Pedir interação com falsa urgência.
- Agendar ou publicar.
