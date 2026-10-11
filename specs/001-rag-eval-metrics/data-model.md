# Data Model: Avaliação e Métricas do Assistente OdontoTest

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-10

Todos os dados ficam em arquivos JSON (UTF-8) dentro de `evaluation/`. Os esquemas formais estão em [contracts/](./contracts/).

## Gabarito (`evaluation/data/gabarito.json`)

| Campo | Tipo | Descrição |
|---|---|---|
| `version` | string | Identificação da versão, alterada pelo responsável a cada mudança de conteúdo (ex.: `2026-10-10.1`) |
| `procedures` | objeto | Para cada procedimento: `anchors`, a lista de termos que o identificam em um trecho (ex.: `clareamento`) |
| `items` | lista de Item | As perguntas |

O hash do arquivo é calculado em cada execução e gravado junto com `version`. Se o conteúdo mudar sem a versão mudar, a comparação detecta pelo hash (FR-026).

### Item do gabarito

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | string | sim | Único e estável (ex.: `clareamento-preco-01`). Nunca é reaproveitado |
| `question` | string | sim | A pergunta como o cliente escreveria |
| `category` | enum | sim | `price`, `duration`, `result`, `indication`, `how_it_works`, `differentials`, `comparison`, `out_of_scope`, `adversarial` |
| `procedure` | string ou null | sim | Chave em `procedures`; null para perguntas gerais ou fora do escopo |
| `answerable` | booleano | sim | Se o material da clínica responde à pergunta |
| `expected_facts` | lista de Fato | se `answerable` | Fatos que a resposta precisa conter |
| `allowed_facts` | lista de Fato | não | Fatos que podem aparecer sem contar como erro |
| `evidence` | lista de string | se `answerable` | Trechos literais do material onde está a resposta |
| `variant_of` | string | não | `id` do item de que este é uma variação de escrita |
| `split` | enum | sim | `dev` ou `holdout` |
| `smoke` | booleano | sim | Se entra na avaliação reduzida |
| `notes` | string | não | Observação livre do responsável |

### Fato

| Campo | Tipo | Descrição |
|---|---|---|
| `type` | enum | `money`, `duration`, `text` |
| `values` | lista de número | Para `money` e `duration`: os valores (ex.: `[500, 1500]` para uma faixa) |
| `unit` | enum | Só para `duration`: `minute`, `hour`, `day`, `month`, `year`, `session`, `visit` |
| `alternatives` | lista de string | Só para `text`: formas aceitas; basta uma aparecer |
| `label` | string | Nome curto para o placar (ex.: `preço`) |

### Regras de validação

- `id` único em todo o gabarito.
- Item com `answerable: true` tem ao menos um fato esperado e ao menos uma evidência.
- Item com `answerable: false` não tem `expected_facts` nem `evidence`.
- Cada string de `evidence` aparece exatamente uma vez no texto do material (comparação normalizada).
- Cada valor de fato `money` ou `duration` aparece em pelo menos uma evidência do próprio item.
- `procedure`, quando preenchido, existe em `procedures`.
- `variant_of`, quando preenchido, aponta para um item existente e do mesmo `split`.
- Cobertura (SC-001): ao menos 40 itens; todo procedimento tem ao menos um item de `price`, `duration` e `result`; ao menos 6 itens com `answerable: false`.
- Um gabarito inválido impede a avaliação e a mensagem lista cada problema com o `id` do item.

## Configuração do assistente (`RagConfig`)

Registrada em cada execução.

| Campo | Descrição |
|---|---|
| `chunk_size`, `chunk_overlap` | Parâmetros de divisão do material |
| `vector_k`, `bm25_k` | Trechos devolvidos por cada busca |
| `chat_model`, `embedding_model` | Modelos usados |
| `temperature`, `seed`, `num_ctx` | Parâmetros de geração |
| `prompt_hash` | Hash das instruções de atendimento |
| `kb_hash`, `kb_chunk_count` | Hash e quantidade dos trechos da base de conhecimento |
| `judge_model` | Modelo do juiz, ou null quando o juiz não rodou |
| `git_commit`, `git_dirty` | Commit do código e se havia alterações não commitadas |

## Avaliação (`evaluation/runs/<run_id>/run.json`)

| Campo | Tipo | Descrição |
|---|---|---|
| `run_id` | string | `<AAAAMMDD-HHMMSS>[-<rótulo>]` |
| `started_at`, `finished_at` | data-hora | Início e fim |
| `status` | enum | `complete` ou `incomplete` |
| `subset` | enum | `dev`, `holdout` ou `smoke` |
| `gabarito_version`, `gabarito_hash` | string | Versão e hash do gabarito usado |
| `config` | RagConfig | Configuração do assistente |
| `repeat` | inteiro | Quantas vezes o conjunto foi rodado |
| `results` | lista de Resultado | Um por pergunta (da primeira repetição) |
| `metrics` | Métricas | Notas agregadas |
| `variance` | objeto | Por métrica: média, mínimo e máximo entre repetições (presente quando `repeat` > 1) |
| `skipped` | lista de string | `id` dos itens não avaliados (preenchido quando `incomplete`) |

