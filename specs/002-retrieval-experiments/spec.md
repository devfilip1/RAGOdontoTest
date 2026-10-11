# Feature Specification: Bancada de Experimentos de Busca

**Feature Branch**: `002-retrieval-experiments`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Bancada de experimentos de busca para o assistente OdontoTest. Declarar estratégias de divisão do material e experimentos de busca em arquivos de configuração, rodar todos com um comando e ver uma tabela comparativa (Score, True Rate, tempo e evidência ancorada), ter uma única fonte de verdade para a configuração do assistente, threshold e HyDE como opções desligadas por padrão, e atalhos de comando em Makefile e em um script para Windows."

## Contexto

O assistente OdontoTest já tem uma avaliação da resposta final, com nota de 97,8% no conjunto de trabalho e uma referência gravada. Essa avaliação diz se o assistente responde certo, mas não ajuda a escolher entre formas diferentes de preparar e buscar o material:

- só existe uma forma de dividir o material por vez, e criar outra apaga o índice anterior;
- os parâmetros da busca estão espalhados no código;
- não há como ver várias configurações lado a lado; a comparação existente é entre duas execuções.

Esta feature cria uma bancada para isso: as estratégias de divisão e os experimentos de busca passam a ser declarados em arquivos de configuração, um comando roda todos e mostra uma tabela comparativa, e o experimento escolhido vira a configuração do assistente. O objetivo é escolher a configuração com base em números e estar pronto para quando o material da clínica crescer.

A bancada mede só a busca. Ela **soma** à avaliação da resposta final, que continua sendo a forma de validar o que o cliente recebe.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Comparar experimentos de busca em uma tabela (Priority: P1)

Como responsável pelo assistente, quero rodar com um comando todos os experimentos de busca declarados e ver uma tabela comparando os resultados, para escolher a configuração de busca com base em números.

**Why this priority**: É o resultado que justifica a feature. Sem a tabela, as estratégias e os experimentos declarados não servem para decidir nada.

**Independent Test**: Com três experimentos declarados, um para cada estratégia inicial, rodar o comando e conferir que a tabela mostra uma linha por experimento, com todas as colunas, ordenada da melhor para a pior, e que um arquivo de resultados é salvo.

**Acceptance Scenarios**:

1. **Given** três experimentos declarados e os índices das suas estratégias criados, **When** o responsável roda o comando de experimentos, **Then** cada experimento é executado sobre as perguntas do gabarito, sem gerar respostas, e uma tabela comparativa é mostrada no fim.
2. **Given** uma execução concluída, **When** o responsável lê a tabela, **Then** ele vê para cada experimento: nome, tipo de busca, estratégia, threshold, quantidade de trechos, HyDE, Score, True Rate, tempo médio por pergunta e evidência ancorada.
3. **Given** experimentos com resultados diferentes, **When** a tabela é mostrada, **Then** as linhas estão ordenadas da melhor para a pior, e o critério de ordenação está escrito junto da tabela.
4. **Given** uma execução em andamento, **When** o responsável acompanha o terminal, **Then** ele vê o progresso de cada experimento.
5. **Given** a opção de detalhe ligada, **When** os experimentos rodam, **Then** cada pergunta aparece em uma linha no formato "pergunta;acertou;nota".
6. **Given** uma execução concluída, **When** o comando termina, **Then** os resultados da tabela estão salvos em um arquivo CSV e o caminho do arquivo é informado.

---

### User Story 2 - Declarar estratégias de divisão que convivem (Priority: P1)

Como responsável pelo assistente, quero declarar em um arquivo as formas de dividir o material, cada uma gerando o seu próprio índice, para poder ter várias ao mesmo tempo e compará-las.

**Why this priority**: É o pré-requisito dos experimentos: sem índices que convivem, não há o que comparar. Entrega valor sozinha porque acaba com o risco de recriar um índice por cima de outro.

**Independent Test**: Declarar as três estratégias iniciais, criar os índices e conferir que os três existem ao mesmo tempo e que cada um tem os trechos esperados para a sua forma de divisão.

**Acceptance Scenarios**:

