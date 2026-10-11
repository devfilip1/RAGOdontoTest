# Research: Bancada de Experimentos de Busca

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-10

Decisões técnicas da Fase 0. Não sobrou nenhum NEEDS CLARIFICATION.

## Medições feitas neste computador

Medido em 2026-10-10 com o índice atual (11 trechos, `nomic-embed-text`) e as 38 perguntas com resposta do conjunto de trabalho:

| Medida | Valor |
|---|---|
| Embedding da pergunta mais busca vetorial | cerca de 55 ms |
| Similaridade (cosseno) do melhor trecho | mínimo 0,54, mediana 0,70, máximo 0,80 |
| Similaridade do 4º trecho | mínimo 0,49, mediana 0,64, máximo 0,71 |
| Similaridade do melhor trecho em perguntas **fora** do material | 0,62 a 0,68 |
| "Relevance score" devolvido hoje pelo Chroma para o melhor trecho | mínimo 0,35, mediana 0,58, máximo 0,72 |
| Geração de uma resposta hipotética (HyDE) com o `llama3`, até 80 tokens | 1,07 s em média |

Os embeddings armazenados têm norma 1 e a coleção usa distância L2.

Três consequências:

1. **A bancada cabe com folga em SC-002.** Três experimentos sobre 38 perguntas levam alguns segundos de busca, mais a carga dos modelos.
2. **O threshold tem pouca margem com este modelo de embedding.** Perguntas fora do material chegam a 0,62–0,68 de similaridade, dentro da faixa das perguntas com resposta (0,54–0,80). Um threshold de 0,7, como no projeto de referência, cortaria o trecho certo em cerca de metade das perguntas. A feature entrega o threshold como opção e a tabela para medir; não se espera que ele seja adotado com o `nomic-embed-text`.
3. **O HyDE dobra o tempo de resposta.** A resposta do assistente leva cerca de 1,0 s; a geração hipotética acrescenta 1,07 s. A coluna de tempo da tabela vai mostrar isso (SC-008).

## D1. YAML para estratégias e experimentos

- **Decision**: `config/strategies.yaml` e `config/experiments.yaml`, lidos com PyYAML (`yaml.safe_load`) e validados com JSON Schema (`jsonschema`, já usado no projeto) mais conferências cruzadas em código. Acrescentar `PyYAML==6.0.3` a `requirements.txt`.
- **Rationale**: Pedido do responsável e mesmo formato do projeto de referência. YAML aceita comentários, o que ajuda em arquivos editados à mão. O PyYAML já está instalado como dependência indireta, então é só declarar. Reaproveitar `jsonschema` mantém um único jeito de validar arquivos no projeto (o gabarito já é validado assim).
- **Alternatives considered**: TOML (rejeitado: listas de objetos ficam verbosas e não foi o pedido); JSON (rejeitado: sem comentários); validar só em código (rejeitado: o esquema documenta o formato e serve de contrato).

## D2. Um módulo de configuração no assistente

- **Decision**: Novo `assistant/settings.py` com as dataclasses `Strategy` e `Experiment`, o carregamento dos dois arquivos, a validação e `assistant_experiment()`. `assistant/config.py` fica só com o que não é parâmetro de experimento: caminhos, modelos, temperatura, limite de resposta, `STOPWORDS`, `QUERY_SYNONYMS` e `TEXT_FIXES`. Saem de `config.py`: `CHUNK_SIZE`, `CHUNK_OVERLAP`, `VECTOR_K`, `BM25_K`, `FINAL_K`, `PATH_DB` e `CHUNKS_PATH`.
- **Rationale**: FR-031 pede um único lugar para a estratégia e os parâmetros de busca do assistente. Manter as constantes antigas ao lado do YAML criaria duas fontes. FR-034 mantém prompt e sinônimos no código.
- **Alternatives considered**: Deixar `config.py` com valores padrão que o YAML sobrescreve (rejeitado: duas fontes, e o leitor não sabe qual vale).

## D3. Um diretório de índice por estratégia, com manifesto

