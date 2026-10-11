"""Testes que usam o Ollama e os índices de verdade. Rodar com: pytest -m integration"""
import builtins
import importlib
import json
import sys

import pytest

pytestmark = pytest.mark.integration


def test_import_has_no_side_effects(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("import não pode abrir o chat nem chamar o modelo")

    monkeypatch.setattr(builtins, "input", fail)
    monkeypatch.setattr("langchain_ollama.ChatOllama.invoke", fail)
    monkeypatch.setattr("langchain_ollama.OllamaEmbeddings.embed_query", fail)
    monkeypatch.setattr("langchain_ollama.OllamaEmbeddings.embed_documents", fail)
    names = ("assistant.config", "assistant.settings", "assistant.index", "assistant.ingest", "assistant.pipeline",
             "assistant.chat")
    for name in names:
        sys.modules.pop(name, None)

    for name in names:
        importlib.import_module(name)


def test_every_index_matches_its_strategy_and_the_current_material():
    """Se falhar, algum índice está ausente ou desatualizado: rode python -m assistant.ingest."""
    from assistant.index import CURRENT, chunks_path, index_state
    from assistant.ingest import build_chunks, load_pages
    from assistant.settings import strategies

    pages = load_pages()
    for strategy in strategies():
        assert index_state(strategy) == (CURRENT, None), strategy.name
        expected = [chunk.page_content for chunk in build_chunks(strategy, pages)]
        with open(chunks_path(strategy.name), encoding="utf-8") as f:
            indexed = [chunk["content"] for chunk in json.load(f)]
        assert indexed == expected, strategy.name


def test_vector_search_by_vector_matches_search_by_text():
    """O pipeline busca com o vetor já calculado; a ordem tem de ser a mesma da busca por texto."""
    from assistant import pipeline
    from assistant.pipeline import RagConfig, retrieve

    config = RagConfig()
    questions = ["Quanto custa o clareamento?", "Quanto tempo leva o implante?", "aparelho fica qnto tempo na boca",
                 "Vocês facilitam o pagamento?", "Qual o endereço da clínica?"]
    for question in questions:
        by_text = pipeline._db(config.strategy).similarity_search(question, k=config.vector_k)
        result = retrieve(question, config)

        assert [chunk.content for chunk in result.vector] == [doc.page_content for doc in by_text], question
        assert all(0 < chunk.similarity <= 1 for chunk in result.fused), question
        # a similarity diminui com a posição na busca vetorial
        similarities = [chunk.similarity for chunk in result.vector]
        assert similarities == sorted(similarities, reverse=True), question


def test_answers_a_price_from_the_right_procedure():
    from assistant.pipeline import RagConfig, answer

    result = answer("Quanto custa o clareamento?", RagConfig())

    assert "500" in result.answer and "1.500" in result.answer
    assert "120" not in result.answer
    assert any("Clareamento Dental" in chunk.content for chunk in result.retrieval.fused)


def test_refuses_what_is_not_in_the_material():
    from assistant.pipeline import NO_ANSWER, RagConfig, answer

    assert NO_ANSWER in answer("Qual o CNPJ da clínica?", RagConfig()).answer


def test_stream_yields_the_same_kind_of_answer():
    from assistant.pipeline import RagConfig, stream_answer

    text = "".join(stream_answer("Quanto custa a limpeza?", RagConfig()))

    assert "120" in text and "250" in text


def test_hyde_generates_a_short_hypothetical_answer():
    from assistant.pipeline import RagConfig, hypothetical_answer

    text = hypothetical_answer("Quanto custa o implante?", RagConfig())

    assert 10 < len(text) < 600


def test_chat_refuses_to_start_without_the_index(monkeypatch, tmp_path, capsys):
    from assistant import chat, index

    monkeypatch.setattr(index, "INDEX_DIR", tmp_path)  # nenhum índice neste diretório
    monkeypatch.setattr(builtins, "input", lambda *args: pytest.fail("o chat não pode abrir sem o índice"))

    code = chat.to_ask()

    assert code == 1
    output = capsys.readouterr().out
    assert "ainda não foi criado" in output and "python -m assistant.ingest section" in output