1. **Given** o arquivo de estratégias com "section", "recursive_500_200" e "page", **When** o responsável manda criar os índices, **Then** três índices são criados, um por estratégia, e nenhum sobrescreve outro.
2. **Given** os índices criados, **When** o responsável cria de novo o índice de uma só estratégia, **Then** os outros dois ficam intactos.
3. **Given** uma estratégia nova de um tipo que já existe (por exemplo, divisão por caracteres com outros tamanhos), **When** o responsável a acrescenta ao arquivo e cria os índices, **Then** o índice dela é criado sem nenhuma outra alteração no projeto.
4. **Given** os índices criados, **When** o responsável roda a verificação da base de conhecimento para uma estratégia, **Then** o resultado se refere ao índice daquela estratégia.

---

### User Story 3 - Uma única fonte de verdade para a configuração do assistente (Priority: P2)

Como responsável pelo assistente, quero que o arquivo de experimentos indique qual experimento o chat e a avaliação da resposta usam, para que adotar o experimento vencedor seja trocar um nome e não reescrever parâmetros em outro lugar.

**Why this priority**: É o que liga a bancada ao assistente. Sem isso, a configuração ficaria em dois lugares e o resultado da tabela teria de ser copiado à mão, com risco de erro.

**Independent Test**: Trocar o nome do experimento do assistente no arquivo, conversar com o assistente e conferir que ele passou a usar a estratégia e os parâmetros do novo experimento; voltar ao nome original e conferir que a avaliação da resposta dá o mesmo resultado da referência.

**Acceptance Scenarios**:

1. **Given** o experimento do assistente apontando para a configuração atual, **When** o responsável roda a avaliação da resposta final, **Then** nenhuma pergunta muda de resultado em relação à referência.
2. **Given** o arquivo de experimentos, **When** o responsável troca o nome do experimento do assistente, **Then** o chat e a avaliação da resposta passam a usar a estratégia e os parâmetros desse experimento, sem outra alteração.
3. **Given** uma avaliação da resposta final concluída, **When** o resultado é gravado, **Then** fica registrado qual experimento e qual estratégia foram usados.
4. **Given** o nome do experimento do assistente apontando para um experimento que não existe, **When** o chat ou a avaliação são iniciados, **Then** a execução é recusada com uma mensagem que diz o que corrigir.

---

### User Story 4 - Testar threshold e HyDE antes de adotar (Priority: P3)

Como responsável pelo assistente, quero ligar em um experimento a nota mínima de similaridade ou o HyDE e ver na tabela o efeito e o custo, para só adotar essas opções se os números mostrarem ganho.

**Why this priority**: São opções com potencial de melhorar a busca, mas com custo. A bancada sem elas já compara estratégias; com elas passa a responder também se vale a pena ligá-las.

**Independent Test**: Declarar um experimento com threshold e outro com HyDE, rodar e conferir que a tabela mostra os valores dessas opções e que o tempo médio do experimento com HyDE é maior que o do mesmo experimento sem ele.

**Acceptance Scenarios**:

1. **Given** um experimento com threshold maior que zero, **When** a busca roda, **Then** os trechos com similaridade abaixo do threshold não entram no resultado.
2. **Given** um experimento com HyDE ligado, **When** a busca roda, **Then** ela usa uma resposta hipotética gerada pelo modelo no lugar da pergunta, e o tempo dessa geração entra no tempo médio por pergunta.
3. **Given** nenhuma alteração nos padrões, **When** um experimento é declarado sem threshold e sem HyDE, **Then** as duas opções ficam desligadas.
4. **Given** um experimento com threshold tão alto que nenhum trecho passa em uma pergunta, **When** a pergunta é avaliada, **Then** ela conta como erro no True Rate e o caso fica visível no detalhe.

---

### User Story 5 - Atalhos para os comandos do projeto (Priority: P3)

Como responsável pelo assistente, quero atalhos curtos para os comandos do dia a dia, para não ter de lembrar a forma completa de cada um.

**Why this priority**: É conveniência. Não muda o que o projeto faz, mas reduz o atrito de uso, que cresce com o número de comandos.

**Independent Test**: Rodar cada atalho nas duas formas e conferir que ele executa o mesmo comando completo.

**Acceptance Scenarios**:

1. **Given** o projeto instalado em Windows com PowerShell, **When** o responsável usa o script de atalhos, **Then** os atalhos funcionam sem instalar nenhuma ferramenta adicional.
2. **Given** um ambiente com `make` disponível, **When** o responsável usa o Makefile, **Then** os mesmos nomes de atalho executam os mesmos comandos.
3. **Given** qualquer das duas formas, **When** o responsável pede a lista de atalhos, **Then** vê cada nome com uma descrição de uma linha.
4. **Given** um atalho inexistente, **When** o responsável tenta usá-lo, **Then** recebe a lista dos atalhos válidos.

