# A profissão de copywriter

> Base de conhecimento do copy-squad. Consolida o que um copywriter faz, quais graus de especialização existem e o que separa um profissional júnior de um sênior. Serve de referência para todos os agentes do squad (em especial para a rubrica de senioridade de cada papel em `data/seniority-matrix.yaml`).

## 1. O que é um copywriter

Um copywriter é o profissional que transforma uma estratégia de negócio em mensagens que levam uma pessoa a agir: clicar, baixar um material, agendar uma reunião, comprar, assinar ou continuar uma jornada. Ele não é apenas "quem escreve bem". Ele pesquisa o público, entende a oferta, cria a mensagem, testa variações e usa os resultados para melhorar.

Em uma frase: **o copywriter é o profissional que transforma estratégia, pesquisa e psicologia do público em palavras que produzem ação mensurável.**

## 2. O que ele faz no dia a dia

A rotina costuma começar com um **briefing**: objetivo, público, produto, canal, oferta, prazo, tom de voz e restrições. O copywriter questiona lacunas, pesquisa concorrentes e clientes, identifica objeções e transforma tudo em uma comunicação clara e persuasiva.

- Pesquisa público, mercado, concorrentes, dores, desejos, objeções e a linguagem real dos clientes.
- Interpreta o briefing e define a mensagem central.
- Cria títulos, hooks, argumentos, CTAs, e-mails, anúncios, landing pages, roteiros e posts.
- Adapta a mesma estratégia para canais diferentes e para estágios diferentes do funil.
- Colabora com designers, mídia, SEO, produto, vendas e CRM.
- Revisa, edita e valida fatos, promessas e consistência de marca.
- Analisa métricas (cliques, conversões, abertura de e-mails, cadastros, vendas) e itera.

Exemplo ilustrativo: para um SaaS de fluxo de caixa, em vez de "Baixe nosso e-book", uma copy orientada ao problema pode ser "Descubra para onde vai o dinheiro da sua empresa e organize seu fluxo de caixa", seguida de um CTA como "Baixar guia gratuito". A diferença está em conectar a oferta a um problema concreto do público.

## 3. O núcleo da profissão: persuasão ética

O copywriter trabalha com **persuasão ética**: apresenta benefícios, evidências e razões reais para agir, sem inventar escassez, autoridade ou resultados. Persuadir não é manipular. O detalhamento está em `knowledge/ethical-persuasion.md`.

### Competências centrais

| Competência | Por que importa | Onde aparece no squad |
|---|---|---|
| Escrita e edição | Clareza, ritmo, gramática, síntese e capacidade de cortar o que não gera valor | `copy-editor`, `conversion-copywriter`, `content-copywriter` |
| Pesquisa | A copy depende de entender produto, mercado, concorrência e linguagem real do cliente | `research-analyst`, `audience-voc` |
| Marketing | Funil, persona, posicionamento, proposta de valor, jornada e conversão orientam a mensagem | `brief-master`, `offer-strategist` |
| Psicologia aplicada | Ajuda a entender motivações, objeções e decisão, sem usar "gatilhos" falsos | `audience-voc`, `hook-angle-creator` |
| Dados e testes | Títulos, CTAs e páginas são hipóteses; testes A/B e métricas mostram o que funciona | `cro-analyst` |
| IA | Serve para pesquisa, brainstorm, variações e adaptação, mas exige verificação e julgamento humano | todos, sob os gates de aprovação |
| Colaboração | Texto e design, mídia, produto e vendas precisam funcionar como um sistema | `copy-chief`, `copy-publisher` |

## 4. Estruturas que ele usa

Não existe fórmula universal, mas frameworks ajudam a organizar o raciocínio. Os mais comuns são **AIDA** (Atenção, Interesse, Desejo, Ação) e **PAS** (Problema, Agitação, Solução). O catálogo completo, com quando usar cada um, está em `knowledge/copy-frameworks.md`.

Outro princípio essencial é traduzir **característica em benefício**:

- Característica: "armazenamento automático na nuvem".
- Benefício: "seus documentos ficam disponíveis mesmo quando você troca de dispositivo".

