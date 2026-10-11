"""Comparação entre duas execuções."""
from evaluation.aggregate import flatten

# Pequena folga para diferenças de ponto flutuante.
EPSILON = 1e-9


def _spread(run, name):
    entry = (run.get("variance") or {}).get(name)
    return entry["max"] - entry["min"] if entry else None


def compare(base, candidate):
    """Devolve a "Comparação" do data-model. Recortes diferentes não são comparáveis."""
    comparison = {
        "base": base["run_id"],
        "candidate": candidate["run_id"],
        "comparable": True,
        "reason": None,
        "warnings": [],
        "metric_deltas": {},
        "regressions": [],
        "improvements": [],
        "config_changes": {},
        "within_noise": {},
    }
    if base["subset"] != candidate["subset"]:
        comparison["comparable"] = False
        comparison["reason"] = (
            f"recortes diferentes: {base['run_id']} é {base['subset']} e "
            f"{candidate['run_id']} é {candidate['subset']}"
        )
        return comparison

    base_results = {result["item_id"]: result for result in base["results"]}
    candidate_results = {result["item_id"]: result for result in candidate["results"]}
    common = [item_id for item_id in base_results if item_id in candidate_results]

    if base["gabarito_hash"] != candidate["gabarito_hash"]:
        left_out = len(set(base_results) ^ set(candidate_results))
        comparison["warnings"].append(
            f"o gabarito mudou entre as execuções ({base['gabarito_version']} → "
            f"{candidate['gabarito_version']}): as métricas não são diretamente comparáveis; "
            f"a comparação por pergunta usa os {len(common)} itens em comum e deixa {left_out} de fora"
        )

    base_flat = flatten(base["metrics"])
    candidate_flat = flatten(candidate["metrics"])
    for name in base_flat:
        before, after = base_flat[name], candidate_flat.get(name)
        delta = after - before if before is not None and after is not None else None
        comparison["metric_deltas"][name] = {"base": before, "candidate": after, "delta": delta}

        spreads = [s for s in (_spread(base, name), _spread(candidate, name)) if s is not None]
        if delta is None or not spreads:
            comparison["within_noise"][name] = None
        else:
            comparison["within_noise"][name] = abs(delta) <= max(spreads) + EPSILON

    for item_id in common:
        before, after = base_results[item_id], candidate_results[item_id]
        if before["passed"] and not after["passed"]:
            comparison["regressions"].append({"item_id": item_id, "cause": after.get("cause")})
        elif not before["passed"] and after["passed"]:
            comparison["improvements"].append({"item_id": item_id, "previous_cause": before.get("cause")})

    for field, before in base["config"].items():
        after = candidate["config"].get(field)
        if before != after and field not in ("git_commit", "git_dirty"):
            comparison["config_changes"][field] = {"base": before, "candidate": after}

    return comparison
