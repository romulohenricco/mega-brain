---
task: write-ux-microcopy
name: write-ux-microcopy
task_name: "Escrever microcopy de interface"
version: "1.0.0"
squad: copy-squad
task_id: write-ux-microcopy
category: production
difficulty: intermediate
responsavel: '@ux-writer'
responsavel_type: Agent
responsible_executor: ux-writer
execution_type: Agent
atomic_layer: Molecule
elicit: true
estimated_time: 30-60min
model: sonnet
status: pending
domain: tactical
Entrada:
- campo: product_flow
  tipo: descrição do fluxo, estados da interface e comportamento confirmado do sistema
  obrigatorio: true
- campo: surface
  tipo: enum (onboarding, form, error, empty_state, dashboard, modal, notification)
  obrigatorio: true
- campo: glossary
  tipo: glossário do produto
  obrigatorio: false
- campo: brand_voice_guide
  tipo: contract:brand-voice-guide
  obrigatorio: false
- campo: brief
  tipo: contract:brief
  obrigatorio: false
Saida:
- campo: ux_copy
  tipo: contract:ux-copy
  persistido_em: .data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json
input: [product-flow, glossary, brand-voice-guide, brief]
output: [ux-copy]
action_items:
  - "Confirmar fluxo, estados e comportamento real do sistema"
  - "Listar os elementos da superfície e seus limites de caracteres"
  - "Escrever cada texto com verbo de ação e linguagem do usuário"
  - "Aplicar a estrutura de erro: o que aconteceu, por quê e o que fazer"
  - "Anotar acessibilidade e termos do glossário"
  - "Registrar suposições e perguntas ao produto"
  - "Autoverificar, persistir e emitir envelope"
acceptance_criteria:
  - "JSON válido contra contracts/ux-copy.schema.json"
  - "Toda mensagem de erro com o que aconteceu, por quê (quando útil) e o que fazer"
  - "Nenhuma frase culpa o usuário"
  - "Cada elemento com character_limit quando o limite existe e todos os textos dentro dele"
  - "accessibility_note em todo elemento com risco (ícone, link, cor, mensagem temporária, campo)"
  - "Termos conforme o glossário; termos novos registrados como proposta"
  - "Zero comportamento de sistema inventado; pendências em meta.assumptions"
  - "Score >= 0.80 em checklists/ux-copy-checklist.md"
pre_condition: "Fluxo e estados da interface descritos, com o comportamento do sistema confirmado por produto ou especificação"
post_condition: "Microcopy persistida como nova versão sem sobrescrever e envelope emitido para o copy-editor"
checklist: checklists/ux-copy-checklist.md
quality_gate: QG-DRAFT
human_gate: null
skill: null
workflows: [wf-copy-production]
performance:
  error_handling: "needs_input com até 5 perguntas sobre comportamento do sistema; texto neutro quando a regra não estiver confirmada; nunca inventar funcionalidade ou prazo"
---

# Task: Escrever microcopy de interface

## Objetivo

Escrever os textos de uma superfície de produto (onboarding, formulário, erro, estado vazio, dashboard, modal ou notificação) de forma clara, útil e humana, explicando o que aconteceu, por quê e o que fazer, de acordo com o glossário e com a realidade do sistema.

## Quando usar / quando não usar

| Usar quando | Não usar quando |
|---|---|
| É preciso texto novo de interface ou de um fluxo de produto | O texto é para aquisição ou campanha: usar tasks do conversion-copywriter |
| Há tela, fluxo ou estado descrito | O fluxo não foi definido: devolver needs_input ao produto via copy-chief |
| Mensagens de erro e estados vazios precisam ser padronizados | O objetivo é revisar texto existente: usar audit-ux-copy |
| Onboarding e ativação precisam de texto | O texto envolve termos legais ou política de privacidade: tratar com compliance e jurídico |

## Entradas

| Campo | Contrato | Obrigatório | Origem |
|---|---|---|---|
| product_flow | descrição do fluxo e estados | Sim | produto, design ou solicitante |
| surface | enum do contrato ux-copy | Sim | pedido |
| glossary | glossário do produto | Não | produto ou biblioteca |
| brand_voice_guide | contracts/brand-voice-guide.schema.json | Não | brand-voice-guardian |
| limites de caracteres | design system ou data/channel-specs.yaml | Não | design |

## Passos