---

### Edge Cases

- O arquivo de configuração tem um erro (estratégia inexistente em um experimento, tipo desconhecido, nome repetido, campo obrigatório faltando, valor fora da faixa): nada é executado, e a mensagem lista cada problema e o que corrigir.
- O índice da estratégia de um experimento ainda não foi criado: o experimento é marcado como não executado, a mensagem diz qual comando rodar, e os outros experimentos rodam normalmente.
- Os parâmetros de uma estratégia foram alterados depois de o índice ser criado: o índice está desatualizado; o responsável é avisado, em vez de receber números de uma divisão que não é a declarada.
- O material da clínica foi trocado depois de os índices serem criados: mesmo aviso de índice desatualizado.
- O tipo de busca é só por palavras, que não produz similaridade de 0 a 1: o Score é calculado da mesma forma para todos os tipos de busca, pela similaridade entre a pergunta e cada trecho devolvido.
- Dois experimentos empatam no critério de ordenação: o desempate segue uma regra fixa e documentada.
- O serviço de modelos cai no meio da execução: os experimentos já concluídos aparecem na tabela, o interrompido é marcado como incompleto e não entra no arquivo de resultados como se fosse completo.
- Não há nenhum experimento declarado: o comando informa isso e termina sem erro de execução.
- Um experimento com HyDE roda quando o modelo de geração não está disponível: o experimento é marcado como não executado, com o motivo, e os outros seguem.
- O experimento do assistente usa uma estratégia cujo índice não existe: o chat recusa iniciar e diz qual comando rodar.

## Requirements *(mandatory)*

### Functional Requirements

**Estratégias de divisão**

- **FR-001**: O sistema DEVE ler as estratégias de divisão do material de um arquivo de configuração editável à mão, cada uma com nome, tipo e parâmetros.
- **FR-002**: O sistema DEVE oferecer três tipos de divisão: por seção (um tratamento por trecho), por caracteres com tamanho e sobreposição configuráveis, e por página.
- **FR-003**: O arquivo DEVE vir com três estratégias: "section" (a divisão atual), "recursive_500_200" (por caracteres, 500 de tamanho e 200 de sobreposição) e "page".
- **FR-004**: Cada estratégia DEVE gerar um índice próprio, e criar ou recriar o índice de uma estratégia NÃO DEVE alterar o de outra.
- **FR-005**: O responsável DEVE poder criar os índices de todas as estratégias com um comando, ou de uma só indicando o nome.
- **FR-006**: Acrescentar uma estratégia de um tipo existente DEVE exigir apenas editar o arquivo de configuração.
- **FR-007**: O sistema DEVE detectar e avisar quando um índice não corresponde mais à estratégia declarada ou ao material atual.

**Experimentos de busca**

- **FR-008**: O sistema DEVE ler os experimentos de outro arquivo de configuração, cada um com: nome, estratégia usada, tipo de busca (híbrida, só vetorial ou só por palavras), quantidade de trechos recuperados, threshold e uso de HyDE.
- **FR-009**: O arquivo DEVE vir com três experimentos, um para cada estratégia inicial, todos com busca híbrida e os demais parâmetros iguais.
- **FR-010**: Threshold e HyDE DEVEM ficar desligados quando não forem declarados.
- **FR-011**: Acrescentar um experimento DEVE exigir apenas editar o arquivo de configuração.

**Validação da configuração**

- **FR-012**: O sistema DEVE validar os dois arquivos antes de executar qualquer coisa e recusar configuração inválida, listando cada problema e o que corrigir. São inválidos, no mínimo: nome repetido, tipo desconhecido, experimento que cita estratégia inexistente, campo obrigatório ausente e valor fora da faixa permitida.
- **FR-013**: O responsável DEVE poder validar a configuração sem rodar experimentos.

**Execução e tabela comparativa**