O copywriter também antecipa objeções: preço, confiança, complexidade, risco, prazo, compatibilidade e necessidade real. No squad, o mapa de objeções vive no contrato `offer-canvas` (campo `objection_responses`) e no `audience-voc` (campo `objections`).

## 5. Graus de especialização

A progressão não é rígida, mas o mercado costuma reconhecer cinco níveis: **júnior, pleno, sênior, lead/gerente e diretor**. Em agências, a trilha clássica é Junior Copywriter, Copywriter, Senior Copywriter e Creative Director. Em empresas, a carreira pode evoluir para Content Strategist, Brand Manager, Marketing Manager ou Copy Director.

| Nível | Responsabilidade típica | O que demonstra domínio |
|---|---|---|
| **Júnior / Trainee** | Escreve variações, posts, e-mails simples, CTAs e peças sob supervisão; aprende tom de voz e processos | Gramática, clareza, pesquisa básica e execução fiel de briefings |
| **Pleno** | Cria campanhas e peças completas, adapta mensagens a canais e participa de revisões e testes | Autonomia, entendimento de funil, SEO, dados e consistência de marca |
| **Sênior** | Lidera conceitos, orienta decisões estratégicas, trabalha com stakeholders e pode mentorar juniores | Estratégia, posicionamento, narrativa, performance e gestão de complexidade |
| **Lead / Gerente de Copy** | Gerencia time, padrões de qualidade, processos, calendários e alinhamento com objetivos de negócio | Liderança, escala de produção e governança de mensagem |
| **Creative Director / Copy Director** | Define visão criativa, aprova campanhas, constrói identidade verbal e conecta criatividade ao resultado do negócio | Estratégia de marca, liderança criativa e impacto comercial |

Como o squad usa isso: cada agente tem um **nível-alvo** (em geral sênior) e uma **rubrica de senioridade** que descreve como seria um output júnior, pleno, sênior, lead e diretor daquele papel. O `copy-chief` e o `approval-owner` registram o nível observado em `agent-evaluation.seniority_level_observed`.

## 6. Especializações possíveis

Depois de dominar a base, o copywriter escolhe uma especialização. Ela pode ser por **formato**, **funil**, **canal** ou **mercado**.

| Especialização | Foco | Agente do squad que a cobre |
|---|---|---|
| Direct response | Resposta mensurável e imediata: anúncios, e-mails, páginas de vendas e ofertas; comum em infoprodutos, cursos, mentorias e SaaS | `conversion-copywriter` |
| SEO copywriting | Conteúdo e páginas que ranqueiam e convertem, unindo intenção de busca, palavras-chave e persuasão | `content-copywriter` |
| E-mail / CRM | Sequências, newsletters, automações, nutrição, reativação e retenção | `email-crm-copywriter` |
| UX writing | Interfaces: botões, erros, onboarding, formulários e mensagens de produto; difere do copy de aquisição, embora compartilhe clareza e empatia | `ux-writer` |
| Brand copywriting | Voz, posicionamento, manifestos, taglines e consistência verbal | `brand-voice-guardian`, `offer-strategist` |
| Advertising copywriting | Conceitos, slogans, roteiros e campanhas publicitárias | `hook-angle-creator`, `conversion-copywriter` |
| B2B / técnico | Traduz produtos complexos (software, finanças, saúde, infraestrutura) em valor compreensível para decisores | `research-analyst`, `conversion-copywriter` |
| Vídeo, social e roteiro | Hooks, roteiros de Reels, YouTube, anúncios em vídeo e narrativas curtas | `video-social-scriptwriter` |
| Case studies e white papers | Provas, autoridade e conteúdo de fundo de funil, sobretudo em B2B | `offer-strategist` (prova), `content-copywriter` |

Para negócios digitais, as especializações mais estratégicas costumam ser **direct response**, **e-mail/CRM**, **landing pages de conversão**, **copy para vídeo/YouTube** e **B2B SaaS**, porque conectam diretamente aquisição, vendas, comunidade e monetização.

## 7. Onde ele atua

