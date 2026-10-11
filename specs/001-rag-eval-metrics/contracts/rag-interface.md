# Contract: Interface do assistente consultável (`assistant/pipeline.py`)

> Em 2026-10-10 o projeto foi reorganizado: `rag.py` virou `assistant/pipeline.py`, `create_db.py` virou `assistant/ingest.py` e `main.py` virou `assistant/chat.py`. A interface descrita aqui não mudou.

Atende FR-030. É a única superfície do assistente que a avaliação usa. O chat interativo (`main.py`) usa a mesma interface.

## `RagConfig`

Objeto imutável com os parâmetros do assistente. Os valores padrão reproduzem o comportamento atual.

| Campo | Padrão | Origem do padrão |
|---|---|---|
| `vector_k` | 3 | valor atual em `main.py` |
| `bm25_k` | 3 | valor atual em `main.py` |
| `chat_model` | `OLLAMA_CHAT_MODEL` ou `llama3` | como hoje |
| `embedding_model` | `OLLAMA_EMBEDDING_MODEL` ou `nomic-embed-text` | como hoje |
| `temperature` | null (padrão do modelo) | como hoje |
| `seed` | null | como hoje |
| `prompt_template` | o texto atual de `main.py` | como hoje |

A avaliação usa `temperature=0` e `seed=42`.

## `retrieve(question, config) -> RetrievalResult`

Devolve o que cada busca recuperou e o conjunto final, sem chamar o modelo de linguagem.

| Campo de `RetrievalResult` | Descrição |
|---|---|
| `vector` | Lista ordenada de trechos da busca vetorial, cada um com `content`, `rank` (a partir de 1) e `score` |
| `bm25` | Lista ordenada de trechos da busca lexical, com os mesmos campos |
| `fused` | Lista final enviada ao modelo: vetorial seguida de lexical, sem repetição, na ordem de hoje |

## `answer(question, config) -> AnswerResult`

Roda a busca e gera a resposta.

| Campo de `AnswerResult` | Descrição |
|---|---|
| `answer` | Texto da resposta |
| `retrieval` | O `RetrievalResult` usado |
| `latency_s` | Tempo total da busca e da geração |

## Garantias

- Importar `rag` não executa nada: não abre o laço de conversa, não recria a base e não chama modelos.
- Com `RagConfig()` padrão, `answer()` monta o mesmo contexto e o mesmo prompt que o `main.py` atual monta para a mesma pergunta.
- `answer()` e `retrieve()` não guardam estado entre chamadas.
- Erros do serviço de modelos sobem como exceção; a função não devolve resposta vazia no lugar.

## Verificação

Um teste de integração compara, para um conjunto fixo de perguntas, o contexto e o prompt montados por `rag.answer()` com os do pipeline anterior à extração, e exige igualdade.
