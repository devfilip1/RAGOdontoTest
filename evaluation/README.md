# Avaliação do assistente OdontoTest

Mede a qualidade das respostas do assistente com um conjunto fixo de perguntas (o gabarito) e guarda o resultado de cada execução, para comparar antes e depois de uma mudança.

Todos os comandos rodam da raiz do projeto, com o ambiente virtual ativo e o Ollama em execução.

## Ciclo de uso

```powershell
# 1. mude algo no assistente (config/*.yaml, prompt, modelo)
python -m assistant.ingest                         # só se mudou uma estratégia ou o PDF
python -m evaluation experiments                   # se a mudança é de busca: compare as configurações
# 2. rode a avaliação da resposta
python -m evaluation run --label o-que-mudei
# 3. o placar já mostra a comparação com a referência; para rever depois:
python -m evaluation compare
# 4. se a mudança ficou, ela vira a nova referência
python -m evaluation baseline set
```

Durante os ajustes, use `--smoke` (10 perguntas) e `--no-judge` para ter resposta em menos de um minuto.

## Comandos

| Comando | O que faz |
|---|---|
| `run` | Roda o recorte `dev` e grava em `evaluation/runs/<id>/` (`run.json` e `report.md`) |
| `run --smoke` | Só as perguntas da avaliação reduzida |
| `run --holdout` | Só a parte reservada (ver abaixo) |
| `run --no-judge` | Sem as métricas de comportamento, bem mais rápido |
| `run --repeat N` | Roda N vezes e mostra a variação de cada métrica |
| `run --experiment NOME` | Roda a avaliação da resposta com outro experimento de `config/experiments.yaml`, sem editar o arquivo |
| `experiments [NOMES] [--verbose]` | Roda os experimentos de busca e mostra a tabela comparativa (ver abaixo) |
| `retrieval [--experiment NOME]` | Detalhe da busca de um experimento: métricas por fonte e as perguntas em que a evidência não chegou ao modelo |
| `compare [BASE] [CANDIDATA]` | Compara duas execuções; sem argumentos, a referência contra a mais recente |
| `baseline set [ID]` / `baseline show` | Marca ou mostra a execução de referência |
| `list` | Lista as execuções gravadas |
| `kb-check [--strategy NOME]` | Verifica o índice de uma estratégia, sem usar modelo |
| `validate` | Valida a configuração e o gabarito; lista as estratégias, o estado de cada índice e os experimentos |
| `calibrate export` / `calibrate score` | Confere o juiz contra a sua avaliação |

## Como ler o placar

**Nota geral** é a fração de perguntas certas. Uma pergunta está certa quando:

- tem resposta no material: todos os fatos esperados aparecem, não aparece nenhum valor estranho e nenhuma regra de atendimento é violada;
- não tem resposta no material: o assistente diz que não tem a informação e não cita preço nem prazo.

**Resposta (determinístico)** e **Busca** são calculadas por comparação de texto e de valores, sem modelo. A mesma resposta sempre recebe a mesma nota.

- "R$ 1.500", "1500 reais" e "mil e quinhentos reais" contam como o mesmo valor; "1 hora" e "60 minutos" também.
- Na busca, um trecho é relevante quando contém a evidência do gabarito. **Evidência ancorada** mede se esse trecho também tem o nome do procedimento. Evidência recuperada e não ancorada é o cenário em que o modelo recebe um preço sem saber de qual procedimento é.
- As três linhas da busca mostram a contribuição da busca vetorial, da lexical e do conjunto que vai para o modelo.

**Comportamento (juiz)** é a opinião de um modelo local sobre tom, objetividade, convite ao agendamento, relevância e fidelidade. Não entra na nota geral. Só confie em um critério depois de conferi-lo com `calibrate`: abaixo de 80% de concordância com você, o placar marca o critério como não confiável.

**Causa dos erros** diz onde mexer:

| Causa | Onde está o problema |
|---|---|
| Falha de busca | O trecho com a resposta não foi recuperado: divisão do material ou busca |
| Falha de resposta | O trecho foi recuperado e a resposta saiu errada: prompt, modelo ou contexto confuso |
| Informação inventada | A resposta traz valor que não está nos trechos, ou responde o que o material não diz |
| Recusa indevida | O trecho foi recuperado e o assistente disse que não tem a informação |
| Violação de regra de atendimento | Fatos certos, mas citou "contexto", "documento" ou "base de dados", respondeu fora do português ou longo demais |

## Bancada de experimentos de busca

`python -m evaluation experiments` roda cada experimento de `config/experiments.yaml` sobre as 38 perguntas com resposta do conjunto de trabalho. Ele mede **só a busca**, sem gerar respostas, por isso leva segundos.

```text
|        Experiment        | Strategy |     Collection    | Threshold | Count |  HyDE | Score | True Rate | Anchored |  Time |
|      section_hybrid      |  hybrid  |      section      |    0.00   |   4   | False |  0.67 |   37/38   |  100.0%  | 39 ms |
|       page_hybrid        |  hybrid  |        page       |    0.00   |   4   | False |  0.64 |   37/38   |  81.8%   | 36 ms |
| recursive_500_200_hybrid |  hybrid  | recursive_500_200 |    0.00   |   4   | False |  0.67 |   31/38   |  81.8%   | 35 ms |
```

