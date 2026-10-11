import copy

import pytest

from evaluation.dataset import GabaritoError, coverage, parse_gabarito, select_subset, validate

SOURCE = """Limpeza Dental
Tempo: 30 a 50 minutos
Investimento: R$ 120 a R$ 250
Resultado: Imediato já na primeira sessão
Clareamento Dental
Investimento: R$ 500 a R$ 1.500
Aparelho Ortodôntico
Investimento: Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300
"""

BASE = {
    "version": "teste",
    "procedures": {"limpeza": {"anchors": ["limpeza"]}, "clareamento": {"anchors": ["clareamento"]}},
    "items": [
        {
            "id": "limpeza-preco-01",
            "question": "Quanto custa a limpeza?",
            "category": "price",
            "procedure": "limpeza",
            "answerable": True,
            "expected_facts": [{"type": "money", "label": "preço", "values": [120, 250]}],
            "evidence": ["Investimento: R$ 120 a R$ 250"],
            "split": "dev",
            "smoke": True,
        },
        {
            "id": "limpeza-tempo-01",
            "question": "Quanto tempo demora a limpeza?",
            "category": "duration",
            "procedure": "limpeza",
            "answerable": True,
            "expected_facts": [{"type": "duration", "label": "tempo", "values": [30, 50], "unit": "minute"}],
            "evidence": ["Tempo: 30 a 50 minutos"],
            "split": "holdout",
            "smoke": False,
        },
        {
            "id": "fora-endereco-01",
            "question": "Qual o endereço?",
            "category": "out_of_scope",
            "procedure": None,
            "answerable": False,
            "split": "dev",
            "smoke": False,
        },
    ],
}


def problems_for(change, check_coverage=False):
    data = copy.deepcopy(BASE)
    change(data)
    return validate(parse_gabarito(data), SOURCE, check_coverage=check_coverage)


def test_valid_gabarito_has_no_problems():
    assert problems_for(lambda data: None) == []


def test_duplicate_id():
    problems = problems_for(lambda data: data["items"].append(copy.deepcopy(data["items"][0])))

    assert any("limpeza-preco-01" in p and "repetido" in p for p in problems)


def test_schema_rejects_answerable_item_without_facts_or_evidence():
    data = copy.deepcopy(BASE)
    del data["items"][0]["expected_facts"]

    with pytest.raises(GabaritoError) as error:
        parse_gabarito(data)

    assert "expected_facts" in str(error.value)


def test_schema_rejects_unanswerable_item_with_evidence():
    data = copy.deepcopy(BASE)
    data["items"][2]["evidence"] = ["Investimento: R$ 120 a R$ 250"]

    with pytest.raises(GabaritoError):
        parse_gabarito(data)


def test_schema_rejects_unknown_category():
    data = copy.deepcopy(BASE)
    data["items"][0]["category"] = "preco"

    with pytest.raises(GabaritoError):
        parse_gabarito(data)


def test_evidence_missing_from_source():
    def change(data):
        data["items"][0]["evidence"] = ["Investimento: R$ 999"]
        data["items"][0]["expected_facts"][0]["values"] = [999]

    problems = problems_for(change)

    assert any("limpeza-preco-01" in p and "aparece 0 vezes" in p for p in problems)


def test_evidence_that_is_not_unique():
    def change(data):
        data["items"][0]["evidence"] = ["R$ 500 a R$ 1.500"]
        data["items"][0]["expected_facts"][0]["values"] = [500, 1500]

    problems = problems_for(change)

    assert any("limpeza-preco-01" in p and "aparece 2 vezes" in p for p in problems)


def test_evidence_matching_ignores_accents_case_and_line_breaks():
    problems = problems_for(
        lambda data: data["items"][0].update(evidence=["investimento:   r$ 120 A r$ 250\nresultado: imediato ja"])
    )

    assert problems == []


def test_fact_value_missing_from_evidence():
    problems = problems_for(lambda data: data["items"][0]["expected_facts"][0].update(values=[120, 300]))

    assert any("limpeza-preco-01" in p and "300" in p and "evidência" in p for p in problems)


def test_unknown_procedure():
    problems = problems_for(lambda data: data["items"][0].update(procedure="botox"))

    assert any("limpeza-preco-01" in p and "botox" in p for p in problems)


def test_variant_of_missing_item():
    problems = problems_for(lambda data: data["items"][0].update(variant_of="nao-existe"))

    assert any("limpeza-preco-01" in p and "nao-existe" in p for p in problems)


def test_variant_of_another_split():
    problems = problems_for(lambda data: data["items"][0].update(variant_of="limpeza-tempo-01"))

    assert any("limpeza-preco-01" in p and "outro split" in p for p in problems)


def test_coverage_rules():
    problems = problems_for(lambda data: None, check_coverage=True)

    assert any("3 itens (mínimo 40)" in p for p in problems)
    assert any("\"limpeza\" sem item de result" in p for p in problems)
    assert any("\"clareamento\" sem item de price" in p for p in problems)
    assert any("1 itens sem resposta no material (mínimo 6)" in p for p in problems)


def test_select_subset():
    gabarito = parse_gabarito(BASE)

    assert [i.id for i in select_subset(gabarito, "dev")] == ["limpeza-preco-01", "fora-endereco-01"]
    assert [i.id for i in select_subset(gabarito, "holdout")] == ["limpeza-tempo-01"]
    assert [i.id for i in select_subset(gabarito, "smoke")] == ["limpeza-preco-01"]


def test_coverage_counts():
    summary = coverage(parse_gabarito(BASE))

    assert summary["total"] == 3
    assert summary["unanswerable"] == 1
    assert summary["by_split"] == {"dev": 2, "holdout": 1}
    assert summary["by_procedure"] == {"limpeza": 2, "(geral)": 1}
