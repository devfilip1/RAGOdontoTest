# Quickstart: Bancada de Experimentos de Busca

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Roteiro para confirmar, de ponta a ponta, que a feature funciona. Os comandos estão em [contracts/cli.md](./contracts/cli.md), os atalhos em [contracts/shortcuts.md](./contracts/shortcuts.md) e os arquivos em [data-model.md](./data-model.md).

## Pré-requisitos

- Dependências instaladas: `.\run.ps1 install`
- Ollama em execução, com `llama3` e `nomic-embed-text`
- Referência da avaliação da resposta já marcada (`python -m evaluation baseline show`)

## 1. Testes de unidade

```powershell
.\run.ps1 test
```

**Esperado**: todos passam, incluindo os que existiam antes da feature (SC-010).

## 2. Configuração válida

```powershell
.\run.ps1 validate
```

**Esperado**: configuração e gabarito válidos; lista as 3 estratégias e os 3 experimentos, com o estado do índice de cada estratégia.

## 3. Índices que convivem

```powershell
.\run.ps1 ingest
```

**Esperado**: três diretórios em `data/index/`: `section` (11 trechos), `recursive_500_200` e `page` (3 trechos), cada um com `chroma/`, `chunks.json` e `manifest.json`.

Depois, recriar só um e conferir que os outros não mudaram (SC-007):

```powershell
python -m assistant.ingest page
```

**Esperado**: a data de `manifest.json` muda só em `data/index/page/`.

## 4. O assistente continua igual

```powershell
.\run.ps1 eval --label bancada
```

**Esperado**: nota geral de 97,8% e a comparação com a referência sem nenhuma regressão e sem nenhuma melhoria (SC-001). O placar mostra o experimento `section_hybrid` e a estratégia `section`.

```powershell
.\run.ps1 chat
```

**Esperado**: o chat responde como antes.

## 5. A tabela comparativa

```powershell
.\run.ps1 experiments
```

**Esperado**:

- barra de progresso por experimento;
- tabela "COMPARISON OF RETRIEVAL STRATEGIES" com 3 linhas e as 10 colunas, ordenada por True Rate e depois por Score;
- a nota sobre o Score abaixo da tabela;
- os caminhos de dois arquivos novos em `evaluation/runs/experiments/`;
- menos de 1 minuto no total (SC-002).

Registrar qual estratégia ficou na frente. A expectativa é `section` com True Rate maior ou igual ao das outras; se não for, anotar o resultado aqui como achado (SC-003).

```powershell
.\run.ps1 experiments --verbose
```

**Esperado**: além da tabela, uma linha por pergunta no formato `pergunta;true;0.71`.

## 6. Um quarto experimento só pelo arquivo

Acrescentar a `config/experiments.yaml`:

```yaml
  - exp_name: section_vector
    collection: section
    search_type: vector
    match_count: 4
```

```powershell
.\run.ps1 experiments
```

**Esperado**: 4 linhas na tabela, sem nenhuma outra alteração no projeto (SC-004). `Threshold` aparece como 0.00 e `HyDE` como False, os padrões.

## 7. Threshold e HyDE

Acrescentar dois experimentos: um igual a `section_hybrid` com `match_threshold: 0.6`, outro com `use_hyde: true`.

```powershell
.\run.ps1 experiments
```

**Esperado**:

- o experimento com threshold tem `Count` igual mas devolve menos trechos em parte das perguntas (visível em `retrieved_count` no CSV de perguntas);
- o experimento com HyDE tem `Time` maior, na casa de 1 segundo a mais por pergunta (SC-008).

Remover os experimentos de teste ao final, ou mantê-los se forem úteis.

## 8. Trocar a configuração do assistente por um nome

Em `config/experiments.yaml`, trocar `assistant: section_hybrid` por `assistant: page_hybrid`.

```powershell
.\run.ps1 retrieval
```

**Esperado**: o resultado é o do experimento `page_hybrid` (SC-005). Voltar para `section_hybrid` ao final.

