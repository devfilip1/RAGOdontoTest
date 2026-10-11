# Contract: Arquivos de resultado da bancada

Gravados em `evaluation/runs/experiments/`, em UTF-8 com BOM (para abrir com acentos no Excel), separador `;` e ponto como separador decimal. O separador `;` evita conflito com as vírgulas das perguntas e é o que o Excel em português espera.

`<data-hora>` é o início da execução, no formato `AAAAMMDD-HHMMSS`.

## `<data-hora>-summary.csv`

Uma linha por experimento, na ordem da tabela.

| Coluna | Exemplo | Descrição |
|---|---|---|
| `experiment` | `section_hybrid` | Nome do experimento |
| `search_type` | `hybrid` | Tipo de busca |
| `collection` | `section` | Estratégia de divisão |
| `match_threshold` | `0.00` | Similaridade mínima |
| `match_count` | `4` | Máximo de trechos |
| `use_hyde` | `false` | Uso de HyDE |
| `score` | `0.6612` | Média das notas das perguntas; vazio se não executado |
| `hits` | `37` | Perguntas em que todas as evidências vieram |
| `total` | `38` | Perguntas avaliadas |
| `true_rate` | `0.9737` | `hits / total` |
| `anchored_rate` | `1.0000` | Fração com evidência ancorada |
| `avg_latency_ms` | `58.3` | Tempo médio da busca por pergunta |
| `status` | `ok` | `ok`, `not_run` ou `incomplete` |
| `reason` | | Motivo, quando `status` não é `ok` |
| `gabarito_version` | `2026-10-10.1` | Versão do gabarito usado |
| `embedding_model` | `nomic-embed-text` | Modelo de embedding |

## `<data-hora>-questions.csv`

Uma linha por experimento e pergunta avaliada.

| Coluna | Exemplo | Descrição |
|---|---|---|
| `experiment` | `section_hybrid` | Nome do experimento |
| `item_id` | `clareamento-preco-01` | Item do gabarito |
| `question` | `Quanto custa o clareamento?` | A pergunta |
| `hit` | `true` | Todas as evidências vieram |
| `score` | `0.7104` | Média da similaridade dos trechos devolvidos |
| `anchored` | `true` | O trecho com a evidência tem o nome do procedimento |
| `retrieved_count` | `3` | Trechos devolvidos |
| `latency_ms` | `54.1` | Tempo da busca |

## Linha por pergunta no terminal (`--verbose`)

```text
Quanto custa o clareamento?;true;0.71
```

Pergunta, `true` ou `false`, e a nota com duas casas, separados por `;`.
