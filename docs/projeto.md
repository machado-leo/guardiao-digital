# Guardião Digital — Projeto Simula & Simplifica
Oct 14, 2026 · @Leonardo
## Resumo do projeto
O Guardião Digital é um assistente de voz que ajuda pessoas idosas a descobrir, na hora, se uma mensagem ou ligação é golpe, e avisa a família quando o risco é alto. O projeto participa do Simula & Simplifica: Algoritmos em Ação (edição 2026.2).
- Público: pessoas idosas ou com baixo letramento digital.
- Canal principal: Alexa (skill própria "Guardião"), com Telegram para alertas à família.
- Cérebro: grafo de decisão em LangGraph + base de golpes consultada por RAG + modelo GPT via API.
- Etapa 1 (Observe): entregue, nota ponderada 9,35. O parecer destacou a relevância social e indicou soluções por voz como caminho.
## O problema (Etapa 1 – Observe)
O idoso que recebe uma mensagem suspeita depende de um familiar estar disponível naquele instante para saber se é golpe. Quando ninguém responde a tempo, a pressão do golpista vence.
Golpes mais comuns contra esse público: falso parente com número novo pedindo PIX, falsa central bancária 0800, falso cancelamento de benefício do INSS e cobrança indevida de frete.
Entradas: mensagens de WhatsApp/SMS, prints, ligações suspeitas, links encurtados com urgência, pedidos de PIX, senhas ou dados.
Saídas: o idoso transfere o dinheiro ou entrega os dados (prejuízo) OU interrompe a fraude depois de confirmar com alguém de confiança.
Passo a passo manual hoje:
- Recebe a mensagem com tom de urgência ou desespero.
- Tenta interpretar sozinho, sob medo e pressão.
- Tenta falar com um filho ou neto; muitas vezes desiste por vergonha ou por falta de resposta.
- Às vezes tenta ligar para o banco ou ir à agência, com filas e demora.
- Decide: se a família responde a tempo, a fraude é evitada; se não, ele faz o PIX.
Gargalo (Etapas 3 e 4): a dependência do tempo de resposta do familiar e a falta de um canal acessível. Sob pressão, muitos idosos não usam navegador ou buscador; falar em voz alta é o jeito mais natural de pedir ajuda.
## A solução proposta
O Guardião substitui a espera pelo familiar por uma verificação imediata por voz: ele faz perguntas curtas, compara o caso com golpes conhecidos, dá uma orientação clara e avisa a família se o risco for alto.
- Pergunta em vez de esperar: o idoso diz "Alexa, abre o Guardião" e o assistente conduz a conversa com perguntas de 2 a 4 segundos de resposta.
- Compara com golpes reais: a situação é cruzada com uma base de golpes brasileiros e regras oficiais (bancos, INSS, Banco Central).
- Orienta sem termos técnicos: a resposta final tem uma ou duas frases, em tom calmo, com uma ação clara ("não faça o PIX, ligue para o número antigo do seu filho").
- Avisa a família: se o risco for crítico, o filho ou neto responsável recebe um alerta no Telegram.
- Regra fixa de segurança: o Guardião nunca diz "pode pagar". Na dúvida, a orientação é sempre confirmar por outro canal antes de qualquer pagamento.
## Arquitetura técnica
A Alexa cuida só da voz (ouvir e falar); toda a decisão acontece no backend, dentro de um grafo de decisão em LangGraph.