| Coluna | O que é |
|---|---|
| `Strategy` | Tipo de busca: `hybrid`, `vector` ou `bm25` |
| `Collection` | Estratégia de divisão usada |
| `Threshold`, `Count`, `HyDE` | Parâmetros do experimento |
| `True Rate` | Perguntas em que **todas** as evidências do gabarito vieram entre os trechos. É a coluna que mede acerto |
| `Score` | Média da similaridade (cosseno, de 0 a 1) entre a pergunta e os trechos devolvidos |
| `Anchored` | Perguntas em que o trecho com a evidência também traz o nome do procedimento |
| `Time` | Tempo médio da busca por pergunta, incluindo a geração do HyDE quando ligado |

Cuidados ao ler:

- **O Score não mede acerto.** Ele diz o quanto os trechos se parecem com a pergunta. A divisão por caracteres tem o mesmo Score da divisão por seção (0,67) e erra 6 perguntas a mais.
- **O Score só é comparável** entre experimentos com o mesmo modelo de embedding e a mesma opção de HyDE. Com HyDE a similaridade é medida contra a resposta hipotética e sai mais alta (0,78 contra 0,67 na medição de 10/10/2026), sem recuperar nenhuma evidência a mais.
- **A ordem é por True Rate**, depois por Score. No empate, experimentos com HyDE ficam depois dos sem.
- **A bancada não vê a resposta.** Duas configurações com o mesmo True Rate podem dar respostas de qualidade diferente. Antes de adotar um experimento, rode `python -m evaluation run --experiment NOME` e compare com a referência.

Cada execução grava dois arquivos em `runs/experiments/`: `<data-hora>-summary.csv`, com a tabela, e `<data-hora>-questions.csv`, com uma linha por experimento e pergunta. O segundo mostra quais perguntas cada experimento erra. Os arquivos usam `;` como separador e abrem direto no Excel.

Um experimento cujo índice está ausente ou desatualizado aparece como não executado, com o comando que resolve, e os outros rodam normalmente. A parte reservada do gabarito nunca entra na bancada.

## Limites do que é medido

- A conferência é por valor, não por frase. Se a resposta atribui o tempo da limpeza ao clareamento e os dois valores são fatos da pergunta, a nota determinística não percebe. O critério "fidelidade" do juiz existe para esses casos.
- A recusa é reconhecida por uma lista de frases em `answer_metrics.py` (`ABSTENTION_PATTERNS`). A frase que o assistente usa está em `assistant/pipeline.py` (`NO_ANSWER`); se ela mudar, atualize a lista.
- A avaliação roda com `temperature=0` e `seed=42`. O chat (`python -m assistant.chat`) também usa temperatura 0, sem `seed` fixo.
- Só perguntas de uma mensagem. Conversas com várias trocas não são avaliadas.

## Gabarito

Fica em `data/gabarito.json`. O formato está em `schemas/gabarito.schema.json`.

Para acrescentar uma pergunta:

1. Copie um item parecido e troque `id` (único, nunca reaproveitado), `question`, `category` e `procedure`.
2. Em `expected_facts`, liste o que a resposta precisa conter. Use `money` e `duration` para valores e `text` para o resto. Em `text`, basta uma das `alternatives` aparecer.
3. Em `evidence`, cole a linha do PDF onde está a resposta. Ela precisa aparecer uma única vez no material; se aparecer mais, cole um trecho maior.
4. Pergunta sem resposta no material: `"answerable": false`, sem `expected_facts` nem `evidence`.
5. Suba `version` e rode `python -m evaluation validate`.

A resposta pode citar, sem contar como erro, outros fatos do mesmo procedimento que estejam no gabarito e os diferenciais da clínica. Para liberar um valor que não é fato de nenhuma pergunta, use `allowed_facts`.

Depois de mudar o gabarito, rode a avaliação de novo e marque a nova referência: execuções com gabaritos diferentes não são diretamente comparáveis, e `compare` avisa quando isso acontece.

### Parte reservada

Cerca de um quarto das perguntas tem `"split": "holdout"` e não entra em `run`. A regra é não olhar para elas enquanto ajusta o assistente. Depois de uma rodada de melhorias, `python -m evaluation run --holdout` mostra se o ganho vale para perguntas que não guiaram os ajustes. Se a nota do `dev` sobe e a da parte reservada não, o assistente foi ajustado para o gabarito e não para o problema.

## Conferir o juiz

```powershell
python -m evaluation calibrate export      # gera data/human_labels.json com 20 respostas
# preencha cada "human" com true ou false, seguindo os critérios descritos no arquivo
python -m evaluation calibrate score
```

Para trocar o modelo do juiz, defina `OLLAMA_JUDGE_MODEL` (o padrão é o mesmo modelo do chat). A conferência vale para um modelo de juiz; ao trocar, confira de novo.

## Testes

```powershell
pytest                    # testes de unidade, sem Ollama
pytest -m integration     # usa o Ollama e o índice de verdade
```
