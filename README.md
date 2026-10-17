# Guardião Digital

Assistente de voz que ajuda pessoas idosas a descobrir, na hora, se uma mensagem ou
ligação é golpe — e avisa a família quando o risco é alto.

Projeto da disciplina **Simula & Simplifica: Algoritmos em Ação** (edição 2026.2).

## Como funciona

A Alexa cuida só da voz (ouvir e falar). Toda a decisão acontece no backend, dentro
de um grafo de decisão em LangGraph:

```
Alexa (skill "Guardião")  ->  backend HTTPS  ->  grafo LangGraph
                                                   |-> base de golpes (RAG)
                                                   |-> GPT via API
                                                   `-> alerta no Telegram
```

A cada resposta do idoso, a Alexa envia o texto ao backend, o grafo atualiza o
estado da conversa e devolve a próxima pergunta ou o veredito. Se o risco passar
do limiar, o alerta vai para o Telegram da família.

**Regra fixa de segurança:** o Guardião nunca diz "pode pagar". Na dúvida, a
orientação é sempre confirmar por outro canal antes de qualquer pagamento.

## Estrutura

| Pasta | Conteúdo |
| --- | --- |
| `backend/` | Endpoint HTTPS que recebe os eventos da Alexa |
| `backend/graph/` | Grafo de decisão em LangGraph (perguntas adaptativas, score de risco) |
| `backend/rag/` | Indexação e consulta da base de golpes (ChromaDB ou FAISS) |
| `backend/alerts/` | Bot do Telegram que avisa a família |
| `skill/` | Skill da Alexa: modelo de interação e configuração do endpoint |
| `data/golpes/` | Base curada à mão: 20 a 30 casos com fontes oficiais |
| `docs/` | Documento do projeto e anotações de etapa |

## Rodando localmente

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # preencha as chaves
```

Teste o grafo por texto antes de ligar na Alexa — é bem mais rápido de iterar:

```bash
python -m backend.cli   # conversa com o Guardião no terminal
python -m pytest        # cenários de golpe, só com as regras (sem GPT nem Langfuse)
```

Outros comandos:

```bash
python -m backend.rag.indexar            # recria o índice depois de editar data/golpes/golpes.json
python -m backend.alerts.descobrir_chat  # mostra o TELEGRAM_CHAT_ID depois do /start no bot
uvicorn backend.app:app --port 8000      # endpoint da Alexa em POST /alexa
```

## Cronograma

- **Etapa 1 – Observe:** entregue (nota ponderada 9,35).
- **Etapa 2 – Construa:** até 21/10 — grafo, base de golpes, score de risco, bot do Telegram.
- **Etapa 3 – Apresente:** até 29/10 — skill ligada ao backend, comparativo gravado, ensaio. Live final 29/10, 19h.

Fora do escopo desta entrega: WhatsApp, Gmail, redes sociais e leitura de prints por OCR.