- **FR-014**: O sistema DEVE oferecer um comando que roda todos os experimentos sobre as perguntas com resposta do conjunto de trabalho do gabarito, medindo só a busca, sem gerar respostas.
- **FR-015**: O responsável DEVE poder rodar um subconjunto dos experimentos indicando os nomes.
- **FR-016**: Durante a execução o sistema DEVE mostrar o progresso de cada experimento.
- **FR-017**: O sistema DEVE oferecer uma opção de detalhe que mostra uma linha por pergunta no formato "pergunta;acertou;nota".
- **FR-018**: Ao final o sistema DEVE mostrar uma tabela com uma linha por experimento e as colunas: experimento, tipo de busca, estratégia, threshold, quantidade de trechos, HyDE, Score, True Rate, tempo médio por pergunta e evidência ancorada.
- **FR-019**: A tabela DEVE estar ordenada da melhor para a pior: primeiro pelo True Rate, depois pelo Score, e o critério DEVE aparecer junto da tabela. No empate de True Rate, experimentos com HyDE ficam depois dos sem HyDE, porque o Score deles não é comparável (ajuste feito na implementação, depois de a primeira tabela mostrar o HyDE em primeiro só pelo Score inflado).
- **FR-020**: O sistema DEVE salvar os resultados da tabela em um arquivo CSV, sem sobrescrever os de execuções anteriores, e informar o caminho.
- **FR-021**: Um experimento que não puder ser executado (índice ausente ou desatualizado, modelo indisponível) DEVE aparecer como não executado, com o motivo e o comando que resolve, sem impedir os demais.
- **FR-022**: A parte reservada do gabarito NÃO DEVE ser usada pelos experimentos.

**Métricas**

- **FR-023**: O True Rate DEVE ser a quantidade de perguntas em que a evidência do gabarito veio entre os trechos recuperados, sobre o total de perguntas avaliadas, mostrada como fração (ex.: 37/38).
- **FR-024**: O Score DEVE ser a média, entre as perguntas, da similaridade (de 0 a 1) entre a pergunta e os trechos recuperados, calculada da mesma forma para qualquer tipo de busca.
- **FR-025**: A evidência ancorada DEVE ser a fração de perguntas em que o trecho com a evidência também traz o nome do procedimento a que ela pertence, como na avaliação já existente.
- **FR-026**: O tempo médio por pergunta DEVE incluir tudo o que a busca do experimento faz, inclusive a geração da resposta hipotética quando o HyDE está ligado.
- **FR-027**: A documentação DEVE dizer que o Score mede semelhança com a pergunta e não acerto, e que só é comparável entre experimentos com o mesmo modelo de embedding.

**Opções de busca**

- **FR-028**: Com threshold maior que zero, a busca NÃO DEVE devolver trechos com similaridade abaixo dele.
- **FR-029**: Com HyDE ligado, a busca DEVE usar uma resposta hipotética gerada pelo modelo no lugar da pergunta.
- **FR-030**: Threshold e HyDE DEVEM valer também no assistente quando o experimento escolhido para ele os tiver ligados.

**Configuração do assistente**

- **FR-031**: O arquivo de experimentos DEVE indicar qual experimento o chat e a avaliação da resposta final usam, e esse DEVE ser o único lugar em que a estratégia e os parâmetros de busca do assistente são definidos.
- **FR-032**: Com o experimento do assistente apontando para a configuração atual, o assistente DEVE se comportar como antes da feature.
- **FR-033**: A avaliação da resposta final DEVE registrar, em cada execução, o experimento e a estratégia usados.
- **FR-034**: O prompt e os sinônimos da busca DEVEM continuar fora dos arquivos de configuração de estratégias e experimentos.

**Atalhos**

- **FR-035**: O projeto DEVE oferecer atalhos com os mesmos nomes em duas formas: um Makefile e um script que funcione em Windows com PowerShell sem instalar nada.
- **FR-036**: Os atalhos DEVEM cobrir: conversar com o assistente, criar os índices, rodar os testes, rodar a avaliação da resposta, rodar os experimentos e verificar a base de conhecimento.
- **FR-037**: As duas formas DEVEM apenas chamar os comandos do projeto, sem lógica própria, e DEVEM listar os atalhos disponíveis com uma descrição de cada um.

### Key Entities

