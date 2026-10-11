# Contract: Comandos

Todos rodam da raiz do projeto. Códigos de saída, como nos comandos existentes: `0` sucesso, `1` erro de execução, `2` uso incorreto ou configuração inválida.

Antes de qualquer execução, os comandos abaixo validam `config/strategies.yaml` e `config/experiments.yaml`. Se houver erro, listam cada problema com o nome do item e o que corrigir, e saem com `2` sem executar nada.

## `python -m assistant.ingest [ESTRATÉGIA...]`

Cria os índices.

- Sem argumentos: todas as estratégias de `config/strategies.yaml`.
- Com nomes: só as indicadas. Nome inexistente: sai com `2` e lista os nomes válidos.

Para cada estratégia: divide o material, grava `data/index/<nome>/` (trechos, banco vetorial e manifesto) e informa o nome e a quantidade de trechos. O índice de uma estratégia não indicada não é tocado.

## `python -m assistant.chat`

Como hoje, usando o experimento indicado em `assistant:`. Se o índice da estratégia estiver ausente ou desatualizado, não inicia: informa o motivo e o comando `python -m assistant.ingest <estratégia>`, e sai com `1`.

## `python -m evaluation experiments [NOMES...] [--verbose]`

Roda os experimentos e mostra a tabela comparativa.

| Opção | Efeito |
|---|---|
| (nenhuma) | Todos os experimentos de `config/experiments.yaml` |
| `NOMES...` | Só os experimentos indicados. Nome inexistente: sai com `2` |
| `--verbose` | Mostra uma linha por pergunta |

Comportamento:

1. Valida a configuração e o gabarito.
2. Confere se o serviço de modelos responde. Se não: informa e sai com `1`.
3. Para cada experimento, na ordem do arquivo:
   - índice ausente ou desatualizado: marca como não executado, com o motivo e o comando que resolve, e segue;
   - senão, roda a busca para cada pergunta com resposta do conjunto de trabalho, com barra de progresso `Retrieving and evaluating`.
4. Com `--verbose`, cada pergunta sai como `pergunta;true;0.71` (ou `false`), com a nota em duas casas.
5. Mostra a tabela.
6. Grava os dois CSV e informa os caminhos.

Sai com `0` também quando algum experimento não foi executado. Sai com `1` se nenhum experimento pôde ser executado.

### Tabela

```text
COMPARISON OF RETRIEVAL STRATEGIES
Ordenado por True Rate, depois por Score (no empate, experimentos com HyDE ficam depois).

Experiment                 Strategy  Collection          Threshold  Count  HyDE   Score  True Rate  Anchored  Time
section_hybrid             hybrid    section             0.00       4      False  0.66   37/38      100.0%    58 ms
recursive_500_200_hybrid   hybrid    recursive_500_200   0.00       4      False  0.63   33/38       72.7%    61 ms
page_hybrid                hybrid    page                0.00       4      False  0.61   38/38      100.0%    55 ms
```

Os números acima são ilustrativos. As colunas `Experiment`, `Strategy` (tipo de busca), `Collection` (estratégia de divisão), `Threshold`, `Count`, `HyDE`, `Score` e `True Rate` têm os nomes do projeto de referência; `Anchored` e `Time` são acréscimos.

Experimentos não executados ou incompletos aparecem depois dos demais, sem métricas, com o motivo em uma linha abaixo da tabela.

Abaixo da tabela aparece a nota: o Score mede semelhança com a pergunta, não acerto, e só é comparável entre experimentos com o mesmo modelo de embedding e a mesma opção de HyDE.

## `python -m evaluation retrieval [--experiment NOME]`

Como hoje (métricas de busca por fonte e lista das perguntas em que a evidência não chegou ao modelo), para um experimento. Sem a opção, usa o experimento do assistente. As opções `--vector-k`, `--bm25-k` e `--final-k` deixam de existir.

## `python -m evaluation run [...] [--experiment NOME]`

A avaliação da resposta final. Mudanças:

- nova opção `--experiment NOME`: roda com outro experimento sem editar o YAML;
- as opções `--vector-k`, `--bm25-k` e `--final-k` deixam de existir (o experimento define esses valores);
- o placar e o registro da execução mostram o experimento e a estratégia usados;
- índice ausente ou desatualizado: não roda, informa o comando e sai com `1`.

As demais opções (`--smoke`, `--holdout`, `--repeat`, `--no-judge`, `--label`) não mudam.

## `python -m evaluation kb-check [--strategy NOME]`

Como hoje, para o índice de uma estratégia. Sem a opção, usa a estratégia do experimento do assistente. Informa também se o índice está desatualizado.

## `python -m evaluation validate`

Passa a validar também os dois arquivos de configuração, além do gabarito, e lista as estratégias e os experimentos declarados, com o estado do índice de cada estratégia (atual, desatualizado ou ausente).
