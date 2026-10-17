# Skill da Alexa

A skill só cuida da voz: cada fala vai para `POST /alexa` no backend, que devolve a
próxima pergunta ou o veredito.

## Criar a skill no console

1. Em [developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask),
   crie uma skill chamada **Guardião Digital**:
   - idioma **Portuguese (BR)**, modelo **Custom**;
   - hospedagem **Provision your own** e modelo **Start from scratch**.
2. Em **Build → Interaction Model → JSON Editor**, cole o conteúdo de
   `interaction-model/pt-BR.json`, clique em **Save** e depois em **Build skill**.
3. Copie o **Skill ID** (`amzn1.ask.skill...`) para `ALEXA_SKILL_ID` no `.env`.

## Ligar ao backend

1. Rode `./skill/subir.sh`. Ele sobe o backend e um túnel HTTPS e mostra a URL do endpoint.
2. Em **Build → Endpoint**, escolha **HTTPS**, cole a URL em **Default Region** e,
   no certificado, escolha *My development endpoint is a sub-domain of a domain that
   has a wildcard certificate from a certificate authority*. Salve.
3. A URL do túnel muda toda vez que o script roda. Atualize o endpoint antes de cada teste.

## Testar

- **Console:** na aba **Test**, ative *Development* e digite ou fale "abre o guardião digital".
- **Echo Dot:** com a mesma conta Amazon do console e o aparelho em português, diga
  "Alexa, abre o Guardião Digital". Skills em desenvolvimento aparecem sozinhas nos
  aparelhos da conta.

## Como a fala chega no backend

- `RespostaIntent`: respostas curtas ("meu filho", "o banco"), num slot próprio.
- `FraseIntent`: frases livres com uma palavra de apoio ("pediram a senha",
  "disseram que ia cortar o benefício"). A Alexa exige essa palavra no
  `AMAZON.SearchQuery`, e ela não chega ao backend: "pediram a senha" chega como "a senha".
- "Sim" e "não" chegam pelos intents prontos da Alexa. Ajuda, repetir, parar e "não
  entendi" (`AMAZON.FallbackIntent`) também são tratados pelo backend.
