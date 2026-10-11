# Quickstart: Avaliação e Métricas do Assistente OdontoTest

**Feature**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Roteiro para confirmar, de ponta a ponta, que a feature funciona. Os comandos estão detalhados em [contracts/cli.md](./contracts/cli.md) e os dados em [data-model.md](./data-model.md).

## Pré-requisitos

- Ambiente virtual ativo: `.venv\Scripts\Activate.ps1`
- Dependências instaladas: `pip install -r requirements.txt`
- Ollama em execução, com os modelos `llama3` e `nomic-embed-text` (`ollama list`)
- Base de conhecimento criada: `python -m assistant.ingest`

## 1. Testes de unidade (sem Ollama)

```powershell
pytest tests/unit
```

**Esperado**: todos passam em poucos segundos. Inclui as 20 respostas de exemplo com formatos variados de valores e prazos, todas com o veredito correto (SC-009).

## 2. Gabarito válido e com cobertura

```powershell
python -m evaluation validate
```

**Esperado**: gabarito válido; ao menos 40 itens; todos os 8 procedimentos com itens de preço, tempo e resultado; ao menos 6 itens sem resposta no material (SC-001).

## 3. Verificações da base de conhecimento

```powershell
python -m evaluation kb-check
```

**Esperado**: termina em menos de 1 minuto (SC-008). Na base atual deve apontar:

- o trecho com `■■■ânio` (texto corrompido na extração de "titânio");
- fatos sem trecho ancorado, entre eles o preço da restauração, que hoje está em um trecho sem o nome do procedimento.

Para conferir a detecção de duplicados: rodar `python -m assistant.ingest` com a limpeza da coleção desativada, rodar `kb-check` e ver a duplicação apontada com a quantidade de repetições; depois recriar a base normalmente.

## 4. O assistente continua igual

```powershell
python -m assistant.chat
```

**Esperado**: o chat abre e responde como antes. `python -c "import assistant.pipeline"` termina sem abrir o chat nem recriar a base (FR-030).

## 5. Avaliação reduzida

```powershell
python -m evaluation run --smoke
```

**Esperado**: placar em menos de 5 minutos (SC-002), com cerca de 10 itens.

## 6. Avaliação completa e referência

```powershell
python -m evaluation run --label referencia
python -m evaluation baseline set
```

**Esperado**:

- placar em menos de 30 minutos (SC-002), com nota geral, métricas de busca por fonte, métricas de resposta, métricas de juiz, tempos e contagem por causa;
- o item do preço do clareamento aparece como errado, com a causa indicada e o valor incorreto listado (SC-003);
- todo item errado tem uma causa (SC-004);
- ao menos uma pergunta sem resposta no material aparece avaliada na métrica de recusa correta;
- uma pasta nova em `evaluation/runs/` com `run.json` e `report.md` (SC-010).

## 7. Repetibilidade

```powershell
python -m evaluation run --repeat 2 --no-judge
```

**Esperado**: a variação informada é de no máximo 3 pontos percentuais em cada métrica (SC-005).

## 8. Comparação

Mudar um parâmetro do assistente (ex.: `vector_k` de 3 para 5), rodar de novo e comparar:

```powershell
python -m evaluation run --label vector-k-5
python -m evaluation compare
```

**Esperado**: a comparação mostra a mudança de configuração, a diferença de cada métrica e as perguntas que mudaram de resultado, com as regressões primeiro. Dá para dizer em menos de 1 minuto se a mudança ajudou (SC-006). Desfazer a mudança ao final.

## 9. Execução interrompida

Parar o Ollama no meio de `python -m evaluation run`.

**Esperado**: a execução informa os itens não avaliados, grava em `evaluation/runs/_incomplete/` e não aparece em `python -m evaluation list`.

## 10. Conferência humana do juiz

```powershell
python -m evaluation calibrate export
# preencher os campos "human" em evaluation/data/human_labels.json
python -m evaluation calibrate score
```

**Esperado**: concordância por critério; a meta é 80% ou mais em 20 respostas (SC-007). Critérios abaixo disso ficam marcados como não confiáveis no placar.

## 11. Parte reservada

```powershell
python -m evaluation run --holdout --label referencia-holdout
```

**Esperado**: placar só com os itens reservados, gravado com o recorte `holdout`. `python -m evaluation compare` entre uma execução `dev` e uma `holdout` é recusado.
