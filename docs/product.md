# Product

## Problem and proposal

Building a RAG assistant is easy; knowing whether a change made it better is not. A new chunk size, a prompt rule, or a different search can fix one question and break three others, and reading a few answers by hand does not show it.

RagLab pairs a small assistant with the tools to measure it: an answer key with known answers, scoring that needs no model, a bench that compares search configurations in seconds, and a history of runs to compare before and after. The assistant itself is deliberately simple, so the measuring is what stands out.

> ⚠️ Inferred: the target audience (developers learning or demonstrating RAG evaluation, and people reviewing the project as a portfolio piece) comes from the root README and from the project being moved to English for publication. It is not stated in the code.

## User roles

| Role | What they do |
|---|---|
| Customer | Asks the DentalSafe assistant about treatments, prices, durations, and how to reach the clinic |
| Maintainer | Changes the assistant, runs the evaluation and the experiments, maintains the answer key |

There is no authentication and no user accounts: both roles are whoever runs the commands on the machine.

## Features

- **Assistant**
  - Chat on the terminal, with the answer streamed as it is written. Rules: [assistant behaviour](business-rules.md#assistant-behaviour)
  - Answers from the brochure only, with a fixed sentence when the brochure has no answer
  - Answers in English whatever the language of the question
- **Search configuration**
  - Chunking strategies declared in a YAML file: by section, by characters, or by page. Each one builds its own index
  - Search experiments declared in a YAML file: hybrid, vector, or word-based search; number of chunks; similarity threshold; HyDE; prompt
  - One line of configuration chooses which experiment the assistant uses
- **Evaluation of the answers**
  - 72 questions with expected facts and the line of the brochure that proves them. Rules: [answer key](business-rules.md#answer-key)
  - Deterministic scoring of facts, refusals, made-up values, and service rules. Rules: [scoring](business-rules.md#scoring)
  - A cause for each wrong answer, which says where to look: search, prompt, or model
  - Comparison with a reference run, regressions first
  - Optional judge model for tone, conciseness, and similar criteria, with a way to check it against a person
- **Search bench**
  - Runs every experiment over the answerable questions, without generating answers, and shows one comparison table
  - Writes the table and a per-question detail as CSV
- **Knowledge-base check**
  - Finds duplicate chunks, corrupted text, and facts separated from the name of their treatment, with no model

## Main journeys

**A customer asks a question**

1. The customer types "How much are braces?" in the chat.
2. The assistant finds the chunks about braces and answers "Braces cost $180–$450 (Initial cost) and $35–$90 (Monthly). Would you like to schedule an assessment?"
3. The customer asks "Do you accept dental insurance?", which the brochure does not cover.
4. The assistant answers "I don't have that information right now. I can help you with our treatments or schedule an assessment for you."

**The maintainer changes the assistant**

1. Changes one thing, for example a prompt rule.
2. Runs `python -m evaluation run --no-judge --label what-i-changed`.
3. Reads the regressions first, then the overall score.
4. If the change stays, sets the run as the new reference with `python -m evaluation baseline set`.

The full cycle, with the commands, is in the [evaluation manual](../evaluation/README.md#workflow).

## Out of scope and known limitations

- No conversation memory: each question is answered on its own.
- One document only, hard-coded as the DentalSafe brochure. Using another document means editing code (see the last section of the [root README](../README.md)).
- Terminal only: no web interface, no API, no messaging channel.
- No scheduling: the assistant invites the customer to schedule but cannot book anything.
- English only. Portuguese support was removed on purpose ([decision 0005](decisions/0005-english-only.md)).

## Glossary

| Term | Meaning | In the code |
|---|---|---|
| Brochure | The clinic's PDF, the assistant's only source of truth | `SOURCE_PDF`, `data/source/DentalSafe.pdf` |
| Chunk | A piece of the brochure stored in an index and sent to the model | `chunks.json`, `RetrievedChunk` |
| Strategy | A way of chunking the brochure; each one has its own index | `Strategy`, `config/strategies.yaml`; called `collection` inside an experiment |
| Experiment | A named search configuration: strategy, search type, number of chunks, threshold, HyDE, prompt | `Experiment`, `config/experiments.yaml` |
| Answer key | The set of questions with expected facts and evidence | `AnswerKey`, `evaluation/data/answer_key.json` |
| Item | One question of the answer key | `Item` |
| Expected fact | Something the answer must contain: money, duration, clock time, or text | `Fact` |
| Evidence | The line of the brochure that proves an answer; must appear exactly once in the brochure | `Item.evidence` |
| Anchor | The name that must be in the same chunk as the evidence, so a value is never retrieved without its treatment | `procedures[...].anchors` |
| Procedure | A treatment, or the `clinic` entry for address, hours, and contact | `Item.procedure` |
| Refusal (abstention) | The assistant saying it does not have the information | `NO_ANSWER`, `detect_abstention` |
| dev / holdout / smoke | Working questions, reserved questions never used for tuning, and a 10-question quick subset of dev | `Item.split`, `Item.smoke` |
| Run | One execution of the evaluation, stored with its configuration and every answer | `evaluation/runs/<id>/run.json` |
| Reference (baseline) | The run later runs are compared with, one per subset | `evaluation/runs/baseline.json` |
| True Rate | In the bench, questions in which every evidence reached the model | `ExperimentResult.true_rate` |
| Score | In the bench, mean similarity between question and chunks; it does not measure correctness | `ExperimentResult.score` |
| HyDE | Searching with a hypothetical answer written by the model instead of the question | `use_hyde`, `hypothetical_answer` |
| Judge | A local model that gives yes/no opinions on subjective criteria; not part of the overall score | `evaluation/judge.py` |
