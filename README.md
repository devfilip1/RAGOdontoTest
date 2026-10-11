# RAG OdontoTest

Assistente virtual da clínica OdontoTest. Responde perguntas de clientes com base no material da clínica (um PDF), usando busca vetorial e lexical sobre o material e um modelo local via Ollama.

## Estrutura

```text
config/         o que você edita para mudar a busca
  strategies.yaml   formas de dividir o material (cada uma gera um índice)
  experiments.yaml  configurações de busca e qual delas o assistente usa
assistant/      o assistente
  config.py       caminhos, modelos, sinônimos e temperatura
  settings.py     lê e valida os dois arquivos de config/
  index.py        onde fica o índice de cada estratégia e se ele está em dia
  ingest.py       lê o PDF, divide conforme a estratégia e cria os índices
  pipeline.py     retrieve() e answer(): a busca e a resposta
  chat.py         chat no terminal
evaluation/     avaliação do assistente (ver evaluation/README.md)
  data/           gabarito de perguntas
  runs/           histórico das execuções e referência
tests/          testes de unidade e de integração
data/
  source/         o PDF da clínica
  index/          um índice por estratégia, gerado pelo ingest (fora do git)
specs/          especificação, plano e tarefas (Spec Kit)
```

## Preparar o ambiente

Requer Python 3.14 e o [Ollama](https://ollama.com) em execução.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

ollama pull llama3
ollama pull nomic-embed-text

python -m assistant.ingest      # cria um índice por estratégia em data/index/
```

Para usar outros modelos ou outro endereço do Ollama, copie `.env.example` para `.env` e ajuste.

## Usar

```powershell
python -m assistant.chat        # conversa no terminal ("sair" encerra)
```

Rode `python -m assistant.ingest` de novo sempre que o PDF ou uma estratégia mudarem, e confira o resultado com `python -m evaluation kb-check`. Para recriar só um índice: `python -m assistant.ingest page`. O chat e a avaliação recusam rodar com um índice desatualizado e dizem qual comando resolve.

## Atalhos

Os comandos do dia a dia têm apelidos, que funcionam sem ativar o ambiente virtual:

```powershell
.\run.ps1 help          # lista os atalhos
.\run.ps1 chat
.\run.ps1 experiments
.\run.ps1 eval --label o-que-mudei
```

O `Makefile` tem os mesmos nomes (`make chat`, `make eval ARGS="--label x"`), para quem tiver o `make` instalado (`winget install ezwinports.make`).

## Configurar a busca

Dois arquivos em `config/` definem como o material é dividido e buscado:

- `strategies.yaml`: as formas de dividir o material. Cada uma gera o seu índice em `data/index/<nome>/`.
- `experiments.yaml`: as configurações de busca (estratégia, tipo de busca, quantidade de trechos, threshold, HyDE). A linha `assistant:` diz qual delas o chat e a avaliação usam.

```powershell
python -m evaluation experiments     # roda todos os experimentos e mostra a tabela comparativa
```

Para mudar a configuração do assistente, troque o nome em `assistant:` e confirme com `python -m evaluation run`.

## Avaliar

```powershell
python -m evaluation run --smoke --no-judge   # 10 perguntas, cerca de 20 segundos
python -m evaluation experiments              # compara as configurações de busca, 10 segundos
python -m evaluation run                      # avaliação completa, comparada com a referência
```

Os comandos, a leitura do placar e a manutenção do gabarito estão em [evaluation/README.md](evaluation/README.md).

## Testes

```powershell
pytest                    # testes de unidade, sem Ollama
pytest -m integration     # exige Ollama e o índice criado
```