- **Decision**: Cada estratégia grava em `data/index/<nome>/`: `chroma/` (banco vetorial), `chunks.json` (trechos, para a busca por palavras) e `manifest.json`. O manifesto guarda o hash da definição da estratégia, o hash do PDF, o modelo de embedding, a quantidade de trechos e a data. Um índice está desatualizado quando qualquer um dos três primeiros difere do atual.
- **Rationale**: FR-004 (índices convivem) e FR-007 (avisar índice desatualizado). Diretórios separados tornam impossível um índice sobrescrever outro. O manifesto permite detectar o erro mais provável com vários índices: mudar o YAML ou o PDF e esquecer de recriar.
- **Alternatives considered**: Várias coleções no mesmo banco Chroma (rejeitado: o `chunks.json` precisaria de separação de qualquer forma, e apagar uma estratégia exigiria operar dentro do banco); sem manifesto (rejeitado: a tabela mostraria números de uma divisão que não é a declarada, sem aviso).
- **Migração**: o índice atual está em `data/index/chroma` e `data/index/chunks.json`. Ele é recriado como `data/index/section/` e os arquivos antigos são apagados. O diretório já está fora do git.

## D4. Tipos de estratégia

- **Decision**: Três tipos, registrados em um dicionário `tipo -> função` em `assistant/ingest.py`:

  | Tipo | Parâmetros | Resultado |
  |---|---|---|
  | `section` | `max_chars` (padrão 1200), `overlap` (padrão 100) | Um trecho por seção; seção maior que `max_chars` é subdividida com o título repetido. É o código atual |
  | `split` | `chunk_size`, `chunk_overlap` (obrigatórios) | Divisão recursiva por caracteres do texto inteiro |
  | `page` | nenhum | Um trecho por página |

  Todos os tipos recebem o mesmo texto limpo: marcadores de lista convertidos em `- item` e as correções de `TEXT_FIXES` aplicadas.
- **Rationale**: FR-002 e FR-006. Com o registro, uma estratégia nova de um tipo existente é só uma entrada no YAML; um tipo novo é uma função e uma linha no registro. A limpeza do texto fica fora das estratégias porque é correção da extração do PDF, não escolha de divisão, e sem ela a comparação misturaria dois efeitos.
- **Nota**: `recursive_500_200` reproduz a abordagem original do projeto (500/200), mas não é idêntica byte a byte ao índice antigo: aquele dividia cada página separadamente e mantinha os marcadores de lista como caractere de controle.
- **Alternatives considered**: Divisão semântica e por tokens (fora do escopo, por decisão do responsável).

## D5. Como os campos do experimento viram parâmetros de busca

- **Decision**:

  | Campo | Efeito |
  |---|---|
  | `collection` | Nome da estratégia cujo índice é usado |
  | `search_type: hybrid` | Busca vetorial e por palavras; cada uma contribui com `ceil(match_count / 2)` trechos; a fusão (RRF) devolve até `match_count` |
  | `search_type: vector` | Só a vetorial, com `match_count` trechos |
  | `search_type: bm25` | Só a busca por palavras, com `match_count` trechos |
  | `match_threshold` | Trechos com similaridade abaixo do valor são descartados depois da fusão; 0 desliga |
  | `use_hyde` | A busca vetorial usa uma resposta hipotética no lugar da pergunta |

- **Rationale**: Com `match_count: 4` e `hybrid`, o resultado é exatamente o de hoje (2 + 2, até 4), o que atende FR-032 sem caso especial. Os nomes dos campos são os do projeto de referência, como pedido.
- **Alternatives considered**: Expor `vector_k`, `bm25_k` e `final_k` no YAML (rejeitado: três números para o que o projeto de referência resolve com um, e combinações sem sentido passam a ser possíveis).

## D6. Similaridade como cosseno, calculada no pipeline

