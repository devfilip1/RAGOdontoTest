# Implementation Plan: Avaliação e Métricas do Assistente OdontoTest

**Branch**: `001-rag-eval-metrics` (pasta da feature; o trabalho está na branch `main`, nenhuma branch foi criada) | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-rag-eval-metrics/spec.md`

## Summary

Criar a avaliação do assistente OdontoTest: um gabarito de ~50 perguntas e um comando que consulta o assistente, calcula métricas de busca, de resposta, de comportamento e de tempo, classifica a causa de cada erro, grava o resultado e compara com uma execução de referência.

Abordagem (detalhes em [research.md](./research.md)):

- Harness próprio em Python, sem framework de avaliação. As métricas principais são determinísticas: fatos tipados (dinheiro, duração, texto) comparados por valor, e evidência localizada por trecho literal do material.
- Juiz local com perguntas binárias e saída estruturada só para o que é subjetivo (relevância, tom, condução para o agendamento, objetividade), em bloco separado do placar e conferido contra avaliação humana.
- O pipeline do assistente sai de `main.py` para um módulo `rag.py` consultável, sem mudar prompt, busca ou modelo.
- Histórico em arquivos JSON, um por execução, com a configuração do assistente gravada junto.

## Technical Context

**Language/Version**: Python 3.14.8 (ambiente virtual `.venv`)

**Primary Dependencies**: já no projeto: `langchain-chroma` 1.1.0, `langchain-ollama` 1.1.0, `langchain-core` 1.6.9, `rank-bm25` 0.2.2, `ollama` 0.6.3 (cliente). A acrescentar em `requirements.txt`: `pytest`, `rich` (já instalado como dependência indireta) e `jsonschema` (idem, para validar o gabarito)

**Storage**: arquivos JSON em `evaluation/data/` (gabarito, conferência humana) e `evaluation/runs/` (uma pasta por execução). A base de conhecimento continua em Chroma (`database/`) e `chunks.json`

**Testing**: `pytest`. Testes de unidade sem Ollama para tudo que é determinístico; um teste de integração (marcado, exige Ollama) para a equivalência de `rag.py` com o pipeline atual

**Target Platform**: computador do responsável: Windows 11, Ollama 0.40.2 local, RTX 4060 Laptop 8 GB

**Project Type**: ferramenta de linha de comando sobre um projeto Python de scripts (sem pacote instalável)

**Performance Goals**: avaliação completa em até 30 min e reduzida em até 5 min (SC-002). Estimado a partir de medição: ~8 min com juiz e ~2 min sem juiz (1,6 s por resposta e 1,5 s por chamada de juiz, modelos na GPU). Verificações da base e testes de unidade em segundos

**Constraints**: tudo local, sem enviar dados a serviços externos; repetível (`temperature=0`, `seed=42`; variação de até 3 pontos percentuais, SC-005); o assistente não pode mudar o que responde no uso normal (FR-030)

**Scale/Scope**: 1 usuário; 1 documento de 3 páginas (8 procedimentos, 11 trechos hoje); ~50 itens no gabarito; dezenas de execuções no histórico

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` ainda é o modelo sem preencher: não há princípios ratificados, portanto não há portões a avaliar. **Resultado: passa (sem portões), antes da Fase 0 e depois da Fase 1.**

Na falta de constituição, o plano segue por conta própria três regras, que podem virar princípios em `/speckit-constitution`:

| Regra adotada | Como o plano atende |
|---|---|
| O medidor é testado antes de medir | Testes de unidade para normalização, métricas, causa e comparação; SC-009 com 20 exemplos |
| Simplicidade | Sem framework de avaliação, sem banco de dados; 3 dependências novas, 2 delas já instaladas |
| Não mudar o que está sendo medido | `rag.py` reproduz o pipeline atual; teste de equivalência do contexto e do prompt |

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-eval-metrics/
├── plan.md              # Este arquivo
├── research.md          # Fase 0: decisões D1 a D16 e medições
├── data-model.md        # Fase 1: gabarito, avaliação, comparação
├── quickstart.md        # Fase 1: roteiro de validação
├── contracts/
│   ├── cli.md                  # Comandos da avaliação
│   ├── rag-interface.md        # Interface do assistente consultável
│   ├── gabarito.schema.json    # Esquema do gabarito
│   ├── gabarito.example.json   # Exemplo válido de gabarito
│   └── run.schema.json         # Esquema do resultado de uma execução
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; não criado por este comando)
```

### Source Code (repository root)

> Estrutura planejada na época. Depois da implementação, os scripts da raiz foram movidos para o pacote `assistant/` e os dados para `data/`; a estrutura atual está no `README.md` da raiz.

```text
create_db.py             # existente; parâmetros de divisão viram constantes nomeadas
main.py                  # existente; passa a ser só o chat interativo, usando rag.py
rag.py                   # NOVO: RagConfig, retrieve(), answer()
requirements.txt         # + pytest, rich, jsonschema
pytest.ini               # NOVO: caminhos de teste e marcador "integration"

