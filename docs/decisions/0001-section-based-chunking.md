# 0001 · Chunk the brochure by section, one treatment per chunk

**Status:** Accepted · **Date:** 2026-10

## Context

The project started with 500-character chunks with a 200-character overlap. The brochure lists each treatment as a short block: a title, a few bullet points, and one line with duration and price. Fixed-size chunks cut across those blocks, so a chunk could end with the price of one treatment and begin with the title of the next. The model then answered with the right kind of number from the wrong treatment, which is the worst kind of error for an assistant that quotes prices.

Measured on the current brochure with the search bench (round `20261011-131829`): 500-character chunks bring every evidence in 41 of 44 questions, and in some of those the chunk with the value does not name its treatment (94.9% anchored).

## Decision

Use the brochure's own headings as chunk boundaries. Each chunk starts with its title and holds everything about one subject. The opening block with the address, hours, and contact has no heading, so it becomes its own chunk titled "DentalSafe — Clinic Information".

## Alternatives considered

- **Fixed-size chunks (the original).** Simple and layout-independent, but it separates values from the treatment they belong to.
- **One chunk per page.** Ties on True Rate on this 3-page brochure (44 of 44), but sends a whole page per chunk, which mixes several treatments in what the model reads and does not scale to longer documents.

## Consequences

- The rule "use only the values of the treatment asked about" becomes checkable: one chunk, one treatment.
- Section detection is a heuristic over capitalization, digits, and colons. A document with another layout can be chunked wrong with no error. `python -m evaluation kb-check` and the test on the real brochure are the safety net.
- A section larger than the limit is split, with the title repeated in each part.
- The other two strategies stay available, so the comparison can be measured again at any time.

**Evidence:** `is_heading`, `split_sections`, and `split_by_section` in [ingest.py](../../assistant/ingest.py); [strategies.yaml](../../config/strategies.yaml); `test_the_real_brochure_gives_one_section_per_subject` in [test_ingest.py](../../tests/unit/test_ingest.py)
