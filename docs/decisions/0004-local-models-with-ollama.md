# 0004 · Run every model locally with Ollama

**Status:** Reconstructed · **Date:** unknown (present since the first commit)

## Context

Evidence from the code: since the first commit the project calls a local Ollama server for both embeddings and generation, and no hosted API or key appears anywhere. The first scripts defaulted to `deepseek-r1:8b` for chat; the default became `llama3` in the commit that reorganized the project into packages.

> ⚠️ Inferred: the reasons (no cost per call, no data leaving the machine, and a project anyone can run without an account) are not written anywhere. They are deduced from the choice itself and from the root README stating that everything runs locally.

## Decision

Chat, HyDE, embeddings, and the judge all run through Ollama on the same machine. Models are chosen with environment variables, with `llama3` and `nomic-embed-text` as defaults.

## Alternatives considered

- **A hosted model API.** Stronger models and a more reliable judge, at the price of keys, cost, and sending the questions out.

## Consequences

- Anyone can clone and run the project with no account, and the evaluation can be repeated at will.
- Quality is bounded by a small model: the remaining errors are the model leaving its role, and the judge is not reliable ([0003](0003-deterministic-scoring.md)).
- Results depend on the exact model build installed. The numbers in the documentation are tied to stored runs for that reason.
- Speed depends on the machine. Typical answer time is 0.6 s where the reference runs were measured.

**Evidence:** [config.py](../../assistant/config.py), `PrefixedEmbeddings` in [ingest.py](../../assistant/ingest.py), `_model` in [pipeline.py](../../assistant/pipeline.py), [.env.example](../../.env.example)