evaluation/              # NOVO
├── __init__.py
├── __main__.py          # python -m evaluation
├── cli.py               # run, compare, baseline, list, kb-check, calibrate, validate
├── dataset.py           # carregar e validar o gabarito; recortes dev/holdout/smoke
├── normalize.py         # texto, dinheiro, duração, números por extenso
├── retrieval_metrics.py # hit, recall, MRR, precisão de contexto, evidência ancorada
├── answer_metrics.py    # fatos, fidelidade numérica, recusa, regras de atendimento
├── judge.py             # juiz local com saída estruturada
├── diagnose.py          # causa de cada erro
├── runner.py            # execução, repetições, execução incompleta
├── aggregate.py         # métricas agregadas e variação
├── history.py           # gravar, listar, referência
├── compare.py           # comparação entre execuções
├── report.py            # placar no terminal e report.md
├── kb_checks.py         # duplicados, âncora, texto corrompido, divergência
├── calibrate.py         # amostra para conferência humana e concordância
├── data/
│   ├── gabarito.json
│   └── human_labels.json     # gerado por "calibrate export"
└── runs/
    ├── baseline.json
    ├── <run_id>/run.json, report.md
    └── _incomplete/

tests/                   # NOVO
├── unit/
│   ├── test_normalize.py
│   ├── test_answer_metrics.py
│   ├── test_retrieval_metrics.py
│   ├── test_diagnose.py
│   ├── test_dataset.py
│   ├── test_aggregate.py
│   ├── test_compare.py
│   ├── test_history.py
│   └── test_kb_checks.py
├── integration/
│   └── test_rag_equivalence.py
└── fixtures/
    └── factual_examples.json  # 20 respostas com o veredito esperado (SC-009)
```

**Structure Decision**: Projeto único, mantendo os scripts na raiz como estão hoje (`create_db.py`, `main.py`). A avaliação fica em um pacote próprio, `evaluation/`, que só conhece o assistente pela interface de `rag.py`. O nome é `evaluation` e não `eval` para não confundir com a função embutida do Python. As execuções em `evaluation/runs/` são versionadas no git, porque o histórico é o produto da feature; `_incomplete/` entra no `.gitignore`.

## Ordem de implementação

Segue as prioridades da spec; cada etapa é utilizável sozinha.

| Etapa | História | Entrega | Requisitos |
|---|---|---|---|
| 0 | Base | `rag.py`, `main.py` reduzido, constantes em `create_db.py`, teste de equivalência, `pytest` configurado | FR-030 |
| 1 | P1 | `normalize`, `dataset`, `answer_metrics`, gabarito v1, `runner`, `report`, comandos `validate` e `run` | FR-001 a FR-004, FR-009, FR-011, FR-015, FR-018 a FR-020, FR-022 |
| 2 | P2 | `retrieval_metrics`, fidelidade numérica, `diagnose`, agrupamentos no placar | FR-006 a FR-008, FR-010, FR-016, FR-017 |
| 3 | P2 | `history`, `compare`, `baseline`, `list`, `--repeat`, recortes `--holdout` e `--smoke` | FR-005, FR-019, FR-021, FR-023 a FR-026 |
| 4 | P3 | `judge`, `calibrate`, regras de atendimento determinísticas | FR-012 a FR-014 |
| 5 | P3 | `kb_checks` e comando `kb-check` | FR-027 a FR-029 |

Ao fim da etapa 3 a avaliação de referência é rodada e marcada (SC-010).

## Riscos

| Risco | Efeito | Tratamento |
|---|---|---|
| O gabarito tem erro (fato ou evidência errados) | O placar acusa erro onde não há | Validação automática (evidência única no material, valor presente na evidência) e revisão do responsável antes da referência |
| O juiz local não concorda com a pessoa | Métricas de comportamento sem valor | Bloco separado no placar, conferência humana, critério marcado como não confiável abaixo de 80%, juiz trocável por variável de ambiente |
| O conversor de valores por extenso não cobre uma forma | Acerto contado como erro | 20 exemplos em teste (SC-009); alternativas em texto no gabarito; itens errados mostram a resposta completa para conferência |
| A extração para `rag.py` muda o comportamento | A referência mede outro assistente | Teste de equivalência do contexto e do prompt antes de rodar a referência |
| A avaliação usa temperatura 0 e o chat não | A nota não reflete exatamente o chat | Registrado em research D10; alinhar na primeira feature de melhoria |
| Ajustar o assistente até acertar o gabarito | Nota alta que não generaliza | Parte reservada (`holdout`) fora dos ajustes |

## Complexity Tracking

Sem violações a justificar: não há constituição ratificada e o desenho não introduz projeto, serviço ou camada além do pacote `evaluation/`.
