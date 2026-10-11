from types import SimpleNamespace

import numpy as np
import pytest
from rank_bm25 import BM25Okapi

from assistant import pipeline
from assistant.pipeline import NO_ANSWER, NO_INFORMATION, RagConfig, build_prompt, retrieve, tokenize
from assistant.settings import Experiment

LIMPEZA = "Limpeza Dental – O Primeiro Passo\nTempo: 30 a 50 minutos\nInvestimento: R$ 120 a R$ 250"
CLAREAMENTO = "Clareamento Dental – Dentes Brancos\nRemover manchas de café\nInvestimento: R$ 500 a R$ 1.500"
APARELHO = "Aparelho Ortodôntico – Sorriso Alinhado\nOpções: Tradicional ou estético\nTempo: 12 a 36 meses"
IMPLANTE = "Implante Dentário – Dente de Volta\nComo funciona: Pino de titânio\nTempo: 3 a 6 meses"
DOCUMENTS = [LIMPEZA, CLAREAMENTO, APARELHO, IMPLANTE]

# Embeddings falsos em 2 dimensões. O vetor da pergunta é sempre (1, 0), então a similarity de cada
# trecho é o primeiro componente do vetor dele (com norma 1).
VECTORS = {
    LIMPEZA: np.array([0.9, np.sqrt(1 - 0.81)]),
    CLAREAMENTO: np.array([0.8, 0.6]),
    IMPLANTE: np.array([0.6, 0.8]),
    APARELHO: np.array([0.3, np.sqrt(1 - 0.09)]),
}
SIMILARITY = {LIMPEZA: 0.9, CLAREAMENTO: 0.8, IMPLANTE: 0.6, APARELHO: 0.3}


def config(search_type="hybrid", match_count=4, match_threshold=0.0, use_hyde=False):
    return RagConfig(experiment="teste", strategy="fake", search_type=search_type, match_count=match_count,
                     match_threshold=match_threshold, use_hyde=use_hyde)


@pytest.fixture
def index(monkeypatch):
    """Índice em memória. Registra o que foi pedido a cada busca e aos modelos."""
    calls = SimpleNamespace(vector_k=[], bm25=0, embedded=[], hyde=[])

    class FakeDb:
        def similarity_search_by_vector(self, embedding, k):
            calls.vector_k.append(k)
            assert list(embedding) == [1.0, 0.0]
            ranked = sorted(DOCUMENTS, key=lambda content: -SIMILARITY[content])
            return [SimpleNamespace(page_content=content) for content in ranked[:k]]

    class FakeEmbeddings:
        def embed_query(self, text):
            calls.embedded.append(("query", text))
            return [2.0, 0.0]  # sem norma 1 de propósito: o pipeline precisa normalizar

        def embed_documents(self, texts):
            calls.embedded.append(("document", texts[0]))
            return [[2.0, 0.0]]

    def fake_bm25(strategy):
        calls.bm25 += 1
        return BM25Okapi([tokenize(d) for d in DOCUMENTS]), DOCUMENTS

    def fake_hyde(question, cfg):
        calls.hyde.append(question)
        return "O aparelho ortodôntico fica de 12 a 36 meses."

    monkeypatch.setattr(pipeline, "_db", lambda strategy: FakeDb())
    monkeypatch.setattr(pipeline, "_bm25", fake_bm25)
    monkeypatch.setattr(pipeline, "_vectors", lambda strategy: VECTORS)
    monkeypatch.setattr(pipeline, "EMBEDDINGS", FakeEmbeddings())
    monkeypatch.setattr(pipeline, "hypothetical_answer", fake_hyde)
    return calls


# --- tokenização ---

def test_tokenize_removes_accents_punctuation_stopwords_and_plural():
    assert tokenize("Quanto custa o Clareamento?") == ["custa", "clareamento"]
    assert tokenize("Quantas sessões são necessárias para as lentes?") == ["sessao", "necessaria", "lente"]


def test_tokenize_expands_customer_words_into_document_words():
    assert tokenize("Quanto custa o clareamento?", expand=True) == ["custa", "investimento", "clareamento"]
    assert "tempo" in tokenize("quanto demora?", expand=True)


def test_documents_are_not_expanded():
    assert tokenize("o valor do investimento") == ["valor", "investimento"]


# --- configuração a partir do experimento ---

def test_config_from_experiment():
    experiment = Experiment("page_vector", "page", "vector", 3, 0.5, True)

    cfg = RagConfig.from_experiment(experiment, seed=42)

    assert (cfg.experiment, cfg.strategy, cfg.search_type) == ("page_vector", "page", "vector")
    assert (cfg.match_count, cfg.match_threshold, cfg.use_hyde, cfg.seed) == (3, 0.5, True, 42)


@pytest.mark.parametrize(
    "search_type, match_count, expected",
    [
        ("hybrid", 4, (2, 2, 4)),
        ("hybrid", 5, (3, 3, 5)),
        ("hybrid", 1, (1, 1, 1)),
        ("vector", 4, (4, 0, 4)),
        ("bm25", 4, (0, 4, 4)),
    ],
)
def test_search_sizes_come_from_match_count(search_type, match_count, expected):
    cfg = config(search_type, match_count)

    assert (cfg.vector_k, cfg.bm25_k, cfg.final_k) == expected


