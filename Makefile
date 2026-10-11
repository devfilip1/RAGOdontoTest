# Atalhos para os comandos do projeto. Uso: make <atalho> [ARGS="argumentos"]
# Os mesmos nomes existem em run.ps1, que funciona no Windows sem instalar o make.
# Um teste confere que os dois arquivos não divergem.

ifeq ($(OS),Windows_NT)
PYTHON ?= .venv/Scripts/python.exe
else
PYTHON ?= .venv/bin/python
endif

ARGS ?=

.DEFAULT_GOAL := help
.PHONY: help install ingest chat test test-integration eval eval-smoke eval-full experiments retrieval kb-check validate compare baseline

help: ## Lista os atalhos
	@$(PYTHON) -c "import re; [print(f'  {m[1]:<18} {m[2]}') for m in re.finditer(r'^([a-z-]+):.*?## (.+)$$', open('Makefile', encoding='utf-8').read(), re.M)]"

install: ## Instala as dependências
	$(PYTHON) -m pip install -r requirements.txt $(ARGS)

ingest: ## Cria os índices de todas as estratégias
	$(PYTHON) -m assistant.ingest $(ARGS)

chat: ## Conversa com o assistente
	$(PYTHON) -m assistant.chat $(ARGS)

test: ## Testes de unidade (sem Ollama)
	$(PYTHON) -m pytest $(ARGS)

test-integration: ## Testes com o Ollama e o índice
	$(PYTHON) -m pytest -m integration $(ARGS)

eval: ## Avaliação da resposta, sem o juiz
	$(PYTHON) -m evaluation run --no-judge $(ARGS)

eval-smoke: ## Avaliação rápida, 10 perguntas
	$(PYTHON) -m evaluation run --smoke --no-judge $(ARGS)

eval-full: ## Avaliação da resposta, com o juiz
	$(PYTHON) -m evaluation run $(ARGS)

experiments: ## Compara os experimentos de busca
	$(PYTHON) -m evaluation experiments $(ARGS)

retrieval: ## Detalhe da busca do experimento do assistente
	$(PYTHON) -m evaluation retrieval $(ARGS)

kb-check: ## Verifica a base de conhecimento
	$(PYTHON) -m evaluation kb-check $(ARGS)

validate: ## Valida a configuração e o gabarito
	$(PYTHON) -m evaluation validate $(ARGS)

compare: ## Compara a última avaliação com a referência
	$(PYTHON) -m evaluation compare $(ARGS)

baseline: ## Marca a última avaliação como referência
	$(PYTHON) -m evaluation baseline set $(ARGS)
