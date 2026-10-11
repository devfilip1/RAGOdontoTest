import pytest

from evaluation.normalize import (
    canonical_text,
    extract_durations,
    extract_money,
    extract_values,
    normalize_text,
    words_to_number,
)


def test_normalize_text_lowercases_strips_accents_and_collapses_spaces():
    assert normalize_text("  Restauração\n  DENTÁRIA –  Cáries ") == "restauracao dentaria – caries"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("R$ 1.500", [1500]),
        ("R$1500", [1500]),
        ("1500 reais", [1500]),
        ("R$ 1.500,00", [1500]),
        ("mil e quinhentos reais", [1500]),
        ("Investimento: R$ 120 a R$ 250", [120, 250]),
        ("de 500 a 1.500 reais", [500, 1500]),
        ("R$ 500 a 1.500", [500, 1500]),
        ("2,5 mil reais", [2500]),
        ("de 2 mil a 6 mil reais", [2000, 6000]),
        ("R$ 1.500 a R$ 3.500 por dente", [1500, 3500]),
        ("Inicial R$ 500 a R$ 1.500 | Mensal R$ 100 a R$ 300", [500, 1500, 100, 300]),
        ("dois mil e quinhentos reais", [2500]),
        ("cento e vinte reais", [120]),
    ],
)
def test_extract_money(text, expected):
    assert extract_money(text) == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Tempo: 30 a 50 minutos", [(30, "minute"), (50, "minute")]),
        ("1 hora", [(60, "minute")]),
        ("até 72h", [(4320, "minute")]),
        ("3 dias", [(4320, "minute")]),
        ("até 14 dias", [(20160, "minute")]),
        ("2 semanas", [(20160, "minute")]),
        ("Tempo: 3 a 6 meses", [(3, "month"), (6, "month")]),
        ("durabilidade superior a 10 anos", [(120, "month")]),
        ("Tempo: 1 a 3 sessões", [(1, "session"), (3, "session")]),
        ("Tempo: 2 a 3 consultas", [(2, "visit"), (3, "visit")]),
        ("três anos", [(36, "month")]),
        ("de uma a três sessões", [(1, "session"), (3, "session")]),
        ("45 min", [(45, "minute")]),
    ],
)
def test_extract_durations(text, expected):
    assert extract_durations(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Não encontrei essa informação no sistema.",
        "Agende uma consulta e conquiste um sorriso novo.",
        "Até 8 tons mais branco",
        "Temos 50% de aprovação",
        "Já na primeira sessão",
    ],
)
def test_text_without_money_or_duration(text):
    assert extract_values(text) == []


def test_money_and_duration_in_the_same_sentence_do_not_mix():
    values = extract_values("Custa R$ 600 a R$ 1.500 e leva de 1 a 3 sessões.")

    assert [(v.kind, v.value) for v in values] == [
        ("money", 600), ("money", 1500), ("duration", 1), ("duration", 3),
    ]


def test_two_numbers_joined_by_e_are_not_added_when_not_a_single_number():
    assert extract_durations("de trinta e cinquenta minutos") == [(30, "minute"), (50, "minute")]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("zero", 0), ("dezenove", 19), ("vinte e cinco", 25), ("cem", 100), ("cento e vinte", 120),
        ("quinhentos", 500), ("mil", 1000), ("mil e quinhentos", 1500), ("dois mil e quinhentos", 2500),
        ("seis mil", 6000), ("doze mil trezentos e quarenta e cinco", 12345),
    ],
)
def test_words_to_number(text, expected):
    assert words_to_number(text) == expected


def test_words_to_number_rejects_text_that_is_not_a_number():
    assert words_to_number("clareamento") is None


def test_canonical_text_keeps_article_but_converts_range():
    assert canonical_text("Agende uma consulta") == "agende uma consulta"
    assert canonical_text("Uma a três sessões") == "1 a 3 sessoes"