- **Decision**: O pipeline calcula o embedding da busca uma vez, usa esse vetor na busca vetorial do Chroma e calcula a similaridade de cosseno entre ele e cada trecho devolvido, a partir dos embeddings do índice mantidos em memória. Cada `RetrievedChunk` ganha o campo `similarity`.
- **Rationale**: FR-024 exige o Score calculado da mesma forma para qualquer tipo de busca, e a busca por palavras não produz nota de 0 a 1. O "relevance score" do Chroma vem de uma conversão da distância L2 que dá valores entre 0,35 e 0,72 para os melhores trechos, menos legível que o cosseno (0,54 a 0,80) e incomparável com o threshold de 0,7 do projeto de referência. Como os embeddings já têm norma 1, o cosseno é um produto interno. Manter os vetores em memória custa 768 números por trecho, o que é irrelevante para este material e aceitável até dezenas de milhares de trechos.
- **Alternatives considered**: Usar o relevance score do Chroma (rejeitado pelos motivos acima); consultar o Chroma de novo para os trechos que só a busca por palavras achou (rejeitado: uma consulta a mais por pergunta); recriar a coleção com espaço de cosseno (rejeitado: resolve a escala, mas não dá nota aos trechos achados só por palavras).

## D7. Definição das métricas da tabela

- **Decision**:
  - **Acertou** (por pergunta): todas as evidências do item estão entre os trechos devolvidos. Em perguntas de comparação, com duas evidências, as duas precisam vir.
  - **True Rate**: acertos sobre o total de perguntas avaliadas, mostrado como fração (`37/38`).
  - **Nota** (por pergunta): média da `similarity` dos trechos devolvidos; 0 quando nenhum trecho é devolvido.
  - **Score**: média das notas das perguntas.
  - **Evidência ancorada**: fração das perguntas em que o trecho com a evidência também tem o nome do procedimento, pela função já existente em `evaluation/retrieval_metrics.py`.
  - **Tempo**: média do tempo de `retrieve()` por pergunta, depois de uma chamada de aquecimento que não conta.
  - **Ordenação**: True Rate decrescente, depois Score decrescente, depois nome. No empate de True Rate, experimentos com HyDE ficam depois dos sem (ajuste na implementação: medido, o HyDE levou o Score de 0,67 para 0,78 com o mesmo True Rate, e ficaria em primeiro por uma nota que não é comparável).
- **Rationale**: FR-019 e FR-023 a FR-026. As definições de Score e True Rate foram inferidas da saída do projeto de referência; aqui o True Rate é ancorado no gabarito, que é mais forte do que uma nota de similaridade acima de um limite. Exigir todas as evidências evita contar como acerto uma comparação que trouxe só um dos dois tratamentos.
- **Limite conhecido**: com HyDE, a similaridade é medida contra a resposta hipotética e tende a ser mais alta, porque um texto de resposta se parece mais com o material do que uma pergunta. O Score de um experimento com HyDE não deve ser comparado com o de um sem. A documentação registra isso junto com a ressalva do modelo de embedding (FR-027).

## D8. HyDE

- **Decision**: Com `use_hyde: true`, o pipeline pede ao modelo de chat uma resposta hipotética curta (até 80 tokens, temperatura 0) e usa o texto dela na busca vetorial. A busca por palavras continua usando a pergunta original. O tempo da geração entra no tempo da busca.
- **Rationale**: FR-029 e FR-026. É a forma usual do HyDE: a resposta hipotética serve para aproximar o vetor de busca do estilo dos documentos. Usá-la também na busca por palavras traria termos inventados para o casamento exato, que é justamente onde a busca por palavras é confiável.
- **Alternatives considered**: Não implementar e omitir a coluna (rejeitado pelo responsável: a tabela deve ter as colunas do projeto de referência, e a coluna só pode existir se a opção funcionar).

## D9. `RagConfig` construído a partir do experimento

