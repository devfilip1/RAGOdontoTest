# Research: Avaliação e Métricas do Assistente OdontoTest

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Date**: 2026-10-10

Decisões técnicas da Fase 0. Não sobrou nenhum NEEDS CLARIFICATION.

## Medições feitas neste computador

Medido em 2026-10-10 (Ryzen 9 8945HS, RTX 4060 Laptop 8 GB, 15 GB de RAM, Ollama 0.40.2, modelos 100% na GPU):

| Operação | Tempo |
|---|---|
| Resposta do `llama3` com 5 trechos de contexto, modelo já carregado | 1,6 s |
| Mesma resposta, modelo frio (primeira chamada) | 10,9 s |
| Chamada de juiz com saída JSON estruturada | 1,5 s |
| Embedding de uma pergunta, modelo frio | 4,6 s |

Com `temperature=0` e `seed=42`, três execuções seguidas da mesma pergunta devolveram texto idêntico.

Consequência para SC-002: com ~52 perguntas, uma resposta e até 5 chamadas de juiz por pergunta, a avaliação completa leva cerca de 8 minutos; sem juiz, cerca de 2 minutos. Os limites de 30 e 5 minutos da spec têm folga.

Na mesma medição o assistente respondeu que "o implante não é mencionado" tendo recebido só os 5 primeiros trechos, em que o implante não aparece. É o comportamento esperado para contexto sem a evidência, e é o tipo de caso que a separação entre falha de busca e falha de resposta precisa distinguir.

## D1. Harness próprio em vez de Ragas ou DeepEval

- **Decision**: Escrever um harness próprio e pequeno em Python, seguindo as definições padrão das métricas de RAG (hit rate@k, recall@k, MRR, precisão de contexto, correção factual, fidelidade, relevância, recusa).
- **Rationale**: A maior parte das métricas desta feature é determinística (comparar valores e prazos, procurar a evidência nos trechos) e não precisa de framework. Ragas e DeepEval foram desenhados em torno de um juiz forte (modelos pagos na nuvem) e dependem de o juiz devolver JSON longo e bem formado; com um modelo local de 8B isso falha com frequência e a nota vira ruído. Também trariam dezenas de dependências a um projeto que roda em Python 3.14, onde a compatibilidade delas não foi verificada. O gabarito tem ~50 itens e um único documento: transparência (ver exatamente por que um item falhou) vale mais do que cobertura de framework.
- **Alternatives considered**: Ragas com juiz local via LangChain (rejeitado pelos motivos acima); DeepEval (mesmo problema e ainda envia telemetria por padrão); só pytest com asserts por pergunta (rejeitado: dá passou/falhou, não placar nem histórico).

## D2. Correção factual por fatos tipados e normalizados

- **Decision**: Cada fato esperado do gabarito tem um tipo: `money`, `duration` ou `text`. Dinheiro e duração são extraídos da resposta e comparados pelo valor numérico (`R$ 1.500`, `1500 reais` e `mil e quinhentos reais` viram 1500). Fatos de texto são comparados por trecho normalizado (minúsculas, sem acento), com lista de alternativas. Um item está correto quando todos os fatos esperados estão presentes **e** a resposta não traz nenhum valor do mesmo tipo fora da lista de valores esperados ou permitidos.
- **Rationale**: Atende FR-009 e os casos de borda da spec: formatos equivalentes contam como acerto, e resposta com o valor certo junto de um valor de outro procedimento conta como erro. A segunda regra é a que pega o erro conhecido do clareamento sem depender de juiz. É determinístico, roda em milissegundos e é testável por unidade (SC-009).
- **Alternatives considered**: Similaridade semântica entre a resposta e uma resposta de referência (rejeitado: "R$ 120 a R$ 250" e "R$ 500 a R$ 1.500" são quase idênticos para um embedding); juiz LLM para correção (rejeitado como método principal: o juiz local erra justamente em números); comparação por string exata (rejeitado: quebra com qualquer variação de formato).
- **Nota**: O conversor de números por extenso cobre o intervalo que aparece no material (até dezenas de milhares). Fora disso, o gabarito pode listar alternativas em `text`.

