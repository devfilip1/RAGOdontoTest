# 0002 · Hybrid search with query synonyms, fused by rank

**Status:** Accepted · **Date:** 2026-10

## Context

The original search was vector-only. Customers and the brochure use different words for the same thing: a customer asks "how much" or "what's the fee", and the brochure writes "Price". Vector search usually bridges that, but not always, and it can prefer a chunk that sounds similar over the one with the fact. Word-based search is exact about treatment names but blind to wording differences.

Measured on the current brochure, section chunks, 44 questions: vector only 43, word-based only 44, hybrid 44.

## Decision

Run both searches over the same chunks. Each contributes half of `match_count`; the results are merged by reciprocal rank fusion. The word-based search normalizes the text (lower case, no stop words, no plural "s") and expands the question, and only the question, with a hand-written map from customer wording to brochure wording.

## Alternatives considered

- **Vector only.** Misses one question here and was the weakest configuration on the previous brochure as well.
- **Word-based only.** Ties with hybrid on this brochure. Hybrid is kept because the two fail in different ways, and a question with no word in common with the brochure still gets vector results.
- **HyDE.** Same True Rate, about 1.2 s more per question, because the model is called before the search.
- **A similarity threshold of 0.6.** Drops the evidence in 8 of 44 questions.
- **A stemming library instead of the plural rule and synonyms.** A new dependency for a 3-page document.

## Consequences

- The synonym map and the stop-word list are specific to this brochure and were tuned on the working questions. They need review when the brochure changes.
- "How much" and "how long" carry the intent in English, so "much" and "long" are synonyms, not stop words. Adding them to the stop words silently breaks price and duration questions.
- The margin between hybrid and word-based is one or zero questions; the choice rests on robustness, not on a measured gap.
- All three search types and the other options stay available as experiments.

**Evidence:** `retrieve` and `tokenize` in [pipeline.py](../../assistant/pipeline.py); `STOPWORDS` and `QUERY_SYNONYMS` in [config.py](../../assistant/config.py); [experiments.yaml](../../config/experiments.yaml); the round `20261011-131829` under `evaluation/runs/experiments/`
