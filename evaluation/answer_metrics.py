"""Métricas determinísticas da resposta: fatos, fidelidade numérica, recusa e regras de atendimento."""
import re

from evaluation.normalize import canonical_text, extract_values, normalize_text

# Trechos (já normalizados) que indicam que o assistente declarou não ter a informação.
# A primeira entrada é a frase mandada pelo prompt; ajustar aqui quando o prompt mudar.
ABSTENTION_PATTERNS = (
    "nao encontrei",
    "nao encontramos",
    "nao tenho essa informacao",
    "nao tenho informac",
    "nao possuo",
    "nao disponho",
    "nao ha informac",
    "nao consta",
    "nao e mencionad",
    "nao foi mencionad",
    "nao sei informar",
    "nao posso",
    "nao consigo",
)

FORBIDDEN_TERMS = {
    "contexto": r"\bcontextos?\b",
    "documento": r"\bdocumentos?\b",
    "base de dados": r"\bbases? de dados\b",
}
MAX_ANSWER_CHARS = 1200

_PT_WORDS = {"o", "a", "de", "que", "e", "para", "com", "nao", "um", "uma", "os", "as", "do", "da", "em", "voce"}
_EN_WORDS = {"the", "is", "and", "of", "to", "you", "for", "with", "our", "your", "this", "that", "are", "can"}


def check_facts(answer, expected_facts):
    """Para cada fato esperado, diz se a resposta o contém."""
    values = {v.key for v in extract_values(answer)}
    text = canonical_text(answer)
    found = []
    for fact in expected_facts:
        if fact.type == "text":
            ok = any(canonical_text(alternative) in text for alternative in fact.alternatives)
        else:
            ok = all(target in values for target in fact.targets())
        found.append({"label": fact.label, "found": ok})
    return found


def unexpected_values(answer, known_facts, kinds=None):
    """Valores de dinheiro ou duração da resposta que não pertencem aos fatos conhecidos.

    kinds limita a conferência a alguns tipos ("money", "duration"); None confere todos.
    """
    known = {target for fact in known_facts for target in fact.targets()}
    labels = []
    for value in extract_values(answer):
        if kinds is not None and value.kind not in kinds:
            continue
        if value.key not in known and value.label not in labels:
            labels.append(value.label)
    return labels


def ungrounded_values(answer, chunks):
    """Valores da resposta que não aparecem em nenhum trecho recuperado."""
    grounded = {v.key for chunk in chunks for v in extract_values(chunk)}
    labels = []
    for value in extract_values(answer):
        if value.key not in grounded and value.label not in labels:
            labels.append(value.label)
    return labels


def factual_ok(answer, expected_facts, allowed_facts=()):
    """Todos os fatos esperados presentes e nenhum valor estranho dos mesmos tipos."""
    kinds = {fact.type for fact in expected_facts if fact.type != "text"}
    return all(f["found"] for f in check_facts(answer, expected_facts)) and not unexpected_values(
        answer, [*expected_facts, *allowed_facts], kinds
    )


def detect_abstention(answer):
    text = normalize_text(answer)
    return any(pattern in text for pattern in ABSTENTION_PATTERNS)


def check_rules(answer):
    """Regras de atendimento com resposta objetiva. Devolve as violações."""
    text = normalize_text(answer)
    violations = []
    for term, pattern in FORBIDDEN_TERMS.items():
        if re.search(pattern, text):
            violations.append(f"forbidden_term:{term}")
    if len(answer) > MAX_ANSWER_CHARS:
        violations.append("too_long")
    words = re.findall(r"[a-z]+", text)
    if sum(w in _EN_WORDS for w in words) > sum(w in _PT_WORDS for w in words):
        violations.append("not_portuguese")
    return violations
