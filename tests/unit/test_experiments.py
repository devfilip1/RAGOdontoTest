import csv
import time
from datetime import datetime
from types import SimpleNamespace

import pytest

from evaluation import experiments as bench
from assistant.settings import Experiment

SECTION = Experiment("section_hybrid", "section", "hybrid", 4)
PAGE = Experiment("page_hybrid", "page", "hybrid", 4, 0.5, True)
RECURSIVE = Experiment("recursive_hybrid", "recursive_500_200", "hybrid", 4)

# Trechos do material falso, por pergunta do gabarito de conftest.py
CLAREAMENTO = "Clareamento Dental\nInvestimento: R$ 500 a R$ 1.500"
LIMPEZA = "Limpeza Dental\nTempo: 30 a 50 minutos\nInvestimento: R$ 120 a R$ 250"
PRICE_ONLY = "Como funciona: gel clareador\nInvestimento: R$ 500 a R$ 1.500"
DIFFERENTIALS = "Por Que Escolher a OdontoTest?\n- Atendimento rápido (até 72h)"


def chunk(content, similarity):
    return SimpleNamespace(content=content, rank=1, score=None, similarity=similarity)


def retrieval(*chunks):
    chunks = [SimpleNamespace(content=c.content, rank=rank, score=None, similarity=c.similarity)
              for rank, c in enumerate(chunks, 1)]
    return SimpleNamespace(vector=chunks, bm25=chunks, fused=chunks)


def to_dataclass(namespace):
    """asdict() do módulo exige dataclass; converte os trechos falsos."""
    from assistant.pipeline import RetrievalResult, RetrievedChunk

    convert = lambda items: [RetrievedChunk(c.content, c.rank, c.score, c.similarity) for c in items]  # noqa: E731
    return RetrievalResult(convert(namespace.vector), convert(namespace.bm25), convert(namespace.fused))


ANSWERS = {
    "Quanto custa o clareamento?": [chunk(CLAREAMENTO, 0.8), chunk(LIMPEZA, 0.6)],
    "Quanto custa a limpeza?": [chunk(LIMPEZA, 0.7)],
    "Em quanto tempo sou atendido?": [chunk(DIFFERENTIALS, 0.5)],
}


def retrieve_all(question, experiment):
    return to_dataclass(retrieval(*ANSWERS.get(question, [])))


def no_index_problem(experiment):
    return None


def run(experiment=SECTION, gabarito=None, retrieve_fn=retrieve_all, **options):
    options.setdefault("index_check", no_index_problem)
    return bench.run_experiment(experiment, bench.select_items(gabarito), gabarito, retrieve_fn=retrieve_fn, **options)


def test_only_answerable_dev_questions_are_evaluated(gabarito):
    ids = [item.id for item in bench.select_items(gabarito)]

    assert ids == ["clareamento-preco-01", "limpeza-preco-01", "dif-atendimento-01"]
    assert "limpeza-tempo-01" not in ids  # parte reservada
    assert "fora-endereco-01" not in ids  # sem resposta no material


def test_experiment_metrics(gabarito):
    result = run(gabarito=gabarito)

    assert result.status == bench.OK
    assert (result.hits, result.total) == (3, 3)
    assert result.true_rate == 1.0
    assert result.score == pytest.approx((0.7 + 0.7 + 0.5) / 3)  # a 1ª pergunta tem média de 0.8 e 0.6
    assert result.anchored_rate == 1.0
    assert result.avg_latency_ms >= 0
    assert [q.retrieved_count for q in result.questions] == [2, 1, 1]


def test_question_score_is_the_mean_similarity_of_the_returned_chunks(gabarito):
    question = run(gabarito=gabarito).questions[0]

    assert question.item_id == "clareamento-preco-01"
    assert question.hit is True
    assert question.score == pytest.approx(0.7)


def test_question_without_chunks_is_a_miss_with_zero_score(gabarito):
    result = run(gabarito=gabarito, retrieve_fn=lambda question, experiment: to_dataclass(retrieval()))

    assert result.status == bench.OK
    assert (result.hits, result.total, result.score) == (0, 3, 0.0)
    assert all(q.retrieved_count == 0 and q.score == 0.0 and not q.hit for q in result.questions)


def test_hit_needs_every_evidence_of_the_item(gabarito):
    from dataclasses import replace

    both = replace(gabarito.by_id()["clareamento-preco-01"], id="comp-01", procedure=None,
                   evidence=("Investimento: R$ 500 a R$ 1.500", "Investimento: R$ 120 a R$ 250"))

    def one_of_two(question, experiment):
        return to_dataclass(retrieval(chunk(CLAREAMENTO, 0.8)))

    def two_of_two(question, experiment):
        return to_dataclass(retrieval(chunk(CLAREAMENTO, 0.8), chunk(LIMPEZA, 0.6)))

    partial = bench.run_experiment(SECTION, [both], gabarito, retrieve_fn=one_of_two, index_check=no_index_problem)
    complete = bench.run_experiment(SECTION, [both], gabarito, retrieve_fn=two_of_two, index_check=no_index_problem)

    assert partial.questions[0].hit is False
    assert complete.questions[0].hit is True


