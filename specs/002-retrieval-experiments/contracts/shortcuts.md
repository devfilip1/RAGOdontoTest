# Contract: Atalhos

Os mesmos nomes existem em `run.ps1` (Windows, sem instalar nada) e em `Makefile` (para quem tem `make`). Os dois usam o Python de `.venv`, então não é preciso ativar o ambiente antes.

```powershell
.\run.ps1 <atalho> [argumentos]
make <atalho> [ARGS="argumentos"]
```

| Atalho | Comando | Descrição mostrada por `help` |
|---|---|---|
| `help` | — | Lista os atalhos |
| `install` | `python -m pip install -r requirements.txt` | Instala as dependências |
| `ingest` | `python -m assistant.ingest` | Cria os índices de todas as estratégias |
| `chat` | `python -m assistant.chat` | Conversa com o assistente |
| `test` | `python -m pytest` | Testes de unidade (sem Ollama) |
| `test-integration` | `python -m pytest -m integration` | Testes com o Ollama e o índice |
| `eval` | `python -m evaluation run --no-judge` | Avaliação da resposta, sem o juiz |
| `eval-smoke` | `python -m evaluation run --smoke --no-judge` | Avaliação rápida, 10 perguntas |
| `eval-full` | `python -m evaluation run` | Avaliação da resposta, com o juiz |
| `experiments` | `python -m evaluation experiments` | Compara os experimentos de busca |
| `retrieval` | `python -m evaluation retrieval` | Detalhe da busca do experimento do assistente |
| `kb-check` | `python -m evaluation kb-check` | Verifica a base de conhecimento |
| `validate` | `python -m evaluation validate` | Valida a configuração e o gabarito |
| `compare` | `python -m evaluation compare` | Compara a última avaliação com a referência |
| `baseline` | `python -m evaluation baseline set` | Marca a última avaliação como referência |

Regras:

- Argumentos extras são repassados ao comando: `.\run.ps1 experiments --verbose`, `make experiments ARGS="--verbose"`.
- Sem atalho, ou com `help`: lista os atalhos com as descrições, e sai com `0`.
- Atalho inexistente: informa que não existe, lista os válidos e sai com `2`.
- O código de saída do atalho é o do comando chamado.
- Os dois arquivos só chamam comandos do projeto. Um teste de unidade confere que declaram os mesmos nomes.

O `make` não está instalado nesta máquina. Para usar o Makefile: `winget install ezwinports.make`.
