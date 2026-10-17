# Roadmap — Guardião Digital

Etapa 2 até **20/10** (2º Ranking em 21/10) · Etapa 3 de **21/10 a 29/10**.

## 1. Validações iniciais
- [x] Criar a skill e confirmar que ela abre na Echo Dot (nome final: "Guardião Digital"; a Dot de outra conta acessa pelo beta test)
- [x] Testar o `AMAZON.SearchQuery` em pt-BR com palavras de apoio (`FraseIntent`)
- [x] Medir quanto o GPT demora numa chamada curta (`gpt-6-luna`: 1,2 a 1,6 s, com picos de ~4 s)

## 2. Grafo de decisão (`backend/graph/`)
- [x] Definir o estado da conversa
- [x] Começar com o relato aberto ("me conta o que aconteceu") e só perguntar o que faltou
- [x] Interpretar as respostas com regras e palavras-chave, chamando o GPT só quando elas não resolverem
- [x] Gerar a fala final pelo GPT, com regras fixas e fala pronta de reserva: nunca dizer "pode pagar"
- [x] Criar uma CLI para testar a conversa por texto
- [x] Ligar o Langfuse ao grafo, com o `sessionId` da Alexa como sessão

## 3. Pontuação de risco
- [x] Definir uma regra de 0 a 100 que dê para explicar: tabela de sinais em `backend/graph/risco.py`
- [x] Definir o limiar de alerta (`RISK_ALERT_THRESHOLD`): baixo < 40, médio 40 a 69, alto ≥ 70
- [x] Usar a base de golpes como sinal de risco ("parecido com um golpe conhecido")

## 4. Base de golpes (`data/golpes/` e `backend/rag/`)
- [x] Escrever 26 casos com descrição, sinais, ação e fonte oficial
- [x] Criar o script que indexa a base no ChromaDB
- [x] Criar a busca, filtrando por pedido e remetente antes de comparar os textos

## 5. Alerta à família (`backend/alerts/`)
- [x] Criar o bot do Telegram que recebe o alerta quando o risco passa do limiar
- [x] Definir uma mensagem curta e clara para o filho ou neto

## 6. Backend (`backend/`)
- [x] Criar o endpoint FastAPI no formato de requisição da Alexa
- [x] Guardar a memória da conversa por `sessionId`
- [x] Validar o `ALEXA_SKILL_ID`
- [x] Fazer logs sem dados pessoais (LGPD)
- [x] Mascarar números nos traces do Langfuse (configurável por `LANGFUSE_MASCARAR`)
- [x] Não chamar `flush()` do Langfuse dentro da requisição da Alexa

## 7. Testes
- [x] Testar roteiros de golpe: falso parente, falsa central, INSS, frete, sequestro, clonagem
- [x] Testar 10 casos legítimos, que não podem gerar alerta
- [x] Medir a latência por etapa pelos traces do Langfuse
- [x] Registrar scores por conversa no Langfuse (risco, nível, alerta, golpe parecido, origem da fala)

## 8. Skill da Alexa (`skill/`)
- [x] Escrever o modelo de interação: intents, slots, reprompt e `shouldEndSession: false`
- [x] Ligar a skill ao endpoint pelo túnel (cloudflared, certificado wildcard no console)
- [x] Testar na Echo Dot com frases reais
- [x] Ícones e política de privacidade para o beta test
- [x] ~~Fala de espera ("deixa eu verificar")~~: dispensada, as respostas ficam abaixo de ~3,5 s
- [ ] Testar mais relatos na Dot, olhando os traces: as respostas curtas pelo `RespostaIntent` ainda saem distorcidas às vezes

## 9. Apresentação
- [ ] Gravar a Alexa comum respondendo ao mesmo golpe
- [ ] Preparar o slide de contexto (o golpe e o gargalo da Etapa 1)
- [ ] (Opcional) Mostrar o caminho do grafo e os scores, abrindo a sessão no Langfuse
- [ ] Deixar o plano B pronto: simulador do console da Amazon
- [ ] Ensaiar a demo em menos de 3 minutos
- [ ] **Antes da demo:** voltar `LANGFUSE_MASCARAR=true` no `.env`, como promete a política de privacidade
- [ ] **Antes da demo:** subir com `RECARREGAR=0 ./skill/subir.sh`

## 10. Extras (só se sobrar tempo)
- [ ] Script de RSS para adicionar golpes novos à base
- [x] Reconhecer farmácia, mercado e prefeitura como remetentes conhecidos

