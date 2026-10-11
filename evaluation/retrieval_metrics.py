"""Métricas de busca: a evidência do gabarito foi recuperada? Em que posição? Com o procedimento junto?"""
from evaluation.normalize import normalize_text

SOURCES = ("vector", "bm25", "fused")


def contains(chunk, snippet):
    return normalize_text(snippet) in normalize_text(chunk)


def score_retrieval(item, chunks, anchors):
    """chunks: textos na ordem em que foram recuperados. Devolve None para pergunta sem resposta."""
    if not item.answerable:
        return None

    relevant = [any(contains(chunk, evidence) for evidence in item.evidence) for chunk in chunks]
    found = [any(contains(chunk, evidence) for chunk in chunks) for evidence in item.evidence]
    first = next((rank for rank, ok in enumerate(relevant, start=1) if ok), None)
    hit = first is not None

    if anchors:
        anchored = any(
            ok and any(contains(chunk, anchor) for anchor in anchors) for chunk, ok in zip(chunks, relevant)
        )
    else:
        anchored = hit

    return {
        "hit": hit,
        "recall": sum(found) / len(found),
        "mrr": 1 / first if hit else 0.0,
        "context_precision": sum(relevant) / len(chunks) if chunks else 0.0,
        "anchored": anchored,
    }


def score_all_sources(item, retrieved, gabarito):
    """retrieved: {"vector": [...], "bm25": [...], "fused": [...]}, cada trecho com "content"."""
    if not item.answerable:
        return None
    anchors = gabarito.anchors(item.procedure)
    return {
        source: score_retrieval(item, [chunk["content"] for chunk in retrieved[source]], anchors)
        for source in SOURCES
    }