O copywriter pode trabalhar em agências, times internos de marketing, startups, e-commerces, produtoras, consultorias ou como freelancer.

- **Agência:** alterna clientes e formatos; ritmo alto; muita variedade.
- **In-house:** aprofunda uma marca, um produto e uma audiência; convive com dados reais de venda.
- **Freelancer:** soma prospecção, proposta, contrato, precificação e gestão financeira à escrita.

O copy-squad foi pensado para o cenário in-house multi-negócio: um mesmo time de agentes atende várias unidades de negócio, cada uma isolada por `{business}`.

## 8. Como entrar e evoluir

Não existe diploma obrigatório de "copywriter". Formações em Publicidade, Marketing, Comunicação, Jornalismo, Letras e áreas afins ajudam, mas portfólio, prática, pesquisa e capacidade de demonstrar resultado pesam muito.

Um caminho eficiente:

1. Estudar escrita, gramática, edição, marketing e fundamentos de copy.
2. Praticar com projetos reais ou fictícios: um anúncio, uma landing page, três e-mails, uma página de produto e um roteiro de vídeo.
3. Montar um portfólio que explique **objetivo, público, problema, estratégia, peça e resultado**, e não apenas o texto final.
4. Buscar vagas como Copywriter, Content Writer, Redator, CRM Copywriter, SEO Content Writer ou UX Writer, lendo as responsabilidades reais de cada vaga.
5. Especializar-se em um mercado e em um tipo de copy; profundidade em B2B, finanças, tecnologia ou produtos digitais tende a gerar diferenciação.

## 9. Como a IA muda a função

A IA acelera rascunhos, variações, resumos, tradução e adaptação de formato, mas não elimina a necessidade de estratégia, verificação de fatos, posicionamento e julgamento. O diferencial do copywriter migra de "produzir muitas palavras" para **decidir o que comunicar, para quem, com qual evidência e como medir o resultado**.

Na prática, o copywriter moderno atua como um **arquiteto de mensagem**: define a tese, cria o sistema de argumentos, orienta a IA, valida fontes, adapta a linguagem à marca e usa dados para evoluir a comunicação. O copy-squad materializa esse modelo: agentes produzem, mas a tese, a oferta, as provas e a publicação seguem sob decisão humana nos gates G1 a G5.

## 10. Sinais de um copywriter sênior

Um profissional sênior não é apenas alguém que escreve textos mais bonitos. Ele consegue:

- Transformar um objetivo de negócio em uma mensagem clara.
- Identificar o argumento que realmente diferencia a oferta.
- Escrever para diferentes estágios de consciência e canais.
- Antecipar objeções sem prometer o que não pode ser entregue.
- Ler métricas e propor os próximos testes.
- Definir e proteger a voz da marca.
- Liderar pessoas, processos e decisões criativas.

### Como esses sinais viram critérios no squad

| Sinal de senioridade | Critério verificável no squad |
|---|---|
| Objetivo de negócio vira mensagem | Brief com `primary_kpi` e `acceptance_criteria` mensuráveis (`QG-BRIEF`) |
| Argumento diferenciador | `offer-canvas.positioning.differentiators` preenchido e ângulos com `reason` |
| Estágios de consciência | `awareness_stage` presente em brief, audience-voc e conversion-copy |
| Objeções sem excesso de promessa | Toda objeção com resposta apoiada em `proof_ids` verificados |
| Leitura de métricas | `performance-analysis` com `sample_size`, `significance` e hipóteses priorizadas por ICE |
| Proteção de voz | `brand-review` com `brand_alignment_score` e ausência de issues críticas |
| Liderança de processo | `copy-chief` com plano completo, gates corretos e escalonamentos registrados |

## 11. Leitura recomendada dentro do squad

- `knowledge/squad-operating-model.md`: como o time se organiza.
- `knowledge/copy-frameworks.md`: frameworks de raciocínio e quando usá-los.
- `knowledge/ethical-persuasion.md`: limites da persuasão.
- `knowledge/metrics-and-evaluation.md`: como medir texto, agente e negócio.
