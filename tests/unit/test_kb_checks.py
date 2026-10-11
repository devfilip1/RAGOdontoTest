from evaluation.kb_checks import find_corrupted, find_duplicates, find_source_mismatch, find_unanchored_facts

HEADING = "Clareamento Dental – Dentes Brancos em Poucos Dias"
PRICE = "Investimento: R$ 500 a R$ 1.500"
LIMPEZA = "Limpeza Dental\nTempo: 30 a 50 minutos\nInvestimento: R$ 120 a R$ 250"
DIFFERENTIAL = "Atendimento rápido (até 72h)"


def test_duplicates_report_the_number_of_repetitions():
    chunks = [LIMPEZA, HEADING, LIMPEZA, "Limpeza  Dental\nTempo: 30 a 50 minutos\n\nInvestimento: R$ 120 a R$ 250"]

    assert find_duplicates(chunks) == [{"content": LIMPEZA, "count": 3}]


def test_no_duplicates():
    assert find_duplicates([LIMPEZA, HEADING]) == []


def test_fact_in_a_chunk_without_the_procedure_name_is_unanchored(gabarito):
    chunks = [HEADING, f"Como funciona: gel clareador\n{PRICE}", LIMPEZA, DIFFERENTIAL]

    assert find_unanchored_facts(gabarito, chunks) == [{
        "kind": "unanchored", "item_id": "clareamento-preco-01", "procedure": "clareamento", "evidence": PRICE,
    }]


def test_fact_with_the_procedure_name_in_some_chunk_is_fine(gabarito):
    chunks = [f"Como funciona: gel\n{PRICE}", f"{HEADING}\n{PRICE}", LIMPEZA, DIFFERENTIAL]

    assert find_unanchored_facts(gabarito, chunks) == []


def test_evidence_cut_by_the_split_is_missing(gabarito):
    chunks = [f"{HEADING}\nInvestimento: R$ 500 a", "R$ 1.500\nResultado", LIMPEZA, DIFFERENTIAL]

    problems = find_unanchored_facts(gabarito, chunks)

    assert [(p["kind"], p["item_id"]) for p in problems] == [("missing", "clareamento-preco-01")]


def test_item_without_procedure_only_needs_the_evidence(gabarito):
    chunks = [f"{HEADING}\n{PRICE}", LIMPEZA]

    problems = find_unanchored_facts(gabarito, chunks)

    assert [(p["kind"], p["item_id"]) for p in problems] == [("missing", "dif-atendimento-01")]


def test_corrupted_characters():
    chunks = ["Pino de ■■■ânio no osso", "texto com �", "sino\x07", LIMPEZA]

    assert find_corrupted(chunks) == [
        {"content": "Pino de ■■■ânio no osso", "chars": ["U+25A0"]},
        {"content": "texto com �", "chars": ["U+FFFD"]},
        {"content": "sino\x07", "chars": ["U+0007"]},
    ]


def test_normal_punctuation_is_not_corrupted():
    assert find_corrupted(["Restauração – ação — R$ 1.500 | Mensal\n\tSiso (até 72h) + polimento"]) == []


def test_sources_with_the_same_content_match():
    report = find_source_mismatch([LIMPEZA, HEADING], [HEADING, LIMPEZA])

    assert report == {"vector_count": 2, "file_count": 2, "only_in_vector": 0, "only_in_file": 0, "mismatch": False}


def test_sources_with_different_count_and_content():
    report = find_source_mismatch([LIMPEZA] * 5 + [HEADING], [LIMPEZA, PRICE])

    assert report == {"vector_count": 6, "file_count": 2, "only_in_vector": 5, "only_in_file": 1, "mismatch": True}
