# Como Contribuir com o Guardião Digital

Obrigado pelo interesse em contribuir com o **Guardião Digital**!

## Regras fundamentais do projeto

Qualquer mudança no código ou na base de golpes deve respeitar quatro invariantes:

1. **Nunca autorizar pagamento:** nenhuma resposta pode dizer "pode pagar", "pode fazer o PIX" ou garantir que uma situação é 100% segura.
2. **Respeito ao tempo da Alexa:** as respostas devem caber com folga na janela de ~8 segundos do hardware Echo.
3. **Linguagem simples e acolhedora:** as falas do veredito devem ter uma ou duas frases curtas ($\le 160$ caracteres na base), sem jargões técnicos.
4. **Privacidade (LGPD):** nunca registrar falas, valores, CPFs ou números de telefone em logs ou testes.

## Adicionando um golpe à base (`data/golpes/golpes.json`)

Cada caso na base deve ter:
- `id`: identificador único em `kebab-case`.
- `nome`: sempre começando com `"golpe "` (ex.: `"golpe do falso parente"`).
- `remetente`: `"familia"`, `"banco"`, `"inss"`, `"loja"` ou `"outro"`.
- `pedidos`: lista com um ou mais valores de `["senha", "codigo", "pix", "link", "dados", "ligar"]`.
- `descricao` e `sinais`: texto claro para busca vetorial.
- `acao`: orientação direta para a pessoa idosa, com no máximo 160 caracteres.
- `fonte`: órgão ou instituição oficial com URL `https://` (Febraban, Banco Central, INSS, Correios, Receita Federal, CERT.br, gov.br).

Depois de editar `data/golpes/golpes.json`, recrie o índice local:

```bash
python -m backend.rag.indexar
```

## Rodando os testes

Antes de abrir um Pull Request, garanta que todos os testes passem:

```bash
python -m pytest
```
