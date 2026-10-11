import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# material da clínica (origem) e índices gerados a partir dele por assistant.ingest, um por estratégia
SOURCE_PDF = ROOT / "data" / "source" / "OdontoTest.pdf"
INDEX_DIR = ROOT / "data" / "index"

# estratégias de divisão e experimentos de busca, editáveis à mão (lidos por assistant.settings)
CONFIG_DIR = ROOT / "config"
STRATEGIES_PATH = CONFIG_DIR / "strategies.yaml"
EXPERIMENTS_PATH = CONFIG_DIR / "experiments.yaml"
SCHEMAS_DIR = CONFIG_DIR / "schemas"
COLLECTION_NAME = "db_odonto_test_ollama"

# Correções aplicadas ao texto extraído. No PDF atual a palavra "titânio" está corrompida no próprio arquivo.
TEXT_FIXES = {"■■■ânio": "titânio"}

# Palavras que não ajudam a busca por palavras (já sem acento).
STOPWORDS = frozenset("""
a o as os um uma uns umas de da do das dos em no na nos nas ao aos e ou que se por para pra pro com sem
qual quais quanto quanta quantos quantas qnto como quando onde eu me meu minha voce voces vc vcs e eh ser
sao tem ter tenho fica ficar faz fazer posso pode isso esse essa este esta ai la mais muito mto ja so
""".split())

# Como o cliente fala -> como o material escreve. Usado só na busca por palavras.
QUERY_SYNONYMS = {
    "custa": ("investimento",), "custam": ("investimento",), "custo": ("investimento",),
    "preco": ("investimento",), "precos": ("investimento",), "valor": ("investimento",),
    "valores": ("investimento",), "cobra": ("investimento",), "cobram": ("investimento",),
    "demora": ("tempo",), "demoram": ("tempo",), "leva": ("tempo",), "levam": ("tempo",),
    "prazo": ("tempo",), "dura": ("durabilidade", "tempo"), "duram": ("durabilidade", "tempo"),
    "funciona": ("feito",), "feita": ("funciona", "feito"), "feitas": ("funciona", "feito"),
    "tipos": ("opcoes",), "tipo": ("opcoes",), "modelos": ("opcoes",),
    "doi": ("dor",), "doem": ("dor",), "dolorido": ("dor",),
    "arrancar": ("extracao",), "tirar": ("extracao",), "extrair": ("extracao",),
    "obturacao": ("restauracao",), "parcelar": ("pagamento",),
}

# Geração. Temperatura 0 porque o assistente informa preços e prazos: a mesma pergunta deve dar a mesma resposta.
TEMPERATURE = 0.0
MAX_ANSWER_TOKENS = 200   # teto de segurança; as respostas pedidas têm até 3 frases
KEEP_ALIVE = "30m"        # mantém o modelo carregado entre as perguntas, para não pagar a carga de novo

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