### Estados

```text
em execução ──► complete     (gravada em runs/<run_id>/; entra no histórico)
            └─► incomplete   (gravada em runs/_incomplete/<run_id>/; fora do histórico)
```

Uma avaliação `complete` nunca é alterada depois de gravada. Só uma avaliação `complete` pode ser referência ou entrar em comparação.

### Resultado por pergunta

| Campo | Tipo | Descrição |
|---|---|---|
| `item_id` | string | Item do gabarito |
| `answer` | string | Resposta do assistente |
| `retrieved` | objeto | Listas `vector`, `bm25` e `fused`; cada trecho com `content`, `rank` e `score` |
| `retrieval` | objeto | Por fonte: `hit`, `recall`, `mrr`, `context_precision`, `anchored` |
| `facts` | lista | Por fato esperado: `label`, `found` |
| `unexpected_values` | lista | Valores de dinheiro ou duração na resposta fora do esperado e do permitido |
| `ungrounded_values` | lista | Valores na resposta que não estão em nenhum trecho recuperado |
| `abstained` | booleano | Se o assistente recusou |
| `rule_violations` | lista de string | Regras de atendimento violadas |
| `judge` | objeto ou null | Por critério (`relevance`, `tone`, `scheduling`, `conciseness`, `faithfulness`): `verdict` e `reason` |
| `latency_s` | número | Tempo de resposta |
| `passed` | booleano | Fatos corretos, recusa correta e nenhuma regra violada |
| `cause` | enum ou null | `retrieval_failure`, `answer_failure`, `fabricated`, `wrong_refusal`, `rule_violation`; null quando `passed` |
| `flags` | lista de string | Sinais secundários (ex.: `evidence_not_anchored`, `other_procedure_value`) |

As notas do juiz nunca alteram `passed`.

### Métricas agregadas

| Grupo | Métricas | Base |
|---|---|---|
| Geral | `pass_rate` | todos os itens |
| Busca (por fonte: `vector`, `bm25`, `fused`) | `hit_rate`, `recall`, `mrr`, `context_precision`, `anchored_rate` | itens com resposta |
| Resposta | `factual_accuracy`, `faithfulness_numeric`, `correct_refusal_rate`, `wrong_refusal_rate`, `rule_compliance` | conforme a métrica |
| Juiz | `relevance`, `tone`, `scheduling`, `conciseness`, `faithfulness_claims`, cada uma com `human_agreement` | itens julgados |
| Operação | `latency_p50`, `latency_p95` | todos os itens |
| Diagnóstico | contagem por `cause`; `pass_rate` por `category` e por `procedure` | conforme o grupo |

As definições estão em [research.md](./research.md) (D2 a D9 e D14).

## Referência (`evaluation/runs/baseline.json`)

| Campo | Descrição |
|---|---|
| `dev` | `run_id` da avaliação de referência do recorte `dev` |
| `holdout` | `run_id` da referência do recorte `holdout` (opcional) |
| `set_at` | Quando a referência foi marcada |

## Comparação (calculada, não gravada)

| Campo | Descrição |
|---|---|
| `base`, `candidate` | Os dois `run_id` |
| `comparable` | Falso quando o recorte ou o hash do gabarito diferem; a mensagem diz qual |
| `metric_deltas` | Por métrica: valor base, valor candidato e diferença |
| `regressions` | Itens que passaram de certo para errado, com a causa nova |
| `improvements` | Itens que passaram de errado para certo |
| `config_changes` | Campos de `RagConfig` que mudaram entre as duas |
| `within_noise` | Por métrica: se a diferença é menor que a variação medida entre repetições |

Quando o gabarito difere, a comparação por item é feita só sobre os `id` presentes nos dois e o aviso informa quantos ficaram de fora.

## Amostra de conferência humana (`evaluation/data/human_labels.json`)

| Campo | Descrição |
|---|---|
| `run_id` | Avaliação de onde as respostas foram tiradas |
| `samples` | Lista com `item_id`, `question`, `answer` e, por critério, `human` (preenchido pelo responsável) |

O arquivo é gerado com o campo `human` vazio e sem as notas do juiz, para o responsável não ser influenciado. A concordância é a fração de respostas em que `human` é igual ao veredito do juiz, calculada por critério.

## Relacionamentos

```text
Gabarito 1 ──── N Item ──── N Fato
Avaliação N ──── 1 Gabarito (por versão e hash)
Avaliação 1 ──── 1 RagConfig
Avaliação 1 ──── N Resultado ──── 1 Item
Referência ──── 1 Avaliação por recorte
Comparação ──── 2 Avaliações
Amostra de conferência ──── 1 Avaliação
```
