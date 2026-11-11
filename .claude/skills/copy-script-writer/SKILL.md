---
name: copy-script-writer
description: "Escreve roteiros de Reels, YouTube, VSL, webinar e anúncio em vídeo com hook nos 3 primeiros segundos, retenção, prova, CTA único e variações para teste."
version: "1.0.0"
owner_squad: copy-squad
megabrain_tier: Tier1
context: conversation
agent: general-purpose
user-invocable: true
argument-hint: "[campaign_id, formato (reel|youtube|ad|story|vsl|webinar), plataforma e duração]"
---

# /copy-script-writer — Script Writer

> **Auto-Trigger:** pedido para escrever roteiro de vídeo curto ou longo, VSL, webinar ou anúncio em vídeo
> **Keywords:** "roteiro de reel da campanha", "roteiro de reels da campanha", "roteiro para reel da campanha", "roteiro para reels da campanha", "roteiro de vsl de venda", "roteiro para vsl de venda", "roteiro de vídeo de venda", "roteiro de video de venda", "roteiro de vídeo da campanha", "roteiro de video da campanha", "roteiro de vídeo de anúncio", "roteiro de video de anuncio", "roteiro de anúncio em vídeo", "roteiro de anuncio em video", "roteiro de vídeo da oferta", "roteiro de video da oferta", "roteiro de webinar de venda", "roteiro de youtube de venda", "roteiro de youtube da campanha"
> **Prioridade:** MÉDIA
> **Tools:** Read, Write, Glob, Grep, Agent (opcional, para delegar ao subagent)

## Propósito

Escreve roteiros cronometrados para vídeo e social, com hook nos primeiros 3 segundos, beats de retenção, tensão, prova e CTA único, direção visual e variações de hook e CTA para teste.

Esta skill é a dona de VSL (contrato `video-script`, `format: vsl`); o conversion-copywriter não produz VSL. Não edita vídeo, não grava e não publica. O resultado é um artefato `video-script` pronto para o copy-editor e, depois, para a produção humana.

## Quando ativar

- Há brief e ângulo aprovado e a demanda é um vídeo (Reels, YouTube, story, anúncio em vídeo, VSL ou webinar).
- É preciso adaptar um ativo longo em roteiro curto.
- A equipe precisa de variações de hook para teste.
- Também cobre legendas e captions por plataforma, via `tasks/write-social-captions.md`.

## Entradas

| Entrada | Obrigatória | Origem |
|---|---|---|
| Brief (ready ou approved) | Sim | `.data/copy-squad/{business}/{campaign_id}/01-strategy/brief.json` |
| Ângulo aprovado | Sim | `.data/copy-squad/{business}/{campaign_id}/03-angles/angles.json` |
| Formato, plataforma e duração | Sim | pedido ou brief |
| Offer-canvas e research packet (provas e direitos de uso) | Não | `01-strategy/offer-canvas.json`, `02-research/research-packet.json` |
| Guia de voz | Não | `.data/copy-squad/{business}/_brand/brand-voice-guide.json` |

## Procedimento

1. Ler `squads/copy-squad/agents/video-social-scriptwriter.md` e assumir o papel, ou delegar ao subagent `copy-squad--video-social-scriptwriter` via Agent tool.
2. Carregar `squads/copy-squad/tasks/write-video-script.md` (ou `tasks/write-social-captions.md` quando o pedido for só legendas), o contrato `contracts/video-script.schema.json` e `checklists/video-script-checklist.md`.
3. Confirmar formato, plataforma, duração e CTA; ler os limites em `data/channel-specs.yaml`.
4. Listar as provas utilizáveis e seus direitos de uso; marcar o restante como unverified.
5. Escrever o hook de até 3 segundos e ao menos 2 alternativas.
6. Distribuir beats de retenção, tensão, prova e CTA, com `time`, `voiceover`, `on_screen_text` e `visual_direction`.
7. Calibrar a duração pela contagem de palavras (cerca de 2,5 por segundo, tolerância de 10%).
8. Marcar claims, gerar variações com hipótese e escrever a caption por plataforma.
9. Autoverificar com o checklist (score >= 0.80) e persistir em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`; emitir o envelope para o `copy-editor`.

## Saída

- Contrato: `squads/copy-squad/contracts/video-script.schema.json`.
- Template humano: `squads/copy-squad/templates/video-script-tmpl.md`.
- Persistência: `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` (nunca sobrescrever versões).
- Envelope: `contracts/handoff-envelope.schema.json`, de `video-social-scriptwriter` para `copy-editor`.

## Gates humanos e risco

- Anúncio pago e VSL ou webinar de venda são risco high (`paid_ad`, `vsl_or_webinar`): G1, G2, G3 e G4 com compliance completo. Qualquer menção a resultado, preço, garantia, autoridade, depoimento, comparativo, saúde ou finanças também eleva para high e exige G3.
- Roteiro de vídeo orgânico é risco medium (`organic_video_script`): G1 e G4, com edição, voz da marca e compliance (modo leve aceito sem claim sensível). Risco low vale só para uso interno (rascunho, variações de hook para teste).
- Nada é publicado ou veiculado sem `approval-decision` com `decision == approved` (nunca `approved_with_edits`), dentro de 72 h e com `payload_sha256` verificado por `squads/copy-squad/scripts/approval_tools.py hash`; o pedido é montado pelo copy-publisher.

## Exemplo

Pedido (exemplo ilustrativo): "Roteiro de Reel de 30 segundos para um SaaS de fluxo de caixa, ângulo 'o dinheiro some no fim do mês'."

Resultado: hook "Seu caixa fecha o mês no vermelho e você não sabe por quê?", beats com linha do tempo animada, CTA "Baixe o modelo de projeção no link da bio", duas variações de hook e uma de CTA, e nenhum claim de resultado.

## Anti-padrões

- Abrir com saudação ou logo antes do hook.
- Roteiro sem tempo ou sem direção visual.
- Vários CTAs concorrentes.
- Prometer resultado garantido ou usar depoimento sem autorização.
- Duração incompatível com o texto falado.
- Tentar editar, renderizar ou publicar o vídeo.

## Quando NÃO Ativar

- O pedido é edição, captação, locução gravada ou publicação de vídeo: fora do escopo do squad.
- Falta ângulo aprovado ou brief: use `/copy-squad` para passar pelo intake e pelo brief antes.
- O pedido é página de vendas, e-mail ou anúncio em texto: use as skills de conversão e de e-mail (VSL é sempre desta skill, nunca do conversion-copywriter).
- O pedido é artigo ou newsletter: use o fluxo de conteúdo do content-copywriter.
- O pedido é reaproveitar um ativo em vários formatos: use `/copy-repurposing-engine`.
