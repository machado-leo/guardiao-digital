# Política de Privacidade: Guardião Digital

Última atualização: 17 de outubro de 2026

O Guardião Digital é uma skill da Alexa criada como projeto acadêmico do
**Simula & Simplifica: Algoritmos em Ação** (edição 2026.2). Ela ajuda pessoas
idosas a descobrir se uma mensagem ou ligação é golpe e, quando o risco é alto,
avisa um familiar. Esta política explica quais dados a skill usa, para quê e por
quanto tempo, de acordo com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

## Quais dados usamos

- **O que você responde às perguntas da skill**, por exemplo quem mandou a
  mensagem, o que foi pedido e se houve urgência. A Alexa transforma sua fala em
  texto e envia esse texto para o nosso servidor.
- **Identificadores técnicos da Alexa**: o identificador da sessão e da skill,
  usados só para manter a conversa em andamento.

A skill **não pede** seu nome, endereço, CPF, dados bancários ou senhas, e não
acessa sua conta Amazon, seus contatos ou suas listas.

## Para que usamos

- Entender suas respostas e fazer a próxima pergunta.
- Comparar o caso com uma base de golpes conhecidos e dar uma orientação.
- Avisar um familiar quando o risco de golpe é alto.
- Medir se a skill está funcionando e respondendo a tempo.

## Com quem os dados são compartilhados

- **Amazon (Alexa)**: recebe e processa sua voz, conforme a política de
  privacidade da própria Amazon.
- **OpenAI**: quando uma resposta não é entendida pelas regras da skill, o texto
  dela é enviado à API da OpenAI para interpretação e para a busca na base de
  golpes. O uso desses dados segue as políticas da OpenAI.
- **Telegram**: quando o risco é alto, um familiar previamente cadastrado recebe
  uma mensagem com o nível de risco, os sinais de golpe encontrados e a orientação
  dada. **Essa mensagem não inclui suas falas, nomes, valores nem números de
  telefone.**
- **Langfuse**: registra o funcionamento técnico de cada conversa (etapas, tempo
  de resposta). Antes do envio, números como telefones, valores e CPF são
  trocados por "[número]".

Não vendemos dados, não usamos dados para publicidade e não compartilhamos com
ninguém além dos serviços acima.

## Por quanto tempo guardamos

- A conversa fica na memória do servidor só enquanto a sessão está aberta e é
  apagada quando ela termina.
- Os registros do servidor guardam apenas o tipo de pedido, a etapa da conversa e
  o tempo de resposta, sem o que você falou.
- Os registros técnicos no Langfuse são usados só durante o projeto e apagados ao
  final dele.

## Seus direitos

Pela LGPD, você pode pedir informações sobre seus dados, a correção ou a
exclusão deles. Para isso, abra uma *issue* no repositório do projeto:
<https://github.com/machado-leo/guardiao-digital/issues>.

## Aviso importante

O Guardião Digital dá orientações e não substitui o seu banco, o INSS ou a
polícia. Ele **nunca autoriza pagamentos**: na dúvida, confirme sempre por outro
canal antes de pagar ou passar qualquer dado.
