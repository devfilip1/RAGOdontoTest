# Development

## Prerequisites

- Python 3.14
- [Ollama](https://ollama.com) running, with the models `llama3` and `nomic-embed-text` pulled
- No account, key, or network access is needed after the models are downloaded

## Running locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

ollama pull llama3
ollama pull nomic-embed-text

python -m assistant.ingest          # builds data/index/<strategy>/ for every strategy
python -m assistant.chat            # "exit" closes it
```

Environment variables, all optional, read from `.env` (copy [.env.example](../.env.example)):

| Variable | For | Default |
|---|---|---|
| `OLLAMA_BASE_URL` | Address of the Ollama server | `http://127.0.0.1:11434` |
| `OLLAMA_CHAT_MODEL` | Model that answers | `llama3` |
| `OLLAMA_EMBEDDING_MODEL` | Model that embeds chunks and questions | `nomic-embed-text` |
| `OLLAMA_JUDGE_MODEL` | Model that judges the behaviour criteria | the chat model |

Changing the embedding model makes every index out of date; run `python -m assistant.ingest` again.

### Shortcuts

`.\run.ps1 <name>` (Windows) or `make <name>` runs the common commands without activating the virtual environment. `.\run.ps1 help` lists them. Extra arguments are passed on: `.\run.ps1 eval --label x`, `make eval ARGS="--label x"`.

## Tests

```powershell
pytest                    # 377 unit tests, about 4 seconds, no model
pytest -m integration     # 10 tests against Ollama and the real indexes, about 8 seconds
```

- **Covered**: configuration parsing and its error messages, extraction clean-up and chunking (including the real brochure), search and fusion with fake embeddings, value extraction, scoring, causes, aggregation, history, comparison, the bench and its CSV files, and the parity of the two shortcut files.
- **Not covered**: the wording of the model's answers, which is what the evaluation is for; the terminal rendering in `report.py`.
- [tests/fixtures/factual_examples.json](../tests/fixtures/factual_examples.json) holds example answers with the verdict the scoring must give. When the scoring gets an answer wrong, add the case there first.

Before calling a change done: `pytest`, and, if the change can affect answers, `python -m evaluation run --no-judge` compared with the reference.

## Build and deploy

None. The project runs from source on one machine, and there is no CI.

## Conventions

- **One module, one test file.** `evaluation/normalize.py` is tested by `tests/unit/test_normalize.py`.
- **Unit tests never need a model.** Searches and models are replaced by fakes; anything that needs Ollama goes in `tests/integration/` with the `integration` marker.
- **Everything a reader sees is in English**: code, comments, messages, tests, documentation.
- **`evaluation` may import `assistant`; `assistant` never imports `evaluation`.**
- **Messages say what to do.** A configuration or index error names the file or item and the fix (`run: python -m assistant.ingest page`).
- **Stored runs are evidence.** A number in the documentation must be traceable to a file under `evaluation/runs/`. Fix the document, never the run.
- **Commit messages** are in English from commit `719853c` on; earlier ones are in Portuguese.

## Common tasks

**Change a prompt rule**

1. Edit `SYSTEM_PROMPT` in [pipeline.py](../assistant/pipeline.py). One change at a time.
2. `python -m evaluation run --no-judge --label what-i-changed`.
3. Read the regressions before the score. If it stays: `python -m evaluation baseline set`.
4. If the refusal sentence `NO_ANSWER` changed, update `ABSTENTION_PATTERNS` in [answer_metrics.py](../evaluation/answer_metrics.py).

**Try another chunking or search**

1. Add a strategy to [strategies.yaml](../config/strategies.yaml) and run `python -m assistant.ingest <name>`, or add an experiment to [experiments.yaml](../config/experiments.yaml).
2. `python -m evaluation kb-check --strategy <name>`, then `python -m evaluation experiments`.
3. Before adopting it: `python -m evaluation run --no-judge --experiment <name>`, then change the `assistant:` line.

A new *kind* of chunking needs a function registered in `STRATEGY_TYPES` in [ingest.py](../assistant/ingest.py) and an entry in [strategies.schema.json](../config/schemas/strategies.schema.json).

**Add or fix a question**

Follow [the steps in the evaluation manual](../evaluation/README.md#answer-key): edit `answer_key.json`, bump `version`, run `python -m evaluation validate`, run the evaluation, and set a new reference.

**Replace the brochure**

1. Put the PDF in `data/source/` and point `SOURCE_PDF` in [config.py](../assistant/config.py) to it.
2. `python -m assistant.ingest`, then `python -m evaluation kb-check`, and read `data/index/section/chunks.json` to confirm the sections came out right.
3. Review the prompt, `QUERY_SYNONYMS`, and the whole answer key: evidence quotes must match the new text.

## Common problems

| Symptom | Cause and fix |
|---|---|
| `the index of strategy "x" is out of date` | The PDF, the strategy, or the embedding model changed. Run the command in the message |
| `model "llama3" is not installed` | `ollama pull llama3` |
| `Ollama did not answer at ...` | Start Ollama, or fix `OLLAMA_BASE_URL` |
| `Invalid answer key: ... appears 2 times in the brochure` | The evidence quote is not unique; paste a longer piece of the line |
| The score moved by one question after an unrelated change | Model variation. Repeat with `--repeat 3` before drawing a conclusion |
| `make` is not found on Windows | Use `.\run.ps1`, which has the same shortcuts |