def test_default_config_uses_the_assistant_experiment():
    from assistant.settings import assistant_experiment

    cfg, experiment = RagConfig(), assistant_experiment()

    assert (cfg.experiment, cfg.strategy) == (experiment.exp_name, experiment.collection)
    assert (cfg.search_type, cfg.match_count) == (experiment.search_type, experiment.match_count)
    assert (cfg.match_threshold, cfg.use_hyde) == (experiment.match_threshold, experiment.use_hyde)


# --- busca híbrida e fusão ---

def test_chunk_found_by_both_searches_comes_first(index):
    result = retrieve("Quanto custa o clareamento?", config())

    assert [chunk.content for chunk in result.vector] == [LIMPEZA, CLAREAMENTO]
    assert result.bm25[0].content == CLAREAMENTO
    assert result.fused[0].content == CLAREAMENTO
    assert [chunk.rank for chunk in result.fused] == list(range(1, len(result.fused) + 1))


def test_each_search_contributes_even_when_the_other_misses(index):
    result = retrieve("aparelho fica quanto tempo", config())  # a vetorial põe o aparelho por último

    assert result.bm25[0].content == APARELHO
    assert APARELHO in [chunk.content for chunk in result.fused]
    assert LIMPEZA in [chunk.content for chunk in result.fused]


def test_match_count_limits_what_goes_to_the_model(index):
    result = retrieve("aparelho clareamento implante limpeza", config(match_count=3))

    assert index.vector_k == [2]
    assert len(result.fused) == 3


def test_lexical_search_drops_chunks_without_any_matching_word(index):
    result = retrieve("xyzabc", config())

    assert result.bm25 == []
    assert [chunk.content for chunk in result.fused] == [LIMPEZA, CLAREAMENTO]


# --- similarity ---

def test_every_chunk_has_the_cosine_similarity_to_the_search_vector(index):
    result = retrieve("aparelho fica quanto tempo", config())

    for chunks in (result.vector, result.bm25, result.fused):
        assert chunks
        for chunk in chunks:
            assert chunk.similarity == pytest.approx(SIMILARITY[chunk.content])


def test_chunk_found_only_by_words_also_has_similarity(index):
    result = retrieve("aparelho fica quanto tempo", config())

    aparelho = next(chunk for chunk in result.fused if chunk.content == APARELHO)
    assert APARELHO not in [chunk.content for chunk in result.vector]
    assert aparelho.similarity == pytest.approx(0.3)


def test_question_is_embedded_once(index):
    retrieve("Quanto custa o clareamento?", config())

    assert index.embedded == [("query", "Quanto custa o clareamento?")]


# --- tipos de busca ---

def test_vector_search_does_not_use_words(index):
    result = retrieve("aparelho fica quanto tempo", config("vector", 3))

    assert index.bm25 == 0 and index.vector_k == [3]
    assert result.bm25 == []
    assert [chunk.content for chunk in result.fused] == [LIMPEZA, CLAREAMENTO, IMPLANTE]


def test_word_search_does_not_use_the_vector_index_but_has_similarity(index):
    result = retrieve("aparelho fica quanto tempo", config("bm25", 2))

    assert index.vector_k == []
    assert result.vector == []
    assert result.fused[0].content == APARELHO
    assert result.fused[0].similarity == pytest.approx(0.3)


# --- threshold ---

def test_threshold_zero_keeps_everything(index):
    assert len(retrieve("aparelho fica quanto tempo", config()).fused) == 4


def test_threshold_drops_chunks_below_and_keeps_the_ones_equal(index):
    result = retrieve("aparelho fica quanto tempo", config(match_threshold=0.8))

    assert [chunk.content for chunk in result.fused] == [LIMPEZA, CLAREAMENTO]
    assert [chunk.rank for chunk in result.fused] == [1, 2]
    assert APARELHO in [chunk.content for chunk in result.bm25]  # o corte é só no que vai para o modelo


def test_threshold_above_every_similarity_returns_nothing(index):
    assert retrieve("Quanto custa o clareamento?", config(match_threshold=0.95)).fused == []


# --- HyDE ---

def test_hyde_searches_with_the_hypothetical_answer_and_words_with_the_question(index):
    result = retrieve("aparelho fica quanto tempo", config(use_hyde=True))

    assert index.hyde == ["aparelho fica quanto tempo"]
    assert index.embedded == [("document", "O aparelho ortodôntico fica de 12 a 36 meses.")]
    assert result.bm25[0].content == APARELHO


def test_without_hyde_the_generation_model_is_not_called(index):
    retrieve("aparelho fica quanto tempo", config())

    assert index.hyde == []


# --- prompt ---

def chunks(*contents):
    return SimpleNamespace(fused=[SimpleNamespace(content=content, rank=rank) for rank, content in enumerate(contents, 1)])


def test_prompt_has_rules_in_system_and_material_before_the_question():
    system, human = build_prompt("Quanto custa a limpeza?", chunks(LIMPEZA, IMPLANTE), config()).to_messages()

    assert system.type == "system" and human.type == "human"
    assert NO_ANSWER in system.content
    assert "{" not in system.content
    assert human.content.index(LIMPEZA) < human.content.index("---") < human.content.index(IMPLANTE)
    assert human.content.rstrip().endswith("Quanto custa a limpeza?")


def test_prompt_without_chunks_says_there_is_no_information():
    _, human = build_prompt("Quanto custa a limpeza?", chunks(), config()).to_messages()

    assert NO_INFORMATION in human.content
    assert human.content.rstrip().endswith("Quanto custa a limpeza?")


def test_refusal_phrase_is_recognized_by_the_evaluation():
    from evaluation.answer_metrics import detect_abstention

    assert detect_abstention(NO_ANSWER)
