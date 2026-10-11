---

description: "Lista de tarefas para a avaliação e métricas do assistente OdontoTest"
---

# Tasks: Avaliação e Métricas do Assistente OdontoTest

**Input**: Design documents from `/specs/001-rag-eval-metrics/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Incluídos. O plano exige testes de unidade para tudo que é determinístico (research D16) e SC-009 depende deles. Em cada história os testes são escritos antes da implementação e devem falhar primeiro.

**Organization**: Tarefas agrupadas por história de usuário, para cada história poder ser implementada e validada sozinha.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependência de tarefa incompleta)
- **[Story]**: história a que a tarefa pertence (US1 a US5)
- **[MANUAL]** na descrição: tarefa que só o responsável pode fazer

## Path Conventions

Projeto único com scripts na raiz (`create_db.py`, `main.py`, `rag.py`), pacote `evaluation/` e testes em `tests/`. Todos os comandos rodam da raiz, com `.venv` ativo. Nomes de campos, enums e regras seguem [data-model.md](./data-model.md); comandos seguem [contracts/cli.md](./contracts/cli.md); decisões D1 a D16 estão em [research.md](./research.md).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependências e esqueleto do projeto

- [X] T001 Acrescentar `pytest`, `rich` e `jsonschema` a `requirements.txt` com a versão fixada (para `rich` e `jsonschema`, usar a versão já instalada, vista em `pip list`) e rodar `pip install -r requirements.txt`
- [X] T002 [P] Criar `pytest.ini` na raiz com `testpaths = tests`, `pythonpath = .` e o marcador `integration: exige Ollama em execução`; `addopts = -m "not integration"` para os testes de integração só rodarem com `pytest -m integration`
- [X] T003 [P] Criar o esqueleto: `evaluation/__init__.py` (vazio), `evaluation/data/`, `evaluation/runs/.gitkeep`, `tests/unit/`, `tests/integration/`, `tests/fixtures/`; acrescentar `evaluation/runs/_incomplete/` e `.pytest_cache/` a `.gitignore`
- [X] T004 [P] Copiar `specs/001-rag-eval-metrics/contracts/gabarito.schema.json` e `run.schema.json` para `evaluation/schemas/`, de onde o código os lê

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Tornar o assistente consultável (FR-030) sem mudar o que ele responde. Segue [contracts/rag-interface.md](./contracts/rag-interface.md) e research D11.

**⚠️ CRITICAL**: Nenhuma história começa antes desta fase terminar. T005 precisa rodar antes de qualquer alteração em `main.py`.

- [X] T005 Antes de alterar `main.py`, criar `tests/fixtures/capture_pipeline_reference.py`: um script que importa `main` com `builtins.input` substituído para devolver, em ordem, 8 perguntas fixas (preço do clareamento, preço do implante, tempo da limpeza, resultado das lentes, valor do aparelho, extração de siso, "por que escolher a OdontoTest", "qual o endereço") e depois `sair`, e com `langchain_ollama.ChatOllama.invoke` substituído por uma função que guarda o prompt recebido (texto de `prompt.to_string()`) e devolve um objeto com `.content = ""`. Rodar o script e gravar `tests/fixtures/pipeline_reference.json` como lista de `{question, prompt}`. Exige Ollama (a busca vetorial usa embeddings)
- [X] T006 Em `create_db.py`, trocar os literais por constantes de módulo `CHUNK_SIZE = 500`, `CHUNK_OVERLAP = 200`, `COLLECTION_NAME = "db_odonto_test_ollama"`, `PATH_DB = "./database"` e `CHUNKS_PATH = "chunks.json"`, usadas nas funções existentes; nenhuma mudança de comportamento
- [X] T007 Criar `rag.py` com: `RagConfig` (dataclass `frozen=True`; campos e padrões da tabela de `contracts/rag-interface.md`: `vector_k=3`, `bm25_k=3`, `chat_model`, `embedding_model`, `temperature=None`, `seed=None`, `prompt_template` com o texto atual de `main.py` copiado sem alteração); `RetrievedChunk(content, rank, score)`; `RetrievalResult(vector, bm25, fused)`; `AnswerResult(answer, retrieval, latency_s)`; `retrieve(question, config)` com a busca vetorial (`similarity_search_with_relevance_scores`) e a BM25 (`query.lower().split()`) como estão hoje e `fused` = vetorial seguida de BM25 sem repetição (`dict.fromkeys`); `build_prompt(question, retrieval, config)` que junta `fused` com `"\n\n----\n\n"` e aplica o template; `answer(question, config)` que mede `latency_s` da busca mais a geração. Recursos (Chroma, BM25, chunks) são carregados na primeira chamada e guardados em cache, nunca na importação. Erros do Ollama sobem como exceção
- [X] T008 Reescrever `main.py` para conter só o laço de conversa: lê a pergunta, encerra com `sair`/`exit`/`quit`, chama `rag.answer(ask, RagConfig())` e imprime `response: <texto>`; a chamada `to_ask()` fica dentro de `if __name__ == "__main__":`. Remover de `main.py` o prompt, a busca e a criação do modelo, que passam a viver em `rag.py`
- [X] T009 Criar `tests/integration/test_rag_equivalence.py` (marcador `integration`): para cada item de `tests/fixtures/pipeline_reference.json`, `rag.build_prompt(question, rag.retrieve(question, RagConfig()), RagConfig())` deve ser igual ao `prompt` gravado. Incluir também um teste de que `import rag` não chama `input` nem o Ollama. Rodar com `pytest -m integration` e confirmar que passa

**Checkpoint**: `python main.py` conversa como antes; `python -c "import rag"` termina sem efeito; o teste de equivalência passa.

---

## Phase 3: User Story 1 - Saber a nota atual do assistente (Priority: P1) 🎯 MVP

**Goal**: Um comando roda o gabarito no assistente e mostra o placar com a nota geral, a correção factual, a recusa correta e os itens errados.

**Independent Test**: `python -m evaluation run` no assistente atual produz um placar e grava `evaluation/runs/<run_id>/run.json`; o item do preço do clareamento aparece como errado (SC-003).

### Tests for User Story 1 ⚠️

> Escrever primeiro e confirmar que falham antes da implementação

- [X] T010 [P] [US1] Criar `tests/fixtures/factual_examples.json` com 20 respostas de exemplo, cada uma com `answer`, `expected_facts`, `allowed_facts` e `expected_verdict`. Cobrir: `R$ 1.500`, `R$1500`, `1500 reais`, `1.500,00`, `mil e quinhentos reais`, faixa `de 500 a 1.500`, `2,5 mil`, duração em minutos/dias/meses/anos/sessões/consultas, `72h`, número por extenso (`três anos`), resposta com o valor certo e mais um valor de outro procedimento (erro), resposta com só um dos dois valores de uma faixa (erro), fato de texto com e sem acento, valor permitido presente (acerto)
- [X] T011 [P] [US1] Criar `tests/unit/test_normalize.py`: `normalize_text` (minúsculas, sem acento, espaços colapsados); `extract_money` e `extract_durations` para cada formato de T010; números por extenso de zero a dezenas de milhares; texto sem valores devolve lista vazia; `R$ 1.500 a R$ 3.500 por dente` devolve os dois valores
- [X] T012 [P] [US1] Criar `tests/unit/test_answer_metrics.py`: teste parametrizado sobre os 20 exemplos de `tests/fixtures/factual_examples.json` exigindo o `expected_verdict` em todos (SC-009); `detect_abstention` reconhece "Não encontrei essa informação no sistema." com e sem acento e não dispara em resposta normal; pergunta sem resposta com dinheiro ou duração na resposta não conta como recusa correta
- [X] T013 [P] [US1] Criar `tests/unit/test_dataset.py` com um gabarito mínimo válido e um caso por regra de `data-model.md` ("Regras de validação"), cada um exigindo o erro com o `id` do item: `id` duplicado; `answerable: true` sem fato ou sem evidência; `answerable: false` com `expected_facts` ou `evidence`; evidência que aparece zero ou mais de uma vez no material; valor `money`/`duration` ausente de todas as evidências do item; `procedure` inexistente em `procedures`; `variant_of` inexistente ou de outro `split`; e os três limites de cobertura (menos de 40 itens, procedimento sem item de `price`/`duration`/`result`, menos de 6 itens com `answerable: false`)

### Implementation for User Story 1

- [X] T014 [P] [US1] Implementar `evaluation/normalize.py`: `normalize_text`, `extract_money(text) -> list[float]`, `extract_durations(text) -> list[(valor, unit)]` com `unit` em `minute`, `hour`, `day`, `month`, `year`, `session`, `visit`, e `words_to_number` para pt-BR (research D2). Fazer T011 passar
- [X] T015 [P] [US1] Implementar `evaluation/dataset.py`: dataclasses `Fact`, `Item`, `Gabarito` com os campos de `data-model.md`; `load_gabarito(path)` que valida contra `evaluation/schemas/gabarito.schema.json` e calcula o hash SHA-256 do arquivo; `validate(gabarito, source_text)` que aplica todas as "Regras de validação" de `data-model.md` e devolve a lista de problemas com o `id` do item; `load_source_text()` que junta o texto das páginas de `base/OdontoTest.pdf`; `coverage(gabarito)` com contagens por `category`, `procedure` e `split`. Fazer T013 passar
- [X] T016 [US1] Implementar em `evaluation/answer_metrics.py`: `check_facts(answer, expected_facts) -> list[{label, found}]`; `unexpected_values(answer, expected_facts, allowed_facts)` que devolve os valores de dinheiro ou duração da resposta fora do esperado e do permitido, só para os tipos presentes em `expected_facts` (research D2); `detect_abstention(answer)` com a lista de padrões em uma constante `ABSTENTION_PATTERNS` (research D7); `factual_ok(...)`. Fazer T012 passar (depende de T014)
- [X] T017 [US1] Escrever `evaluation/data/gabarito.json` versão `2026-10-10.1` a partir de `base/OdontoTest.pdf`, no formato de `contracts/gabarito.schema.json` e seguindo `contracts/gabarito.example.json`: `procedures` com as âncoras dos 8 procedimentos (limpeza, clareamento, restauração, canal, implante, aparelho, extração, lentes); cerca de 52 itens: para cada procedimento, `price`, `duration`, `result` e um entre `indication`/`how_it_works`; 3 de `differentials` (atendimento em até 72h, procedimentos no mesmo dia, facilidade de pagamento); 6 ou mais `out_of_scope` (endereço, horário, convênio, telefone, nome do dentista, parcelamento em quantas vezes); 5 variações de escrita com `variant_of` (informal, erro de digitação, sem acento); 3 de `comparison` com duas evidências; 3 `adversarial` com `answerable: false`. Incluir `clareamento-preco-01` com a nota do erro conhecido. Marcar cerca de 25% como `split: "holdout"` distribuídos por `category` e `procedure`, e cerca de 10 como `smoke: true`, um por `category`. Para o implante, não usar como evidência a linha com `■■■ânio`
- [X] T018 [US1] Implementar em `evaluation/runner.py`: `ItemResult` com os campos de "Resultado por pergunta" de `data-model.md`; `evaluate_item(item, answer_result)` que preenche `answer`, `retrieved`, `facts`, `unexpected_values`, `abstained`, `latency_s` e `passed` (fatos corretos e sem valor inesperado para `answerable: true`; recusa sem dinheiro nem duração para `answerable: false`), deixando `retrieval`, `judge` e `cause` como null e `ungrounded_values`, `rule_violations` e `flags` vazios; `run_evaluation(items, config, on_progress)` que chama `rag.answer` com `temperature=0` e `seed=42`, e que, em exceção do serviço ou `KeyboardInterrupt`, devolve `status = "incomplete"` com `skipped` preenchido (FR-022); `preflight()` que confere se o Ollama responde e se os modelos da configuração estão instalados
- [X] T019 [P] [US1] Implementar `evaluation/aggregate.py` com `aggregate(results, items)` devolvendo: `overall.pass_rate` e `item_count`; `answer.factual_accuracy` (itens com resposta), `correct_refusal_rate` (itens sem resposta em que recusou) e `wrong_refusal_rate` (itens com resposta em que recusou); `operational.latency_p50` e `latency_p95`. Métricas sem itens na base valem null
- [X] T020 [P] [US1] Implementar em `evaluation/history.py`: `snapshot_config(rag_config, judge_model)` com todos os campos de "Configuração do assistente" de `data-model.md` (`chunk_size` e `chunk_overlap` de `create_db`, `prompt_hash`, `kb_hash` e `kb_chunk_count` a partir de `chunks.json`, `git_commit` e `git_dirty` via `git`); `new_run_id(label)` no formato `<AAAAMMDD-HHMMSS>[-<rótulo>]`; `save_run(run)` que valida contra `evaluation/schemas/run.schema.json` e grava em `evaluation/runs/<run_id>/run.json` se `complete` ou em `evaluation/runs/_incomplete/<run_id>/run.json` se `incomplete`
- [X] T021 [US1] Implementar `evaluation/report.py`: `print_scoreboard(run, gabarito)` com `rich` (nota geral, métricas de resposta, tempos e uma tabela dos itens errados com pergunta, resposta, esperado e valores inesperados) e `write_report(run, gabarito, path)` que grava o mesmo conteúdo em `report.md` com todos os itens, incluindo os trechos recuperados (FR-020). Rótulos em português
- [X] T022 [US1] Implementar `evaluation/cli.py` com `argparse` e `evaluation/__main__.py`: comando `validate` (valida, mostra a cobertura, código de saída `2` se inválido) e comando `run [--label TEXTO]` seguindo os passos 1 a 5 de `contracts/cli.md` (valida o gabarito, `preflight`, executa com barra de progresso, grava, mostra o placar; código `1` e lista dos itens não avaliados se incompleta). Nesta fase `run` usa os itens com `split: "dev"`
- [X] T023 [US1] Rodar `python -m evaluation validate` e corrigir `evaluation/data/gabarito.json` até ficar válido e com a cobertura de SC-001
- [ ] T024 [US1] [MANUAL] O responsável revisa `evaluation/data/gabarito.json`: confere perguntas, fatos esperados e evidências contra `base/OdontoTest.pdf`, acrescenta os exemplos reais de respostas erradas que tiver e sobe `version` se alterar algo
- [X] T025 [US1] Rodar `pytest tests/unit` (tudo passa) e `python -m evaluation run --label primeira`; conferir que o placar aparece, que `evaluation/runs/<run_id>/run.json` e `report.md` existem e que `clareamento-preco-01` está errado com o valor incorreto em `unexpected_values` (SC-003). Se o assistente acertar esse item nesta execução, registrar o fato em `notes` do item em vez de forçar a falha

**Checkpoint**: A nota atual do assistente existe e está gravada.

---

## Phase 4: User Story 2 - Descobrir onde está o erro (Priority: P2)

**Goal**: Métricas de busca separadas das de resposta e uma causa para cada item errado.

**Independent Test**: Depois de `python -m evaluation run`, todo item errado tem `cause` preenchida (SC-004) e o placar mostra as métricas de busca por fonte e as notas por tipo de pergunta e por procedimento.

### Tests for User Story 2 ⚠️

- [X] T026 [P] [US2] Criar `tests/unit/test_retrieval_metrics.py`: evidência no 1º, no 3º e em nenhum chunk (`hit`, `mrr` 1, 1/3 e 0); item com duas evidências e só uma recuperada (`recall` 0,5); `context_precision` com 1 chunk relevante em 4; comparação normalizada (acento, maiúsculas, quebras de linha dentro do chunk); `anchored` verdadeiro quando o chunk com a evidência contém uma âncora do procedimento e falso quando não contém; item com `answerable: false` devolve null
- [X] T027 [P] [US2] Criar `tests/unit/test_diagnose.py` com um caso por linha da tabela de research D14, na ordem de precedência: sem resposta no material e respondeu → `fabricated`; evidência não recuperada → `retrieval_failure`; evidência recuperada e recusou → `wrong_refusal`; evidência recuperada e valor fora dos trechos → `fabricated`; evidência recuperada e fato errado ou faltando → `answer_failure`; item que passou → null. Conferir também os sinais `evidence_not_anchored` e `other_procedure_value`
- [X] T028 [P] [US2] Acrescentar a `tests/unit/test_answer_metrics.py` os casos de `ungrounded_values`: valor da resposta presente em um chunk (vazio), valor ausente de todos os chunks (listado), mesmo valor em formato diferente no chunk (vazio)

### Implementation for User Story 2

- [X] T029 [P] [US2] Implementar `evaluation/retrieval_metrics.py`: `score_retrieval(item, chunks, anchors) -> {hit, recall, mrr, context_precision, anchored}` conforme research D3 a D5, e `score_all_sources(item, retrieval_result, gabarito)` para `vector`, `bm25` e `fused`. Fazer T026 passar
- [X] T030 [US2] Acrescentar `ungrounded_values(answer, chunks)` a `evaluation/answer_metrics.py` (research D6, camada determinística). Fazer T028 passar
- [X] T031 [P] [US2] Implementar `evaluation/diagnose.py`: `classify(item, result) -> (cause, flags)` com a tabela de research D14 e os valores de `cause` de `data-model.md` (`retrieval_failure`, `answer_failure`, `fabricated`, `wrong_refusal`, `rule_violation`). `other_procedure_value` é marcado quando um valor inesperado da resposta é fato esperado de um item de outro procedimento. Fazer T027 passar
- [X] T032 [US2] Em `evaluation/runner.py`, preencher `retrieval`, `ungrounded_values`, `cause` e `flags` de cada `ItemResult` usando T029 a T031
- [X] T033 [US2] Em `evaluation/aggregate.py`, acrescentar: `retrieval` por fonte (`hit_rate`, `recall`, `mrr`, `context_precision`, `anchored_rate`, só itens com resposta); `answer.faithfulness_numeric` (fração de respostas sem `ungrounded_values`); `diagnosis.by_cause`, `by_category` e `by_procedure`
- [X] T034 [US2] Em `evaluation/report.py`, acrescentar ao placar e ao `report.md`: tabela de busca com uma linha por fonte, contagem por causa, notas por tipo de pergunta e por procedimento, e a causa e os sinais em cada item errado
- [X] T035 [US2] Rodar `pytest tests/unit` e `python -m evaluation run --label diagnostico`; conferir que nenhum item errado tem `cause` null (SC-004) e que as três fontes de busca aparecem no placar

**Checkpoint**: Cada erro tem uma causa e dá para ver se o problema está na busca ou na resposta.

---

## Phase 5: User Story 3 - Comparar antes e depois de uma mudança (Priority: P2)

**Goal**: Histórico das execuções, referência e comparação com regressões em destaque.

**Independent Test**: Duas execuções com configurações diferentes; `python -m evaluation compare` mostra a mudança de configuração, a diferença por métrica e os itens que mudaram de resultado.

### Tests for User Story 3 ⚠️

- [X] T036 [P] [US3] Criar `tests/unit/test_history.py` usando `tmp_path`: execução `complete` vai para `runs/<run_id>/` e `incomplete` para `runs/_incomplete/<run_id>/`; `list_runs` não devolve incompletas e ordena da mais recente para a mais antiga; `set_baseline` recusa execução inexistente ou incompleta e guarda a referência por recorte (`dev`, `holdout`); `latest_run(subset)`
- [X] T037 [P] [US3] Criar `tests/unit/test_compare.py`: diferença por métrica; item de certo para errado em `regressions` com a causa nova e de errado para certo em `improvements`; nota geral maior com regressões presentes mantém as regressões na saída; recortes diferentes → `comparable` falso com o motivo; hash de gabarito diferente → aviso, comparação só dos `id` em comum e contagem dos que ficaram de fora; `config_changes` lista só os campos que mudaram; `within_noise` verdadeiro quando a diferença é menor que a variação medida
- [X] T038 [P] [US3] Criar `tests/unit/test_aggregate.py`: `variance` com média, mínimo e máximo por métrica a partir de N conjuntos de resultados; percentis de latência; métrica sem itens na base vale null; `select_subset` devolve só `dev`, só `holdout` ou só `smoke`

### Implementation for User Story 3

- [X] T039 [US3] Em `evaluation/history.py`, acrescentar `load_run`, `list_runs`, `latest_run(subset)`, `set_baseline(run_id)` e `get_baseline(subset)` sobre `evaluation/runs/baseline.json` com os campos `dev`, `holdout` e `set_at`. Fazer T036 passar
- [X] T040 [P] [US3] Implementar `evaluation/compare.py`: `compare(base, candidate) -> Comparison` com os campos de "Comparação" de `data-model.md` (`comparable`, `metric_deltas`, `regressions`, `improvements`, `config_changes`, `within_noise`). Fazer T037 passar
- [X] T041 [US3] Acrescentar `select_subset(gabarito, subset)` a `evaluation/dataset.py` e `variance(metric_sets)` a `evaluation/aggregate.py`; em `evaluation/runner.py`, aceitar `repeat` (roda o conjunto N vezes, guarda `results` da primeira repetição e `variance` quando `repeat` > 1). Fazer T038 passar
- [X] T042 [US3] Em `evaluation/report.py`, acrescentar `print_comparison(comparison)`: regressões primeiro, depois mudanças de configuração, tabela de métricas com a diferença e a marca "dentro da variação", melhorias e o aviso de gabarito diferente; e, no placar de `run`, a linha de variação por métrica quando houver
- [X] T043 [US3] Em `evaluation/cli.py`, acrescentar: opções `--smoke`, `--holdout` (mutuamente exclusivas) e `--repeat N` em `run`, gravando `subset` e `repeat`; comparação automática com a referência do mesmo recorte ao fim de `run` (passo 6 de `contracts/cli.md`); comandos `compare [BASE] [CANDIDATA]` (código `2` se os recortes diferem), `baseline set [RUN_ID]`, `baseline show` e `list`
- [X] T044 [US3] Rodar `python -m evaluation run --repeat 2 --label repetibilidade` e conferir que a variação é de no máximo 3 pontos percentuais em cada métrica (SC-005); se passar disso, investigar a causa antes de seguir
- [X] T045 [US3] Rodar `python -m evaluation run --label referencia` e `python -m evaluation baseline set` (SC-010). Depois validar a comparação: rodar com `vector_k=5` (parâmetro temporário), `python -m evaluation compare`, conferir a mudança de configuração e os itens alterados, e desfazer o parâmetro

**Checkpoint**: A referência do assistente atual está gravada e qualquer mudança futura pode ser comparada com ela.

---

## Phase 6: User Story 4 - Medir o comportamento de atendente (Priority: P3)

**Goal**: Regras de atendimento conferidas por texto, critérios subjetivos avaliados por juiz local e conferência do juiz contra uma pessoa.

**Independent Test**: `python -m evaluation run` mostra o bloco de comportamento; `calibrate export` e `calibrate score` informam a concordância por critério.

### Tests for User Story 4 ⚠️

- [X] T046 [P] [US4] Acrescentar a `tests/unit/test_answer_metrics.py` os casos de `check_rules`: resposta com "contexto", "documento" ou "base de dados" (com e sem acento, maiúsculas) é violação; palavra parecida que não é violação (ex.: "documentação" não deve ser confundida se a regra for por palavra inteira); resposta acima do tamanho máximo; resposta limpa sem violações
- [X] T047 [P] [US4] Criar `tests/unit/test_calibrate.py`: amostra de tamanho pedido, distribuída por `category`, sem as notas do juiz e com `human` vazio; `score` calcula a concordância por critério; critério abaixo de 0,8 é marcado como não confiável; amostra com `human` não preenchido é ignorada e contada
- [X] T048 [P] [US4] Acrescentar a `tests/unit/test_diagnose.py`: fatos certos com regra violada → `rule_violation` e `passed` falso; fatos errados com regra violada mantém a causa de maior precedência

### Implementation for User Story 4

- [X] T049 [US4] Acrescentar `check_rules(answer) -> list[str]` a `evaluation/answer_metrics.py` com as regras de research D9 em constantes (`FORBIDDEN_TERMS`, `MAX_ANSWER_CHARS`); em `evaluation/runner.py`, preencher `rule_violations` e incluir "nenhuma regra violada" em `passed`; em `evaluation/diagnose.py`, acrescentar a última linha da tabela D14. Fazer T046 e T048 passar
- [X] T050 [P] [US4] Implementar `evaluation/judge.py` conforme research D8: constante `CRITERIA` com `relevance`, `tone`, `scheduling`, `conciseness` e `faithfulness`, cada um com uma rubrica de uma frase e dois exemplos; `judge_answer(question, answer, chunks, model)` com uma chamada por critério via cliente `ollama`, `temperature=0`, `seed=42` e `format` com o esquema `{veredito: boolean, motivo: string}`; modelo lido de `OLLAMA_JUDGE_MODEL`, com o modelo de chat como padrão; JSON inválido vira veredito null com o motivo do erro, sem derrubar a execução
- [X] T051 [US4] Em `evaluation/runner.py`, chamar o juiz para cada item quando habilitado e preencher `judge`; em `evaluation/cli.py`, acrescentar `--no-judge` a `run` e gravar `judge_model` (null quando desligado); em `evaluation/aggregate.py`, acrescentar o grupo `judge` com `score` por critério (ignorando vereditos null) e `answer.rule_compliance`
- [X] T052 [P] [US4] Implementar `evaluation/calibrate.py`: `export_sample(run, size=20)` grava `evaluation/data/human_labels.json` no formato de "Amostra de conferência humana" de `data-model.md`; `score_agreement(labels, run)` devolve a concordância por critério e grava o resultado em `evaluation/data/judge_agreement.json`. Fazer T047 passar
- [X] T053 [US4] Em `evaluation/cli.py`, acrescentar `calibrate export [RUN_ID] [--size 20]` e `calibrate score`; em `evaluation/report.py`, acrescentar o bloco "Comportamento (juiz)" separado das métricas determinísticas, com a concordância humana de `judge_agreement.json` quando existir e a marca "não confiável" nos critérios abaixo de 80%; `aggregate` preenche `human_agreement`
- [X] T054 [US4] Rodar `python -m evaluation run --label com-juiz` e `python -m evaluation calibrate export`
- [ ] T055 [US4] [MANUAL] O responsável preenche os campos `human` das 20 respostas em `evaluation/data/human_labels.json` e roda `python -m evaluation calibrate score`; meta de 80% por critério (SC-007). Para critérios abaixo da meta, ajustar a rubrica em `evaluation/judge.py` ou testar outro modelo em `OLLAMA_JUDGE_MODEL` e repetir T054

**Checkpoint**: O comportamento de atendente é medido e se sabe quais critérios do juiz são confiáveis.

---

## Phase 7: User Story 5 - Verificações rápidas da base de conhecimento (Priority: P3)

**Goal**: Um comando sem modelo de linguagem que aponta defeitos da base de conhecimento em segundos.

**Independent Test**: `python -m evaluation kb-check` em menos de 1 minuto aponta o trecho com `■■■ânio` e os fatos sem trecho ancorado; em uma base com duplicados, aponta a quantidade de repetições.

### Tests for User Story 5 ⚠️

- [X] T056 [P] [US5] Criar `tests/unit/test_kb_checks.py` com listas de chunks em memória: `find_duplicates` devolve o conteúdo e a quantidade de repetições e ignora diferenças de espaço; `find_unanchored_facts` lista o item cuja evidência só aparece em chunk sem âncora do procedimento e não lista quando existe um chunk com evidência e âncora; `find_corrupted` pega `■` (U+25A0), U+FFFD e caracteres de controle e não pega acentos, `–`, `—` e `|`; `find_source_mismatch` aponta quantidade e conteúdo diferentes entre a base vetorial e o arquivo de trechos

### Implementation for User Story 5

- [X] T057 [US5] Implementar `evaluation/kb_checks.py` conforme research D15: as quatro funções de T056 e `load_kb()` que lê os documentos da coleção Chroma (`create_db.COLLECTION_NAME`, `create_db.PATH_DB`, via `_collection.get()`) e os trechos de `create_db.CHUNKS_PATH`, sem chamar embeddings. Fazer T056 passar
- [X] T058 [US5] Em `evaluation/cli.py`, acrescentar `kb-check` (lista cada problema e o total por tipo; código `0` mesmo com problemas, `1` se não conseguir ler a base); em `evaluation/report.py`, acrescentar `print_kb_report`
- [X] T059 [US5] Rodar `python -m evaluation kb-check` e conferir: termina em menos de 1 minuto (SC-008); aponta o trecho com `■■■ânio`; aponta fatos sem trecho ancorado (entre eles o preço da restauração). Conferir a detecção de duplicados com uma cópia temporária da base em `tmp` contendo trechos repetidos, sem alterar `database/`

**Checkpoint**: Todas as histórias funcionam de forma independente.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Fechamento e validação de ponta a ponta

- [X] T060 [P] Criar `evaluation/README.md`: o que cada comando faz, como ler o placar (o que é determinístico e o que é juiz), como acrescentar uma pergunta ao gabarito, a regra de não consultar a parte reservada durante os ajustes e o ciclo "mudar → `run` → `compare`"
- [X] T061 Rodar `python -m evaluation run --holdout --label referencia-holdout` e `python -m evaluation baseline set`; conferir que `python -m evaluation compare` entre uma execução `dev` e uma `holdout` é recusado
- [X] T062 Conferir a execução interrompida: parar o Ollama durante `python -m evaluation run`, confirmar a lista de itens não avaliados, a gravação em `evaluation/runs/_incomplete/` e a ausência em `python -m evaluation list` (FR-022)
- [X] T063 Rodar `pytest tests/unit` e `pytest -m integration`; tudo passa
- [X] T064 Percorrer os 11 passos de `specs/001-rag-eval-metrics/quickstart.md`, medir os tempos de SC-002 (completa em até 30 min, reduzida em até 5 min) e anotar em `specs/001-rag-eval-metrics/quickstart.md` qualquer resultado diferente do esperado

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup; bloqueia todas as histórias. T005 → T006 → T007 → T008 → T009, nesta ordem
- **US1 (Phase 3)**: depende da Phase 2
- **US2 (Phase 4)**: depende da US1 (usa `runner`, `aggregate`, `report` e o gabarito)
- **US3 (Phase 5)**: depende da US1; recomendado depois da US2, para a referência (T045) já ter as métricas de busca e as causas
- **US4 (Phase 6)**: depende da US1 e da US2 (`diagnose`)
- **US5 (Phase 7)**: depende só da Phase 2 e de T015 e T017 (gabarito); pode ser feita a qualquer momento depois deles
- **Polish (Phase 8)**: depende das histórias desejadas

### User Story Dependencies

```text
Setup ─► Foundational ─► US1 ─┬─► US2 ─┬─► US3 (referência com tudo medido)
                              │        └─► US4
                              └─► US5 (só precisa do gabarito)
