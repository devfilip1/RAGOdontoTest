from dataclasses import dataclass
from types import SimpleNamespace

from evaluation.runner import FactIndex, evaluate_item, run_evaluation

CLAREAMENTO = "Clareamento Dental\nInvestimento: R$ 500 a R$ 1.500"
MIXED = "Limpeza\nInvestimento: R$ 120 a R$ 250\nClareamento Dental – Dentes Brancos"


@dataclass
class Chunk:
    """Mesmo formato de assistant.pipeline.RetrievedChunk, sem importar o pipeline."""
    content: str
    rank: int
    score: float | None = None


def answer_result(text, chunks=(CLAREAMENTO,), latency=1.234):
    retrieved = [Chunk(content, rank, 0.5) for rank, content in enumerate(chunks, 1)]
    retrieval = SimpleNamespace(vector=retrieved, bm25=retrieved, fused=retrieved)
    return SimpleNamespace(answer=text, retrieval=retrieval, latency_s=latency)


def evaluate(gabarito, item_id, text, chunks=(CLAREAMENTO,), judge_fn=None):
    item = gabarito.by_id()[item_id]
    return evaluate_item(item, answer_result(text, chunks), gabarito, FactIndex(gabarito), judge_fn)


def test_right_answer_passes(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01", "O clareamento custa de R$ 500 a R$ 1.500.")

    assert result["passed"] is True
    assert result["cause"] is None
    assert result["facts"] == [{"label": "preço", "found": True}]
    assert result["retrieval"]["fused"]["hit"] is True
    assert result["latency_s"] == 1.234


def test_known_error_price_of_another_procedure(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01", "O clareamento custa de R$ 120 a R$ 250.",
                      chunks=(MIXED, CLAREAMENTO))

    assert result["passed"] is False
    assert result["unexpected_values"] == ["R$ 120", "R$ 250"]
    assert result["cause"] == "answer_failure"
    assert result["flags"] == ["other_procedure_value"]


def test_right_value_plus_value_of_another_procedure_fails(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01",
                      "Custa de R$ 500 a R$ 1.500. A limpeza sai por R$ 120 a R$ 250.", chunks=(MIXED, CLAREAMENTO))

    assert result["passed"] is False
    assert result["facts"] == [{"label": "preço", "found": True}]


def test_other_facts_of_the_same_procedure_are_allowed(gabarito):
    result = evaluate(gabarito, "limpeza-preco-01", "A limpeza custa de R$ 120 a R$ 250 e leva de 30 a 50 minutos.",
                      chunks=("Limpeza Dental\nTempo: 30 a 50 minutos\nInvestimento: R$ 120 a R$ 250",))

    assert result["passed"] is True


def test_clinic_differentials_are_allowed_in_any_answer(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01",
                      "Custa de R$ 500 a R$ 1.500 e você é atendido em até 72h.",
                      chunks=(CLAREAMENTO, "Atendimento rápido (até 72h)"))

    assert result["passed"] is True


def test_evidence_not_retrieved_is_retrieval_failure(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01", "Não encontrei essa informação no sistema.", chunks=(MIXED,))

    assert result["passed"] is False
    assert result["abstained"] is True
    assert result["cause"] == "retrieval_failure"


def test_value_outside_the_chunks_is_fabricated(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01", "O clareamento custa R$ 399.")

    assert result["ungrounded_values"] == ["R$ 399"]
    assert result["cause"] == "fabricated"


def test_unanswerable_question_refused_passes(gabarito):
    result = evaluate(gabarito, "fora-endereco-01", "Não encontrei essa informação no sistema.")

    assert result["passed"] is True
    assert result["retrieval"] is None


def test_unanswerable_question_answered_is_fabricated(gabarito):
    result = evaluate(gabarito, "fora-endereco-01", "Ficamos na Rua das Flores, 123.")

    assert result["passed"] is False
    assert result["cause"] == "fabricated"


def test_rule_violation_fails_an_otherwise_right_answer(gabarito):
    result = evaluate(gabarito, "clareamento-preco-01", "Segundo o contexto, custa de R$ 500 a R$ 1.500.")

    assert result["passed"] is False
    assert result["rule_violations"] == ["forbidden_term:contexto"]
    assert result["cause"] == "rule_violation"


def test_judge_verdicts_are_stored_and_do_not_change_passed(gabarito):
    def judge(question, answer, chunks):
        return {"tone": {"verdict": False, "reason": "seco"}}

    result = evaluate(gabarito, "clareamento-preco-01", "Custa de R$ 500 a R$ 1.500.", judge_fn=judge)

    assert result["judge"] == {"tone": {"verdict": False, "reason": "seco"}}
    assert result["passed"] is True


def test_run_evaluation_complete_with_repetitions(gabarito):
    calls = []

    def answer_fn(question, config):
        calls.append(question)
        return answer_result("Não encontrei essa informação no sistema.")

    progress = []
    outcome = run_evaluation(list(gabarito.items), gabarito, None, repeat=2,
                             on_progress=lambda: progress.append(1), answer_fn=answer_fn)

    assert outcome["status"] == "complete"
    assert outcome["skipped"] == []
    assert [len(results) for results in outcome["repetitions"]] == [5, 5]
    assert len(calls) == len(progress) == 10


def test_judge_runs_only_on_the_first_repetition(gabarito):
    judged = []

    def judge(question, answer, chunks):
        judged.append(question)
        return {"tone": {"verdict": True, "reason": ""}}

    run_evaluation(list(gabarito.items), gabarito, None, judge_fn=judge, repeat=2,
                   answer_fn=lambda question, config: answer_result("Não encontrei essa informação."))

    assert len(judged) == 5


def test_service_failure_makes_the_run_incomplete(gabarito):
    def answer_fn(question, config):
        if "limpeza" in question and "tempo" in question.lower():
            raise ConnectionError("Ollama fora do ar")
        return answer_result("Não encontrei essa informação no sistema.")

    outcome = run_evaluation(list(gabarito.items), gabarito, None, answer_fn=answer_fn)

    assert outcome["status"] == "incomplete"
    assert outcome["skipped"] == ["limpeza-tempo-01", "dif-atendimento-01", "fora-endereco-01"]
    assert len(outcome["repetitions"][0]) == 2
    assert "Ollama fora do ar" in outcome["error"]


def test_interruption_makes_the_run_incomplete(gabarito):
    def answer_fn(question, config):
        raise KeyboardInterrupt

    outcome = run_evaluation(list(gabarito.items), gabarito, None, answer_fn=answer_fn)

    assert outcome["status"] == "incomplete"
    assert len(outcome["skipped"]) == 5
