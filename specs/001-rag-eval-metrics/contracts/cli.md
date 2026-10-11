# Contract: Linha de comando da avaliação

Todos os comandos rodam da raiz do projeto, com o ambiente virtual ativo: `python -m evaluation <comando>`.

Convenções:

- Saída legível no terminal (stdout); erros em stderr.
- Código de saída `0` em sucesso, `1` em erro de execução, `2` em uso incorreto ou dado inválido.
- A avaliação é um placar: nota baixa não é erro e não muda o código de saída.
- Mensagens e rótulos do placar em português.

## `run`

Roda a avaliação e grava o resultado.

```text
python -m evaluation run [--smoke | --holdout] [--repeat N] [--no-judge] [--label TEXTO] [--vector-k N] [--bm25-k N]
```

| Opção | Efeito |
|---|---|
| (nenhuma) | Recorte `dev` completo, com juiz |
| `--smoke` | Só os itens marcados como `smoke` |
| `--holdout` | Só a parte reservada |
| `--repeat N` | Roda N vezes e informa a variação por métrica (padrão 1) |
| `--no-judge` | Pula as métricas de juiz |
| `--label TEXTO` | Acrescenta um rótulo ao `run_id` (ex.: `chunk-por-procedimento`) |
| `--vector-k N`, `--bm25-k N` | Experimento: roda com outra quantidade de trechos recuperados, sem alterar o assistente (acrescentado na implementação) |

Comportamento:

1. Valida o gabarito. Se inválido: lista os problemas e sai com `2`, sem consultar o assistente.
2. Confere se o serviço de modelos responde e se os modelos estão instalados. Se não: diz qual falta e sai com `1`.
3. Consulta o assistente item a item, mostrando o progresso.
4. Grava `evaluation/runs/<run_id>/run.json` e `report.md`.
5. Mostra o placar: nota geral, métricas por grupo, contagem por causa, notas por tipo de pergunta e por procedimento, e a lista de itens errados com resposta, esperado e causa.
6. Se existe referência do mesmo recorte, mostra a comparação com ela.

Se a execução é interrompida ou um item falha por erro do serviço: grava em `evaluation/runs/_incomplete/<run_id>/`, lista os itens não avaliados e sai com `1`.

## `compare`

```text
python -m evaluation compare [BASE] [CANDIDATA]
```

- Sem argumentos: referência do recorte `dev` contra a avaliação completa mais recente.
- Um argumento: referência contra a avaliação informada.
- Dois argumentos: as duas avaliações informadas.

Mostra: mudanças de configuração, diferença por métrica (com indicação de quando a diferença é menor que a variação medida), regressões e melhorias por item. Regressões aparecem antes de tudo, mesmo quando a nota geral subiu.

Se os recortes diferem: sai com `2`. Se o gabarito difere: mostra o aviso, compara só os itens em comum e informa quantos ficaram de fora.

## `baseline`

```text
python -m evaluation baseline set [RUN_ID]
python -m evaluation baseline show
```

`set` sem argumento marca a avaliação completa mais recente. Só aceita avaliação `complete`; a referência é guardada por recorte.

## `list`

```text
python -m evaluation list
```

Lista as avaliações completas, da mais recente para a mais antiga: `run_id`, recorte, versão do gabarito, nota geral e marca de referência.

## `kb-check`

```text
python -m evaluation kb-check
```

Verifica a base de conhecimento sem usar modelo de linguagem: trechos duplicados, fatos do gabarito sem trecho ancorado, texto corrompido e divergência entre a base vetorial e o arquivo de trechos. Lista cada problema e o total por tipo. Sai com `0` também quando encontra problemas; `1` só se não conseguir ler a base.

## `calibrate`

```text
python -m evaluation calibrate export [RUN_ID] [--size 20]
python -m evaluation calibrate score
```

- `export`: gera `evaluation/data/human_labels.json` com uma amostra de respostas da avaliação (a mais recente, por padrão), distribuída por tipo de pergunta, com os campos de avaliação humana vazios e sem as notas do juiz.
- `score`: lê o arquivo preenchido e mostra a concordância entre a pessoa e o juiz por critério. Critérios abaixo de 80% são marcados como não confiáveis. O resultado é mostrado nos placares seguintes.

## `validate`

```text
python -m evaluation validate
```

Valida o gabarito e mostra a cobertura (itens por tipo, por procedimento e por recorte). Sai com `2` se inválido.