```

As histórias compartilham `runner.py`, `aggregate.py`, `report.py` e `cli.py`. Por isso US2, US3 e US4 não rodam em paralelo entre si: cada uma acrescenta ao que a anterior deixou.

### Within Each User Story

- Testes antes da implementação, falhando primeiro
- `normalize` → `answer_metrics` → `runner` → `aggregate`/`report` → `cli`
- Tarefas de execução (T025, T035, T044, T045, T054, T059) vêm por último na história
- Se uma execução gravada antes ficar sem campos novos (ex.: `cause`), ela continua válida no histórico; a comparação trata campo ausente como null

### Parallel Opportunities

- Phase 1: T002, T003 e T004 em paralelo, depois de T001
- US1: T010 a T013 em paralelo; depois T014 e T015 em paralelo; T019 e T020 em paralelo com T017 e T018
- US2: T026 a T028 em paralelo; T029 e T031 em paralelo
- US3: T036 a T038 em paralelo; T040 em paralelo com T039
- US4: T046 a T048 em paralelo; T050 e T052 em paralelo
- US5 inteira em paralelo com US2, US3 ou US4 (toca só `kb_checks.py`, mais um acréscimo em `cli.py` e `report.py`)

---

## Parallel Example: User Story 1

```text
# Testes da US1, juntos:
Task: "Criar tests/fixtures/factual_examples.json com 20 respostas de exemplo"
Task: "Criar tests/unit/test_normalize.py"
Task: "Criar tests/unit/test_answer_metrics.py"
Task: "Criar tests/unit/test_dataset.py"