- **Decision**: `RagConfig` passa a ter `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde` no lugar de `vector_k`, `bm25_k` e `final_k`, que viram propriedades calculadas (D5). `RagConfig()` sem argumentos usa o experimento indicado em `assistant:` no YAML. `RagConfig.from_experiment(nome)` monta a configuração de qualquer experimento. Os recursos em cache (banco, BM25, embeddings) passam a ser por estratégia.
- **Rationale**: FR-031 a FR-033. O chat, a avaliação da resposta e a bancada usam o mesmo objeto e o mesmo `retrieve()`, então a bancada mede exatamente a busca que o assistente faz.
- **Efeito na avaliação existente**: `python -m evaluation run` perde as opções `--vector-k`, `--bm25-k` e `--final-k` e ganha `--experiment NOME`, que roda a avaliação da resposta com outro experimento sem editar o YAML. O registro de cada execução ganha `experiment`, `strategy`, `search_type`, `match_count`, `match_threshold` e `use_hyde`.

## D10. Comando `experiments` e arquivos de resultado

- **Decision**: Novo `evaluation/experiments.py` com a execução e as métricas, e o comando `python -m evaluation experiments [NOMES...] [--verbose]`. Para cada execução são gravados dois arquivos em `evaluation/runs/experiments/`: `<data-hora>-summary.csv` (a tabela) e `<data-hora>-questions.csv` (uma linha por experimento e pergunta). `evaluation/retrieval_only.py` é absorvido pelo módulo novo, e o comando `retrieval` passa a aceitar `--experiment`.
- **Rationale**: FR-014 a FR-021. O resumo é o que o responsável pediu; o arquivo por pergunta é o que permite ver quais perguntas cada experimento erra, que é a informação necessária para agir sobre a tabela. Nome com data e hora atende "sem sobrescrever" (FR-020). Um experimento não executado ou incompleto aparece no resumo com `status` e `reason`, e não tem linhas no arquivo de perguntas além das concluídas.
- **Alternatives considered**: Um CSV só, com a tabela (rejeitado: não mostra onde cada experimento erra); JSON como nas execuções da avaliação (rejeitado: o pedido foi CSV, que abre direto em planilha).

## D11. Atalhos

- **Decision**: `Makefile` e `run.ps1` na raiz, com os mesmos nomes: `help`, `install`, `ingest`, `chat`, `test`, `test-integration`, `eval`, `eval-smoke`, `eval-full`, `experiments`, `retrieval`, `kb-check`, `validate`, `compare`, `baseline`. Os dois usam o Python de `.venv` diretamente, então funcionam sem ativar o ambiente. Argumentos extras são repassados: `.\run.ps1 eval --label x` e `make eval ARGS="--label x"`. Um teste de unidade confere que os dois arquivos declaram os mesmos nomes.
- **Rationale**: FR-035 a FR-037. O `make` não está instalado na máquina, então o `run.ps1` é o caminho que funciona hoje; o Makefile atende ao pedido e a quem tiver `make`. A tabela nome → comando existe nos dois arquivos, o que é duplicação de uma lista de 15 linhas e não de lógica; o teste de paridade impede que divirjam.
- **Alternatives considered**: O Makefile chamar o `run.ps1` (rejeitado: o Makefile deixaria de funcionar fora do Windows); um módulo Python de tarefas chamado pelos dois (rejeitado: uma camada a mais para apelidar comandos).
- **Nota**: o `run.ps1` depende de a política de execução do PowerShell permitir scripts locais, o que já é o caso nesta máquina, porque o `Activate.ps1` do ambiente virtual é usado.

## D12. Verificação da base por estratégia

- **Decision**: `python -m evaluation kb-check` ganha `--strategy NOME`; sem a opção, verifica a estratégia do experimento do assistente. A verificação também informa se o índice está desatualizado.
- **Rationale**: Cenário 4 da História 2. A verificação já existe; só precisa saber qual índice ler.

## D13. Testes

- **Decision**: Testes de unidade sem Ollama para: carga e validação dos YAML (um caso por erro de FR-012), os três tipos de divisão, o manifesto e a detecção de índice desatualizado, os tipos de busca, o threshold e o HyDE (com índice e modelo falsos), as métricas, a ordenação e os CSV da bancada, e a paridade dos atalhos. Os testes existentes que usam as constantes removidas são adaptados. Os testes de integração continuam conferindo o assistente de verdade.
- **Rationale**: Padrão do projeto e pedido do responsável. A prova de SC-001 não é teste de unidade: é a avaliação da resposta final comparada com a referência.
