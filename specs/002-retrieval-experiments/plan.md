# Implementation Plan: Bancada de Experimentos de Busca

**Branch**: `002-retrieval-experiments` (pasta da feature; o trabalho está na branch `main`, nenhuma branch foi criada) | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-retrieval-experiments/spec.md`

## Summary

Declarar as estratégias de divisão e os experimentos de busca em dois arquivos YAML, criar um índice por estratégia, e acrescentar um comando que roda todos os experimentos sobre o gabarito e mostra uma tabela comparativa com Score, True Rate, evidência ancorada e tempo. O arquivo de experimentos passa a indicar qual experimento o assistente usa, e esse vira o único lugar em que a estratégia e os parâmetros de busca são definidos. Threshold e HyDE entram como opções reais da busca, desligadas por padrão. Um `Makefile` e um `run.ps1` apelidam os comandos do projeto.

Abordagem (detalhes em [research.md](./research.md)):

- `assistant/settings.py` carrega e valida os YAML; `RagConfig` é montado a partir de um experimento, e o chat, a avaliação da resposta e a bancada usam o mesmo `retrieve()`.
- Um diretório por estratégia em `data/index/<nome>/`, com um manifesto que permite detectar índice desatualizado.
- A similaridade passa a ser o cosseno calculado no pipeline, igual para qualquer tipo de busca, o que dá base comum ao Score e ao threshold.
- A bancada reaproveita as métricas de `evaluation/retrieval_metrics.py` e grava dois CSV por execução.

## Technical Context

**Language/Version**: Python 3.14.8 (ambiente virtual `.venv`)

**Primary Dependencies**: já no projeto: `langchain-chroma`, `langchain-ollama`, `langchain-text-splitters`, `rank-bm25`, `pypdf`, `jsonschema`, `rich`, `numpy` (dependência do Chroma). A declarar em `requirements.txt`: `PyYAML==6.0.3`, já instalado como dependência indireta

**Storage**: arquivos. Configuração em `config/*.yaml`; um índice por estratégia em `data/index/<nome>/` (Chroma, `chunks.json`, `manifest.json`), fora do git; resultados da bancada em CSV em `evaluation/runs/experiments/`, versionados

**Testing**: `pytest`. Testes de unidade sem Ollama para tudo que é determinístico (validação dos YAML, divisão, manifesto, tipos de busca, threshold, HyDE com modelo falso, métricas, ordenação, CSV, paridade dos atalhos). Testes de integração para o assistente de verdade. A prova de que o assistente não mudou é a avaliação da resposta comparada com a referência

**Target Platform**: computador do responsável: Windows 11, PowerShell, Ollama local, RTX 4060 Laptop 8 GB

**Project Type**: ferramenta de linha de comando sobre um projeto Python em pacotes (`assistant/`, `evaluation/`)

**Performance Goals**: os três experimentos iniciais em menos de 1 minuto (SC-002). Medido: cerca de 55 ms por pergunta para embedding e busca, 38 perguntas por experimento. O assistente mantém o tempo de resposta atual (cerca de 1,0 s) com o experimento padrão

**Constraints**: tudo local; o assistente não pode mudar de comportamento com o experimento padrão (FR-032, SC-001); prompt e sinônimos continuam no código (FR-034); a parte reservada do gabarito não é usada pela bancada (FR-022)

**Scale/Scope**: 1 usuário; 1 documento de 3 páginas; 3 estratégias e 3 experimentos iniciais, com espaço para dezenas; 38 perguntas por experimento

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` ainda é o modelo sem preencher: não há princípios ratificados, portanto não há portões a avaliar. **Resultado: passa (sem portões), antes da Fase 0 e depois da Fase 1.**

O plano mantém as três regras adotadas na feature 001:

| Regra adotada | Como o plano atende |
|---|---|
| O medidor é testado antes de medir | Testes de unidade para as métricas, a ordenação e os CSV da bancada |
| Simplicidade | Uma dependência declarada (já instalada); sem serviço nem banco novos; atalhos sem camada intermediária |
| Não mudar o que está sendo medido | O experimento padrão reproduz a busca atual; SC-001 exige a mesma nota e nenhuma pergunta mudando de resultado |

## Project Structure

### Documentation (this feature)

```text
specs/002-retrieval-experiments/
├── plan.md              # Este arquivo
├── research.md          # Fase 0: medições e decisões D1 a D13
├── data-model.md        # Fase 1: estratégias, experimentos, índice, resultados
├── quickstart.md        # Fase 1: roteiro de validação
├── contracts/
│   ├── cli.md                     # Comandos novos e alterados
│   ├── shortcuts.md               # Atalhos do Makefile e do run.ps1
│   ├── results-csv.md             # Formato dos dois CSV e da linha por pergunta
│   ├── strategies.schema.json     # Esquema de config/strategies.yaml
│   ├── experiments.schema.json    # Esquema de config/experiments.yaml
│   ├── strategies.example.yaml    # Conteúdo inicial de config/strategies.yaml
│   └── experiments.example.yaml   # Conteúdo inicial de config/experiments.yaml
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; não criado por este comando)
```

### Source Code (repository root)

```text
config/                         # NOVO
├── strategies.yaml             # estratégias de divisão
├── experiments.yaml            # experimentos e o experimento do assistente
└── schemas/
    ├── strategies.schema.json
    └── experiments.schema.json

assistant/
├── config.py                   # ALTERADO: saem os parâmetros de divisão e de busca e os caminhos do índice
├── settings.py                 # NOVO: Strategy, Experiment, carga e validação dos YAML, experimento do assistente
├── index.py                    # NOVO: caminhos por estratégia, manifesto, estado do índice
├── ingest.py                   # ALTERADO: tipos de divisão (section, split, page), um índice por estratégia
├── pipeline.py                 # ALTERADO: RagConfig por experimento, tipos de busca, similaridade, threshold, HyDE
└── chat.py                     # ALTERADO: recusa iniciar com índice ausente ou desatualizado

evaluation/
├── experiments.py              # NOVO: execução da bancada, métricas, ordenação, CSV (absorve retrieval_only.py)
├── retrieval_only.py           # REMOVIDO
├── cli.py                      # ALTERADO: comando experiments; --experiment em run e retrieval; --strategy em kb-check
├── report.py                   # ALTERADO: tabela comparativa; experimento e estratégia no placar
├── history.py                  # ALTERADO: registro do experimento na execução
├── kb_checks.py                # ALTERADO: índice por estratégia
├── schemas/run.schema.json     # ALTERADO: campos do experimento; chunk_size e chunk_overlap aceitam null
└── runs/experiments/           # NOVO: CSV da bancada

tests/
├── unit/
│   ├── test_settings.py        # NOVO: validação dos YAML
│   ├── test_index.py           # NOVO: manifesto e estado do índice
│   ├── test_experiments.py     # NOVO: métricas, ordenação, CSV, experimentos não executados
│   ├── test_shortcuts.py       # NOVO: paridade entre Makefile e run.ps1
│   ├── test_ingest.py          # ALTERADO: os três tipos de divisão
│   └── test_pipeline.py        # ALTERADO: tipos de busca, threshold, HyDE, similaridade
└── integration/test_assistant.py   # ALTERADO: índice por estratégia

Makefile                        # NOVO
run.ps1                         # NOVO
requirements.txt                # + PyYAML
README.md, evaluation/README.md, docs/guia-do-projeto.html   # atualizados
```

**Structure Decision**: Mantém a estrutura atual (`assistant/`, `evaluation/`, `tests/`, `data/`) e acrescenta `config/` na raiz para os dois YAML e os seus esquemas. A configuração fica fora de `assistant/` porque é editada pelo responsável e lida tanto pelo assistente quanto pela avaliação. A lógica de índice ganha um módulo próprio (`assistant/index.py`) porque é usada pela ingestão, pelo pipeline, pela bancada e pela verificação da base.

## Ordem de implementação

Segue as prioridades da spec. As histórias P1 dependem uma da outra na ordem inversa da spec: os índices por estratégia (História 2) vêm antes da tabela (História 1).

| Etapa | História | Entrega | Requisitos | Conferência |
|---|---|---|---|---|
| 0 | Base | `PyYAML` em `requirements.txt`; `config/` com os YAML e os esquemas; `assistant/settings.py` com carga e validação | FR-001, FR-008 a FR-013 | Testes de unidade, um por erro de configuração |
| 1 | US2 (P1) | `assistant/index.py`; tipos de divisão; `ingest` por estratégia; `kb-check --strategy` | FR-002 a FR-007 | `kb-check` nos três índices |
| 2 | US3 (P2) | `RagConfig` por experimento; pipeline lendo o índice da estratégia; registro do experimento em `run.json`; `run --experiment` | FR-031 a FR-034 | Avaliação da resposta em 97,8%, sem pergunta mudando de resultado |
| 3 | US1 (P1) | Similaridade no pipeline; `evaluation/experiments.py`; comando `experiments`; tabela e CSV | FR-014 a FR-027 | Rodar os três experimentos em menos de 1 minuto |
| 4 | US4 (P3) | Tipos de busca `vector` e `bm25`; threshold; HyDE | FR-028 a FR-030 | Experimentos de teste na tabela; tempo do HyDE visível |
| 5 | US5 (P3) | `Makefile`, `run.ps1`, teste de paridade | FR-035 a FR-037 | Cada atalho no `run.ps1` |
| 6 | Fechamento | README, guia e roteiro do `quickstart.md` | FR-027 | Quickstart completo |

A etapa 2 vem antes da etapa 3 porque a bancada usa o mesmo `RagConfig` do assistente; fazer a tabela primeiro exigiria uma segunda forma de configurar a busca.

## Riscos

| Risco | Efeito | Tratamento |
|---|---|---|
| A troca de `vector_k`/`bm25_k`/`final_k` por `match_count` muda a busca do assistente | A nota cai sem intenção | `match_count: 4` com `hybrid` reproduz 2 + 2 até 4 (research D5); SC-001 confere com a referência |
| Usar o vetor da pergunta direto no Chroma muda a ordem da busca vetorial | Resultados diferentes dos atuais | O vetor é o mesmo que o Chroma calcularia; um teste de integração compara a ordem com a busca por texto |
| O threshold não tem margem com o `nomic-embed-text` | A opção existe e não é útil hoje | Registrado em research; a tabela mostra o efeito; adoção é decisão do responsável |
| Índice desatualizado passa despercebido | Tabela com números de outra divisão | Manifesto e recusa de execução (FR-007) |
| O Score é lido como acerto | Escolha da estratégia errada | Ordenação por True Rate; nota abaixo da tabela; ressalva na documentação (FR-027) |
| `Makefile` e `run.ps1` divergem | Atalho que existe em um e não no outro | Teste de paridade dos nomes |
| O `make` não pode ser testado nesta máquina | Makefile com erro não percebido | Instalar com `winget` durante a validação, ou registrar no quickstart que só a paridade foi conferida |
| A estratégia `section` não é a melhor na tabela | Expectativa de SC-003 não se confirma | É um resultado válido: registrar como achado, sem ajustar a bancada |

## Complexity Tracking

Sem violações a justificar: não há constituição ratificada, e o desenho acrescenta dois módulos ao assistente, um à avaliação e uma pasta de configuração, sem projeto, serviço ou camada novos.
