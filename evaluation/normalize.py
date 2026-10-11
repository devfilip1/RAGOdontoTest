"""Normalização de texto e extração de valores (dinheiro e duração) em pt-BR."""
import re
import unicodedata
from dataclasses import dataclass

NUMBER_WORDS = {
    "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5,
    "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13,
    "quatorze": 14, "catorze": 14, "quinze": 15, "dezesseis": 16, "dezessete": 17, "dezoito": 18,
    "dezenove": 19, "vinte": 20, "trinta": 30, "quarenta": 40, "cinquenta": 50, "sessenta": 60,
    "setenta": 70, "oitenta": 80, "noventa": 90, "cem": 100, "cento": 100, "duzentos": 200,
    "duzentas": 200, "trezentos": 300, "trezentas": 300, "quatrocentos": 400, "quatrocentas": 400,
    "quinhentos": 500, "quinhentas": 500, "seiscentos": 600, "seiscentas": 600, "setecentos": 700,
    "setecentas": 700, "oitocentos": 800, "oitocentas": 800, "novecentos": 900, "novecentas": 900,
    "mil": 1000,
}

# unidade escrita -> (fator, unidade canônica)
UNIT_WORDS = {
    "minuto": (1, "minute"), "minutos": (1, "minute"), "min": (1, "minute"),
    "hora": (60, "minute"), "horas": (60, "minute"), "h": (60, "minute"),
    "dia": (1440, "minute"), "dias": (1440, "minute"),
    "semana": (10080, "minute"), "semanas": (10080, "minute"),
    "mes": (1, "month"), "meses": (1, "month"),
    "ano": (12, "month"), "anos": (12, "month"),
    "sessao": (1, "session"), "sessoes": (1, "session"),
    "consulta": (1, "visit"), "consultas": (1, "visit"),
}

# unidade do gabarito -> (fator, unidade canônica)
FACT_UNITS = {
    "minute": (1, "minute"), "hour": (60, "minute"), "day": (1440, "minute"),
    "month": (1, "month"), "year": (12, "month"),
    "session": (1, "session"), "visit": (1, "visit"),
}

_WORD = re.compile(r"[a-z]+")
_NUMBER = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?")
_DIGITS_MIL = re.compile(r"(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)\s*mil\b")
_UNIT = re.compile(r"\s*(" + "|".join(sorted(UNIT_WORDS, key=len, reverse=True)) + r")\b")
_MONEY_BEFORE = re.compile(r"r\$\s*$")
_MONEY_AFTER = re.compile(r"\s*(?:reais|real)\b")
_RANGE_BETWEEN = re.compile(r"\s*(?:a|ate|e|ou|-|–|—)\s*(?:r\$\s*)?")
_RANGE_AFTER_ONE = re.compile(r"\s+(?:a|ou|ate)\s+(?:\d|" + "|".join(NUMBER_WORDS) + r")")


@dataclass(frozen=True)
class Value:
    kind: str  # "money" ou "duration"
    value: float
    unit: str | None  # unidade canônica da duração
    label: str  # como mostrar no placar

    @property
    def key(self):
        return (self.kind, round(self.value, 2), self.unit)


def normalize_text(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def _parse_number(raw):
    return float(raw.replace(".", "").replace(",", "."))


def _format_number(value):
    return f"{value:g}" if value != int(value) else str(int(value))


def format_money(value):
    """1500 -> 'R$ 1.500'; 99.9 -> 'R$ 99,90'."""
    if value == int(value):
        return "R$ " + f"{int(value):,}".replace(",", ".")
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _parse_run(tokens, i, text):
    """Lê uma sequência de números por extenso a partir de tokens[i]."""
    total = current = 0
    last = None
    j = i
    end = tokens[i].start()
    while j < len(tokens):
        k = j
        if j > i:
            if text[end:tokens[j].start()].strip():
                break
            if tokens[j].group() == "e":
                if j + 1 >= len(tokens) or text[tokens[j].end():tokens[j + 1].start()].strip():
                    break
                k = j + 1
        word = tokens[k].group()
        if word not in NUMBER_WORDS:
            break
        number = NUMBER_WORDS[word]
        if word == "mil":
            total += (current or 1) * 1000
            current = 0
        else:
            # "trinta e cinquenta" são dois números, não 80
            if last is not None and last != 1000 and number >= last:
                break
            current += number
        last = number
        end = tokens[k].end()
        j = k + 1
    return total + current, j, end


def replace_number_words(text):
    """Troca números por extenso por dígitos. Espera texto já normalizado."""
    tokens = list(_WORD.finditer(text))
    pieces = []
    pos = 0
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.group() not in NUMBER_WORDS or token.start() < pos:
            i += 1
            continue
        value, next_i, end = _parse_run(tokens, i, text)
        single = next_i == i + 1
        # "um"/"uma" sozinhos são artigo ("agende uma consulta"), salvo em faixa ("uma a três")
        if single and token.group() in ("um", "uma") and not _RANGE_AFTER_ONE.match(text, end):
            i += 1
            continue
        pieces.append(text[pos:token.start()])
        pieces.append(str(value))
        pos = end
        i = next_i
    pieces.append(text[pos:])
    return "".join(pieces)


def canonical_text(text):
    """Texto normalizado, com '2,5 mil' e números por extenso convertidos em dígitos."""
    text = normalize_text(text)
    text = _DIGITS_MIL.sub(lambda m: _format_number(_parse_number(m.group(1)) * 1000), text)
    return replace_number_words(text)


def extract_values(text):
    """Devolve os valores de dinheiro e duração do texto, na ordem em que aparecem."""
    text = canonical_text(text)
    found = []  # [início, fim, número, kind, unit, label]
    for match in _NUMBER.finditer(text):
        number = _parse_number(match.group())
        kind = unit = label = None
        unit_match = _UNIT.match(text, match.end())
        if _MONEY_BEFORE.search(text[:match.start()]) or _MONEY_AFTER.match(text, match.end()):
            kind = "money"
        elif unit_match:
            kind = "duration"
            factor, unit = UNIT_WORDS[unit_match.group(1)]
            label = f"{_format_number(number)} {unit_match.group(1)}"
            number *= factor
        found.append([match.start(), match.end(), number, kind, unit, label])

    # faixas: "30 a 50 minutos", "de 500 a 1.500 reais", "R$ 500 a 1.500"
    for first, second in zip(found, found[1:]):
        if not _RANGE_BETWEEN.fullmatch(text[first[1]:second[0]]):
            continue
        if first[3] is None and second[3] == "money":
            first[3] = "money"
        elif first[3] is None and second[3] == "duration":
            unit_word = second[5].split(" ", 1)[1]
            factor, unit = UNIT_WORDS[unit_word]
            first[3:] = ["duration", unit, f"{_format_number(first[2])} {unit_word}"]
            first[2] *= factor
        elif second[3] is None and first[3] == "money":
            second[3] = "money"

    values = []
    for _, _, number, kind, unit, label in found:
        if kind == "money":
            values.append(Value("money", number, None, format_money(number)))
        elif kind == "duration":
            values.append(Value("duration", number, unit, label))
    return values


def extract_money(text):
    return [v.value for v in extract_values(text) if v.kind == "money"]


def extract_durations(text):
    return [(v.value, v.unit) for v in extract_values(text) if v.kind == "duration"]


def words_to_number(text):
    """Converte um número por extenso ('mil e quinhentos') em número; None se não for um."""
    converted = replace_number_words(normalize_text(text))
    return _parse_number(converted) if _NUMBER.fullmatch(converted) else None
