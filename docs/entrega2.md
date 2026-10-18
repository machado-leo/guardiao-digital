# Entrega 2 – Construa (respostas do formulário)

Respostas enviadas no formulário do Simula & Simplifica. Prazo para o 2º Ranking: **20/10**.

## Abordagem

Agente de IA

## Ferramentas, linguagens ou plataformas utilizadas

- Python 3.11 com FastAPI (endpoint HTTPS que recebe a Alexa) e LangGraph (grafo de decisão com memória da conversa).
- Alexa Skills Kit com uma skill própria em pt-BR, "Guardião Digital", testada numa Echo Dot pelo beta test.
- OpenAI: GPT para interpretar respostas livres, reescrever as perguntas e escrever a fala final, e embeddings para a busca.
- ChromaDB como banco vetorial, com uma base de 26 golpes curada à mão de fontes oficiais (Febraban, INSS, Banco Central, Correios, Receita Federal, CERT.br).
- Bot do Telegram para o alerta à família (escolhi por ser mais simples de integrar que o WhatsApp, que fica como melhoria futura).
- Langfuse para observabilidade, com mascaramento de números por causa da LGPD (desligado só nos testes com dados fictícios, para analisar os traces completos).
- Cloudflare Tunnel para expor o servidor local em HTTPS (o ideal seria uma VM isolada com domínio próprio, mas optei por algo simples nesta etapa).
- Pytest com 85 testes automatizados.

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

O desenvolvimento foi conduzido em parceria com ferramentas de IA (Claude Code e Gemini), seguindo um planejamento estruturado em fases:

1. Planejamento e Roadmap:
   - Levantamento dos tipos de golpes mais comuns contra idosos no Brasil (falso parente, falso suporte de banco, INSS).
   - Definição do escopo da Alexa: atuar estritamente como interface de voz, mantendo o processamento e as regras em um backend dedicado.
   - Desenho do fluxo de tomada de decisão (perguntas dinâmicas, regras determinísticas de risco e limites rígidos de tempo para a Alexa).
2. Backend e Arquitetura (FastAPI + LangGraph):
   - Construção do grafo no LangGraph com nós isolados: extração dos campos, checagem vetorial, pontuação de risco e geração de fala.
   - Divisão clara de papéis: regras de palavras-chave extraem os campos da conversa e o GPT só entra quando elas não entendem; regras fixas calculam o score (0 a 100); e o GPT ajusta a linguagem das perguntas e da fala final, sem nunca decidir o risco.
3. Validação, Testes e Calibração:
   - Criação da base de golpes no ChromaDB com testes de distância de cosseno para evitar falsos positivos.
   - Testes unitários e de integração simulando cenários incompletos e calibrando timeouts para manter as respostas entre ~1 e ~3,5 segundos, dentro do limite de ~8 s da Alexa.
   - Integração do alerta silencioso no Telegram para a família em casos de alto risco.

## Um erro ou dificuldade técnica e como resolveu

1. A busca vetorial pura falhava em relatos vagos (ex.: "uma mulher pediu dinheiro" aproximava-se de falsos suportes bancários com distância 0,41).
2. O pareamento incorreto gerava orientações cruzadas críticas, como tratar pedidos de código de autenticação com instruções voltadas a transferências PIX.
3. Testes empíricos mapearam os intervalos reais de distância de cosseno: correspondências legítimas ficavam em até ~0,29, enquanto relatos sem relação superavam 0,60.
4. A correção combinou pré-filtragem por metadados (remetente e pedido) com um limiar de corte de distância, garantindo que a base só retorne referências do mesmo tipo de golpe.

## Como você testou a solução

A validação do sistema foi estruturada em quatro níveis de teste e observabilidade:

1. Testes Automatizados de Regras e Integração (85 casos com pytest):
   - Cobertura dos padrões de golpes catalogados e de mensagens legítimas de controle (ex.: avisos de fatura sem solicitação de dados, garantindo ausência de falso alarme).
   - Validação de fluxos conversacionais de múltiplos turnos, regras de segurança na fala e nas perguntas, contrato do endpoint da Alexa e disparo da notificação para o Telegram.
2. Simulação Interativa via Linha de Comando (CLI):
   - Execução de cenários textuais com inspeção direta do cálculo de risco (0 a 100), dos fatores que somaram pontos e do golpe correspondente retornado pelo ChromaDB.
3. Teste Ponta a Ponta em Hardware Real (Echo Dot):
   - Caso crítico (falso parente com número novo pedindo PIX): acionamento por voz com "Alexa, abre o Guardião Digital", orientação imediata para não transferir e disparo automático do alerta no Telegram da família.
   - Caso legítimo: resposta tranquilizadora sem alerta à família.
   - Na prática a diferença ficou clara: a Alexa comum responde de forma genérica ou diz que não pode ajudar, enquanto o Guardião conduz a verificação e orienta na hora.
4. Observabilidade e Auditoria (Langfuse):
   - Registro de cada sessão via traces, permitindo auditar o caminho percorrido no grafo, a latência de cada nó, a pontuação de risco e se a fala final foi gerada pelo GPT ou substituída pela fala pronta de segurança.

A abordagem resolve o gargalo da Entrega 1: o idoso recebe a verificação na hora, direto pelo dispositivo de voz, sem depender da resposta de um parente, e a família é avisada automaticamente quando o risco é alto.

## Imagens (5)

1. `skill-app-alexa`: a skill Guardião Digital ativa no app da Alexa
2. `codigo`: `backend/graph/risco.py`, a tabela de sinais de risco
3. `langfuse-e-servidor`: trace de uma conversa no Langfuse e o servidor rodando com o `subir.sh`
4. `Screenshot_1`: conversa no terminal e o alerta chegando no Telegram
5. `teste2`: casos legítimos e de risco passando, e os 85 testes no total