- **Estratégia de divisão**: uma forma de dividir o material. Tem nome único, tipo (seção, caracteres ou página) e parâmetros próprios do tipo.
- **Índice**: o material dividido e preparado para busca segundo uma estratégia. Pertence a uma única estratégia e registra com que definição e com que material foi criado.
- **Experimento**: uma configuração de busca. Tem nome único, a estratégia usada, o tipo de busca, a quantidade de trechos, o threshold e o uso de HyDE.
- **Experimento do assistente**: a indicação de qual experimento o chat e a avaliação da resposta usam.
- **Resultado por pergunta**: para um experimento e uma pergunta, se a evidência veio, a nota de similaridade, se veio ancorada e o tempo da busca.
- **Resultado do experimento**: uma linha da tabela, com os parâmetros do experimento, True Rate, Score, evidência ancorada, tempo médio e o estado (executado, não executado ou incompleto, com o motivo).
- **Execução da bancada**: um conjunto de resultados de experimentos produzidos por um comando, com data, versão do gabarito e o arquivo de resultados salvo.
- **Atalho**: um nome curto associado a um comando completo do projeto e a uma descrição.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Depois da feature, a avaliação da resposta final continua em 97,8% no conjunto de trabalho, sem nenhuma pergunta mudando de resultado em relação à referência.
- **SC-002**: Rodar os três experimentos iniciais leva menos de 1 minuto no total.
- **SC-003**: A tabela mostra os três experimentos com todas as colunas e permite dizer, em menos de 1 minuto de leitura, qual estratégia recupera a evidência em mais perguntas. A expectativa é que "section" tenha True Rate maior ou igual ao das outras duas; se não tiver, o resultado é registrado como achado e não é ajustado para confirmar a expectativa.
- **SC-004**: O responsável acrescenta um quarto experimento editando só o arquivo de configuração e o vê na tabela na execução seguinte.
- **SC-005**: O responsável troca a configuração do assistente alterando um único nome em um único arquivo.
- **SC-006**: 100% dos erros de configuração previstos são recusados antes de qualquer execução, com mensagem que aponta o item errado.
- **SC-007**: Os três índices iniciais existem ao mesmo tempo, e recriar um deles não altera o conteúdo dos outros dois.
- **SC-008**: Um experimento com HyDE ligado aparece na tabela com tempo médio por pergunta maior que o do mesmo experimento sem HyDE, tornando o custo visível.
- **SC-009**: Todos os atalhos funcionam nas duas formas e executam o mesmo comando.
- **SC-010**: Todos os testes que existiam antes da feature continuam passando.

## Assumptions

- O responsável é a única pessoa que usa o projeto, no terminal, em Windows com PowerShell, e tudo roda localmente, como hoje.
- A avaliação da resposta final não é substituída nem alterada no que mede. A bancada escolhe a configuração de busca; a avaliação existente continua validando a resposta.
- Os experimentos usam as perguntas com resposta do conjunto de trabalho do gabarito (38 hoje). Perguntas sem resposta no material não têm evidência a recuperar e ficam fora.
- A ordenação "da melhor para a pior" é pelo True Rate, com o Score como desempate, porque o True Rate mede acerto contra o gabarito e o Score mede só semelhança.
- A definição de Score e True Rate foi inferida da saída de um projeto de referência visto em prints, sem acesso ao código dele. As definições desta spec são as que valem para este projeto.
- "Quantidade de trechos recuperados" é o máximo de trechos que a busca devolve para uma pergunta. Como a busca híbrida combina duas buscas, o plano definirá como esse número se divide entre elas, mantendo o comportamento atual no experimento do assistente.
- O experimento inicial do assistente reproduz a configuração atual: estratégia "section", busca híbrida, até 4 trechos, sem threshold e sem HyDE.
- Threshold e HyDE só entram na configuração do assistente se a tabela mostrar ganho; a decisão é do responsável e não faz parte desta feature.
- O `make` não está instalado na máquina do responsável. O script para Windows é o caminho que funciona de imediato; o Makefile atende a quem tiver `make`.
- Ficam fora do escopo: divisão semântica e por tokens, mudanças no prompt, no modelo ou no gabarito, e memória de conversa.
- Os índices são gerados localmente e continuam fora do controle de versão; os arquivos de configuração e os resultados salvos ficam versionados.
- A descrição recebida veio com três trechos cortados (itens 3 e 6 e uma restrição) e um bloco repetido. O conteúdo foi completado a partir do plano combinado antes: o assistente deve continuar se comportando como hoje; threshold e HyDE só entram no assistente com ganho comprovado, e a coluna de tempo mostra o custo; o prompt e os sinônimos continuam no código.