arquitetura · Alexa, backend, grafo de decisão, base de golpes e Telegram
A cada resposta do idoso, a Alexa envia o texto ao backend, o grafo atualiza o estado da conversa e devolve a próxima pergunta ou o veredito. Se o risco passar do limiar, o alerta vai para o Telegram da família.
Tecnologias:
- Voz: Alexa Skills Kit, skill personalizada "Guardião", sessão aberta entre as perguntas (shouldEndSession: false).
- Backend: Python, com endpoint HTTPS (túnel para testes ou AWS Lambda).
- Decisão: LangGraph, com memória da conversa pelo sessionId da Alexa.
- Base de golpes: ChromaDB ou FAISS, com 20 a 30 casos curados e suas fontes.
- Modelo: GPT via API, usado para interpretar respostas e redigir a fala final.
- Alerta: bot do Telegram.
## Fluxo de conversa por voz
A conversa é feita de perguntas curtas, e a próxima pergunta depende da resposta anterior. Isso evita que a Alexa corte a fala do idoso e é onde o grafo de decisão mostra o "algoritmo em ação".
Perguntas-base (cada resposta preenche um campo do estado):
- Quem mandou a mensagem? → remetente (filho, neto, banco, INSS, loja)
- Por onde chegou? É um número novo? → canal e numero_novo
- O que pediram? → pedido (PIX, senha, código, clicar em link, ligar para um número)
- Tem prazo ou ameaça? → urgencia
Exemplos de ramificação:
- Remetente "filho" + número novo → pergunta qual foi a desculpa para o número novo e quanto ele pediu.
- Remetente "banco" → pergunta se pediram senha, código ou para ligar em algum número.
- Remetente "INSS" → pergunta se mandaram link para prova de vida ou recadastramento.
Exemplo de diálogo:
Idoso: Alexa, abre o Guardião. Guardião: Oi, seu José. Quem te mandou a mensagem? Idoso: Meu filho. Guardião: Ele está usando um número novo? Idoso: Tá, disse que o celular caiu na água. Guardião: E ele pediu dinheiro? Idoso: Pediu 400 reais no PIX. Guardião: Seu José, esse é um golpe muito comum. Não faça o PIX. Ligue agora para o número antigo do seu filho. Vou avisar a Ana para ela te ligar também.
Tempo de escuta: a sessão fica aberta entre as perguntas. Se o idoso demorar, a Alexa repete a pergunta com calma (reprompt) antes de encerrar.
## Diferencial
O Guardião não compete em "inteligência geral": ele segue um protocolo de verificação, consulta golpes brasileiros atuais, nunca autoriza pagamento e avisa a família. Nenhuma das alternativas faz essas quatro coisas juntas.
Alternativa
O que faz bem
Onde falha para o idoso sob pressão
Google
Encontra informação
Exige digitar e escolher resultados; anúncios podem levar a sites falsos
Gemini / ChatGPT
Responde perguntas abertas
O idoso precisa saber o que perguntar; respostas longas; não avisa ninguém
Alexa tradicional
Comandos simples por voz
Não entende situações com contexto; resposta genérica ou "não entendi"
Alexa+
Conversa natural em português, com IA generativa
Responde de forma geral, não conduz a verificação nem avisa a família; após o acesso antecipado exige Prime ou R$ 99,90/mês
Guardião Digital
Conduz perguntas, compara com golpes reais, dá ordem clara, alerta a família
Depende de a skill funcionar no aparelho (ver Riscos)
Como defender na banca: o Google e o Gemini são fontes passivas para quem sabe pesquisar. O Guardião é uma verificação ativa, feita para quem não sabe o que perguntar, no momento em que o golpe acontece.
Sobre a Alexa+: ela chegou ao Brasil em acesso antecipado em 18 de junho de 2026, gratuita até pelo menos 30 de outubro de 2026, e depois incluída no Prime ou por R$ 99,90/mês (Diário da Mídia, IstoÉ Dinheiro). Não afirme que o projeto é inédito nem que a Alexa "é burra".
## Escopo e cronograma
O projeto cabe nas duas semanas restantes se o foco ficar no núcleo: conversa guiada, base de golpes, pontuação de risco e alerta à família. A Etapa 2 vai até 21/10 e a Etapa 3 termina em 29/10, com a live final às 19h (site do projeto).
Etapa 2 – Construa (até 21/10)
- ☐ Testar se uma skill de teste abre na Dot 3 com "Alexa, abre o Guardião" (primeiro dia)
- ☐ Montar o grafo no LangGraph com 3 a 5 perguntas adaptativas
- ☐ Criar a base de golpes curada à mão: 20 a 30 casos com fontes oficiais (Febraban, Banco Central, INSS, CERT.br)
- ☐ Indexar a base em um banco vetorial local (ChromaDB ou FAISS)
- ☐ Definir a regra de pontuação de risco (0 a 100) e o limiar para alertar a família
- ☐ Criar o bot do Telegram que recebe o alerta
- ☐ Testar tudo por texto antes de ligar na Alexa
Etapa 3 – Apresente (até 29/10)
- ☐ Ligar a skill da Alexa ao backend (endpoint HTTPS com túnel ou AWS Lambda)
- ☐ Ajustar o tempo de resposta para caber no limite da Alexa
- ☐ Gravar a comparação: a mesma pergunta na Alexa tradicional e no Guardião
- ☐ (Opcional) Script que lê um feed RSS e adiciona golpes novos à base
- ☐ Ensaiar a demonstração e preparar o plano B
Fica de fora (trabalhos futuros): WhatsApp, Gmail, leitura de redes sociais (X, Facebook) e análise de prints por OCR.
## Riscos e cuidados
O maior risco técnico é a demora na resposta: a Alexa espera poucos segundos (cerca de 8) pelo backend, e uma cadeia com RAG e GPT pode passar disso.
Risco
Como evitar
Resposta do backend demora demais
Modelo rápido, base pequena, respostas curtas; usar uma fala de espera ("deixa eu verificar")
Skill não abre em aparelho com Alexa+
Desenvolver na Alexa tradicional; há relatos de skills com "peça a…" falhando na Alexa+ (Neptune Forum)
Captura de frase livre não funciona
O slot AMAZON.SearchQuery precisa de uma frase de apoio (ex.: "a mensagem diz {duvida}"); testar em pt-BR
Wi-Fi falha na apresentação
Simulador do console da Amazon aberto no notebook como plano B
Sistema diz que um golpe é seguro
Regra fixa: nunca dizer "pode pagar"; na dúvida, mandar confirmar por outro canal
Alucinação do modelo
O RAG reduz (não elimina) o risco; resposta ancorada nas fontes da base
Privacidade (LGPD): as falas vão para a API da OpenAI. Não guardar dados pessoais além do necessário para a sessão e não registrar nomes, valores ou números de telefone nos logs.
## Roteiro da demonstração
A demonstração deve mostrar, em menos de 3 minutos, o contraste entre a Alexa comum e o Guardião diante do mesmo golpe.
- Contexto (30 s): um slide com o golpe do falso parente e o gargalo da Etapa 1.
- Sem o Guardião: tocar a gravação da Alexa tradicional respondendo "meu filho pediu 300 reais num número novo, é golpe?".
- Com o Guardião, ao vivo na Dot 3: "Alexa, abre o Guardião" e as três ou quatro perguntas curtas até o veredito.
- Alerta: mostrar na tela o celular do "filho" recebendo a mensagem no Telegram.
- Por dentro (opcional): o caminho que o grafo percorreu e o trecho da base de golpes que foi usado.
Plano B: se o Echo ou o Wi-Fi falhar, rodar a mesma conversa no simulador do console da Amazon.
## Trabalhos futuros e fontes
Trabalhos futuros:
- Atualização automática da base com feeds de fontes confiáveis (CERT.br, Febraban, seções de checagem de notícias), passando por um agente curador antes de entrar na base.
- Envio de prints pelo Telegram com leitura do texto da imagem (OCR).
- Conexão com WhatsApp e Gmail.
- Painel para a família acompanhar as consultas e os alertas.
Fontes:
- Simula & Simplifica – site oficial
- Diário da Mídia – Alexa+: acesso antecipado no Brasil
- IstoÉ Dinheiro – Amazon lança Alexa+ no Brasil; veja preço
- Forbes Brasil – Alexa+ chega ao Brasil
- Overdrive – Dispositivos compatíveis com Alexa+
- Neptune Systems Forum – skills "ask/tell" na Alexa+
