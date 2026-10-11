import json
import re
import sys

from langchain_chroma.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from assistant.config import (
    COLLECTION_NAME,
    OLLAMA_BASE_URL,
    OLLAMA_EMBEDDING_MODEL,
    ROOT,
    SOURCE_PDF,
    TEXT_FIXES,
)
from assistant.index import chroma_dir, chunks_path, index_dir, write_manifest
from assistant.settings import SettingsError, load_settings

BULLET = "\x7f"  # é assim que o marcador de lista do PDF sai na extração
HEADING_STOPWORDS = {"a", "o", "e", "de", "da", "do", "das", "dos", "com", "para", "um", "uma", "em", "que", "sem", "–"}


class PrefixedEmbeddings(Embeddings):
    """O nomic-embed-text foi treinado com um prefixo que diz se o texto é documento ou pergunta."""

    def __init__(self, model, base_url):
        self._inner = OllamaEmbeddings(model=model, base_url=base_url)
        self._prefixed = model.startswith("nomic-embed-text")

    def embed_documents(self, texts):
        if self._prefixed:
            texts = [f"search_document: {text}" for text in texts]
        return self._inner.embed_documents(texts)

    def embed_query(self, text):
        if self._prefixed:
            text = f"search_query: {text}"
        return self._inner.embed_query(text)


EMBEDDINGS = PrefixedEmbeddings(OLLAMA_EMBEDDING_MODEL, OLLAMA_BASE_URL)


def load_pages():
    """Texto de cada página do material, como sai do PDF."""
    return [page.extract_text() for page in PdfReader(SOURCE_PDF).pages]


def clean_text(text):
    """Corrige a extração: marcadores de lista viram '- item' e as correções de TEXT_FIXES são aplicadas.

    Vale para todas as estratégias, para a comparação entre elas medir só a divisão.
    """
    for wrong, right in TEXT_FIXES.items():
        text = text.replace(wrong, right)

    lines = []
    pending_bullet = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line == BULLET:
            pending_bullet = True
            continue
        lines.append(f"- {line}" if pending_bullet else line)
        pending_bullet = False
    return "\n".join(lines)


def is_heading(line):
    """Título de seção: linha curta, sem dois-pontos, com quase todas as palavras em maiúscula inicial."""
    if line.startswith("- ") or ":" in line or line.endswith(".") or len(line) > 90:
        return False
    words = [word for word in re.findall(r"[^\W\d_]+", line) if word.lower() not in HEADING_STOPWORDS]
    if len(words) < 2:
        return False
    return sum(word[0].isupper() for word in words) / len(words) >= 0.75


def split_sections(text):
    """Divide um texto já limpo em seções: lista de (título, linhas do corpo)."""
    sections = []
    in_heading = False
    for line in text.splitlines():
        # um título longo quebra em duas linhas; a segunda pode ter uma palavra só ("Permanente")
        continuation = (
            in_heading and not line.startswith("- ") and ":" not in line and line[0].isupper() and len(line.split()) <= 6
        )
        if in_heading and (is_heading(line) or continuation) and not sections[-1][1]:
            sections[-1][0] += f" {line}"
        elif is_heading(line):
            sections.append([line, []])
            in_heading = True
        elif sections:
            sections[-1][1].append(line)
            in_heading = False
    return [(title, body) for title, body in sections]


def split_by_section(pages, parameters):
    """Um trecho por seção, para cada valor ficar junto do nome do tratamento a que pertence."""
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=parameters["max_chars"], chunk_overlap=parameters["overlap"], length_function=len
    )
    chunks = []
    # as páginas são emendadas: uma seção pode começar em uma página e terminar na outra
    for title, body in split_sections("\n".join(pages)):
        content = "\n".join([title, *body])
        # seção maior que o limite: divide o corpo e repete o título em cada parte
        if len(content) <= parameters["max_chars"]:
            parts = [content]
        else:
            parts = [f"{title}\n{part}" for part in divisor.split_text("\n".join(body))]
        chunks.extend((part, {"section": title}) for part in parts)
    return chunks


def split_by_characters(pages, parameters):
    """Divisão recursiva por caracteres do texto inteiro."""
    divisor = RecursiveCharacterTextSplitter(
        chunk_size=parameters["chunk_size"], chunk_overlap=parameters["chunk_overlap"], length_function=len
    )
    return [(part, {}) for part in divisor.split_text("\n".join(pages))]


def split_by_page(pages, parameters):
    """Um trecho por página."""
    return [(page, {"page": number}) for number, page in enumerate(pages, start=1) if page]


# Para criar um tipo novo de divisão: escreva a função e registre aqui (e no esquema config/schemas).
STRATEGY_TYPES = {
    "section": split_by_section,
    "split": split_by_characters,
    "page": split_by_page,
}


def build_chunks(strategy, pages):
    """Divide o material segundo a estratégia. pages é o texto de cada página, como sai do PDF."""
    if strategy.type not in STRATEGY_TYPES:
        raise ValueError(f"tipo de estratégia desconhecido: {strategy.type}")

    source = SOURCE_PDF.relative_to(ROOT).as_posix()
    cleaned = [clean_text(page) for page in pages]
    return [
        Document(page_content=content, metadata={"source": source, "strategy": strategy.name, **extra})
        for content, extra in STRATEGY_TYPES[strategy.type](cleaned, strategy.parameters)
    ]


def save_chunks(strategy, chunks):
    data = []

    for chunk in chunks:
        data.append({
            "content": chunk.page_content,
            "metadata": chunk.metadata
        })

    index_dir(strategy.name).mkdir(parents=True, exist_ok=True)
    with open(chunks_path(strategy.name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def vectorize_chunks(strategy, chunks):
    directory = str(chroma_dir(strategy.name))
    # apaga a coleção antiga para não duplicar os chunks a cada execução
    Chroma(collection_name=COLLECTION_NAME, persist_directory=directory, embedding_function=EMBEDDINGS).delete_collection()
    Chroma.from_documents(chunks, EMBEDDINGS, collection_name=COLLECTION_NAME, persist_directory=directory)


def build_index(strategy, pages=None):
    """Cria ou recria o índice de uma estratégia, sem tocar nos índices das outras."""
    chunks = build_chunks(strategy, pages if pages is not None else load_pages())
    save_chunks(strategy, chunks)
    vectorize_chunks(strategy, chunks)
    write_manifest(strategy, len(chunks))
    return len(chunks)


def main(argv=None):
    """python -m assistant.ingest [ESTRATÉGIA...] — sem argumentos, cria os índices de todas."""
    names = list(sys.argv[1:] if argv is None else argv)
    try:
        declared = load_settings().strategies
    except SettingsError as error:
        print(f"Configuração inválida: {len(error.problems)} problema(s)")
        for problem in error.problems:
            print(f"  - {problem}")
        return 2

    unknown = [name for name in names if name not in declared]
    if unknown:
        print(f"Estratégia inexistente: {', '.join(unknown)}. Use uma de: {', '.join(declared)}")
        return 2

    pages = load_pages()
    for name in names or declared:
        count = build_index(declared[name], pages)
        print(f"{name}: {count} trechos em data/index/{name}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