def test_anchored_rate_counts_only_questions_about_a_procedure(gabarito):
    def unanchored(question, experiment):
        if "clareamento" in question:
            return to_dataclass(retrieval(chunk(PRICE_ONLY, 0.8)))
        return retrieve_all(question, experiment)

    result = run(gabarito=gabarito, retrieve_fn=unanchored)

    assert result.hits == 3
    assert result.questions[0].anchored is False
    assert result.anchored_rate == 0.5  # clareamento não, limpeza sim; a pergunta geral fica fora


def test_warm_up_call_is_not_measured(gabarito):
    calls = []

    def slow_first(question, experiment):
        calls.append(question)
        if len(calls) == 1:
            time.sleep(0.2)
        return retrieve_all(question, experiment)

    result = run(gabarito=gabarito, retrieve_fn=slow_first)

    assert calls[0] == "Olá" and len(calls) == 4
    assert result.avg_latency_ms < 100


def test_latency_includes_everything_the_search_does(gabarito):
    def slow(question, experiment):
        time.sleep(0.05)  # como a geração do HyDE dentro da busca
        return retrieve_all(question, experiment)

    assert run(gabarito=gabarito, retrieve_fn=slow).avg_latency_ms >= 50


def test_missing_or_stale_index_is_not_run_and_does_not_search(gabarito):
    calls = []
    reason = "o índice da estratégia \"page\" ainda não foi criado; rode: python -m assistant.ingest page"

    result = run(PAGE, gabarito, retrieve_fn=lambda q, e: calls.append(q), index_check=lambda experiment: reason)

    assert (result.status, result.reason) == (bench.NOT_RUN, reason)
    assert result.questions == [] and calls == []


def test_one_experiment_that_cannot_run_does_not_stop_the_others(gabarito):
    results = bench.run_all(
        [PAGE, SECTION], bench.select_items(gabarito), gabarito, retrieve_fn=retrieve_all,
        index_check=lambda experiment: "índice ausente" if experiment is PAGE else None,
    )

    assert [result.status for result in results] == [bench.NOT_RUN, bench.OK]


def test_failure_at_warm_up_is_not_run(gabarito):
    def offline(question, experiment):
        raise ConnectionError("Ollama fora do ar")

    result = run(gabarito=gabarito, retrieve_fn=offline)

    assert result.status == bench.NOT_RUN
    assert "Ollama fora do ar" in result.reason


def test_failure_in_the_middle_is_incomplete_and_keeps_what_finished(gabarito):
    def fails_on_the_second(question, experiment):
        if "limpeza" in question:
            raise ConnectionError("Ollama caiu")
        return retrieve_all(question, experiment)

    result = run(gabarito=gabarito, retrieve_fn=fails_on_the_second)

    assert result.status == bench.INCOMPLETE
    assert [q.item_id for q in result.questions] == ["clareamento-preco-01"]
    assert "1 de 3" in result.reason and "Ollama caiu" in result.reason


def test_progress_and_question_callbacks(gabarito):
    progress, seen = [], []

    run(gabarito=gabarito, on_progress=lambda: progress.append(1), on_question=seen.append)

    assert len(progress) == 3
    assert [q.item_id for q in seen] == ["clareamento-preco-01", "limpeza-preco-01", "dif-atendimento-01"]


def result_with(experiment, hits, total, score, status=bench.OK, reason=""):
    questions = [
        bench.QuestionResult(experiment.exp_name, f"item-{n}", f"Pergunta {n}?", n < hits, score, True, 2, 40.0)
        for n in range(total)
    ]
    return bench.ExperimentResult(experiment, status, reason, questions)


def test_sorted_by_true_rate_then_score_then_name():
    a = result_with(Experiment("b_exp", "section", "hybrid", 4), 3, 4, 0.60)
    b = result_with(Experiment("a_exp", "section", "hybrid", 4), 3, 4, 0.60)
    best = result_with(Experiment("z_exp", "section", "hybrid", 4), 4, 4, 0.10)
    higher_score = result_with(Experiment("c_exp", "section", "hybrid", 4), 3, 4, 0.90)

    ordered = bench.sort_results([a, b, best, higher_score])

    assert [r.experiment.exp_name for r in ordered] == ["z_exp", "c_exp", "a_exp", "b_exp"]


def test_hyde_does_not_win_a_tie_with_its_inflated_score():
    plain = result_with(Experiment("section_hybrid", "section", "hybrid", 4), 3, 4, 0.67)
    hyde = result_with(Experiment("section_hyde", "section", "hybrid", 4, 0.0, True), 3, 4, 0.78)
    better_hyde = result_with(Experiment("better_hyde", "section", "hybrid", 4, 0.0, True), 4, 4, 0.78)

    ordered = bench.sort_results([hyde, plain, better_hyde])

    assert [r.experiment.exp_name for r in ordered] == ["better_hyde", "section_hybrid", "section_hyde"]


