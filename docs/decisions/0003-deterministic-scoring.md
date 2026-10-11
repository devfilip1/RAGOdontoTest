# 0003 · Score answers by extracted values, not by a judge model

**Status:** Accepted · **Date:** 2026-10

## Context

An evaluation is only useful if the same answer always gets the same score and the score can be trusted. The common approach, asking a model to grade each answer, fails both tests with a small local model: it varies between runs and it is often wrong. In the run `20261011-132553-with-judge`, the judge gave 5.9% for conciseness to answers of one or two sentences.

What matters most for this assistant is also easy to check mechanically: prices, durations, and opening hours are either the ones in the brochure or not.

## Decision

The overall score is computed with no model. Money, durations, and clock times are extracted from the answer and compared with the answer key; refusals are recognized by a list of phrases; service rules are pattern checks. A judge model is kept for subjective criteria, shown in a separate block, never part of the score, and marked unreliable until it agrees with human labels at least 80% of the time.

About a quarter of the questions are reserved and never used while tuning, so a gain can be confirmed on questions that did not guide it.

## Alternatives considered

- **Judge model for everything.** Not repeatable and not accurate enough with a local model.
- **Exact text match against a reference answer.** Too strict: "$900–$2,000" and "between $900 and $2,000" are the same answer.
- **A hosted judge model.** Would break the local-only choice ([0004](0004-local-models-with-ollama.md)).

## Consequences

- The check is by value, not by sentence. If an answer assigns the cleaning's duration to the whitening and both are valid facts for the question, the score does not notice.
- Every way of writing a value must be handled in `normalize.py`; a new format is a new test case in `factual_examples.json`.
- The refusal sentence in the prompt and the phrase list in the scoring must stay in step. A unit test enforces it.
- Qualities that cannot be extracted as values (tone, the closing invitation, the 3-sentence limit) are not part of the score.
- With 21 reserved questions, each is worth almost 5 points; the reserved score is coarse.

**Evidence:** [normalize.py](../../evaluation/normalize.py), [answer_metrics.py](../../evaluation/answer_metrics.py), `evaluate_item` in [runner.py](../../evaluation/runner.py), [judge.py](../../evaluation/judge.py), [calibrate.py](../../evaluation/calibrate.py)