## 9. Configuração inválida

Um de cada vez, desfazendo depois:

| Alteração | Mensagem esperada |
|---|---|
| Dois experimentos com o mesmo `exp_name` | nome repetido, com o nome |
| `collection: nao_existe` | estratégia inexistente, com a lista das válidas |
| `type: semantic` em uma estratégia | tipo desconhecido, com os tipos válidos |
| `match_count: 0` | valor fora da faixa |
| `assistant: nao_existe` | experimento do assistente inexistente |
| `chunk_sise: 500` em uma estratégia `split` | parâmetro desconhecido |

```powershell
.\run.ps1 experiments
```

**Esperado**: em todos os casos, nada é executado, a mensagem aponta o item e o comando sai com código 2 (SC-006).

## 10. Índice ausente e desatualizado

Apagar `data/index/page/` e rodar `.\run.ps1 experiments`.

**Esperado**: `page_hybrid` aparece como não executado, com o comando `python -m assistant.ingest page`; os outros dois rodam normalmente.

Recriar o índice, mudar `chunk_size` de `recursive_500_200` para 400 e rodar de novo.

**Esperado**: `recursive_500_200_hybrid` aparece como não executado, com o motivo "índice desatualizado". Desfazer a alteração ao final.

## 11. Atalhos nas duas formas

```powershell
.\run.ps1 help
.\run.ps1 nao-existe
```

**Esperado**: a lista com 15 atalhos e descrições; no segundo, a mensagem de atalho inexistente e a lista.

Com o `make` instalado (`winget install ezwinports.make`):

```powershell
make help
make validate
make experiments ARGS="--verbose"
```

**Esperado**: os mesmos resultados dos atalhos do `run.ps1` (SC-009). Sem o `make`, a paridade dos nomes é conferida pelo teste de unidade.

## Resultado da validação (2026-10-10)

Passo 5, tabela dos três experimentos iniciais (8,6 s no total):

```text
|        Experiment        | Strategy |     Collection    | Threshold | Count |  HyDE | Score | True Rate | Anchored |  Time |
|      section_hybrid      |  hybrid  |      section      |    0.00   |   4   | False |  0.67 |   37/38   |  100.0%  | 40 ms |
|       page_hybrid        |  hybrid  |        page       |    0.00   |   4   | False |  0.64 |   37/38   |  81.8%   | 36 ms |
| recursive_500_200_hybrid |  hybrid  | recursive_500_200 |    0.00   |   4   | False |  0.67 |   31/38   |  81.8%   | 36 ms |
```

A expectativa de SC-003 se confirmou: `section` tem True Rate igual ao de `page` e maior que o de `recursive_500_200`, e é a única com 100% de evidência ancorada.

Passo 7, com os experimentos de teste:

```text
|   section_hybrid_hyde    |  hybrid  |      section      |    0.00   |   4   |  True |  0.78 |   37/38   |  100.0%  | 1758 ms |
|       section_bm25       |   bm25   |      section      |    0.00   |   4   | False |  0.65 |   37/38   |  100.0%  |  33 ms  |
|      section_vector      |  vector  |      section      |    0.00   |   4   | False |  0.66 |   35/38   |  97.0%   |  35 ms  |
|    section_hybrid_t60    |  hybrid  |      section      |    0.60   |   4   | False |  0.66 |   35/38   |  97.0%   |  34 ms  |
```

Com threshold de 0,6, uma pergunta ficou sem nenhum trecho. O HyDE não recuperou nenhuma evidência a mais.

Passos 9 e 10: as seis configurações inválidas foram recusadas com código 2 e mensagem apontando o item; com o índice de `page` ausente e o de `recursive_500_200` desatualizado, os dois apareceram como não executados e `section_hybrid` rodou normalmente.

Passo 11: os atalhos do `run.ps1` foram conferidos. O `Makefile` não foi executado, porque o `make` não está instalado nesta máquina; só a paridade com o `run.ps1` foi conferida por teste.