def test_experiments_that_did_not_finish_go_last():
    not_run = bench.ExperimentResult(PAGE, bench.NOT_RUN, "índice ausente")
    incomplete = result_with(RECURSIVE, 1, 1, 0.9, bench.INCOMPLETE, "interrompido")
    ok = result_with(SECTION, 0, 2, 0.1)

    ordered = bench.sort_results([not_run, incomplete, ok])

    assert [r.status for r in ordered] == [bench.OK, bench.NOT_RUN, bench.INCOMPLETE]


def test_question_line_format():
    hit = bench.QuestionResult("e", "i", "Quanto custa o clareamento?", True, 0.7149, True, 2, 40.0)
    miss = bench.QuestionResult("e", "i", "Os tratamentos doem?", False, 0.6, False, 2, 40.0)

    assert bench.format_question_line(hit) == "Quanto custa o clareamento?;true;0.71"
    assert bench.format_question_line(miss) == "Os tratamentos doem?;false;0.60"


def read(path):
    raw = path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")  # BOM, para o Excel abrir com acentos
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def test_csv_files(tmp_path):
    results = [
        result_with(SECTION, 3, 4, 0.66125),
        bench.ExperimentResult(PAGE, bench.NOT_RUN, "índice ausente; rode: python -m assistant.ingest page"),
    ]
    started_at = datetime(2026, 10, 10, 23, 5, 9)

    summary_path, questions_path = bench.write_csv(results, started_at, "2026-10-10.1", "nomic-embed-text", tmp_path)

    assert summary_path.name == "20261010-230509-summary.csv"
    assert questions_path.name == "20261010-230509-questions.csv"

    summary = read(summary_path)
    assert tuple(summary[0]) == bench.SUMMARY_COLUMNS
    assert summary[0] == {
        "experiment": "section_hybrid", "search_type": "hybrid", "collection": "section", "match_threshold": "0.00",
        "match_count": "4", "use_hyde": "false", "score": "0.6613", "hits": "3", "total": "4", "true_rate": "0.7500",
        "anchored_rate": "1.0000", "avg_latency_ms": "40.0", "status": "ok", "reason": "",
        "gabarito_version": "2026-10-10.1", "embedding_model": "nomic-embed-text",
    }
    assert summary[1]["experiment"] == "page_hybrid"
    assert (summary[1]["match_threshold"], summary[1]["use_hyde"]) == ("0.50", "true")
    assert (summary[1]["status"], summary[1]["score"], summary[1]["hits"]) == ("not_run", "", "")
    assert "python -m assistant.ingest page" in summary[1]["reason"]

    questions = read(questions_path)
    assert tuple(questions[0]) == bench.QUESTION_COLUMNS
    assert len(questions) == 4  # só o experimento que rodou tem linhas
    assert questions[0] == {
        "experiment": "section_hybrid", "item_id": "item-0", "question": "Pergunta 0?", "hit": "true",
        "score": "0.6613", "anchored": "true", "retrieved_count": "2", "latency_ms": "40.0",
    }
    assert questions[3]["hit"] == "false"


def test_two_runs_do_not_overwrite_each_other(tmp_path):
    started_at = datetime(2026, 10, 10, 23, 5, 9)
    results = [result_with(SECTION, 1, 1, 0.5)]

    first, _ = bench.write_csv(results, started_at, "v", "m", tmp_path)
    second, second_questions = bench.write_csv(results, started_at, "v", "m", tmp_path)

    assert first != second and first.exists() and second.exists()
    assert second.name == "20261010-230509-2-summary.csv"
    assert second_questions.name == "20261010-230509-2-questions.csv"


def test_comparison_table_has_the_reference_columns_and_keeps_full_names():
    from evaluation.report import experiments_table

    lines = experiments_table([
        result_with(Experiment("recursive_500_200_hybrid", "recursive_500_200", "hybrid", 4), 31, 38, 0.67),
        bench.ExperimentResult(PAGE, bench.NOT_RUN, "índice ausente"),
    ])

    header = [cell.strip() for cell in lines[1].strip("|").split("|")]
    assert header == ["Experiment", "Strategy", "Collection", "Threshold", "Count", "HyDE", "Score", "True Rate",
                      "Anchored", "Time"]
    first = [cell.strip() for cell in lines[3].strip("|").split("|")]
    assert first == ["recursive_500_200_hybrid", "hybrid", "recursive_500_200", "0.00", "4", "False", "0.67",
                     "31/38", "100.0%", "40 ms"]
    second = [cell.strip() for cell in lines[4].strip("|").split("|")]
    assert second == ["page_hybrid", "hybrid", "page", "0.50", "4", "True", "-", "-", "-", "-"]
    assert len({len(line) for line in lines}) == 1
