# Frameworks de copy

> Frameworks organizam o raciocínio; não substituem pesquisa nem prova. Nenhum é obrigatório. Escolha pelo estágio de consciência do público, pelo canal e pelo objetivo. Estes frameworks são conhecimento geral de domínio, usados como apoio pelos agentes do squad.

## 1. Quadro de escolha rápida

| Situação | Framework indicado | Agente que mais usa |
|---|---|---|
| Peça curta com um objetivo claro (anúncio, e-mail) | AIDA | `conversion-copywriter` |
| Público sente a dor e quer alívio | PAS | `conversion-copywriter`, `email-crm-copywriter` |
| Transformação visível entre dois estados | BAB | `conversion-copywriter`, `video-social-scriptwriter` |
| Descrever produto ou recurso | Característica, vantagem, benefício (FAB) | `conversion-copywriter`, `ux-writer` |
| Título ou assunto de e-mail | 4U | `hook-angle-creator`, `email-crm-copywriter` |
| Página de vendas longa | PASTOR | `conversion-copywriter` |
| Lead com história e qualificação | QUEST | `content-copywriter`, `video-social-scriptwriter` |
| Decidir a abertura da mensagem | Níveis de consciência | `brief-master`, `audience-voc` |
| Decidir quão diferente a promessa precisa ser | Estágios de sofisticação | `offer-strategist`, `hook-angle-creator` |
| Entender por que o cliente "contrata" o produto | Jobs to be done (JTBD) | `audience-voc` |
| Alinhar mensagens-chave | Messaging house | `offer-strategist`, `brand-voice-guardian` |
| Explicar por que escolher esta oferta | Proposta de valor | `offer-strategist` |

## 2. AIDA

**Atenção, Interesse, Desejo, Ação.**

- **Atenção:** um hook específico e relevante para o público.
- **Interesse:** um fato, uma pergunta ou uma consequência que mantém a leitura.
- **Desejo:** benefício concreto, prova e imagem do resultado possível.
- **Ação:** CTA específico, coerente com o que o leitor vai receber.

Quando usar: anúncios, e-mails curtos, posts. Cuidado: não use como camisa de força; a prova precisa vir antes do CTA.

## 3. PAS

**Problema, Agitação, Solução.**

- **Problema:** nomeie a dor com as palavras do cliente (`audience-voc.customer_phrases`).
- **Agitação:** mostre o custo de manter a situação, sem exagerar nem culpar.
- **Solução:** apresente o mecanismo e a oferta como saída, com prova.

Quando usar: público consciente do problema. Limite ético: a agitação deve ser proporcional e verdadeira; sem medo fabricado (ver `knowledge/ethical-persuasion.md`).

## 4. BAB

**Before, After, Bridge (Antes, Depois, Ponte).**

- **Antes:** a situação atual, reconhecível.
- **Depois:** o estado desejado, realista.
- **Ponte:** como o produto leva de um ao outro.

Quando usar: transformação visível, roteiros de vídeo, depoimentos de caso real. Cuidado: o "depois" precisa ser sustentado por prova.

## 5. Característica, vantagem, benefício (FAB)

Transforme cada característica em benefício concreto.

| Característica | Vantagem | Benefício |
|---|---|---|
| Armazenamento automático na nuvem | Não depende de um dispositivo | Seus documentos ficam disponíveis mesmo quando você troca de aparelho |
| Conciliação bancária integrada | Dados entram sem digitação | Você fecha o mês em menos tempo e com menos erro |

Exemplos ilustrativos. Regra do squad: benefício que implique resultado mensurável é claim e segue para verificação.

## 6. 4U

**Útil, Urgente, Único, Ultraespecífico.** Checklist para títulos e assuntos.

- **Útil:** o leitor percebe valor.
- **Urgente:** só se houver urgência legítima.
- **Único:** diferencia-se do que o público já leu.
- **Ultraespecífico:** números, prazos ou situações concretas, desde que verdadeiros.

Quando usar: geração e ranqueamento de hooks, assuntos de e-mail, headlines de anúncio.

## 7. PASTOR

**Problem, Amplify, Story, Transformation, Offer, Response.**

Estrutura para páginas de vendas e cartas longas.

1. **Problema:** quem é o público e qual dor enfrenta.
2. **Amplificação:** consequências de não resolver.
3. **História e prova:** casos, dados e demonstração verificados.
4. **Transformação:** o estado após a solução.
5. **Oferta:** o que é, preço, garantia, condições.
6. **Resposta:** CTA e redução de risco.

