# Data Model: Bancada de Experimentos de Busca

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-10

Os esquemas formais e exemplos estão em [contracts/](./contracts/).

## Estratégia de divisão (`config/strategies.yaml`)

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `name` | string | sim | Único. Só letras minúsculas, dígitos e `_`. Vira o nome do diretório do índice |
| `type` | enum | sim | `section`, `split` ou `page` |
| `parameters` | objeto | depende do tipo | Parâmetros do tipo |

Parâmetros por tipo:

| Tipo | Parâmetro | Tipo | Regra |
|---|---|---|---|
| `section` | `max_chars` | inteiro | opcional, padrão 1200, mínimo 200 |
| `section` | `overlap` | inteiro | opcional, padrão 100, mínimo 0, menor que `max_chars` |
| `split` | `chunk_size` | inteiro | obrigatório, mínimo 50 |
| `split` | `chunk_overlap` | inteiro | obrigatório, mínimo 0, menor que `chunk_size` |
| `page` | — | — | não aceita parâmetros |

Regras de validação:

- `name` único no arquivo.
- `type` conhecido.
- Parâmetro desconhecido para o tipo é erro (pega erro de digitação).
- Ao menos uma estratégia declarada.

## Experimento (`config/experiments.yaml`)

| Campo | Tipo | Obrigatório | Padrão | Regra |
|---|---|---|---|---|
| `exp_name` | string | sim | — | Único. Letras minúsculas, dígitos e `_` |
| `collection` | string | sim | — | Nome de uma estratégia existente |
| `search_type` | enum | sim | — | `hybrid`, `vector` ou `bm25` |
| `match_count` | inteiro | sim | — | De 1 a 20 |
| `match_threshold` | número | não | 0.0 | De 0 a 1; 0 desliga |
| `use_hyde` | booleano | não | false | — |

O arquivo tem também:

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `assistant` | string | sim | `exp_name` de um experimento do arquivo |
| `experiments` | lista | sim | Pode ser vazia só se `assistant` não for usado; na prática, ao menos o experimento do assistente |

Regras de validação:

- `exp_name` único.
- `collection` existe em `strategies.yaml`.
- `assistant` existe em `experiments`.
- `use_hyde: true` com `search_type: bm25` é erro: o HyDE só atua na busca vetorial.

Um arquivo inválido impede qualquer execução, e a mensagem lista cada problema com o nome do item e o que corrigir (FR-012).

## Índice (`data/index/<estratégia>/`)

| Arquivo | Conteúdo |
|---|---|
| `chroma/` | Banco vetorial com os trechos e os embeddings |
| `chunks.json` | Lista de `{content, metadata}`; `metadata` tem `source`, `strategy` e, conforme o tipo, `section` ou `page` |
| `manifest.json` | Como o índice foi criado |

### Manifesto

| Campo | Descrição |
|---|---|
| `strategy` | Nome da estratégia |
| `definition_hash` | Hash de `type` e `parameters` (com os padrões aplicados) |
| `source_hash` | Hash do arquivo do material |
| `embedding_model` | Modelo de embedding usado |
| `chunk_count` | Quantidade de trechos |
| `created_at` | Data e hora |

### Estados do índice

```text
ausente ──(ingest)──► atual ──(YAML, PDF ou modelo de embedding mudou)──► desatualizado ──(ingest)──► atual
```

| Estado | Condição | Efeito |
|---|---|---|
| ausente | o diretório ou o manifesto não existe | Experimento não executado; o chat recusa iniciar |
| desatualizado | `definition_hash`, `source_hash` ou `embedding_model` difere do atual | Experimento não executado; o chat avisa e recusa iniciar |
| atual | os três conferem | Uso normal |

Nos dois primeiros casos a mensagem informa o comando: `python -m assistant.ingest <estratégia>`.

## Configuração de busca do assistente (`RagConfig`)

Montada a partir de um experimento. Substitui os campos `vector_k`, `bm25_k` e `final_k`, que passam a ser calculados.

