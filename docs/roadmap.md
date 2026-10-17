# Roadmap — Guardião Digital

Prazo final: **29/10**.

## 1. Validações iniciais
- [ ] Criar uma skill "Guardião" de teste e confirmar que "Alexa, abre o Guardião" funciona na Dot 3
- [ ] Testar o `AMAZON.SearchQuery` em pt-BR com uma frase de apoio
- [ ] Medir quanto o GPT demora numa chamada curta, para saber o que cabe nos ~8 segundos da Alexa

## 2. Grafo de decisão (`backend/graph/`)
- [ ] Definir o estado da conversa: `remetente`, `canal`, `numero_novo`, `pedido`, `urgencia`, `risco`
- [ ] Criar os nós de pergunta e as ramificações para filho/neto, banco e INSS
- [ ] Interpretar as respostas com regras e palavras-chave, chamando o GPT só quando elas não resolverem
- [ ] Gerar o veredito com a regra fixa: nunca dizer "pode pagar"
- [ ] Criar uma CLI para testar a conversa por texto
- [ ] Ligar o Langfuse ao grafo (`CallbackHandler` no `config`, `sessionId` da Alexa como `session_id`), desligável por `LANGFUSE_ENABLED`

## 3. Pontuação de risco
- [ ] Definir uma regra de 0 a 100 que dê para explicar (ex.: número novo +30, PIX +30, urgência +20)
- [ ] Definir o limiar de alerta (`RISK_ALERT_THRESHOLD`)

## 4. Base de golpes (`data/golpes/` e `backend/rag/`)
- [ ] Escrever de 20 a 30 casos com descrição, sinais, orientação e fonte (Febraban, BCB, INSS, CERT.br)
- [ ] Criar o script que indexa a base no ChromaDB
- [ ] Criar a função de busca e ligá-la ao veredito, para a resposta citar o golpe parecido

## 5. Alerta à família (`backend/alerts/`)
- [ ] Criar o bot do Telegram que recebe o alerta quando o risco passa do limiar
- [ ] Definir uma mensagem curta e clara para o filho ou neto

## 6. Backend (`backend/`)
- [ ] Criar o endpoint FastAPI no formato de requisição da Alexa
- [ ] Guardar a memória da conversa por `sessionId`
- [ ] Validar o `ALEXA_SKILL_ID`
- [ ] Fazer logs sem dados pessoais (LGPD)
- [ ] Mascarar nomes, valores e telefones antes de enviar os traces ao Langfuse
- [ ] Não chamar `flush()` do Langfuse dentro da requisição da Alexa

## 7. Testes por texto
- [ ] Testar roteiros de falso filho, falso banco, INSS, frete e um caso legítimo
- [ ] Medir a latência do começo ao fim, etapa por etapa, pelos traces do Langfuse

## 8. Skill da Alexa (`skill/`)
- [ ] Escrever o modelo de interação: intents, slots, reprompt e `shouldEndSession: false`
- [ ] Ligar a skill ao endpoint pelo túnel (ngrok ou cloudflared), ou pela Lambda se o túnel der problema
- [ ] Adicionar a fala de espera ("deixa eu verificar")
- [ ] Testar na Dot 3 com frases reais

## 9. Apresentação
- [ ] Gravar a Alexa comum respondendo ao mesmo golpe
- [ ] Preparar o slide de contexto (o golpe e o gargalo da Etapa 1)
- [ ] (Opcional) Mostrar o caminho que o grafo percorreu e o trecho da base usado, abrindo o trace no Langfuse
- [ ] Deixar o plano B pronto: simulador do console da Amazon
- [ ] Ensaiar a demo em menos de 3 minutos

## 10. Extras (só se sobrar tempo)
- [ ] Script de RSS para adicionar golpes novos à base

**Se apertar, cortar nesta ordem:** extras, a tela "por dentro do grafo" e as ramificações de INSS e banco. O caso do falso filho sozinho já sustenta a demo.
