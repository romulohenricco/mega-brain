# Checklist: Qualidade de Roteiro de Vídeo e Social

## Metadata
```yaml
id: video-script-checklist
name: "Checklist de Roteiro de Vídeo, Legendas e Captions"
version: 1.0.0
executor: copy-chief           # validador do gate QG-DRAFT (D7)
self_check_by: video-social-scriptwriter  # produtor; a autochecagem não aprova o gate
related_task: write-video-script
related_tasks: [write-video-script, write-social-captions]
quality_gate: QG-DRAFT
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que roteiros e legendas tenham hook forte nos primeiros 3 segundos, retenção planejada, prova honesta, CTA único, duração compatível com a locução, aderência à plataforma e variações para teste. Itens `blocking` reprovam o roteiro mesmo que o score global seja alto.

---

## Fase 1: Enquadramento

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | Formato (reel, youtube, ad, story, vsl, webinar), plataforma e duração estão declarados | blocking | [ ] | |
| 2 | O `brief_id` corresponde a um brief ready/approved e o ângulo usado está aprovado | blocking | [ ] | |
| 3 | O CTA do roteiro coincide com o objetivo e o destino do brief | normal | [ ] | |
| 4 | Os limites da plataforma de data/channel-specs.yaml foram consultados | normal | [ ] | |

**Score Fase 1:** ___/4

---

## Fase 2: Hook e retenção

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 5 | O hook ocupa no máximo 3 segundos de locução e abre o roteiro | blocking | [ ] | |
| 6 | O hook é específico para o público do brief (sem saudação genérica ou logo antes do hook) | blocking | [ ] | |
| 7 | Há beat de retenção a cada 5 a 8 segundos (curtos) ou 30 a 60 segundos (longos) | normal | [ ] | |
| 8 | Existe tensão honesta derivada do problema real do público, sem ameaça inventada | normal | [ ] | |
| 9 | Há momento de prova ou demonstração antes do CTA | normal | [ ] | |
| 10 | Cada beat tem uma ideia, com `time`, `voiceover`, `on_screen_text` e `visual_direction` | normal | [ ] | |

**Score Fase 2:** ___/6

---

## Fase 3: Duração e clareza

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 11 | A soma da locução (cerca de 2,5 palavras por segundo) está dentro de 10% de duration_seconds | normal | [ ] | |
| 12 | Os tempos dos beats são sequenciais, sem lacunas ou sobreposição | normal | [ ] | |
| 13 | A linguagem é falada, em frases curtas, sem jargão não explicado | normal | [ ] | |
| 14 | A direção visual é suficiente para a produção entender a cena sem adivinhar | normal | [ ] | |
| 15 | O texto em tela é legível (curto) e não repete literalmente toda a locução | normal | [ ] | |

**Score Fase 3:** ___/5

---

## Fase 4: Prova, claims e ética

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 16 | Toda prova usada vem do research packet ou da offer-canvas, com status de verificação | blocking | [ ] | |
| 17 | Nenhum depoimento, número, prêmio ou autoridade foi inventado; exemplos estão marcados como ilustrativos | blocking | [ ] | |
| 18 | Depoimentos e imagens de pessoas têm usage_rights granted ou a cena está marcada needs_approval | blocking | [ ] | |
| 19 | Claims sensíveis estão listados em `claims`, com meta.risk_level high e sinalização de G3 (também para `data_privacy` e urgência/escassez) | blocking | [ ] | |
| 20 | Não há promessa de resultado garantido, urgência ou escassez falsa | blocking | [ ] | |

**Score Fase 4:** ___/5

---

## Fase 5: CTA, variações e legendas

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 21 | Existe um único CTA principal, específico e coerente | normal | [ ] | |
| 22 | Há pelo menos 2 variações de hook e 1 de CTA, cada uma com hipótese | normal | [ ] | |
| 23 | A caption existe, respeita o limite da plataforma e a primeira linha funciona como hook | normal | [ ] | |
| 24 | Legendas de plataformas diferentes não são cópias idênticas | normal | [ ] | |
| 25 | Hashtags e menções seguem as regras da plataforma, sem excesso | normal | [ ] | |

**Score Fase 5:** ___/5

---

## Fase 6: Contrato e entrega

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 26 | O JSON valida contra contracts/video-script.schema.json (ou content-piece para post independente) | blocking | [ ] | |
| 27 | meta.artifact_id usa prefixo `vid-` (ou `cnt-` para post) e produced_by é video-social-scriptwriter | normal | [ ] | |
| 28 | A versão foi gravada como nova (v{n}) sem sobrescrever e o envelope foi emitido para o copy-editor | blocking | [ ] | |

**Score Fase 6:** ___/3

---

## Veto conditions

- Hook ausente, acima de 3 segundos ou precedido de saudação genérica.
- Depoimento, resultado, número, prêmio ou autoridade inventado.
- Uso de imagem ou depoimento de pessoa sem direito de uso confirmado.
- Promessa de resultado garantido, urgência ou escassez falsa.
- Claim sensível sem marcação, sem risk_level high e sem sinalização de G3.
- JSON inválido contra o schema ou versão anterior sobrescrita.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Hook longo ou genérico | Reescrever com a dor, a pergunta ou o resultado possível do público; cortar até 3 segundos |
| Sem retenção | Inserir virada, prova ou demonstração nos intervalos do formato |
| Locução maior que a duração | Cortar o que não sustenta hook, prova ou CTA, ou propor versão mais longa |
| Prova não verificada | Marcar unverified, substituir por demonstração do processo e sinalizar G3 |
| Vários CTAs | Eleger o CTA do brief e mover os demais para a legenda como opção |
| Legendas iguais | Reescrever por plataforma com hook e tom próprios |
| Sem variações | Gerar 2 variações de hook e 1 de CTA com hipótese |

Máximo de 2 ciclos de retrabalho; depois, escalar ao copy-chief.

## Edge cases

- **VSL e webinar:** os intervalos de retenção são maiores, mas cada bloco precisa de uma razão para continuar; o CTA aparece também no meio quando a plataforma permitir.
- **Anúncio em vídeo pago e VSL de venda:** risco high; exigem compliance, G3 (se houver claim sensível, `data_privacy` ou urgência/escassez) e G4; vídeo orgânico publicado é no mínimo medium e exige G4; low só para variação de uso interno. VSL é do video-social-scriptwriter. A política de anúncios da plataforma entra em platform_policy_flags.
- **Vídeo sem voz (apenas texto em tela):** a regra de palavras por segundo vale para o texto em tela e o tempo de leitura.
- **Plataforma sem especificação:** usar limite conservador e registrar em meta.assumptions.
- **Roteiro adaptado de artigo:** conferir que nenhum dado novo foi introduzido e que as fontes permanecem.
- **Crianças ou saúde no vídeo:** tratar como risco high e encaminhar a revisão especializada.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

```
Itens aplicáveis: ___ / 28
Itens OK: ___
Score = ___ / ___ = 0.__
Decisão: [ ] APPROVE  [ ] REVIEW (rework)  [ ] VETO (escalar copy-chief)
```