- **Ajuste na implementação**: quando a pergunta é de um procedimento, todos os valores da resposta são conferidos (não só os do tipo perguntado), e são aceitos os fatos do mesmo procedimento presentes em outros itens do gabarito e os diferenciais da clínica. Sem isso, "o implante custa R$ 2.500 a R$ 6.000 e requer 2 a 3 consultas" passaria em uma pergunta de preço mesmo trazendo o prazo de outro procedimento, e "a limpeza custa R$ 120 a R$ 250 e leva 30 a 50 minutos" seria reprovada por citar um fato correto. Em perguntas sem procedimento, só os tipos perguntados são conferidos.

## D3. Evidência por trecho de texto, não por ID de chunk

- **Decision**: O gabarito guarda a evidência de cada pergunta como um ou mais trechos literais do material (ex.: `Investimento: R$ 500 a R$ 1.500`). Um chunk recuperado é relevante quando contém a evidência (comparação normalizada). A validação do gabarito exige que cada trecho de evidência apareça exatamente uma vez no texto completo do material.
- **Rationale**: As próximas features vão mudar a divisão do material. IDs de chunk e posições mudariam a cada ajuste e o gabarito teria de ser refeito; o texto do material não muda. A exigência de unicidade evita ambiguidade real do documento: "R$ 500 a R$ 1.500" é o preço do clareamento e também a entrada do aparelho, mas as linhas completas são diferentes.
- **Alternatives considered**: Gabarito por ID de chunk (rejeitado: frágil); por posição de caractere no documento (rejeitado: quebra se a extração ou o pré-processamento do texto mudar); juiz LLM decidindo relevância de cada chunk (rejeitado: lento e instável para algo que o texto resolve).

## D4. Evidência ancorada como métrica separada

- **Decision**: Além de "a evidência foi recuperada", medir "evidência ancorada": o chunk que contém a evidência também contém o nome do procedimento a que ela pertence (lista de âncoras por procedimento, ex.: `clareamento`). A mesma regra, aplicada a toda a base, é a verificação FR-028.
- **Rationale**: É a causa raiz do erro já conhecido. Hoje existe um chunk com o título "Clareamento Dental" e o preço da limpeza, e chunks com preço sem o nome do procedimento. A busca pode "acertar" o trecho e mesmo assim entregar ao modelo um contexto enganoso. Medir isso separado mostra o problema sem misturá-lo ao hit rate.
- **Alternatives considered**: Exigir âncora para o chunk contar como relevante (rejeitado: zeraria o recall em vários itens e esconderia a diferença entre "não achou" e "achou sem contexto").

## D5. Métricas de busca por fonte

- **Decision**: Calcular hit@k, recall@k, MRR e precisão de contexto para três listas: busca vetorial, busca lexical (BM25) e o conjunto combinado enviado ao modelo. `k` é o número de trechos que cada busca devolve na configuração avaliada.
- **Rationale**: FR-008. O assistente junta duas buscas sem reordenar; sem medir cada uma não dá para saber qual contribui e qual só adiciona ruído.
- **Definições**:
  - **hit@k**: 1 se ao menos um trecho de evidência está nos k recuperados.
  - **recall@k**: fração dos trechos de evidência do item encontrados nos k recuperados (importa em perguntas de comparação, com mais de uma evidência).
  - **MRR**: 1 / posição do primeiro chunk relevante (0 se nenhum).
  - **precisão de contexto**: fração dos chunks recuperados que contêm alguma evidência do item.
  - Perguntas sem resposta no material ficam fora das métricas de busca.

## D6. Fidelidade em duas camadas

- **Decision**: Camada determinística: todo valor de dinheiro ou duração na resposta precisa aparecer em algum trecho recuperado; se não aparece, é "informação inventada". Camada de juiz (opcional, P3): para afirmações não numéricas, o juiz responde se a resposta afirma algo que o contexto não sustenta.
- **Rationale**: FR-010. Neste domínio os erros que custam caro são números (preço, prazo). A camada determinística cobre isso com 100% de repetibilidade. A camada de juiz fica separada no placar para não contaminar a nota confiável.
- **Alternatives considered**: Decomposição em afirmações atômicas + verificação por NLI, como no Ragas (rejeitado: depende de juiz forte).

