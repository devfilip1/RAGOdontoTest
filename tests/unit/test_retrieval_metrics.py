import pytest

from evaluation.dataset import Fact, Item
from evaluation.retrieval_metrics import score_retrieval

PRICE = "Investimento: R$ 500 a R$ 1.500"
TIME = "Tempo: Consultório: no mesmo dia | Completo: até 14 dias"

HEADING = "Clareamento Dental – Dentes Brancos em Poucos Dias\nIdeal para quem quer:"
WITH_PRICE = "Como funciona: Gel clareador profissional\nsupervisionado.\nInvestimento: R$ 500 a R$ 1.500"
ANCHORED = HEADING + "\n" + WITH_PRICE
OTHER = "Limpeza Dental\nInvestimento: R$ 120 a R$ 250"


def item(evidence=(PRICE,), answerable=True):
    return Item(
        id="x", question="?", category="price", procedure="clareamento", answerable=answerable,
        split="dev", smoke=False,
        expected_facts=(Fact("money", "preço", (500, 1500)),) if answerable else (),
        evidence=evidence if answerable else (),
    )


def test_evidence_in_first_chunk():
    score = score_retrieval(item(), [ANCHORED, OTHER, OTHER], ["clareamento"])

    assert score == {"hit": True, "recall": 1.0, "mrr": 1.0, "context_precision": pytest.approx(1 / 3), "anchored": True}


def test_evidence_in_third_chunk():
    score = score_retrieval(item(), [OTHER, HEADING, ANCHORED], ["clareamento"])

    assert score["hit"] is True
    assert score["mrr"] == pytest.approx(1 / 3)


def test_evidence_not_retrieved():
    score = score_retrieval(item(), [OTHER, HEADING], ["clareamento"])

    assert score == {"hit": False, "recall": 0.0, "mrr": 0.0, "context_precision": 0.0, "anchored": False}


def test_recall_with_two_evidences_and_one_retrieved():
    score = score_retrieval(item(evidence=(PRICE, TIME)), [ANCHORED, OTHER], ["clareamento"])

    assert score["hit"] is True
    assert score["recall"] == 0.5


def test_context_precision_one_relevant_in_four():
    score = score_retrieval(item(), [OTHER, ANCHORED, HEADING, OTHER], ["clareamento"])

    assert score["context_precision"] == 0.25
    assert score["mrr"] == 0.5


def test_matching_ignores_accents_case_and_line_breaks():
    chunk = "CLAREAMENTO\ninvestimento:\nr$ 500 a r$ 1.500"

    assert score_retrieval(item(), [chunk], ["Clareamento"])["hit"] is True
    assert score_retrieval(item(evidence=("Tempo: Consultorio: no mesmo dia | completo: ate 14 dias",)), [TIME], [])["hit"]


def test_evidence_retrieved_without_the_procedure_name_is_not_anchored():
    score = score_retrieval(item(), [WITH_PRICE, HEADING], ["clareamento"])

    assert score["hit"] is True
    assert score["anchored"] is False


def test_anchor_in_a_different_chunk_does_not_count():
    assert score_retrieval(item(), [HEADING, WITH_PRICE], ["clareamento"])["anchored"] is False


def test_item_without_anchors_is_anchored_when_hit():
    assert score_retrieval(item(), [WITH_PRICE], [])["anchored"] is True


def test_unanswerable_item_has_no_retrieval_score():
    assert score_retrieval(item(answerable=False), [ANCHORED], ["clareamento"]) is None


def test_no_chunks_retrieved():
    assert score_retrieval(item(), [], ["clareamento"])["context_precision"] == 0.0
