"""Verificações da base de conhecimento, sem modelo de linguagem (research D15)."""
import json
import unicodedata
from collections import Counter

from evaluation.normalize import normalize_text
from evaluation.retrieval_metrics import contains

# Caracteres que indicam falha na extração do texto do PDF.
CORRUPTED_CHARS = {"■", "□", "�"}
ALLOWED_CONTROL = {"\n", "\r", "\t"}


def load_kb(strategy_name):
    """Devolve (trechos da base vetorial, trechos do arquivo usado pela busca lexical) de uma estratégia."""
    from langchain_chroma.vectorstores import Chroma

    from assistant.config import COLLECTION_NAME
    from assistant.index import chroma_dir, chunks_path
    from assistant.ingest import EMBEDDINGS

    db = Chroma(collection_name=COLLECTION_NAME, persist_directory=str(chroma_dir(strategy_name)),
                embedding_function=EMBEDDINGS)
    vector_chunks = db._collection.get(include=["documents"])["documents"]
    with open(chunks_path(strategy_name), "r", encoding="utf-8") as f:
        file_chunks = [chunk["content"] for chunk in json.load(f)]
    return vector_chunks, file_chunks


def find_duplicates(chunks):
    """Trechos armazenados mais de uma vez, com a quantidade de repetições."""
    counts = Counter(normalize_text(chunk) for chunk in chunks)
    first = {}
    for chunk in chunks:
        first.setdefault(normalize_text(chunk), chunk)
    return [{"content": first[key], "count": count} for key, count in counts.items() if count > 1]


def find_unanchored_facts(gabarito, chunks):
    """Evidências do gabarito que não têm nenhum trecho com o nome do procedimento junto (FR-028).

    kind "missing": nenhum trecho contém a evidência inteira (ex.: a divisão cortou a linha).
    kind "unanchored": há trechos com a evidência, mas nenhum deles tem o nome do procedimento.
    """
    problems = []
    seen = set()
    for item in gabarito.items:
        anchors = gabarito.anchors(item.procedure)
        for evidence in item.evidence:
            if (item.procedure, evidence) in seen:
                continue
            seen.add((item.procedure, evidence))
            holders = [chunk for chunk in chunks if contains(chunk, evidence)]
            if not holders:
                kind = "missing"
            elif anchors and not any(contains(chunk, anchor) for chunk in holders for anchor in anchors):
                kind = "unanchored"
            else:
                continue
            problems.append({"kind": kind, "item_id": item.id, "procedure": item.procedure, "evidence": evidence})
    return problems


def find_corrupted(chunks):
    """Trechos com caracteres corrompidos na extração."""
    problems = []
    for chunk in chunks:
        bad = sorted({
            char for char in chunk
            if char in CORRUPTED_CHARS or (unicodedata.category(char) == "Cc" and char not in ALLOWED_CONTROL)
        })
        if bad:
            problems.append({"content": chunk, "chars": [f"U+{ord(char):04X}" for char in bad]})
    return problems


def find_source_mismatch(vector_chunks, file_chunks):
    """Diferenças entre a base vetorial e o arquivo de trechos, que deveriam ter o mesmo conteúdo."""
    vector = Counter(normalize_text(chunk) for chunk in vector_chunks)
    lexical = Counter(normalize_text(chunk) for chunk in file_chunks)
    return {
        "vector_count": len(vector_chunks),
        "file_count": len(file_chunks),
        "only_in_vector": sum((vector - lexical).values()),
        "only_in_file": sum((lexical - vector).values()),
        "mismatch": vector != lexical,
    }


def run_checks(gabarito, vector_chunks, file_chunks):
    return {
        "chunk_count": len(vector_chunks),
        "duplicates": find_duplicates(vector_chunks),
        "unanchored": find_unanchored_facts(gabarito, vector_chunks),
        "corrupted": find_corrupted(vector_chunks),
        "source_mismatch": find_source_mismatch(vector_chunks, file_chunks),
    }