## D7. Recusa correta por padrão de texto

- **Decision**: Considerar que o assistente recusou quando a resposta normalizada contém a frase mandada pelas instruções de atendimento ("não encontrei essa informação") ou um dos padrões equivalentes de uma lista curta e configurável. Em perguntas sem resposta, também se exige que a resposta não traga dinheiro nem duração.
- **Rationale**: FR-011. O prompt já define uma frase fixa de recusa; detectar por padrão é exato e barato. A lista de padrões fica em um só lugar para ser ajustada quando o prompt mudar.
- **Métricas**: taxa de recusa correta (perguntas sem resposta em que recusou) e taxa de recusa indevida (perguntas com resposta em que recusou).

## D8. Juiz local, binário, com saída estruturada

- **Decision**: Para relevância, tom, condução para o agendamento e objetividade, usar um modelo local via Ollama com `temperature=0`, `seed` fixo e saída JSON com esquema (`veredito` booleano + `motivo`). Uma chamada por critério, com rubrica de uma frase e exemplos. O modelo do juiz é configurável por `OLLAMA_JUDGE_MODEL`; o padrão é o mesmo modelo de chat.
- **Rationale**: Atende a suposição "tudo local" da spec. Perguntas binárias com esquema são o formato em que modelos pequenos erram menos; a medição acima mostrou 1,5 s por chamada com JSON válido. As notas de juiz ficam em um bloco próprio do placar, nunca entram no "acertou/errou" do item, e são conferidas contra a avaliação humana (FR-014, SC-007). Se a concordância ficar abaixo de 80% em um critério, o placar marca esse critério como não confiável.
- **Alternatives considered**: Notas de 1 a 5 (rejeitado: pouco repetíveis em modelos pequenos); juiz na nuvem (rejeitado pela suposição de tudo local; pode ser revisto pelo responsável); o mesmo modelo julgar sem conferência humana (rejeitado: viés de autoavaliação sem controle).
- **Risco conhecido**: o juiz padrão é o mesmo modelo que responde. Mitigação: conferência humana e possibilidade de trocar o juiz por variável de ambiente.

## D9. Regras de atendimento determinísticas

- **Decision**: Conferir por texto as regras que têm resposta objetiva: não mencionar "contexto", "documento" ou "base de dados"; responder em português; tamanho máximo da resposta.
- **Rationale**: FR-013 e cenário 2 da História 4. Não precisam de juiz, então entram no resultado "acertou/errou" do item como causa "violação de regra de atendimento".

## D10. Repetibilidade

- **Decision**: A avaliação chama o assistente com `temperature=0` e `seed=42`, valores que ficam gravados na configuração da execução. `run --repeat N` roda N vezes e grava, por métrica, a média e a diferença entre o maior e o menor valor.
- **Rationale**: FR-021 e SC-005. A medição mostrou saída idêntica com esses parâmetros. O chat interativo continua com o comportamento atual (FR-030); a temperatura passa a ser um campo da configuração, com o valor atual como padrão fora da avaliação.
- **Ajuste na implementação**: antes de medir, a avaliação faz uma pergunta de aquecimento que não entra no resultado, para a carga dos modelos não contar como tempo de resposta. O juiz só avalia a primeira repetição de `--repeat`.
- **Limite conhecido**: a avaliação mede o assistente com temperatura 0, que não é a do chat interativo hoje. Alinhar os dois é uma decisão para a primeira feature de melhoria.

## D11. Assistente consultável (FR-030)

- **Decision**: Extrair de `main.py` um módulo `rag.py` com `RagConfig`, `retrieve(question, config)` e `answer(question, config)`. `main.py` passa a ser só o laço de conversa, protegido por `if __name__ == "__main__"`. Os parâmetros de divisão em `create_db.py` viram constantes nomeadas para entrarem no registro da configuração.
- **Rationale**: Hoje a busca e a resposta estão dentro do `while` de `to_ask()`, que roda na importação. Sem a extração, a avaliação teria de copiar o pipeline, e mediria uma cópia. O prompt, os valores de `k`, a ordem de fusão e o modelo ficam exatamente como estão.
- **Alternatives considered**: Avaliar pelo terminal, alimentando `stdin` (rejeitado: não dá acesso aos trechos recuperados); duplicar o pipeline dentro da avaliação (rejeitado: as duas cópias divergem).

