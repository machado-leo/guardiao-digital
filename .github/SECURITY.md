# Política de Segurança

## Regras de segurança do Guardião Digital

O Guardião Digital lida com situações de potencial fraude financeira contra pessoas idosas. Por isso, a segurança e a privacidade são tratadas como requisitos críticos:

- **Validação de origem:** o endpoint `/alexa` confere o `ALEXA_SKILL_ID` e rejeita requisições com *timestamp* fora da tolerância de 150 segundos (prevenção contra ataques de repetição).
- **Decisão determinística:** o cálculo de risco (0 a 100) é feito por regras explícitas em `backend/graph/risco.py`, nunca por decisão livre do modelo de linguagem.
- **Trava contra autorização de pagamento:** toda fala gerada passa por validação em `backend/graph/fala.py` e `backend/graph/veredito.py`. Se o modelo demorar, citar termos proibidos ou tentar autorizar pagamento, o sistema usa a fala pronta escrita à mão.
- **Proteção de dados (LGPD):** a memória da conversa é apagada ao fim da sessão, os logs não guardam o que foi falado e números são mascarados antes do envio ao Langfuse. Detalhes em [`docs/privacidade.md`](../docs/privacidade.md).

## Como relatar um problema de segurança

- **Nunca publique chaves de API, tokens do Telegram ou dados pessoais reais** em *issues* ou *Pull Requests*.
- Caso encontre uma falha que faça o assistente autorizar pagamentos indevidos, vazar dados pessoais nos logs ou aceitar requisições inválidas, abra uma *issue* descrevendo os passos para reproduzir com dados fictícios.
