import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv

load_dotenv()

PASTA_BASE = "base/OdontoTest.pdf"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
EMBEDDINGS = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)


def create_db():
    documents =load_documents()
    chunks = split_to_chunks(documents)
    vectorize_chunks(chunks)

def load_documents():
    loader = PyPDFLoader(PASTA_BASE)
    documents = loader.load()
    return documents

def split_to_chunks(documents):
    divisor = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200, length_function=len, add_start_index=True)
    chunks = divisor.split_documents(documents)

    print(len(chunks))
    return chunks

def vectorize_chunks(chunks):
    db = Chroma.from_documents(chunks, EMBEDDINGS, collection_name="db_odonto_test_ollama", persist_directory="./database")
    print("banco de dados criado com sucesso")


create_db()