## D12. Histórico em arquivos JSON

- **Decision**: Cada execução concluída grava uma pasta `evaluation/runs/<data-hora>[-<rótulo>]/` com `run.json` (tudo) e `report.md` (placar legível). `evaluation/runs/baseline.json` aponta para a execução de referência. Execuções incompletas vão para `evaluation/runs/_incomplete/` e não entram em listagens nem comparações.
- **Rationale**: FR-022 a FR-026. Um usuário, um computador, dezenas de execuções: arquivos são suficientes, legíveis e versionáveis no git. A configuração gravada inclui parâmetros de divisão, valores de `k`, modelos, temperatura, `seed`, hash do prompt, hash da base de conhecimento, hash do gabarito e commit do git.
- **Alternatives considered**: SQLite (rejeitado: não há consulta que justifique); MLflow ou similar (rejeitado: infraestrutura demais para o tamanho do problema).

## D13. Parte reservada e avaliação reduzida

- **Decision**: Cada item do gabarito tem `split` (`dev` ou `holdout`) e `smoke` (booleano). `run` usa só `dev`; `run --holdout` usa só a parte reservada e grava o resultado marcado como tal; `run --smoke` usa os ~10 itens marcados, um por tipo de pergunta. Cerca de 25% dos itens ficam em `holdout`, distribuídos por tipo e procedimento.
- **Rationale**: FR-005 e FR-019. Com um material pequeno é fácil ajustar o assistente para acertar exatamente as perguntas que se vê. A parte reservada é a conferência de que a melhoria generaliza. Comparações só são feitas entre execuções do mesmo recorte.

## D14. Classificação da causa

- **Decision**: Regra fixa, uma causa principal por item errado, na ordem:

  | Situação | Causa |
  |---|---|
  | Pergunta sem resposta no material e o assistente respondeu | informação inventada |
  | Pergunta com resposta e a evidência não foi recuperada | falha de busca |
  | Evidência recuperada e o assistente recusou | recusa indevida |
  | Evidência recuperada e a resposta tem valor que não está em nenhum trecho recuperado | informação inventada |
  | Evidência recuperada e fatos errados ou faltando | falha de resposta |
  | Fatos certos, regra de atendimento violada | violação de regra de atendimento |

  Sinais secundários (ex.: evidência recuperada mas não ancorada; valor de outro procedimento presente) são gravados junto.
- **Rationale**: FR-016 e SC-004. Uma regra fixa garante 100% de itens classificados e é testável por unidade.

## D15. Verificações da base de conhecimento

- **Decision**: `kb-check` lê a base vetorial e o arquivo de trechos usado pela busca lexical e verifica: trechos duplicados (FR-027); fato do gabarito sem nenhum chunk ancorado (FR-028); caracteres corrompidos, como `■` e U+FFFD (FR-029); e divergência entre as duas fontes (quantidade e conteúdo).
- **Rationale**: Os três primeiros são requisitos. O quarto foi acrescentado porque a busca vetorial e a lexical leem de lugares diferentes e já ficaram dessincronizadas neste projeto (55 documentos na base vetorial para 11 trechos no arquivo). Não usa modelo, então roda em segundos (SC-008).

## D16. Testes de unidade e dependências

- **Decision**: `pytest` para as partes determinísticas (normalização, métricas, classificação de causa, validação do gabarito, comparação, verificações da base), sem depender do Ollama. Acrescentar `pytest` e `rich` a `requirements.txt` (`rich` já está instalado como dependência indireta e é usado para o placar no terminal).
- **Rationale**: O medidor precisa ser mais confiável do que o que ele mede. Um erro na normalização de valores falsificaria todo o placar. SC-009 é atendido por um arquivo de 20 respostas de exemplo com o veredito esperado.