# Depois, módulos sem dependência entre si:
Task: "Implementar evaluation/normalize.py"
Task: "Implementar evaluation/dataset.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational (o assistente consultável, com o teste de equivalência)
3. Phase 3: US1
4. **PARAR e VALIDAR**: o responsável revisa o gabarito (T024) e lê o primeiro placar (T025)

Nesse ponto já existe a nota atual do assistente.

### Incremental Delivery

1. Setup + Foundational → assistente consultável
2. US1 → nota atual (MVP)
3. US2 → causa de cada erro
4. US3 → referência gravada e comparação; a partir daqui dá para começar as features de melhoria do assistente
5. US4 → comportamento de atendente
6. US5 → verificações da base (pode ser adiantada)

### Pontos em que o responsável participa

- **T024**: revisar o gabarito antes do primeiro placar
- **T055**: avaliar 20 respostas para conferir o juiz
- Depois de T045: decidir as metas de qualidade a partir da referência (SC-010)

---

## Notes

- [P] = arquivos diferentes, sem dependência de tarefa incompleta
- Cada tarefa de implementação cita o teste que precisa passar
- Nenhuma tarefa altera o prompt, a busca, a divisão do material ou o modelo do assistente; a única mudança no assistente é a extração para `rag.py` (FR-030)
- Commits só quando o responsável pedir
- As execuções em `evaluation/runs/` são versionadas; `_incomplete/` não

