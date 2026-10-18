# Entrega 2 – Construa (rascunho do formulário)

Respostas para colar no formulário do Simula & Simplifica. Prazo para o 2º Ranking: **20/10**.

## Abordagem

Agente de IA

## Ferramentas, linguagens ou plataformas utilizadas

Python 3.11 com FastAPI (endpoint HTTPS que recebe a Alexa) e LangGraph (grafo de decisão
com memória da conversa). Alexa Skills Kit com uma skill própria em pt-BR, "Guardião
Digital", testada numa Echo Dot pelo beta test. OpenAI: GPT para interpretar respostas
livres e escrever a fala final, e embeddings para a busca. ChromaDB como banco vetorial,
com uma base de 26 golpes curada à mão de fontes oficiais (Febraban, INSS, Banco Central,
Correios, Receita Federal, CERT.br). Bot do Telegram para o alerta à família. Langfuse
para observabilidade, com números mascarados por causa da LGPD. Cloudflare Tunnel para
expor o servidor local em HTTPS. Pytest com 85 testes automatizados.

## Regras de negócio, cálculos e condições

1. A conversa preenche 5 campos: remetente (família, banco, INSS, loja ou outro), número
   novo, desculpa, pedido (PIX, senha, código, link, dados, ligar ou nada) e urgência. Se o
   relato já trouxer tudo, vai direto ao veredito. Se faltar algo, o Guardião faz só a
   pergunta que falta, seguindo o roteiro daquele remetente.
2. Interpretação: primeiro regras de palavras-chave, que são rápidas e previsíveis. O GPT
   só entra se as regras não entenderem. Do GPT só vale o "sim": um "não" do modelo pode
   só significar que o relato não tocou no assunto.
3. Busca na base: antes de comparar textos, a busca filtra os golpes com o mesmo pedido e
   o mesmo remetente. O caso só conta como parecido se a distância de cosseno ficar abaixo
   de um limite calibrado com conversas de teste.
4. Risco de 0 a 100, somando sinais com pontos fixos. Senha ou código pedido: 70.
   PIX, link, dados ou "ligue para outro número": 30. Número novo: 30. Instituição pedindo
   isso por mensagem: 30. Urgência ou ameaça: 20. Parecido com golpe da base: 20.
   Padrão do falso parente (família + número novo + PIX): 20. O total vai no máximo até 100.
5. Faixas: baixo (< 40) tranquiliza, mas manda confirmar. Médio (40 a 69) manda confirmar
   por outro caminho. Alto (≥ 70) diz que é golpe provável e avisa a família no Telegram.
6. Regras fixas da fala: o GPT escreve a fala a partir de uma decisão que ele não toma.
   Se a fala autorizar pagamento, garantir que é seguro, citar nome de golpe, passar do
   tamanho ou demorar mais de 3 s, ela é descartada e entra uma fala pronta escrita à mão.
   O Guardião nunca diz "pode pagar".
7. As perguntas do meio também passam pelo GPT, que as reescreve com o que a pessoa já
   contou ("Seu neto explicou por que trocou de número?"), mas sem dar opinião antes do
   veredito. Se a versão do GPT não terminar em uma única pergunta, perder as opções da
   original, falar em golpe ou demorar mais de 2 s, vale a pergunta pronta.
8. Privacidade: a memória da conversa é apagada quando a sessão termina, os logs não
   guardam o que foi falado e o alerta não leva nomes nem valores.

## Como você utilizou a IA para construir a solução

> ⚠️ Substitua pelo prompt que você realmente usou, se tiver guardado. O texto abaixo é
> só um modelo.

Usei o Claude Code como par de programação no repositório inteiro: montar o grafo do
LangGraph, escrever os testes, calibrar a busca e ajustar o tempo de resposta para a
Alexa. Principal prompt:

"Quero um assistente de voz na Alexa para idosos descobrirem se uma mensagem é golpe. A
Alexa só cuida da voz: monte um backend em FastAPI com um grafo em LangGraph que pergunta
só o que falta (remetente, número novo, pedido, urgência), compara o relato com uma base
de golpes brasileiros no ChromaDB, calcula um risco de 0 a 100 por uma tabela de sinais
explicáveis e avisa a família pelo Telegram quando o risco for alto. O GPT pode escrever a
fala, mas nunca decide o risco e nunca pode dizer 'pode pagar'. Cada resposta tem que
caber no tempo limite da Alexa."

## Um erro ou dificuldade técnica e como resolveu

A busca na base de golpes dava falsos positivos. Um relato vago como "uma mulher pediu
dinheiro" era considerado parecido com um golpe de banco (distância 0,41), e o Guardião
dava a orientação errada: um pedido de código chegou a receber a orientação de um golpe
de PIX. Para resolver, rodei várias conversas de teste e medi as distâncias. Os acertos
reais ficavam até ~0,29, e os casos sem relação passavam de 0,6. A solução teve duas
partes: filtrar a base pelo mesmo pedido e remetente antes de comparar os textos, e só
aceitar o caso parecido abaixo de um limite calibrado. Depois disso, cada orientação passou
a vir de um golpe do mesmo tipo.

Outras dificuldades, se quiser trocar:
- A Alexa transcreve "um" e "uma" como "1", e "uma vez" virava valor em dinheiro. Agora
  valores pequenos não contam como dinheiro.
- A Alexa mostrava "Erro ao comunicar-se com a Skill" sem nada chegar no servidor. A causa
  era o tipo de certificado do endpoint: com o túnel do Cloudflare é preciso marcar a opção
  de certificado *wildcard*.
- O tempo de resposta: a Alexa espera ~8 s, e RAG + GPT podia passar disso. Coloquei um
  limite de 3 s na fala do GPT, com uma fala pronta de reserva. Cada fala agora responde
  entre 0,01 e ~3,5 s.

## Como você testou a solução

Testei em três níveis. Primeiro, 85 testes automatizados (pytest), que rodam só com as
regras: os golpes da base, casos legítimos que não podem gerar alarme (o banco avisando
que a fatura fechou, sem pedir nada, por exemplo), conversas completas de várias falas, as
regras da fala, o endpoint da Alexa e o alerta do Telegram. Segundo, conversas por texto
no terminal (CLI), que mostram o risco, os motivos e o golpe parecido de cada caso.
Terceiro, de ponta a ponta numa Echo Dot real: "Alexa, abre o Guardião Digital", contar o
golpe do falso parente pedindo PIX de um número novo, receber a orientação de não pagar e
ver o alerta chegar no Telegram da família. Também testei um caso legítimo, que foi
tranquilizado sem alerta. Cada conversa vira um trace no Langfuse, onde conferi o caminho
do grafo, o risco, o tempo de cada fala e se a fala veio do GPT ou da reserva. Isso
resolve o gargalo da Entrega 1: o idoso não precisa mais esperar um familiar responder,
recebe a verificação na hora e a família é avisada automaticamente.

## Imagens (1 a 5)

1. Echo Dot ou app da Alexa com a skill aberta (`skill/assets/skill-app-alexa.jpg`)
2. Alerta chegando no Telegram da família
3. Trace de uma conversa no Langfuse (caminho do grafo, risco, scores)
4. Código: `backend/graph/risco.py` (tabela de sinais) ou o grafo em `backend/graph/grafo.py`
5. Terminal com os 85 testes passando ou uma conversa no CLI mostrando o risco

## Autoavaliação

Respostas pessoais: evolução no uso de IA (1 a 5), satisfação com a etapa (1 a 5),
recomendaria o projeto (1 a 10) e facilidade da plataforma (1 a 5).
