import pytest

from assistant.ingest import build_chunks, clean_text, is_heading, split_sections
from assistant.settings import Strategy

B = "\x7f"  # marcador de lista como sai do PDF

PAGE_1 = f"""OdontoTest – Transforme Seu Sorriso com
Segurança, Rapidez e Resultado Garantido
Na OdontoTest, cada tratamento é planejado para entregar resultado visível, conforto durante o
processo e máxima durabilidade.
Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável
O que você ganha:
{B}
Sensação imediata de boca limpa
{B}
Hálito mais fresco
Tempo: 30 a 50 minutos
Investimento: R$ 120 a R$ 250
Implante Dentário – Tenha Seu Dente de Volta de Forma
Permanente
Ideal para quem quer:
{B}
Solução definitiva
"""
PAGE_2 = f"""Como funciona: Pino de ■■■ânio no osso e prótese natural.
Investimento: R$ 2.500 a R$ 6.000
Por Que Escolher a OdontoTest?
{B}
Atendimento rápido (até 72h)
{B}
Facilidade de pagamento
Agende Agora Sua Avaliação
Quanto mais você espera, maior pode ser o problema — e o custo. Na OdontoTest, você resolve
desde o básico até tratamentos completos com segurança e previsibilidade.
"""
PAGES = [PAGE_1, PAGE_2]

SECTION = Strategy("section", "section", {"max_chars": 1200, "overlap": 100})
IMPLANTE = "Implante Dentário – Tenha Seu Dente de Volta de Forma Permanente"


@pytest.mark.parametrize(
    "line",
    [
        "Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável",
        "Restauração Dentária – Acabe com Cáries Antes que Virem",
        "Aparelho Ortodôntico – Sorriso Alinhado e Harmônico",
        "Por Que Escolher a OdontoTest?",
        "Agende Agora Sua Avaliação",
    ],
)
def test_headings(line):
    assert is_heading(line)


@pytest.mark.parametrize(
    "line",
    [
        "Tempo: 30 a 50 minutos",
        "Ideal para quem quer:",
        "- Sensação imediata de boca limpa",
        "- Siso incluso",
        "- Tecnologia Moderna e Menos Dor",
        "Planejamento com previsibilidade",
        "supervisionado.",
        "Permanente",
        "processo e máxima durabilidade. Você não está apenas fazendo um procedimento — está",
    ],
)
def test_body_lines_are_not_headings(line):
    assert not is_heading(line)


def test_clean_text_turns_bullets_into_list_items_and_applies_fixes():
    cleaned = clean_text(PAGE_2)

    assert B not in cleaned
    assert "- Atendimento rápido (até 72h)\n- Facilidade de pagamento" in cleaned
    assert "Pino de titânio no osso" in cleaned
    assert "Investimento: R$ 2.500 a R$ 6.000" in cleaned
    assert "\n\n" not in cleaned


def test_sections_follow_the_headings_across_pages():
    text = "\n".join(clean_text(page) for page in PAGES)

    sections = dict(split_sections(text))

    assert list(sections) == [
        "OdontoTest – Transforme Seu Sorriso com Segurança, Rapidez e Resultado Garantido",
        "Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável",
        IMPLANTE,
        "Por Que Escolher a OdontoTest?",
        "Agende Agora Sua Avaliação",
    ]
    assert sections["Limpeza Dental – O Primeiro Passo Para um Sorriso Saudável"] == [
        "O que você ganha:",
        "- Sensação imediata de boca limpa",
        "- Hálito mais fresco",
        "Tempo: 30 a 50 minutos",
        "Investimento: R$ 120 a R$ 250",
    ]


def test_section_strategy_keeps_each_value_with_its_treatment():
    chunks = build_chunks(SECTION, PAGES)

    assert len(chunks) == 5
    implante = chunks[2]
    assert implante.page_content.startswith(IMPLANTE + "\n")
    assert "R$ 2.500 a R$ 6.000" in implante.page_content  # a seção começa em uma página e termina na outra
    assert "R$ 120" not in implante.page_content
    assert implante.metadata == {"source": "data/source/OdontoTest.pdf", "strategy": "section", "section": IMPLANTE}


def test_section_larger_than_the_limit_is_split_with_the_title_repeated():
    body = "\n".join(f"Detalhe {n}: " + "informação do tratamento " * 6 for n in range(20))
    small = Strategy("small", "section", {"max_chars": 400, "overlap": 50})

    chunks = build_chunks(small, [f"Tratamento Longo – Um Exemplo Grande\n{body}\n"])

    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.page_content.startswith("Tratamento Longo – Um Exemplo Grande\n")
        assert len(chunk.page_content) <= 400 + len("Tratamento Longo – Um Exemplo Grande\n")


def test_split_strategy_respects_the_chunk_size_and_uses_clean_text():
    strategy = Strategy("recursive_200_50", "split", {"chunk_size": 200, "chunk_overlap": 50})

    chunks = build_chunks(strategy, PAGES)

    assert len(chunks) > 3
    assert all(len(chunk.page_content) <= 200 for chunk in chunks)
    text = "\n".join(chunk.page_content for chunk in chunks)
    assert B not in text and "titânio" in text
    assert chunks[0].metadata == {"source": "data/source/OdontoTest.pdf", "strategy": "recursive_200_50"}


def test_split_strategy_can_separate_a_value_from_its_treatment():
    strategy = Strategy("recursive_200_50", "split", {"chunk_size": 200, "chunk_overlap": 50})

    chunks = build_chunks(strategy, PAGES)

    with_price = [chunk.page_content for chunk in chunks if "R$ 2.500 a R$ 6.000" in chunk.page_content]
    assert with_price and not any("Implante" in content for content in with_price)


def test_page_strategy_makes_one_chunk_per_page():
    chunks = build_chunks(Strategy("page", "page", {}), PAGES)

    assert [chunk.metadata["page"] for chunk in chunks] == [1, 2]
    assert chunks[0].page_content == clean_text(PAGE_1)
    assert chunks[1].metadata == {"source": "data/source/OdontoTest.pdf", "strategy": "page", "page": 2}


def test_unknown_strategy_type():
    with pytest.raises(ValueError, match="semantic"):
        build_chunks(Strategy("x", "semantic", {}), PAGES)