## Notas da implementação (2026-10-10)

- **Pendentes, só o responsável pode fazer**: T024 (revisar o gabarito) e T055 (avaliar as 20 respostas de `evaluation/data/human_labels.json` e rodar `calibrate score`). O passo 10 do quickstart depende de T055.
- **Ordem**: os módulos compartilhados (`runner.py`, `aggregate.py`, `report.py`, `cli.py`) foram escritos já na forma final, e não história a história. As execuções pedidas em T025, T035, T044, T045 e T054 foram feitas com duas execuções reais: `20261010-192659-repetibilidade` (2 repetições, sem juiz) e `20261010-193039-referencia` (com juiz, marcada como referência).
- **T062**: a execução interrompida foi simulada fazendo o assistente falhar na 4ª pergunta, sem parar o Ollama de verdade. O resultado foi gravado em `_incomplete/`, o comando saiu com código 1 e a execução não apareceu em `list`.
- **T059**: a detecção de duplicados foi conferida só pelos testes de unidade; a base real não tem duplicados e não foi feita uma cópia adulterada.
- **Acréscimos fora das tarefas**: `tests/unit/test_runner.py`; opções `--vector-k` e `--bm25-k` em `run`; pergunta de aquecimento antes de medir; ajuste na conferência de valores descrito em research D2.
- **Medições**: avaliação completa com juiz em 8 min 27 s e sem juiz em cerca de 1 min 50 s por repetição; reduzida sem juiz em 34 s; `kb-check` em 3 s; variação entre as 2 repetições gravadas de 0 pontos percentuais (uma execução de teste anterior, já apagada, variou 2,6).
