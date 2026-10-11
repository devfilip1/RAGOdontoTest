"""Causa principal de cada resposta errada (research D14)."""

CAUSES = ("retrieval_failure", "answer_failure", "fabricated", "wrong_refusal", "rule_violation")


def classify(item, result, other_procedure_labels=()):
    """Devolve (causa, sinais). A causa é None quando o item passou.

    result: dict com passed, retrieval, facts, unexpected_values, ungrounded_values, abstained, rule_violations.
    other_procedure_labels: valores inesperados que são fato de outro procedimento.
    """
    flags = []
    fused = (result.get("retrieval") or {}).get("fused")
    if fused and fused["hit"] and not fused["anchored"]:
        flags.append("evidence_not_anchored")
    if other_procedure_labels:
        flags.append("other_procedure_value")

    if result["passed"]:
        return None, flags

    facts_ok = all(fact["found"] for fact in result["facts"]) and not result["unexpected_values"]

    if not item.answerable:
        cause = "fabricated" if not result["abstained"] or result["unexpected_values"] else "rule_violation"
    elif not fused["hit"]:
        cause = "retrieval_failure"
    elif result["abstained"] and not facts_ok:
        cause = "wrong_refusal"
    elif result["ungrounded_values"]:
        cause = "fabricated"
    elif not facts_ok:
        cause = "answer_failure"
    else:
        cause = "rule_violation"
    return cause, flags
