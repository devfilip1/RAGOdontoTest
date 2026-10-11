import pytest

from assistant.settings import SettingsError, parse_settings

STRATEGIES = """
strategies:
  - name: section
    type: section
  - name: recursive_500_200
    type: split
    parameters:
      chunk_size: 500
      chunk_overlap: 200
  - name: page
    type: page
"""

EXPERIMENTS = """
assistant: section_hybrid
experiments:
  - exp_name: section_hybrid
    collection: section
    search_type: hybrid
    match_count: 4
    match_threshold: 0.0
    use_hyde: false
  - exp_name: recursive_hybrid
    collection: recursive_500_200
    search_type: hybrid
    match_count: 4
  - exp_name: page_vector
    collection: page
    search_type: vector
    match_count: 2
"""


def problems(strategies=STRATEGIES, experiments=EXPERIMENTS):
    with pytest.raises(SettingsError) as error:
        parse_settings(strategies, experiments)
    return error.value.problems


def test_valid_configuration():
    settings = parse_settings(STRATEGIES, EXPERIMENTS)

    assert list(settings.strategies) == ["section", "recursive_500_200", "page"]
    assert list(settings.experiments) == ["section_hybrid", "recursive_hybrid", "page_vector"]
    assert settings.assistant.exp_name == "section_hybrid"
    assert settings.assistant.collection == "section"


def test_experiment_defaults_keep_threshold_and_hyde_off():
    experiment = parse_settings(STRATEGIES, EXPERIMENTS).experiments["recursive_hybrid"]

    assert experiment.match_threshold == 0.0
    assert experiment.use_hyde is False


def test_section_defaults():
    strategies = parse_settings(STRATEGIES, EXPERIMENTS).strategies

    assert strategies["section"].parameters == {"max_chars": 1200, "overlap": 100}
    assert strategies["recursive_500_200"].parameters == {"chunk_size": 500, "chunk_overlap": 200}
    assert strategies["page"].parameters == {}


def test_definition_hash_changes_only_with_the_definition():
    base = parse_settings(STRATEGIES, EXPERIMENTS).strategies
    explicit = parse_settings(
        STRATEGIES.replace("type: section", "type: section\n    parameters: {max_chars: 1200, overlap: 100}"), EXPERIMENTS
    ).strategies
    changed = parse_settings(STRATEGIES.replace("chunk_size: 500", "chunk_size: 400"), EXPERIMENTS).strategies

    assert base["section"].definition_hash() == explicit["section"].definition_hash()
    assert base["recursive_500_200"].definition_hash() != changed["recursive_500_200"].definition_hash()
    assert base["page"].definition_hash() == changed["page"].definition_hash()


@pytest.mark.parametrize(
    "old, new, expected",
    [
        ("name: page", "name: section", ["section", "repetido"]),
        ("type: page", "type: semantic", ["page", "semantic", "section, split, page"]),
        ("chunk_size: 500", "chunk_sise: 500", ["recursive_500_200", "chunk_sise"]),
        ("      chunk_overlap: 200\n", "", ["recursive_500_200", "chunk_overlap"]),
        ("type: page", "type: page\n    parameters: {chunk_size: 100}", ["page", "parâmetros"]),
        ("chunk_overlap: 200", "chunk_overlap: 500", ["recursive_500_200", "chunk_overlap", "menor"]),
        ("type: section", "type: section\n    parameters: {max_chars: 300, overlap: 300}", ["section", "overlap", "menor"]),
        ("chunk_size: 500", "chunk_size: 10", ["recursive_500_200", "chunk_size", "50"]),
        ("name: page", "name: Page Strategy", ["Page Strategy", "minúsculas"]),
    ],
)
def test_invalid_strategies(old, new, expected):
    assert old in STRATEGIES
    found = problems(strategies=STRATEGIES.replace(old, new))

    assert any(all(text in problem for text in expected) for problem in found), found


@pytest.mark.parametrize(
    "old, new, expected",
    [
        ("exp_name: page_vector", "exp_name: section_hybrid", ["section_hybrid", "repetido"]),
        ("collection: page", "collection: nao_existe", ["page_vector", "nao_existe", "section, recursive_500_200, page"]),
        ("match_count: 2", "match_count: 0", ["page_vector", "match_count", "1 a 20"]),
        ("match_count: 2", "match_count: 21", ["page_vector", "match_count", "1 a 20"]),
        ("match_threshold: 0.0", "match_threshold: 1.5", ["section_hybrid", "match_threshold", "0 a 1"]),
        ("search_type: vector", "search_type: semantic", ["page_vector", "semantic", "hybrid, vector, bm25"]),
        ("assistant: section_hybrid", "assistant: nao_existe", ["assistant", "nao_existe"]),
        ("    search_type: vector\n", "", ["page_vector", "search_type"]),
        ("use_hyde: false", "use_hyde: talvez", ["section_hybrid", "use_hyde"]),
        ("match_count: 2", "match_count: 2\n    top_k: 3", ["page_vector", "top_k"]),
    ],
)
def test_invalid_experiments(old, new, expected):
    assert old in EXPERIMENTS
    found = problems(experiments=EXPERIMENTS.replace(old, new))

    assert any(all(text in problem for text in expected) for problem in found), found


def test_hyde_needs_vector_search():
    found = problems(experiments=EXPERIMENTS.replace("search_type: vector", "search_type: bm25\n    use_hyde: true"))

    assert any("page_vector" in p and "use_hyde" in p and "bm25" in p for p in found)


def test_all_problems_are_reported_together():
    found = problems(
        strategies=STRATEGIES.replace("type: page", "type: semantic"),
        experiments=EXPERIMENTS.replace("match_count: 2", "match_count: 0").replace("assistant: section_hybrid", "assistant: x"),
    )

    assert len(found) >= 3
    assert any("strategies.yaml" in p for p in found) and any("experiments.yaml" in p for p in found)


def test_malformed_yaml():
    found = problems(strategies="strategies:\n  - name: [sem fechar")

    assert len(found) == 1 and "strategies.yaml" in found[0] and "YAML" in found[0]


def test_empty_file():
    assert any("strategies.yaml" in p for p in problems(strategies=""))


def test_no_strategies_declared():
    assert any("strategies" in p for p in problems(strategies="strategies: []"))