Quando usar: landing page de venda, VSL, e-mail longo. Mapeia para as seções de `conversion-copy.sections` (landing page e e-mail) ou para as cenas de `video-script` (VSL, que é do `video-social-scriptwriter`).

## 8. QUEST

**Qualify, Understand, Educate, Stimulate, Transition.**

- **Qualificar** o leitor certo.
- **Compreender** o problema dele.
- **Educar** com informação útil.
- **Estimular** o desejo com prova.
- **Transicionar** para a ação.

Quando usar: conteúdo educativo com conversão suave, newsletters, artigos com CTA final.

## 9. Níveis de consciência do mercado

Descrevem o quanto o público conhece o problema, as soluções e a oferta. No contrato `brief` e em `audience-voc`, o campo é `awareness_stage`.

| Estágio | O público sabe... | Abertura recomendada |
|---|---|---|
| `unaware` | Que existe um problema? Não | Identificação com uma situação ou sintoma; história |
| `problem_aware` | Sente a dor, não conhece soluções | Nomear a dor e abrir o caminho |
| `solution_aware` | Conhece soluções, não a sua | Mecanismo e diferença |
| `product_aware` | Conhece sua oferta, tem dúvidas | Prova, comparação justa, resposta a objeções |
| `most_aware` | Quer comprar | Oferta, condições, CTA direto |

Quanto mais baixa a consciência, mais longa e narrativa a copy; quanto mais alta, mais direta.

## 10. Estágios de sofisticação do mercado

Medem o quanto o mercado já ouviu promessas parecidas.

1. **Primeira promessa:** o mercado é novo; a promessa direta basta.
2. **Promessa ampliada:** concorrentes repetem a promessa; amplie escala ou velocidade.
3. **Mecanismo:** o mercado desconfia; explique o mecanismo único.
4. **Mecanismo ampliado:** mecanismos se multiplicam; detalhe e aprimore o mecanismo.
5. **Identificação:** o mercado está saturado; conecte com identidade e experiência do cliente.

Uso: o `hook-angle-creator` consulta o estágio para decidir se o ângulo deve ser de promessa, mecanismo ou identificação; o `research-analyst` mapeia as promessas dos concorrentes.

## 11. Jobs to be done (JTBD)

O cliente "contrata" um produto para realizar um progresso em uma situação.

Formato: *Quando [situação], eu quero [motivação], para que [resultado esperado].*

Exemplo ilustrativo: "Quando o caixa aperta no fim do mês, quero enxergar para onde foi o dinheiro, para decidir o que cortar sem parar a operação."

Uso: `audience-voc.jobs_to_be_done` alimenta o brief, os ângulos e os CTAs; ajuda a distinguir a dor funcional da emocional e social.

## 12. Messaging house

Estrutura de mensagens:

- **Teto:** promessa central (uma frase).
- **Pilares (3):** argumentos principais.
- **Fundação:** provas, fatos e exemplos de cada pilar.
- **Voz:** tom e vocabulário (`brand-voice-guide`).

Uso: `offer-strategist` monta a casa; os copywriters mantêm toda peça dentro dos pilares; o `brand-voice-guardian` checa a consistência.

## 13. Proposta de valor

Formato de apoio: *Para [público], que [necessidade], o [produto] é [categoria] que [benefício principal]. Diferente de [alternativa], nós [diferencial verificável].*

Regras:

- O diferencial deve ser verificável (`offer-canvas.positioning.differentiators`).
- A categoria define com quem o público compara.
- Preço, garantia e resultado entram apenas com fonte e aprovação.

## 14. Combinando frameworks

| Peça | Combinação típica |
|---|---|
| Landing page de venda | Nível de consciência (abertura) + PASTOR (estrutura) + FAB (seções de benefício) |
| E-mail de nutrição | QUEST + 4U no assunto |
| Anúncio curto | AIDA ou PAS + 4U no headline |
| Roteiro de Reel | BAB com hook de 3 segundos |
| Brief | JTBD + níveis de consciência + proposta de valor |

## 15. Anti-padrões

- Aplicar o framework sem pesquisa de público.
- Usar PAS para fabricar dor.
- Copiar a estrutura de um concorrente sem mecanismo próprio.
- Escolher o framework antes de definir o estágio de consciência.
- Tratar 4U como obrigação de urgência: sem urgência legítima, o "U" de urgente não se aplica.
