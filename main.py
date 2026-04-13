import os
from langchain_chroma.vectorstores import Chroma
from dotenv import load_dotenv
from create_db import EMBEDDINGS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama


load_dotenv()
PATH_DB = "./database"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "deepseek-r1:8b")

prompt_template = """
Você é um assistente da clínica OdontoTest.

Use APENAS o contexto fornecido para responder.

Pergunta: {ask}

Contexto:
{knowledge}

Regras:
- Responda de forma direta e curta
- Use apenas informações do contexto
- Não invente informações
- Seja claro e profissional
"""

def to_ask():
    ask = input("Digite sua pergunta: ")

    db = Chroma(collection_name="db_odonto_test_ollama", persist_directory=PATH_DB, embedding_function=EMBEDDINGS)

    results = db.similarity_search_with_relevance_scores(ask, k=3)

    if len(results) == 0 or results[0][1] < 0.5:
        print("Desculpe, não sei a resposta para essa pergunta.")
    
    result_text = []
    for result in results:
        result_text.append(result[0].page_content)

    knowledge = "\n\n----\n\n".join(result_text)

    prompt = ChatPromptTemplate.from_template(prompt_template)
    prompt = prompt.invoke({"ask": ask, "knowledge": knowledge})

    model = ChatOllama(model=OLLAMA_CHAT_MODEL, base_url=OLLAMA_BASE_URL)
    response = model.invoke(prompt)
    print("response:", response.content)


to_ask()