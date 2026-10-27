# Roteiro do vídeo – Entrega 3 (Apresente)

Vídeo pitch do Guardião Digital para a Entrega 3 do Simula & Simplifica. Prazo: **28/10**
(a live de premiação é em 29/10, às 19h).

## O que a banca pede

Do vídeo "Detalhamento Entrega 3" e do formulário de entrega:

- A entrega é só o **link do YouTube**, com o vídeo marcado como **Público**. Vídeo privado
  conta como entrega não feita e tira o direito ao certificado.
- De preferência, **aparecer você e a tela** juntos (Clipchamp → "Tela e câmera").
- Mostrar **como a solução foi construída** (ferramentas) e, principalmente, **o fluxo
  funcionando** da entrada até a saída.
- **Curto e claro.** Alvo: 3 minutos.
- **Vender o projeto:** mostrar o tempo ou o dinheiro que ele economiza.
- Assistir o vídeo inteiro antes de subir e regravar o que não ficou bom.

## Montagem da gravação

- **Tela:** terminal do `./skill/subir.sh` ou o trace no Langfuse atualizando enquanto a Dot fala.
- **Câmera:** você no canto da tela. Nas cenas da Alexa, a Echo Dot (com a luz azul visível)
  e o celular do "neto" com o Telegram aberto no mesmo quadro.
- Grave cada cena separada, várias vezes, e junte as melhores no Clipchamp.
- Exporte em 1080p.

## Roteiro (~3 min)

### Cena 1 – O problema (20–30 s)

**Mostra:** você na câmera e, na tela, o print de uma mensagem do tipo "Oi vó, troquei de
número, me faz um PIX urgente".

**Fala:**
> "Quando um idoso recebe uma mensagem assim, ele depende de um filho ou neto responder
> naquela hora pra saber se é golpe. Se ninguém responde, a pressão do golpista vence.
> O Guardião Digital é uma skill da Alexa que faz essa verificação na hora, por voz, e
> avisa a família quando o risco é alto."

### Cena 2 – A Alexa comum (30 s)

**Mostra:** a Echo Dot em close, sem abrir a skill.

**Pergunta** (a mesma frase da cena 3, palavra por palavra):
> "Alexa, meu neto mandou mensagem de um número novo pedindo 300 reais no PIX, disse que
> era urgente. É golpe?"

**Fala depois da resposta:**
> "Ela responde de forma geral, mas não pergunta nada sobre o que aconteceu e não avisa
> ninguém."

Cuidados:
- Deixe a resposta da Alexa inteira, sem cortes, para a comparação ser justa.
- Ajuste a fala ao que ela realmente responder.
- Se a Dot estiver com a Alexa+, diga isso no vídeo ("essa é a Alexa+, com IA generativa").
- Não diga que a Alexa "é burra".

### Cena 3 – O Guardião com o mesmo golpe (40 s)

**Mostra:** a Dot e o celular com o Telegram no mesmo quadro.

**Diálogo:**
> **Você:** "Alexa, abre o Guardião Digital."
> **Guardião:** "Oi, eu sou o Guardião. Me conta o que aconteceu."
> **Você:** "Meu neto mandou mensagem de um número novo pedindo 300 reais no PIX, disse que
> era urgente."
> **Guardião:** "Isso tem muita cara de golpe, então não faça o PIX. Ligue para o número
> antigo do seu neto, que está salvo na sua agenda. Vou avisar sua família para te ligar
> também."

**Mostra:** o alerta chegando no Telegram, com zoom no celular.

**Fala:**
> "Mesma pergunta. O Guardião dá uma ordem clara, nunca diz 'pode pagar', e a família
> recebe o alerta na hora."

### Cena 4 – Quando o relato vem incompleto (40 s)

Mostra o que a Alexa comum não faz: conduzir a verificação com perguntas.

**Diálogo:**
> **Você:** "Alexa, abre o Guardião Digital."
> **Você:** "Recebi uma mensagem do banco."
> **Guardião:** "E o que pediram? Sua senha, um código, ou para ligar em algum número?"
> **Você:** "Pediram o código que chegou por SMS."
> **Guardião:** "Falaram que era urgente, ou fizeram alguma ameaça?"
> **Você:** "Disseram que a conta ia ser bloqueada hoje."
> **Guardião:** "Atenção: isso tem muita cara de golpe. O banco nunca pede senha ou código
> por mensagem. Não passe nada e ligue para o número que está atrás do seu cartão. Vou
> avisar sua família para te ligar também."

