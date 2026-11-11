# Roteiro de Vídeo — {asset_id}

> Template humano do contrato `contracts/video-script.schema.json`. Preencha a partir do JSON persistido em `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json` (`meta.artifact_id = {asset_id}-v{n}`; o payload de aprovação traz `draft_id = {asset_id}-v{n}`). Todos os exemplos de preenchimento são ilustrativos.

## 1. Identificação

| Campo | Valor |
|---|---|
| Negócio | {business} |
| Campanha | {campaign_id} |
| Brief | {brief_id} |
| Ângulo | {angle_id} |
| Artefato (`artifact_id`) | {asset_id}-v{n} |
| Ativo (`asset_id`) | {asset_id} (estável entre versões) |
| Produzido por | video-social-scriptwriter |
| Status | draft / ready / needs_approval |
| Nível de risco | low (só uso interno) / medium (vídeo orgânico publicado) / high (anúncio pago, VSL de venda ou claim sensível) |
| Confiança | 0 a 1 |

## 2. Enquadramento

| Campo | Valor |
|---|---|
| Formato (`format`) | reel / youtube / ad / story / vsl / webinar |
| Plataforma (`platform`) | |
| Duração (`duration_seconds`) | |
| Objetivo do brief | |
| Público e estágio de consciência | |
| Tom de voz (guia de voz) | |
| CTA principal (`cta`) | |

## 3. Hook (0 a 3 segundos)

- **Hook (`hook`):**
- **Por que prende este público:**
- **Variação de hook B:** (hipótese: )
- **Variação de hook C:** (hipótese: )

## 4. Roteiro por beat

| Tempo (`time`) | Locução (`voiceover`) | Texto em tela (`on_screen_text`) | Direção visual (`visual_direction`) | Função do beat |
|---|---|---|---|---|
| 0-3s | | | | Hook |
| | | | | Problema / tensão |
| | | | | Virada |
| | | | | Prova ou demonstração |
| | | | | CTA |

Conferência de duração: palavras da locução ______ / (duração x 2,5) = ______ (tolerância de 10%).

## 5. Prova e claims

| Claim ou prova (`claims`) | Fonte / proof_id | Status (verified / unverified) | Direito de uso | Ação necessária |
|---|---|---|---|---|
| | | | granted / pending / unknown | |

- Gate sinalizado: G3 (sim / não)
- Cenas alternativas sem a prova, caso não seja aprovada:

## 6. CTA e variações para teste (`variations`)

| ID | Elemento | Texto | Hipótese | Métrica esperada |
|---|---|---|---|---|
| V1 | Hook | | | |
| V2 | Hook | | | |
| V3 | CTA | | | |

## 7. Caption (`caption`) por plataforma

| Plataforma | Legenda | Limite | Hashtags |
|---|---|---|---|
| | | | |

## 8. Notas de produção

- Locação, enquadramento, trilha e ritmo sugeridos:
- Material de apoio (b-roll, gráficos, capturas de tela):
- Restrições (direito de imagem, marcas de terceiros, legendas obrigatórias):
- Acessibilidade (legendas embutidas, contraste, descrição de áudio quando aplicável):

## 9. Suposições e pendências (`meta.assumptions`)

-
-

## 10. Revisão e aprovação

| Etapa | Responsável | Resultado | Data |
|---|---|---|---|
| Gate QG-DRAFT | copy-chief | | |
| Edição | copy-editor | | |
| Voz da marca | brand-voice-guardian | | |
| Compliance (risco high ou claim sensível; modo leve em uso interno) | compliance-checker | | |
| Aprovação G3 (claims) | approval-owner | | |
| Aprovação G4 (publicação, obrigatória em toda ação externa) | approval-owner | | |

Publicação, edição de vídeo e agendamento não fazem parte deste artefato: dependem de `approval-decision` com `decision: approved` e `payload_sha256` igual (`approved_with_edits` abre nova rodada) e são conduzidos pelo copy-publisher e pela equipe de produção.
