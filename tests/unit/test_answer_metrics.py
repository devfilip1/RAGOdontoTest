import json
from pathlib import Path

import pytest

from evaluation.answer_metrics import (
    MAX_ANSWER_CHARS,
    check_facts,
    check_rules,
    detect_abstention,
    factual_ok,
    unexpected_values,
    ungrounded_values,
)
from evaluation.dataset import Fact

EXAMPLES = json.loads((Path(__file__).parents[1] / "fixtures" / "factual_examples.json").read_text(encoding="utf-8"))


def _facts(raw):
    return [
        Fact(f["type"], f["label"], tuple(f.get("values", ())), f.get("unit"), tuple(f.get("alternatives", ())))
        for f in raw
    ]


def test_fixture_has_the_twenty_examples_of_sc009():
    assert len(EXAMPLES) == 20


@pytest.mark.parametrize("example", EXAMPLES, ids=[e["name"] for e in EXAMPLES])
def test_factual_examples(example):
    verdict = factual_ok(
        example["answer"], _facts(example["expected_facts"]), _facts(example.get("allowed_facts", []))
    )

    assert verdict is example["expected_verdict"]


def test_check_facts_reports_each_fact():
    facts = _facts([
        {"type": "money", "label": "valor inicial", "values": [500, 1500]},
        {"type": "money", "label": "mensalidade", "values": [100, 300]},
    ])

    assert check_facts("A entrada é de R$ 500 a R$ 1.500.", facts) == [
        {"label": "valor inicial", "found": True},
        {"label": "mensalidade", "found": False},
    ]


def test_unexpected_values_respects_kinds():
    known = _facts([{"type": "money", "label": "preço", "values": [2500, 6000]}])
    answer = "O implante custa R$ 2.500 a R$ 6.000 e requer 2 a 3 consultas."

    assert unexpected_values(answer, known, kinds={"money"}) == []
    assert unexpected_values(answer, known) == ["2 consultas", "3 consultas"]


@pytest.mark.parametrize(
    "answer",
    [
        "Não encontrei essa informação no sistema.",
        "nao encontrei essa informacao no sistema",
        "Infelizmente NÃO ENCONTREI essa informação. Posso ajudar com outra dúvida?",
        "O implante não é mencionado entre os procedimentos.",
    ],
)
def test_detect_abstention(answer):
    assert detect_abstention(answer)


def test_normal_answer_is_not_abstention():
    assert not detect_abstention("O clareamento custa de R$ 500 a R$ 1.500. Vamos agendar sua avaliação?")


# --- fidelidade numérica (US2) ---

CHUNKS = ["Clareamento Dental\nInvestimento: R$ 500 a R$ 1.500\nTempo: Completo: até 14 dias"]


def test_values_present_in_chunks_are_grounded():
    assert ungrounded_values("Custa de R$ 500 a R$ 1.500.", CHUNKS) == []


def test_value_absent_from_chunks_is_ungrounded():
    assert ungrounded_values("Custa R$ 500, com desconto fica R$ 399.", CHUNKS) == ["R$ 399"]


def test_same_value_in_another_format_is_grounded():
    assert ungrounded_values("Custa até mil e quinhentos reais e leva 2 semanas.", CHUNKS) == []


# --- regras de atendimento (US4) ---

@pytest.mark.parametrize(
    "answer, violation",
    [
        ("De acordo com o contexto, custa R$ 500.", "forbidden_term:contexto"),
        ("Segundo o DOCUMENTO fornecido, custa R$ 500.", "forbidden_term:documento"),
        ("Não achei nos documentos.", "forbidden_term:documento"),
        ("Isso não está na minha base de dados.", "forbidden_term:base de dados"),
    ],
)
def test_forbidden_terms(answer, violation):
    assert check_rules(answer) == [violation]


def test_similar_words_are_not_forbidden():
    assert check_rules("Traga sua documentação e venha conhecer a clínica, sem pretexto para adiar.") == []


def test_too_long_answer():
    assert "too_long" in check_rules("O clareamento é ótimo para você. " * (MAX_ANSWER_CHARS // 30 + 2))


def test_answer_in_english():
    assert check_rules("The whitening treatment is the best option for you and your smile.") == ["not_portuguese"]


def test_clean_answer_has_no_violations():
    assert check_rules("O clareamento custa de R$ 500 a R$ 1.500. Vamos agendar sua avaliação?") == []
