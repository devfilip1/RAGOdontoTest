import pytest

from evaluation.aggregate import aggregate, flatten, variance

DEV = ["clareamento-preco-01", "limpeza-preco-01", "dif-atendimento-01", "fora-endereco-01"]


def test_overall_and_answer_metrics(gabarito, make_result):
    results = [
        make_result("clareamento-preco-01", passed=False, unexpected=["R$ 120"]),
        make_result("limpeza-preco-01"),
        make_result("dif-atendimento-01", passed=False, cause="wrong_refusal", abstained=True),
        make_result("fora-endereco-01", passed=False, ungrounded=["R$ 99"], unexpected=["R$ 99"]),
    ]

    metrics = aggregate(results, gabarito.by_id())

    assert metrics["overall"] == {"pass_rate": 0.25, "item_count": 4}
    assert metrics["answer"]["factual_accuracy"] == pytest.approx(1 / 3)
    assert metrics["answer"]["wrong_refusal_rate"] == pytest.approx(1 / 3)
    assert metrics["answer"]["correct_refusal_rate"] == 0.0
    assert metrics["answer"]["faithfulness_numeric"] == 0.75
    assert metrics["answer"]["rule_compliance"] == 1.0
    assert metrics["diagnosis"]["by_cause"] == {
        "retrieval_failure": 0, "answer_failure": 1, "fabricated": 1, "wrong_refusal": 1, "rule_violation": 0,
    }
    assert metrics["diagnosis"]["by_category"] == {"price": 0.5, "differentials": 0.0, "out_of_scope": 0.0}
    assert metrics["diagnosis"]["by_procedure"] == {"clareamento": 0.0, "limpeza": 1.0}


def test_retrieval_metrics_use_only_answerable_items(gabarito, make_result):
    results = [
        make_result("clareamento-preco-01", passed=False, cause="retrieval_failure", hit=False),
        make_result("limpeza-preco-01"),
        make_result("fora-endereco-01"),
    ]

    fused = aggregate(results, gabarito.by_id())["retrieval"]["fused"]

    assert fused["hit_rate"] == 0.5
    assert fused["mrr"] == 0.5
    assert fused["context_precision"] == 0.25


def test_anchored_rate_ignores_items_without_procedure(gabarito, make_result):
    results = [make_result("limpeza-preco-01"), make_result("dif-atendimento-01", hit=False, passed=False)]

    assert aggregate(results, gabarito.by_id())["retrieval"]["fused"]["anchored_rate"] == 1.0


def test_metric_without_items_is_none(gabarito, make_result):
    metrics = aggregate([make_result("fora-endereco-01")], gabarito.by_id())

    assert metrics["answer"]["factual_accuracy"] is None
    assert metrics["retrieval"]["fused"]["hit_rate"] is None
    assert metrics["answer"]["correct_refusal_rate"] == 1.0
    assert metrics["judge"] is None


def test_empty_run_does_not_fail(gabarito):
    metrics = aggregate([], gabarito.by_id())

    assert metrics["overall"] == {"pass_rate": None, "item_count": 0}
    assert metrics["operational"] == {"latency_p50": 0.0, "latency_p95": 0.0}


def test_latency_percentiles(gabarito, make_result):
    results = [make_result(item_id, latency=latency) for item_id, latency in zip(DEV, [1.0, 2.0, 3.0, 10.0])]

    assert aggregate(results, gabarito.by_id())["operational"] == {"latency_p50": 2.0, "latency_p95": 10.0}


def test_judge_scores_ignore_null_verdicts_and_carry_human_agreement(gabarito, make_result):
    def verdicts(tone):
        return {"tone": {"verdict": tone, "reason": ""}, "scheduling": {"verdict": True, "reason": ""}}

    results = [
        make_result("clareamento-preco-01", judge=verdicts(True)),
        make_result("limpeza-preco-01", judge=verdicts(False)),
        make_result("fora-endereco-01", judge=verdicts(None)),
    ]

    judge = aggregate(results, gabarito.by_id(), human_agreement={"tone": 0.9})["judge"]

    assert judge["tone"] == {"score": 0.5, "human_agreement": 0.9}
    assert judge["scheduling"] == {"score": 1.0, "human_agreement": None}


def test_variance_reports_mean_min_and_max(gabarito, make_result):
    first = aggregate([make_result("clareamento-preco-01"), make_result("limpeza-preco-01")], gabarito.by_id())
    second = aggregate(
        [make_result("clareamento-preco-01", passed=False), make_result("limpeza-preco-01")], gabarito.by_id()
    )

    summary = variance([first, second])

    assert summary["overall.pass_rate"] == {"mean": 0.75, "min": 0.5, "max": 1.0}
    assert summary["retrieval.fused.hit_rate"] == {"mean": 1.0, "min": 1.0, "max": 1.0}
    assert "answer.correct_refusal_rate" not in summary


def test_flatten_names(gabarito, make_result):
    flat = flatten(aggregate([make_result("limpeza-preco-01")], gabarito.by_id()))

    assert flat["overall.pass_rate"] == 1.0
    assert "retrieval.vector.mrr" in flat
    assert "answer.rule_compliance" in flat
    assert "operational.latency_p95" in flat
