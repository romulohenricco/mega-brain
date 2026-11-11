# Checklist: Qualidade de UX Copy

## Metadata
```yaml
id: ux-copy-checklist
name: "Checklist de Microcopy de Interface (UX Copy)"
version: 1.0.0
executor: copy-chief           # validador do gate QG-DRAFT (D7)
self_check_by: ux-writer  # produtor; a autochecagem não aprova o gate
related_task: write-ux-microcopy
related_tasks: [write-ux-microcopy, audit-ux-copy]
quality_gate: QG-DRAFT
scale: 0-1
thresholds: {approve: 0.80, review: 0.60}
```

## Purpose

Garantir que a microcopy de interface seja clara, acionável, acessível, consistente com o glossário, dentro dos limites de espaço e honesta sobre o comportamento do sistema. Itens `blocking` reprovam a entrega mesmo que o score global seja alto.

---

## Fase 1: Contexto e fidelidade ao sistema

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 1 | Superfície (onboarding, form, error, empty_state, dashboard, modal, notification) e contexto estão declarados | blocking | [ ] | |
| 2 | Os estados da tela (normal, carregando, erro, vazio, sucesso) estão cobertos ou a lacuna está justificada | normal | [ ] | |
| 3 | Nenhum texto afirma funcionalidade, regra, prazo ou comportamento que não foi confirmado | blocking | [ ] | |
| 4 | O que depende de regra não confirmada está em meta.assumptions e em pergunta ao produto | normal | [ ] | |

**Score Fase 1:** ___/4

---

## Fase 2: Clareza e ação

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 5 | Cada mensagem tem uma ideia e entende-se em uma leitura | normal | [ ] | |
| 6 | Botões e links usam verbo e objeto e fazem sentido fora de contexto (sem "Clique aqui", "OK" ou "Enviar" soltos) | normal | [ ] | |
| 7 | Toda mensagem de erro explica o que aconteceu, por quê (quando útil) e o que fazer | blocking | [ ] | |
| 8 | Nenhuma frase culpa o usuário ou usa tom de acusação | blocking | [ ] | |
| 9 | Não há jargão ou código técnico exposto sem tradução | normal | [ ] | |
| 10 | Estados vazios dizem o que é o espaço e o primeiro passo para preenchê-lo | normal | [ ] | |

**Score Fase 2:** ___/6

---

## Fase 3: Glossário e consistência

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 11 | Os termos seguem o glossário do produto | normal | [ ] | |
| 12 | Cada conceito usa um único termo ao longo da superfície (sem sinônimos concorrentes) | normal | [ ] | |
| 13 | Termos novos estão registrados como proposta em glossary_terms_used e em meta.assumptions | normal | [ ] | |
| 14 | O tom está de acordo com o guia de voz para o contexto (erro, sucesso, onboarding) | normal | [ ] | |

**Score Fase 3:** ___/4

---

## Fase 4: Espaço e acessibilidade

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 15 | Cada elemento tem character_limit quando o limite existe e o texto cabe sem truncar sentido | normal | [ ] | |
| 16 | Rótulos de campos são visíveis e não dependem apenas de placeholder | normal | [ ] | |
| 17 | Há accessibility_note em todo elemento com risco (ícone sem rótulo, link genérico, dependência de cor, mensagem temporária) | normal | [ ] | |
| 18 | Mensagens de erro identificam o campo e não dependem só de cor ou posição | normal | [ ] | |
| 19 | Notificações temporárias permanecem visíveis tempo suficiente e são anunciáveis por leitor de tela | normal | [ ] | |

**Score Fase 4:** ___/5

---

## Fase 5: Contexto sensível e escopo

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 20 | Mensagens de pagamento, privacidade, dados pessoais ou saúde usam tom neutro e estão sinalizadas para compliance | blocking | [ ] | |
| 21 | Não há tom promocional, urgência ou escassez dentro do fluxo de uso | blocking | [ ] | |
| 22 | O texto não é copy de aquisição ou campanha (se for, devolvido ao copy-chief) | normal | [ ] | |

**Score Fase 5:** ___/3

---

## Fase 6: Contrato e entrega

| # | Check | Tipo | Status | Notas |
|---|-------|------|--------|-------|
| 23 | O JSON valida contra contracts/ux-copy.schema.json | blocking | [ ] | |
| 24 | meta.artifact_id usa prefixo `uxc-` e produced_by é ux-writer | normal | [ ] | |
| 25 | A versão foi gravada como nova (v{n}) sem sobrescrever e o envelope foi emitido para o copy-editor | blocking | [ ] | |
| 26 | Na auditoria: problemas classificados por severidade e priorizados por impacto e esforço (em assumptions e no reason do envelope) | normal | [ ] | |

**Score Fase 6:** ___/4

---

## Veto conditions

- Mensagem de erro sem ação possível ou que culpa o usuário.
- Texto que afirma comportamento, prazo ou funcionalidade inexistente ou não confirmada.
- Tom promocional, urgência ou escassez no fluxo de uso do produto.
- Mensagem sensível (pagamento, privacidade, saúde) sem sinalização para compliance.
- JSON inválido contra o schema ou versão anterior sobrescrita.

## Auto-correção (o que fazer quando falha)

| Falha | Correção |
|---|---|
| Erro genérico | Reescrever com o que aconteceu, o motivo e a próxima ação; criar fallback com caminho de suporte para erros desconhecidos |
| Frase culpabilizante | Descrever a situação e oferecer o caminho ("Esse e-mail parece incompleto...") |
| Comportamento não confirmado | Trocar por texto neutro, registrar a suposição e abrir pergunta ao produto |
| Texto excede limite | Oferecer versão curta, mover detalhe para texto de ajuda ou tooltip |
| Termos divergentes | Padronizar pelo glossário ou propor termo único |
| Falta de acessibilidade | Adicionar rótulo, alternativa textual e anúncio para leitor de tela; pedir decisão ao design se for estrutural |
| Tom promocional | Reescrever em tom informativo e encaminhar a promoção ao conversion-copywriter via copy-chief |

Máximo de 2 ciclos de retrabalho; depois, escalar ao copy-chief. O gate QG-DRAFT é decidido pelo copy-chief (executor); a autoverificação do produtor não aprova o gate. Texto aplicado em interface de produção é ação externa (`update_page`): risco mínimo medium e G4.

## Edge cases

- **Idioma ou regionalismo:** manter português do Brasil neutro; localização para outro mercado é da localization-specialist.
- **Erro crítico ou perda de dados:** tom sério, sem humor, com instrução clara e canal de ajuda.
- **Termos legais (aceite, privacidade):** o squad escreve a explicação simples; o texto legal vem de jurídico.
- **Texto gerado dinamicamente:** documentar variáveis (nome, valor, data) e o formato esperado para não quebrar a frase.
- **Plural e gênero:** prever singular e plural; evitar suposição de gênero do usuário.
- **Interface compacta (mobile):** priorizar a versão curta e garantir que a ação principal continue clara.

## Score final = itens OK / total → APPROVE ≥ 0.80 · REVIEW 0.60–0.79 · VETO < 0.60

```
Itens aplicáveis: ___ / 26
Itens OK: ___
Score = ___ / ___ = 0.__
Decisão: [ ] APPROVE  [ ] REVIEW (rework)  [ ] VETO (escalar copy-chief)
```
