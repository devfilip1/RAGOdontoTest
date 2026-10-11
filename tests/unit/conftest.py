import pytest

from evaluation.aggregate import aggregate
from evaluation.dataset import Fact, Gabarito, Item

ITEMS = (
    Item(id="clareamento-preco-01", question="Quanto custa o clareamento?", category="price",
         procedure="clareamento", answerable=True, split="dev", smoke=True,
         expected_facts=(Fact("money", "preço", (500, 1500)),), evidence=("Investimento: R$ 500 a R$ 1.500",)),
    Item(id="limpeza-preco-01", question="Quanto custa a limpeza?", category="price",
         procedure="limpeza", answerable=True, split="dev", smoke=False,
         expected_facts=(Fact("money", "preço", (120, 250)),), evidence=("Investimento: R$ 120 a R$ 250",)),
    Item(id="limpeza-tempo-01", question="Quanto tempo demora a limpeza?", category="duration",
         procedure="limpeza", answerable=True, split="holdout", smoke=False,
         expected_facts=(Fact("duration", "tempo", (30, 50), "minute"),), evidence=("Tempo: 30 a 50 minutos",)),
    Item(id="dif-atendimento-01", question="Em quanto tempo sou atendido?", category="differentials",
         procedure=None, answerable=True, split="dev", smoke=False,
         expected_facts=(Fact("duration", "prazo", (72,), "hour"),), evidence=("Atendimento rápido (até 72h)",)),
    Item(id="fora-endereco-01", question="Qual o endereço?", category="out_of_scope",
         procedure=None, answerable=False, split="dev", smoke=False),
)


@pytest.fixture
def gabarito():
    return Gabarito(
        version="teste", hash="hash-teste",
        procedures={"clareamento": ["clareamento"], "limpeza": ["limpeza"]},
        items=ITEMS,
    )


@pytest.fixture
def make_result(gabarito):
    """Resultado por pergunta, no formato do run.schema.json."""
    items = gabarito.by_id()

    def factory(item_id, passed=True, cause=None, hit=True, latency=1.0, abstained=None, judge=None,
                unexpected=(), ungrounded=(), violations=()):
        item = items[item_id]
        if not passed and cause is None:
            cause = "answer_failure" if item.answerable else "fabricated"
        score = {"hit": hit, "recall": float(hit), "mrr": float(hit), "context_precision": 0.5 if hit else 0.0,
                 "anchored": hit}
        chunk = {"content": "trecho", "rank": 1, "score": 0.5}
        return {
            "item_id": item_id,
            "answer": "resposta",
            "retrieved": {"vector": [chunk], "bm25": [chunk], "fused": [chunk]},
            "retrieval": {"vector": dict(score), "bm25": dict(score), "fused": dict(score)} if item.answerable else None,
            "facts": [{"label": fact.label, "found": passed} for fact in item.expected_facts],
            "unexpected_values": list(unexpected),
            "ungrounded_values": list(ungrounded),
            "abstained": (not item.answerable and passed) if abstained is None else abstained,
            "rule_violations": list(violations),
            "judge": judge,
            "latency_s": latency,
            "passed": passed,
            "cause": cause,
            "flags": [],
        }

    return factory


@pytest.fixture
def make_run(gabarito):
    """Execução completa, no formato do run.schema.json."""

    def factory(run_id, results, subset="dev", status="complete", gabarito_hash="hash-teste", variance=None,
                **config):
        run = {
            "run_id": run_id,
            "started_at": "2026-10-10T10:00:00-03:00",
            "finished_at": "2026-10-10T10:05:00-03:00",
            "status": status,
            "subset": subset,
            "gabarito_version": "teste",
            "gabarito_hash": gabarito_hash,
            "config": {
                "chunk_size": 500, "chunk_overlap": 200, "vector_k": 3, "bm25_k": 3, "chat_model": "llama3",
                "embedding_model": "nomic-embed-text", "temperature": 0, "seed": 42, "num_ctx": None,
                "prompt_hash": "p", "kb_hash": "k", "kb_chunk_count": 11, "judge_model": None,
                "git_commit": "abc1234", "git_dirty": False, **config,
            },
            "repeat": 1,
            "results": results,
            "metrics": aggregate(results, gabarito.by_id()),
            "skipped": [],
        }
        if variance:
            run["variance"] = variance
        return run

    return factory
