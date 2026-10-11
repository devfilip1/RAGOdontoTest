---

description: "Lista de tarefas para a bancada de experimentos de busca"
---

# Tasks: Bancada de Experimentos de Busca

**Input**: Design documents from `/specs/002-retrieval-experiments/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluídos. O plano mantém o padrão do projeto: testes de unidade sem Ollama para tudo que é determinístico (research D13). Em cada história os testes são escritos antes da implementação e devem falhar primeiro.

**Organization**: Tarefas agrupadas por história de usuário. As fases seguem a ordem de dependência, que difere da ordem de prioridade da spec: a tabela (US1) precisa dos índices por estratégia (US2) e do `RagConfig` por experimento (US3), então vem depois deles.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história a que a tarefa pertence (US1 a US5, como na spec)
- **[MANUAL]** na descrição: depende de uma decisão do responsável

## Path Conventions

Pacotes `assistant/` e `evaluation/`, testes em `tests/`, configuração nova em `config/`. Os comandos rodam da raiz. Nomes de campos e regras seguem [data-model.md](./data-model.md); comandos seguem [contracts/cli.md](./contracts/cli.md); decisões D1 a D13 estão em [research.md](./research.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependência declarada e arquivos de configuração no lugar

- [X] T001 Acrescentar `PyYAML==6.0.3` a `requirements.txt` (já está instalado; conferir com `pip show pyyaml`)
- [X] T002 [P] Criar `config/strategies.yaml` e `config/experiments.yaml` com o conteúdo de `specs/002-retrieval-experiments/contracts/strategies.example.yaml` e `experiments.example.yaml`, e copiar `strategies.schema.json` e `experiments.schema.json` do mesmo diretório para `config/schemas/`
- [X] T003 [P] Criar `evaluation/runs/experiments/.gitkeep`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Carga e validação dos dois arquivos de configuração (FR-001, FR-008 a FR-013). Tudo o mais depende disso.

**⚠️ CRITICAL**: Nenhuma história começa antes desta fase terminar.

- [X] T004 Criar `tests/unit/test_settings.py`, passando textos YAML para as funções de carga (sem ler `config/`), com um caso por regra de `data-model.md`: configuração válida devolve 3 estratégias e 3 experimentos; padrões `match_threshold` 0.0 e `use_hyde` false quando omitidos; padrões `max_chars` 1200 e `overlap` 100 no tipo `section`; e os erros, cada um exigindo o nome do item na mensagem: `name` repetido, `exp_name` repetido, `type` desconhecido, parâmetro desconhecido para o tipo (ex.: `chunk_sise`), `split` sem `chunk_size` ou `chunk_overlap`, `page` com parâmetros, `chunk_overlap` não menor que `chunk_size`, `overlap` não menor que `max_chars`, `collection` que não existe em estratégias (mensagem lista as válidas), `match_count` fora de "De 1 a 20", `match_threshold` fora de "De 0 a 1", `search_type` desconhecido, `assistant` que não existe em `experiments`, `use_hyde: true` com `search_type: bm25`, e YAML malformado. Conferir também que todos os problemas são listados juntos, não só o primeiro
- [X] T005 Criar `assistant/settings.py`: dataclasses congeladas `Strategy(name, type, parameters)` (com os padrões do tipo aplicados e método `definition_hash()`) e `Experiment(exp_name, collection, search_type, match_count, match_threshold=0.0, use_hyde=False)`; exceção `SettingsError(problems)`; `parse_settings(strategies_text, experiments_text)` que valida contra `config/schemas/*.schema.json` com `jsonschema`, aplica as conferências cruzadas de `data-model.md` e levanta `SettingsError` com todos os problemas; `load_settings()` com cache, que lê `config/strategies.yaml` e `config/experiments.yaml`; e os acessos `strategies()`, `experiments()`, `get_strategy(nome)`, `get_experiment(nome)` e `assistant_experiment()`. Mensagens em português, dizendo o que corrigir. Fazer T004 passar
- [X] T006 Em `assistant/config.py`, acrescentar `CONFIG_DIR = ROOT / "config"`, `STRATEGIES_PATH`, `EXPERIMENTS_PATH` e `SCHEMAS_DIR`, usados por `assistant/settings.py`. Não remover nada ainda: as constantes antigas saem em T017

**Checkpoint**: `python -c "from assistant.settings import load_settings; load_settings()"` roda sem erro.

---

## Phase 3: User Story 2 - Declarar estratégias de divisão que convivem (Priority: P1)

**Goal**: Um índice por estratégia em `data/index/<nome>/`, criado a partir do YAML, com manifesto.

**Independent Test**: `python -m assistant.ingest` cria `section`, `recursive_500_200` e `page`; recriar um não altera os outros; `kb-check --strategy` lê o índice certo.

### Tests for User Story 2 ⚠️

- [X] T007 [P] [US2] Criar `tests/unit/test_index.py` com `tmp_path`: `index_dir(nome)` devolve `<raiz>/<nome>`; `write_manifest` grava os campos `strategy`, `definition_hash`, `source_hash`, `embedding_model`, `chunk_count` e `created_at`; `index_state` devolve `missing` sem diretório ou sem manifesto, `current` quando os três conferem, e `stale` com o motivo quando muda a definição da estratégia, o hash do material ou o modelo de embedding; a mensagem de `missing` e de `stale` traz o comando `python -m assistant.ingest <estratégia>`
- [X] T008 [P] [US2] Atualizar `tests/unit/test_ingest.py`: manter os testes de títulos e seções; trocar o uso de `CHUNK_SIZE` por parâmetros da estratégia; acrescentar `clean_text` (marcador `\x7f` vira `- item`, `TEXT_FIXES` aplicado), o tipo `split` (nenhum trecho maior que `chunk_size`, texto limpo, `metadata.strategy` preenchido), o tipo `page` (um trecho por página, com `metadata.page` a partir de 1), o tipo `section` com `max_chars` pequeno (subdivide e repete o título) e um tipo não registrado (erro)

### Implementation for User Story 2

- [X] T009 [US2] Criar `assistant/index.py`: `INDEX_DIR` (de `assistant.config`), `index_dir(nome)`, `chroma_dir(nome)`, `chunks_path(nome)`, `manifest_path(nome)`; `source_hash()` (SHA-256 de `SOURCE_PDF`); `write_manifest(strategy, chunk_count)`; `read_manifest(nome)`; `index_state(strategy) -> (estado, motivo)` com os estados `current`, `stale` e `missing` da tabela "Estados do índice" de `data-model.md`; e `require_index(strategy)`, que levanta `IndexError_` (exceção própria) com o motivo e o comando quando o estado não é `current`. As funções aceitam um diretório base opcional, para os testes. Fazer T007 passar
- [X] T010 [US2] Reescrever a divisão em `assistant/ingest.py`: `load_pages()` devolve o texto de cada página; `clean_text(text)` converte os marcadores de lista em `- item` e aplica `TEXT_FIXES`; funções `split_by_section(pages, parameters)` (o código atual de `split_sections`, com `max_chars` e `overlap` no lugar de `CHUNK_SIZE` e `CHUNK_OVERLAP`, sobre as páginas emendadas), `split_by_characters(pages, parameters)` (`RecursiveCharacterTextSplitter` sobre o texto inteiro) e `split_by_page(pages, parameters)`; registro `STRATEGY_TYPES = {"section": ..., "split": ..., "page": ...}`; `build_chunks(strategy, pages)` que devolve os `Document` com `metadata` contendo `source`, `strategy` e `section` ou `page`. Fazer T008 passar
- [X] T011 [US2] Em `assistant/ingest.py`, trocar `create_db()` por `build_index(strategy)`, que grava `chunks.json`, recria a coleção em `chroma_dir(nome)` e escreve o manifesto, e por `main(argv)`: sem argumentos cria os índices de todas as estratégias; com nomes, só os indicados; nome inexistente sai com código 2 listando os válidos; `SettingsError` sai com código 2 listando os problemas. Para cada estratégia imprime o nome e a quantidade de trechos. Manter `EMBEDDINGS` e `PrefixedEmbeddings` como estão
- [X] T012 [US2] Em `evaluation/kb_checks.py`, `load_kb(strategy_name)` passa a ler `chroma_dir` e `chunks_path` da estratégia; em `evaluation/cli.py`, `kb-check` ganha `--strategy NOME` (padrão: a estratégia do experimento do assistente) e informa o estado do índice antes dos resultados; em `evaluation/report.py`, `print_kb_report` mostra o nome da estratégia e o aviso de índice desatualizado
- [X] T013 [US2] Em `evaluation/cli.py`, `validate` passa a validar também a configuração (código 2 e lista de problemas em `SettingsError`) e, em `evaluation/report.py`, a listar as estratégias com o estado do índice de cada uma e os experimentos, marcando o do assistente
- [X] T014 [US2] Rodar `pytest tests/unit`, depois `python -m assistant.ingest` e conferir os três diretórios em `data/index/`; rodar `python -m assistant.ingest page` e conferir que só o manifesto de `page` muda (SC-007); rodar `python -m evaluation kb-check --strategy` para as três e registrar o resultado de cada uma. Não apagar ainda `data/index/chroma` nem `data/index/chunks.json`: o assistente ainda os usa até T017

**Checkpoint**: Os três índices existem e convivem; o assistente continua funcionando com o índice antigo.

---

## Phase 4: User Story 3 - Uma única fonte de verdade para a configuração do assistente (Priority: P2)

**Goal**: O chat e a avaliação da resposta leem a estratégia e os parâmetros de busca do experimento indicado em `assistant:`.

**Independent Test**: A avaliação da resposta dá 97,8% sem nenhuma pergunta mudando de resultado em relação à referência; trocar `assistant:` muda o índice e os parâmetros usados.

### Tests for User Story 3 ⚠️

- [X] T015 [P] [US3] Atualizar `tests/unit/test_pipeline.py`: `RagConfig.from_experiment` copia `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde`; as propriedades calculadas seguem research D5 (`hybrid` com `match_count` 4 dá `vector_k` 2, `bm25_k` 2, `final_k` 4; com 5 dá 3, 3 e 5; `vector` com 4 dá 4, 0 e 4; `bm25` com 4 dá 0, 4 e 4); adaptar os testes de fusão existentes para construir a configuração por `match_count`; o índice falso passa a ser por estratégia
- [X] T016 [P] [US3] Acrescentar a `tests/unit/test_history.py` e a `tests/unit/conftest.py`: a configuração gravada de uma execução inclui `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde`; `chunk_size` e `chunk_overlap` podem ser null; uma execução gravada antes da feature (sem os campos novos) continua válida no esquema e comparável

### Implementation for User Story 3

- [X] T017 [US3] Em `assistant/pipeline.py`: `RagConfig` troca `vector_k`, `bm25_k` e `final_k` por `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde`, com `vector_k`, `bm25_k` e `final_k` como propriedades (research D5); `RagConfig()` sem argumentos usa `assistant_experiment()`; `RagConfig.from_experiment(nome_ou_objeto, **overrides)`; os caches `_db` e `_bm25` passam a receber o nome da estratégia e leem de `assistant/index.py`. Em `assistant/config.py`, remover `CHUNK_SIZE`, `CHUNK_OVERLAP`, `VECTOR_K`, `BM25_K`, `FINAL_K`, `PATH_DB` e `CHUNKS_PATH`. A busca continua só híbrida nesta tarefa; `vector` e `bm25` entram em T033. Fazer T015 passar
- [X] T018 [US3] Em `assistant/chat.py`, antes do laço, chamar `require_index` para a estratégia do experimento do assistente; com índice ausente ou desatualizado, ou com `SettingsError`, imprimir o motivo e o comando e sair com código 1 (ou 2 para configuração inválida), sem abrir o chat
- [X] T019 [US3] Em `evaluation/history.py`, `snapshot_config` grava os campos do experimento, lê os trechos de `chunks_path(strategy)` e preenche `chunk_size` e `chunk_overlap` com `chunk_size`/`chunk_overlap` ou `max_chars`/`overlap` da estratégia, ou null; em `evaluation/schemas/run.schema.json` e em `specs/001-rag-eval-metrics/contracts/run.schema.json`, acrescentar os campos novos como opcionais e permitir null em `chunk_size` e `chunk_overlap`. Fazer T016 passar
- [X] T020 [US3] Em `evaluation/cli.py`: `run` e `retrieval` perdem `--vector-k`, `--bm25-k` e `--final-k` e ganham `--experiment NOME` (padrão: o experimento do assistente; nome inexistente sai com código 2 listando os válidos); antes de rodar, `require_index` (código 1 com o motivo e o comando). Em `evaluation/report.py`, a linha "Assistente" do placar mostra o experimento, a estratégia, o tipo de busca e `match_count`. Ajustar `evaluation/retrieval_only.py` para receber o `RagConfig` do experimento
- [X] T021 [US3] Atualizar `tests/integration/test_assistant.py` para ler o índice pela estratégia do experimento do assistente (`chunks_path`, `build_chunks`) e acrescentar um teste de que `python -m assistant.chat` recusa iniciar quando a estratégia do assistente aponta para um índice ausente (com o diretório de índice redirecionado para `tmp_path`). Apagar `data/index/chroma` e `data/index/chunks.json`, que não são mais lidos
- [X] T022 [US3] Rodar `pytest tests/unit` e `pytest -m integration`; rodar `python -m evaluation run --no-judge --label bancada-us3` e conferir na comparação com a referência: nota geral de 97,8%, nenhuma regressão e nenhuma melhoria (SC-001). Se alguma pergunta mudar de resultado, conferir se os trechos enviados ao modelo são os mesmos da referência antes de seguir; diferença só no texto da resposta com os mesmos trechos é ruído do modelo e deve ser registrada, não corrigida

**Checkpoint**: A configuração de busca do assistente vem só de `config/experiments.yaml`, e o assistente responde como antes.

---

## Phase 5: User Story 1 - Comparar experimentos de busca em uma tabela (Priority: P1) 🎯 MVP

**Goal**: `python -m evaluation experiments` roda os experimentos, mostra a tabela comparativa e grava os dois CSV.

**Independent Test**: Com os três experimentos iniciais, a tabela sai com 3 linhas e as 10 colunas, ordenada por True Rate e Score, em menos de 1 minuto, e dois arquivos novos aparecem em `evaluation/runs/experiments/`.

### Tests for User Story 1 ⚠️

- [X] T023 [P] [US1] Acrescentar a `tests/unit/test_pipeline.py`: cada `RetrievedChunk` de `vector`, `bm25` e `fused` traz `similarity` igual ao cosseno entre o vetor da busca e o embedding do trecho (com embeddings falsos de valores conhecidos), inclusive nos trechos achados só pela busca por palavras; a busca vetorial usa o mesmo vetor, calculado uma única vez por pergunta
- [X] T024 [P] [US1] Criar `tests/unit/test_experiments.py` com uma função de busca falsa e o gabarito de `conftest.py`: `hit` exige todas as evidências (item com duas evidências e só uma recuperada dá `false`); `score` da pergunta é a média da `similarity` dos trechos devolvidos e 0 quando nenhum; perguntas sem resposta e itens de `holdout` não são avaliados; o resultado do experimento traz `hits`, `total`, `score`, `anchored_rate` e `avg_latency_ms`; a chamada de aquecimento não entra no tempo; ordenação por True Rate decrescente, depois Score decrescente, depois nome; experimento com índice ausente ou desatualizado vira `not_run` com o motivo e o comando, sem impedir os demais; exceção do serviço no meio vira `incomplete` e mantém só as perguntas concluídas; `not_run` e `incomplete` ficam depois dos `ok`; linha de detalhe no formato `pergunta;true;0.71`; `summary.csv` e `questions.csv` com as colunas de `contracts/results-csv.md`, separador `;`, UTF-8 com BOM, e nome `<AAAAMMDD-HHMMSS>-summary.csv`; duas execuções não se sobrescrevem

### Implementation for User Story 1

- [X] T025 [US1] Em `assistant/pipeline.py` (research D6): cache por estratégia dos embeddings do índice (`_collection.get(include=["embeddings", "documents"])`), normalizados; `retrieve()` calcula o vetor da busca uma vez com `EMBEDDINGS.embed_query`, faz a busca vetorial com esse vetor (`similarity_search_by_vector_with_relevance_scores`) e preenche `similarity` em todos os trechos devolvidos; `RetrievedChunk` ganha `similarity: float | None = None`. Fazer T023 passar
- [X] T026 [US1] Acrescentar a `tests/integration/test_assistant.py` um teste de que, para 5 perguntas, a ordem dos trechos da busca vetorial por vetor é a mesma da busca por texto (`similarity_search_with_relevance_scores`), e de que a `similarity` do melhor trecho fica entre 0 e 1
- [X] T027 [US1] Criar `evaluation/experiments.py` (research D7 e D10): `QuestionResult` e `ExperimentResult` com os campos de `data-model.md`; `run_experiment(experiment, items, gabarito, retrieve_fn=None, on_progress=None, on_question=None)` com os estados `ok`, `not_run` e `incomplete`; `run_all(experiments, ...)`; `sort_results(results)`; `format_question_line(result)`; `write_csv(results, directory, started_at)` que grava os dois arquivos e devolve os caminhos. Trazer para este módulo o que `evaluation/retrieval_only.py` faz (métricas por fonte e lista de perguntas em que a evidência não chegou) e apagar `evaluation/retrieval_only.py`. Fazer T024 passar
- [X] T028 [US1] Em `evaluation/report.py`, `print_experiments(results, console)`: título `COMPARISON OF RETRIEVAL STRATEGIES`, a linha do critério de ordenação, as colunas `Experiment`, `Strategy`, `Collection`, `Threshold`, `Count`, `HyDE`, `Score`, `True Rate`, `Anchored` e `Time`, com `Threshold` e `Score` em duas casas, `True Rate` como `hits/total`, `Anchored` em porcentagem e `Time` em ms; os experimentos `not_run` e `incomplete` depois dos demais, sem métricas, com o motivo em uma linha abaixo da tabela; e a nota sobre o Score de `contracts/cli.md`
- [X] T029 [US1] Em `evaluation/cli.py`, comando `experiments [NOMES...] [--verbose]` seguindo os passos 1 a 6 de `contracts/cli.md`: valida a configuração e o gabarito (código 2); confere o serviço de modelos (código 1); barra de progresso `Retrieving and evaluating` por experimento; com `--verbose`, uma linha por pergunta; tabela; grava os CSV em `evaluation/runs/experiments/` e informa os caminhos; código 0 se ao menos um experimento rodou, 1 se nenhum. Nome de experimento inexistente sai com código 2 listando os válidos. O comando `retrieval` passa a usar `evaluation/experiments.py`
- [X] T030 [US1] Rodar `pytest tests/unit` e `pytest -m integration`; rodar `python -m evaluation experiments`, medir o tempo total (SC-002: menos de 1 minuto) e conferir a tabela e os dois CSV; rodar com `--verbose`. Registrar em `specs/002-retrieval-experiments/quickstart.md`, no passo 5, a tabela obtida e qual estratégia ficou na frente; se `section` não tiver True Rate maior ou igual ao das outras, registrar como achado, sem ajustar nada (SC-003)
- [X] T031 [US1] Rodar `python -m evaluation run --no-judge --label bancada-us1` e conferir de novo SC-001 (97,8%, sem regressão), porque T025 mudou a forma de fazer a busca vetorial

**Checkpoint**: A tabela comparativa funciona com os três experimentos iniciais.

---

## Phase 6: User Story 4 - Testar threshold e HyDE antes de adotar (Priority: P3)

**Goal**: Tipos de busca `vector` e `bm25`, threshold e HyDE como opções reais, desligadas por padrão.

**Independent Test**: Um experimento com threshold devolve menos trechos em parte das perguntas; um com HyDE aparece com tempo médio maior que o mesmo experimento sem ele.

### Tests for User Story 4 ⚠️

- [X] T032 [P] [US4] Acrescentar a `tests/unit/test_pipeline.py`, com índice e modelo falsos: `search_type: vector` não chama a busca por palavras e devolve até `match_count` trechos; `search_type: bm25` não faz busca vetorial, mas os trechos têm `similarity`; `match_threshold` 0 não descarta nada; com threshold, trechos de `similarity` menor que o valor saem de `fused` e os de valor igual ficam; threshold acima de todas as similaridades devolve `fused` vazio; com `use_hyde`, o texto usado no embedding é a resposta hipotética e a busca por palavras recebe a pergunta original; sem `use_hyde`, o modelo de geração não é chamado na busca; `answer()` com `fused` vazio ainda monta o prompt e chama o modelo
- [X] T033 [P] [US4] Acrescentar a `tests/unit/test_experiments.py`: pergunta com `fused` vazio conta como erro, com `score` 0 e `retrieved_count` 0; o tempo medido inclui a geração do HyDE (função de busca falsa com atraso)

### Implementation for User Story 4

- [X] T034 [US4] Em `assistant/pipeline.py`: `retrieve()` respeita `search_type` (pula a busca que não se aplica); aplica `match_threshold` depois da fusão, renumerando `rank`; com `use_hyde`, gera a resposta hipotética com o modelo de chat (temperatura 0, até 80 tokens, prompt em uma constante `HYDE_PROMPT`) e usa o texto dela no embedding da busca (research D8). `build_prompt` trata `fused` vazio enviando o bloco de informações vazio. Fazer T032 e T033 passar
- [X] T035 [US4] Acrescentar temporariamente a `config/experiments.yaml` quatro experimentos sobre `section` com `match_count` 4: `section_vector` (`vector`), `section_bm25` (`bm25`), `section_hybrid_t60` (`hybrid`, `match_threshold: 0.6`) e `section_hybrid_hyde` (`hybrid`, `use_hyde: true`); rodar `python -m evaluation experiments` e conferir: as colunas `Threshold` e `HyDE` mostram os valores; `section_hybrid_hyde` tem `Time` maior que `section_hybrid` (SC-008); no CSV de perguntas, `section_hybrid_t60` tem `retrieved_count` menor em parte das perguntas. Registrar a tabela no passo 7 de `specs/002-retrieval-experiments/quickstart.md`
- [X] T036 [US4] [MANUAL] Decidir com o responsável quais dos quatro experimentos de T035 ficam em `config/experiments.yaml`. Padrão se não houver resposta: manter `section_vector` e `section_bm25`, que mostram a contribuição de cada busca, e remover os de threshold e HyDE, deixando-os como exemplo comentado no arquivo

**Checkpoint**: As opções existem, a tabela mostra o efeito e o custo, e o assistente continua com as duas desligadas.

---

## Phase 7: User Story 5 - Atalhos para os comandos do projeto (Priority: P3)

**Goal**: Os mesmos 15 atalhos em `run.ps1` e em `Makefile`.

**Independent Test**: `.\run.ps1 help` lista os atalhos; cada atalho roda o comando de `contracts/shortcuts.md`.

### Tests for User Story 5 ⚠️

- [X] T037 [P] [US5] Criar `tests/unit/test_shortcuts.py`: lê `Makefile` e `run.ps1` como texto e confere que os dois declaram exatamente os 15 nomes de `contracts/shortcuts.md` (`help`, `install`, `ingest`, `chat`, `test`, `test-integration`, `eval`, `eval-smoke`, `eval-full`, `experiments`, `retrieval`, `kb-check`, `validate`, `compare`, `baseline`), que cada nome aponta para o mesmo comando nos dois arquivos e que cada um tem descrição

### Implementation for User Story 5

- [X] T038 [P] [US5] Criar `run.ps1` na raiz: uma tabela ordenada nome → (comando, descrição); usa `.venv\Scripts\python.exe` a partir da pasta do script; repassa os argumentos extras ao comando; sem atalho ou com `help`, lista os atalhos com as descrições e sai com 0; atalho inexistente informa, lista os válidos e sai com 2; o código de saída é o do comando chamado; se `.venv` não existir, diz como criar
- [X] T039 [P] [US5] Criar `Makefile` na raiz com os mesmos 15 alvos, todos `.PHONY`: variável `PYTHON` apontando para `.venv/Scripts/python.exe` no Windows (`ifeq ($(OS),Windows_NT)`) e `.venv/bin/python` nos demais; `ARGS` repassado ao comando; `help` como alvo padrão, listando os alvos com as descrições a partir de comentários `## ` ao lado de cada alvo
- [X] T040 [US5] Rodar `pytest tests/unit/test_shortcuts.py`; rodar cada atalho do `run.ps1` que não seja demorado (`help`, `validate`, `kb-check`, `test`, `experiments`, `retrieval`, `eval-smoke`, `compare`) e conferir `.\run.ps1 nao-existe` (código 2) e o repasse de argumentos (`.\run.ps1 experiments --verbose`)
- [ ] T041 [US5] [MANUAL] Conferir o `Makefile` com o `make` de verdade: perguntar ao responsável se pode instalar com `winget install ezwinports.make`; se sim, rodar `make help`, `make validate` e `make experiments ARGS="--verbose"`; se não, registrar em `specs/002-retrieval-experiments/quickstart.md` que só a paridade dos nomes foi conferida por teste

**Checkpoint**: Todas as histórias funcionam.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentação e validação de ponta a ponta

- [X] T042 [P] Atualizar `README.md`: a pasta `config/` na estrutura, os dois YAML, `python -m assistant.ingest [estratégia]`, a seção de atalhos com `.\run.ps1` e `make`, e como trocar a configuração do assistente
- [X] T043 [P] Atualizar `evaluation/README.md`: o comando `experiments` e como ler a tabela; a definição de True Rate e de Score, com as ressalvas de que o Score mede semelhança e não acerto e só é comparável com o mesmo modelo de embedding e a mesma opção de HyDE (FR-027); `--experiment` no lugar de `--vector-k`, `--bm25-k` e `--final-k`; `kb-check --strategy`; os CSV; e o ciclo "experimentos para escolher a busca, avaliação para validar a resposta"
- [X] T044 Atualizar `docs/guia-do-projeto.html` (o que mudou em como funciona, comandos, mapa de arquivos, onde mexer) e republicar o artefato pelo mesmo caminho de arquivo
- [X] T045 Percorrer os passos 9 e 10 de `specs/002-retrieval-experiments/quickstart.md` (seis configurações inválidas, índice ausente e índice desatualizado), conferindo as mensagens e os códigos de saída (SC-006), e desfazer cada alteração
- [X] T046 Conferir SC-004 e SC-005: acrescentar um experimento só pelo YAML e vê-lo na tabela; trocar `assistant:` para `page_hybrid`, rodar `python -m evaluation retrieval`, conferir que o resultado é o de `page_hybrid`, e voltar para `section_hybrid`
- [X] T047 Rodar `pytest tests/unit` e `pytest -m integration` (SC-010) e a avaliação final `python -m evaluation run --no-judge --label bancada-final`, conferindo SC-001 contra a referência; registrar os números em uma seção "Notas da implementação" ao fim deste arquivo

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup; bloqueia todas as histórias
- **US2 (Phase 3)**: depende da Phase 2
- **US3 (Phase 4)**: depende da US2 (o pipeline passa a ler os índices por estratégia)
- **US1 (Phase 5)**: depende da US3 (a bancada usa o `RagConfig` por experimento)
- **US4 (Phase 6)**: depende da US1 (o efeito das opções é conferido na tabela)
- **US5 (Phase 7)**: T038 e T039 dependem só dos nomes dos comandos; T040 depende da US1, porque roda o atalho `experiments`
- **Polish (Phase 8)**: depende das histórias desejadas

### User Story Dependencies

```text
Setup ─► Foundational ─► US2 ─► US3 ─► US1 ─► US4
                                        └────► US5 (validação dos atalhos)
```

A ordem difere das prioridades da spec (US1 e US2 são P1, US3 é P2) porque a tabela precisa das duas outras para existir. A US3 foi puxada para antes da US1 para a bancada e o assistente usarem a mesma configuração desde o início, em vez de criar uma segunda forma de configurar a busca só para a bancada.

### Within Each User Story

- Testes antes da implementação, falhando primeiro
- `settings` → `index` → `ingest` → `pipeline` → `evaluation` → `cli`
- As tarefas de execução (T014, T022, T030, T031, T035, T040) vêm por último na história
- T022 e T031 são portões: se a nota mudar em relação à referência por causa da busca, a história não está pronta

### Parallel Opportunities

- Phase 1: T002 e T003 em paralelo com T001
- US2: T007 e T008 em paralelo
- US3: T015 e T016 em paralelo
- US1: T023 e T024 em paralelo
- US4: T032 e T033 em paralelo
- US5: T037, T038 e T039 em paralelo, e podem ser adiantadas para qualquer momento depois da Phase 2
- Phase 8: T042 e T043 em paralelo

`assistant/pipeline.py` é alterado em T017, T025 e T034, e `evaluation/cli.py` em T012, T013, T020 e T029: essas tarefas não rodam em paralelo entre si.

---

## Parallel Example: User Story 1

```text
# Testes da US1, juntos:
Task: "Acrescentar a tests/unit/test_pipeline.py os testes de similarity"
Task: "Criar tests/unit/test_experiments.py"

# US5 pode andar ao mesmo tempo, em arquivos próprios:
Task: "Criar run.ps1"
Task: "Criar Makefile"
```

---

## Implementation Strategy

### MVP First

O MVP é a tabela comparativa (US1), que exige as Phases 1 a 5:

1. Setup e Foundational: configuração carregada e validada
2. US2: os três índices
3. US3: o assistente lendo do YAML, com SC-001 conferido
4. US1: a tabela
5. **PARAR e VALIDAR**: ler a tabela e conferir SC-001, SC-002 e SC-003

### Incremental Delivery

1. Phases 1 a 3 → três índices que convivem (já útil: acaba o risco de sobrescrever)
2. Phase 4 → uma fonte de verdade para o assistente
3. Phase 5 → a tabela (MVP)
4. Phase 6 → threshold e HyDE medidos
5. Phase 7 → atalhos
6. Phase 8 → documentação e roteiro

### Pontos em que o responsável participa

- **T036**: quais experimentos extras ficam no YAML
- **T041**: autorizar ou não a instalação do `make`
- Depois de T030: ler a tabela e decidir se a configuração do assistente muda

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta
- Nenhuma tarefa altera o prompt, os sinônimos, o modelo ou o gabarito
- O experimento do assistente continua `section_hybrid` ao fim de todas as tarefas; mudar é decisão do responsável
- A parte reservada do gabarito (`--holdout`) não é usada em nenhuma tarefa
- Commits só quando o responsável pedir

## Notas da implementação (2026-10-10)

- **Pendente**: T041 (conferir o `Makefile` com o `make` de verdade). O `make` não está instalado e não foi instalado sem autorização. O que foi conferido: a paridade de nomes, comandos e descrições entre `Makefile` e `run.ps1`, por teste de unidade. A receita `help` do Makefile nunca foi executada.
- **T036, padrão aplicado**: sem resposta do responsável, ficaram no YAML `section_vector` e `section_bm25`; os experimentos de threshold e HyDE ficaram como exemplo comentado, com os números medidos.
- **Ordem**: o `assistant/pipeline.py` foi escrito já na forma final (experimento, similaridade, tipos de busca, threshold e HyDE) antes do primeiro portão. Por isso uma única execução da avaliação (`20261010-232839-bancada`) vale para T022, T031 e T047: o código de busca não mudou depois dela.
- **SC-001 conferido**: nota geral de 97,8%, nenhuma regressão e nenhuma melhoria em relação à referência; os trechos enviados ao modelo são idênticos aos da referência, em conteúdo e ordem, nas 46 perguntas. Cinco respostas têm texto diferente com os mesmos trechos, que é o ruído do modelo já conhecido.
- **SC-002**: os três experimentos iniciais rodaram em 8,6 s. Com os sete experimentos, incluindo o de HyDE, 81 s.
- **SC-003, expectativa confirmada**: `section_hybrid` 37/38 com 100% de evidência ancorada; `page_hybrid` 37/38 com 81,8%; `recursive_500_200_hybrid` 31/38 com 81,8%.
- **Achados da bancada**: a busca só por palavras empata com a híbrida (37/38) e a só vetorial fica atrás (35/38); threshold de 0,6 piora (35/38); HyDE mantém 37/38, sobe o Score de 0,67 para 0,78 e leva a busca de 39 ms para 1758 ms.
- **Ajuste fora do plano**: o desempate da tabela passou a colocar experimentos com HyDE depois dos sem, no empate de True Rate. Na primeira tabela o HyDE apareceu em primeiro só pelo Score inflado. Registrado em FR-019, research D7 e no contrato do comando.
- **Ajuste no `run.ps1`**: repassa a entrada quando recebe texto por pipe, e é salvo em UTF-8 com BOM, exigido pelo PowerShell 5 para os acentos.
- **SC-004 a SC-007 e SC-009**: conferidos pelos passos 6 a 11 do quickstart, exceto a parte do `make`.
- **Testes**: 308 de unidade e 8 de integração passando.