Com o GPT ligado, as perguntas são reescritas a partir do relato e podem sair um pouco
diferentes do texto acima.

**Fala:**
> "Quando falta informação, ele pergunta só o que precisa pra decidir."

### Cena 5 – Sem falso alarme (20 s, opcional)

Se o tempo apertar, essa é a primeira cena a cortar.

**Diálogo:**
> **Você:** "Minha filha pediu para eu comprar pão."
> **Guardião:** pergunta se é um número novo → "Não, o número de sempre."
> **Guardião:** pergunta o que ela pediu → "Pediu para comprar pão na padaria."
> **Guardião:** pergunta se houve urgência → "Não."
> **Guardião:** tranquiliza e não manda alerta.

**Fala:**
> "Ele também sabe quando não é golpe, e aí não assusta ninguém."

### Cena 6 – Como foi construído (30 s)

**Mostra a tela:** o diagrama do README e o trace da cena 3 no Langfuse (caminho do grafo,
risco 100, os sinais que somaram pontos e o golpe parecido encontrado na base).

**Fala:**
> "A Alexa cuida só da voz. A decisão acontece num backend em Python com FastAPI e
> LangGraph. O relato é comparado com 26 golpes reais de fontes oficiais, como Febraban,
> INSS e Banco Central, guardados no ChromaDB. O risco, de 0 a 100, é calculado por regras
> fixas e explicáveis. O GPT só ajusta a linguagem e nunca decide se é golpe. Se o risco
> passa de 70, a família recebe o alerta no Telegram. Tudo isso é coberto por 85 testes
> automatizados."

### Cena 7 – O valor (15–20 s)

**Fala:**
> "Antes, o idoso dependia de alguém responder, o que podia levar horas, ou nunca
> acontecer. Com o Guardião, a verificação leva menos de um minuto e a família fica sabendo
> na hora, antes do PIX."

Se citar o prejuízo com golpes, use um número com fonte (por exemplo, os dados de fraude
da Febraban da Etapa 1) e mostre a fonte na tela.

### Cena 8 – Fechamento (15 s)

**Fala:**
> "O Guardião não substitui a família, ele ganha tempo até ela chegar. Os próximos passos
> são o WhatsApp, a leitura de prints e uma base de golpes que se atualiza sozinha.
> Obrigado!"

## Checklist antes de gravar

- [ ] `LANGFUSE_MASCARAR=true` no `.env` (a política de privacidade promete o mascaramento
      e o trace aparece no vídeo).
- [ ] Rodar `./skill/subir.sh` e colar a nova URL `/alexa` no Endpoint do console da Alexa
      (opção de certificado wildcard).
- [ ] Fazer uma conversa completa de teste antes de gravar.
- [ ] Se for usar o computador da empresa para o backend, confirmar que a rede não bloqueia
      o cloudflared.
- [ ] Nada sensível na tela: `.env`, token do bot, chat ID, abas e notificações da empresa.
- [ ] Responder a skill com frases, não com palavras soltas ("pediram o código…",
      "disseram que…"), porque o modelo de interação capta melhor assim.
- [ ] Ambiente silencioso e Dot perto do microfone.
- [ ] Plano B: gravar a mesma conversa no simulador do console da Amazon.

## Publicação no YouTube

- **Título:** `Guardião Digital: Alexa que detecta golpes contra idosos e avisa a família | Simula e Simplifica`
- **Descrição:**
  > Skill da Alexa que escuta o relato de uma mensagem ou ligação suspeita, compara com 26
  > golpes reais documentados por fontes oficiais, orienta em linguagem simples e avisa a
  > família pelo Telegram quando o risco é alto. Projeto do Simula & Simplifica 2026.2.
  > Código: <link do GitHub>
- **Visibilidade: Público.**
- [ ] Assistir o vídeo inteiro antes de enviar.
- [ ] Abrir o link numa aba anônima e conferir se toca.
- [ ] Colar o link no formulário (Entrega 3) até 28/10.
- [ ] Conferir se o e-mail de contato da inscrição está certo (os 10 primeiros podem ser
      chamados para a live).
