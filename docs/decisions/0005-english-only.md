# 0005 · English only, replacing Portuguese instead of supporting both

**Status:** Accepted · **Date:** 2026-10-11

## Context

The project was first written in Portuguese, around a Portuguese brochure for a clinic called OdontoTest. To publish it for an English-speaking audience, the owner replaced the brochure with an English one for a clinic called DentalSafe, with new content (address, hours, contact, prices in US dollars).

Language runs through more than the prompt: stop words, synonyms, number words, money and time formats, refusal phrases, and the rule that checks the language of the answer.

## Decision

Replace, do not add. Portuguese stop words, synonyms, number words, refusal phrases, and the old answer key were removed. The assistant always answers in English, even when the question is in another language. Runs measured on the Portuguese brochure were deleted from the repository, and every number in the documentation was measured again.

## Alternatives considered

- **A language setting with two rule sets.** Twice the scoring rules and tests for a case nobody will run, and Portuguese number words such as "um" would be read as numbers inside English text.
- **Translating the old answer key.** Prices, field names, and several answers changed, and questions about the address and hours went from unanswerable to answerable.

## Consequences

- One vocabulary to maintain, and scoring rules that match the brochure's format (`$2,000`, `9:00 AM`).
- The before-and-after story had to be measured again: the `original_baseline` experiment reproduces the project's starting point on the English brochure, because the Portuguese runs are not comparable.
- A question in Portuguese is still understood by the vector search and answered in English; the answer key has one such question on purpose.
- Supporting another language later means bringing back per-language rules in `normalize.py`, `answer_metrics.py`, and `config.py`.
- Commit messages before `719853c` remain in Portuguese.

**Evidence:** `SYSTEM_PROMPT` rule 1 in [pipeline.py](../../assistant/pipeline.py); `check_rules` in [answer_metrics.py](../../evaluation/answer_metrics.py); [normalize.py](../../evaluation/normalize.py); the item `adv-portuguese-01` in [answer_key.json](../../evaluation/data/answer_key.json)