| Campo | Origem |
|---|---|
| `experiment` | `exp_name` |
| `strategy` | `collection` |
| `search_type`, `match_count`, `match_threshold`, `use_hyde` | Do experimento |
| `vector_k`, `bm25_k`, `final_k` (calculados) | Ver research D5 |
| `chat_model`, `embedding_model`, `temperature`, `seed`, `max_answer_tokens`, `prompt_template`, `user_template` | Como hoje |

### Trecho recuperado (`RetrievedChunk`)

| Campo | Descrição |
|---|---|
| `content`, `rank`, `score` | Como hoje (`score` é a nota própria de cada busca) |
| `similarity` | Novo: cosseno entre o vetor da busca e o trecho, de 0 a 1 |

## Resultado por pergunta (bancada)

| Campo | Tipo | Descrição |
|---|---|---|
| `experiment` | string | Nome do experimento |
| `item_id` | string | Item do gabarito |
| `question` | string | A pergunta |
| `hit` | booleano | Todas as evidências do item vieram entre os trechos |
| `score` | número | Média da `similarity` dos trechos devolvidos; 0 se nenhum |
| `anchored` | booleano | O trecho com a evidência tem o nome do procedimento |
| `retrieved_count` | inteiro | Quantos trechos foram devolvidos |
| `latency_ms` | número | Tempo de `retrieve()` |

## Resultado do experimento (linha da tabela)

| Campo | Tipo | Descrição |
|---|---|---|
| `experiment`, `search_type`, `collection`, `match_threshold`, `match_count`, `use_hyde` | — | Os parâmetros do experimento |
| `score` | número ou vazio | Média dos `score` das perguntas |
| `hits`, `total` | inteiros | Acertos e perguntas avaliadas; a tabela mostra `hits/total` |
| `anchored_rate` | número ou vazio | Fração de perguntas com evidência ancorada |
| `avg_latency_ms` | número ou vazio | Média do tempo por pergunta |
| `status` | enum | `ok`, `not_run` ou `incomplete` |
| `reason` | string | Motivo e comando que resolve, quando `status` não é `ok` |

### Estados do experimento em uma execução

```text
declarado ─► ok           (todas as perguntas avaliadas)
          ├► not_run      (índice ausente ou desatualizado; modelo indisponível)
          └► incomplete   (o serviço de modelos caiu no meio)
```

Só experimentos `ok` entram na ordenação. Os demais aparecem no fim da tabela, sem métricas, com o motivo. Um experimento `incomplete` tem no arquivo de perguntas só as linhas que concluiu.

## Execução da bancada (`evaluation/runs/experiments/`)

| Arquivo | Conteúdo |
|---|---|
| `<AAAAMMDD-HHMMSS>-summary.csv` | Uma linha por experimento, na ordem da tabela, com os campos de "Resultado do experimento" mais `gabarito_version` e `embedding_model` |
| `<AAAAMMDD-HHMMSS>-questions.csv` | Uma linha por experimento e pergunta, com os campos de "Resultado por pergunta" |

Os arquivos de uma execução nunca são alterados nem sobrescritos por outra.

## Registro da avaliação da resposta final (acréscimo a `run.json`)

`config` ganha os campos `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde`. `chunk_size` e `chunk_overlap` passam a aceitar null, para estratégias sem esses parâmetros. Execuções gravadas antes da feature continuam válidas.

## Atalho

| Campo | Descrição |
|---|---|
| nome | Mesmo nome no `Makefile` e no `run.ps1` |
| comando | O comando completo do projeto |
| descrição | Uma linha, mostrada por `help` |

## Relacionamentos

```text
Estratégia 1 ──── 0..1 Índice ──── 1 Manifesto
Estratégia 1 ──── N Experimento
Arquivo de experimentos 1 ──── 1 Experimento do assistente
Experimento 1 ──── 1 RagConfig
Execução da bancada 1 ──── N Resultado do experimento ──── N Resultado por pergunta ──── 1 Item do gabarito
Avaliação da resposta final N ──── 1 Experimento
```