1. **Mapear estados.** Descrever os estados da tela (normal, carregando, erro, vazio, sucesso, bloqueado) e a ação possível em cada um, confirmando o comportamento real do sistema.
2. **Carregar glossário e voz.** Ler glossário e tom por contexto; se não houver glossário, propor termos e marcar como proposta.
3. **Listar elementos.** Enumerar título, descrição, botões, rótulos, placeholders, ajuda, mensagens de erro, confirmações e notificações.
4. **Definir limites.** Registrar character_limit por elemento (design system ou valor conservador registrado em assumptions).
5. **Escrever os textos.** Frases ativas, verbo de ação, uma ideia por mensagem, linguagem do usuário; botões com verbo e objeto.
6. **Aplicar estrutura de erro.** Para cada erro: o que aconteceu, por quê (quando útil) e o que fazer agora; sem culpa, sem código técnico exposto.
7. **Anotar acessibilidade.** Registrar rótulos, alternativas textuais, dependência de cor, leitura por leitor de tela e tempo de exibição de mensagens temporárias.
8. **Registrar glossário e suposições.** Preencher glossary_terms_used; listar em meta.assumptions e em perguntas tudo o que depende de regra não confirmada.
9. **Tratar contexto sensível.** Em pagamento, privacidade, saúde ou erro crítico manter tom neutro e sinalizar revisão de compliance.
10. **Autoverificar e persistir.** Aplicar checklists/ux-copy-checklist.md, corrigir até 0.80, gravar `04-drafts/{asset_id}/v{n}.json` e emitir envelope.

## Saída

- **Contrato:** `contracts/ux-copy.schema.json` (meta com artifact_id de prefixo `uxc-`).
- **Persistência:** `.data/copy-squad/{business}/{campaign_id}/04-drafts/{asset_id}/v{n}.json`.
- **Envelope:** from_agent `ux-writer`, to_agent `copy-editor`, artifact_type `ux-copy`, status `ready` ou `needs_input`, `human_approval_required` true quando medium ou high, gate `G3` se houver menção sensível, `data_privacy` ou urgência/escassez.

## Acceptance Criteria (Critérios de aceite)

- Todos os elementos da superfície cobertos, em todos os estados relevantes.
- Estrutura de erro aplicada em 100% das mensagens de erro.
- Limites de caracteres respeitados.
- Acessibilidade anotada onde há risco.
- Glossário respeitado; perguntas ao produto registradas.
- Autoverificação >= 0.80.

## Quality gate e checklist

- **Gate:** QG-DRAFT; produtor ux-writer, executor (validador) copy-chief com `checklists/ux-copy-checklist.md`. O copy-editor revisa na sequência; mensagens sensíveis (pagamento, privacidade, dados pessoais) passam por compliance. Texto de interface que será aplicado em produção é ação externa (`update_page`): risco mínimo `medium` e G4; `low` vale só para rascunho interno.
- **Checklist:** `checklists/ux-copy-checklist.md`; APPROVE >= 0.80, REVIEW 0.60 a 0.79, VETO < 0.60 ou veto condition.
- Retrabalho máximo de 2 ciclos.

## Tratamento de erro e fallback

| Situação | Ação |
|---|---|
| Comportamento do sistema não confirmado | Texto neutro que não afirma o comportamento e pergunta aberta ao produto |
| Limite de caracteres desconhecido | Usar limite conservador, registrar e oferecer versão curta |
| Glossário ausente | Propor termos, marcar como proposta e pedir decisão do produto |
| Pedido de tom promocional no fluxo de uso | Recusar e sugerir encaminhar a promoção ao conversion-copywriter |
| Erro sem causa conhecida | Mensagem de fallback com caminho de suporte, sem culpar o usuário |

## Handoff

Para `copy-editor`. Mensagens de pagamento, privacidade ou dados pessoais seguem para o compliance-checker via copy-chief. Mudanças de glossário voltam ao approval-owner. O squad não altera o produto; a aplicação do texto na interface é feita por produto e engenharia somente após `approval-decision` `approved` com `payload_sha256` igual (`approved_with_edits` abre nova rodada).

## Exemplo

Entrada resumida (exemplo ilustrativo): campo de e-mail com formato inválido em cadastro.

```json
{
  "surface": "form",
  "context": "Cadastro, campo de e-mail, validação ao sair do campo",
  "copy": [
    {"element": "rotulo_email", "text": "E-mail de trabalho", "character_limit": 30, "accessibility_note": "Rótulo visível, não apenas placeholder"},
    {"element": "erro_email", "text": "Esse e-mail parece incompleto. Confira se tem o @ e o domínio, por exemplo nome@empresa.com.", "character_limit": 120, "accessibility_note": "Associar ao campo por aria-describedby; não depender só da cor vermelha"}
  ],
  "glossary_terms_used": ["e-mail"]
}
```

## Anti-padrões

- "Ocorreu um erro. Tente novamente." em tudo.
- Culpar o usuário ("você digitou errado").
- Inventar prazos ou regras.
- Botões vagos como "OK" ou "Clique aqui".
- Dois termos para o mesmo conceito.
- Tom promocional dentro do fluxo de uso.
