"""Placar no terminal e em report.md."""
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from evaluation.judge import CRITERIA
from evaluation.normalize import format_money

SUBSET_LABELS = {"dev": "completo (dev)", "holdout": "parte reservada (holdout)", "smoke": "reduzido (smoke)"}
SOURCE_LABELS = {"vector": "Vetorial", "bm25": "Lexical (BM25)", "fused": "Combinada (enviada ao modelo)"}
CAUSE_LABELS = {
    "retrieval_failure": "Falha de busca",
    "answer_failure": "Falha de resposta",
    "fabricated": "Informação inventada",
    "wrong_refusal": "Recusa indevida",
    "rule_violation": "Violação de regra de atendimento",
}
CATEGORY_LABELS = {
    "price": "Preço", "duration": "Tempo", "result": "Resultado", "indication": "Indicação",
    "how_it_works": "Como funciona", "differentials": "Diferenciais", "comparison": "Comparação",
    "out_of_scope": "Fora do escopo", "adversarial": "Tentativa de tirar do papel",
}
FLAG_LABELS = {
    "evidence_not_anchored": "evidência recuperada sem o nome do procedimento",
    "other_procedure_value": "valor de outro procedimento",
}
VIOLATION_LABELS = {"too_long": "resposta longa demais", "not_portuguese": "resposta fora do português"}
UNIT_LABELS = {
    "minute": "min", "hour": "h", "day": "dias", "month": "meses", "year": "anos",
    "session": "sessões", "visit": "consultas",
}
METRIC_LABELS = {
    "overall.pass_rate": "Nota geral",
    "answer.factual_accuracy": "Correção factual",
    "answer.faithfulness_numeric": "Fidelidade numérica",
    "answer.correct_refusal_rate": "Recusa correta",
    "answer.wrong_refusal_rate": "Recusa indevida",
    "answer.rule_compliance": "Regras de atendimento",
    "operational.latency_p50": "Tempo típico (p50)",
    "operational.latency_p95": "Tempo dos mais lentos (p95)",
}
RETRIEVAL_LABELS = {
    "hit_rate": "Acerto", "recall": "Recall", "mrr": "MRR",
    "context_precision": "Precisão de contexto", "anchored_rate": "Evidência ancorada",
}
ANSWER_NOTES = {
    "factual_accuracy": "perguntas com resposta: todos os fatos certos e nenhum valor estranho",
    "faithfulness_numeric": "respostas sem valor que não esteja nos trechos recuperados",
    "correct_refusal_rate": "perguntas sem resposta no material em que ele recusou",
    "wrong_refusal_rate": "perguntas com resposta em que ele recusou (menor é melhor)",
    "rule_compliance": "respostas sem violar regra de atendimento",
}
LOWER_IS_BETTER = {"answer.wrong_refusal_rate", "operational.latency_p50", "operational.latency_p95"}


def metric_label(name):
    if name in METRIC_LABELS:
        return METRIC_LABELS[name]
    group, _, rest = name.partition(".")
    if group == "retrieval":
        source, _, metric = rest.partition(".")
        return f"Busca {SOURCE_LABELS[source].split(' ')[0].lower()}: {RETRIEVAL_LABELS[metric].lower()}"
    if group == "judge":
        return f"Juiz: {CRITERIA.get(rest, {}).get('label', rest).lower()}"
    return name


def pct(value):
    return "—" if value is None else f"{value * 100:.1f}%"


def _value(name, value):
    if value is None:
        return "—"
    if name.startswith("operational."):
        return f"{value:.1f} s"
    if name.endswith(".mrr"):
        return f"{value:.2f}"
    return pct(value)


def _delta(name, delta):
    if delta is None:
        return "—"
    if name.startswith("operational."):
        return f"{delta:+.1f} s"
    if name.endswith(".mrr"):
        return f"{delta:+.2f}"
    return f"{delta * 100:+.1f} pp"


def describe_fact(fact):
    if fact.type == "money":
        return f"{fact.label}: " + " a ".join(format_money(value) for value in fact.values)
    if fact.type == "duration":
        return f"{fact.label}: " + " a ".join(f"{value:g}" for value in fact.values) + f" {UNIT_LABELS[fact.unit]}"
    return f"{fact.label}: \"{fact.alternatives[0]}\""


def describe_expected(item):
    if not item.answerable:
        return "dizer que não tem a informação"
    return "; ".join(describe_fact(fact) for fact in item.expected_facts)


def describe_problem(result):
    parts = []
    missing = [fact["label"] for fact in result["facts"] if not fact["found"]]
    if missing:
        parts.append("faltou: " + ", ".join(missing))
    if result["unexpected_values"]:
        parts.append("valor inesperado: " + ", ".join(result["unexpected_values"]))
    if result["ungrounded_values"]:
        parts.append("fora dos trechos: " + ", ".join(result["ungrounded_values"]))
    for violation in result["rule_violations"]:
        kind, _, term = violation.partition(":")
        parts.append(f"citou \"{term}\"" if kind == "forbidden_term" else VIOLATION_LABELS.get(violation, violation))
    parts.extend(FLAG_LABELS.get(flag, flag) for flag in result["flags"])
    return "; ".join(parts)


def _short(text, limit=160):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _describe_assistant(config):
    """Linha do placar que diz com que configuração a avaliação rodou."""
    if config.get("experiment"):
        search = {"hybrid": "híbrida", "vector": "vetorial", "bm25": "por palavras"}.get(config["search_type"], "?")
        extras = ""
        if config.get("match_threshold"):
            extras += f", threshold {config['match_threshold']:.2f}"
        if config.get("use_hyde"):
            extras += ", HyDE"
        return (f"{config['chat_model']}, experimento {config['experiment']} (estratégia {config['strategy']}, "
                f"{config['kb_chunk_count']} trechos, busca {search}, até {config['match_count']} trechos{extras})")
    # execuções gravadas antes dos experimentos
    return (f"{config['chat_model']}, {config['kb_chunk_count']} trechos, "
            f"k vetorial {config['vector_k']}, k lexical {config['bm25_k']}"
            + (f", até {config['final_k']} trechos por pergunta" if config.get("final_k") else ""))


def sections(run, gabarito):
    """Seções do placar como (título, colunas, linhas), usadas pelo terminal e pelo report.md."""
    metrics = run["metrics"]
    items = gabarito.by_id()
    out = []

    config = run["config"]
    out.append(("Resumo", ["", ""], [
        ["Nota geral", f"{pct(metrics['overall']['pass_rate'])} de {metrics['overall']['item_count']} perguntas"],
        ["Recorte", SUBSET_LABELS[run["subset"]]],
        ["Gabarito", run["gabarito_version"]],
        ["Assistente", _describe_assistant(config)],
        ["Tempo de resposta", f"típico {metrics['operational']['latency_p50']:.1f} s, "
                              f"mais lentos {metrics['operational']['latency_p95']:.1f} s"],
    ]))

    out.append(("Resposta (determinístico)", ["Métrica", "Nota", "O que mede"], [
        [METRIC_LABELS[f"answer.{name}"], pct(metrics["answer"][name]), note] for name, note in ANSWER_NOTES.items()
    ]))

    out.append(("Busca (perguntas com resposta no material)", ["Fonte", *RETRIEVAL_LABELS.values()], [
        [SOURCE_LABELS[source], *(_value(f"retrieval.{source}.{name}", metrics["retrieval"][source][name])
                                  for name in RETRIEVAL_LABELS)]
        for source in SOURCE_LABELS
    ]))

    if metrics.get("judge"):
        rows = []
        for criterion, entry in metrics["judge"].items():
            agreement = entry.get("human_agreement")
            status = "não conferido" if agreement is None else ("sim" if agreement >= 0.8 else "NÃO CONFIÁVEL")
            rows.append([CRITERIA[criterion]["label"], pct(entry["score"]), pct(agreement), status])
        out.append((f"Comportamento (juiz: {config['judge_model']}; não entra na nota geral)",
                    ["Critério", "Nota", "Concordância com a pessoa", "Confiável?"], rows))

    causes = metrics["diagnosis"]["by_cause"]
    if any(causes.values()):
        out.append(("Causa dos erros", ["Causa", "Perguntas"], [
            [CAUSE_LABELS[cause], str(count)] for cause, count in causes.items() if count
        ]))

    out.append(("Por tipo de pergunta", ["Tipo", "Nota"], [
        [CATEGORY_LABELS[name], pct(value)] for name, value in metrics["diagnosis"]["by_category"].items()
    ]))
    if metrics["diagnosis"]["by_procedure"]:
        out.append(("Por procedimento", ["Procedimento", "Nota"], [
            [name, pct(value)] for name, value in metrics["diagnosis"]["by_procedure"].items()
        ]))

    if run.get("variance"):
        rows = [
            [metric_label(name), _value(name, entry["mean"]), _value(name, entry["min"]), _value(name, entry["max"]),
             _delta(name, entry["max"] - entry["min"]).lstrip("+")]
            for name, entry in run["variance"].items() if not name.startswith(("retrieval.vector", "retrieval.bm25"))
        ]
        out.append((f"Variação entre {run['repeat']} repetições", ["Métrica", "Média", "Mínimo", "Máximo", "Amplitude"], rows))

    wrong = [result for result in run["results"] if not result["passed"]]
    if wrong:
        out.append((f"Perguntas erradas ({len(wrong)})", ["Item", "Pergunta", "Resposta", "Esperado", "Causa", "Detalhe"], [
            [result["item_id"], items[result["item_id"]].question, _short(result["answer"]),
             describe_expected(items[result["item_id"]]), CAUSE_LABELS.get(result["cause"], "—"),
             describe_problem(result)]
            for result in wrong
        ]))
    return out


def _print_wrong_items(console, title, rows):
    """As perguntas erradas saem em blocos: em tabela as colunas ficam estreitas demais."""
    console.print(f"[bold]{title}[/bold]\n")
    for item_id, question, answer, expected, cause, detail in rows:
        console.print(f"[red]✗[/red] [bold]{item_id}[/bold]  ({cause})")
        console.print(f"    Pergunta: {escape(question)}")
        console.print(f"    Resposta: {escape(answer)}")
        console.print(f"    Esperado: {escape(expected)}")
        if detail:
            console.print(f"    Detalhe:  {escape(detail)}")
        console.print()


def _print_sections(console, parts):
    for title, columns, rows in parts:
        if columns[0] == "Item":
            _print_wrong_items(console, title, rows)
            continue
        table = Table(title=title, title_justify="left", show_header=any(columns), header_style="bold")
        for column in columns:
            table.add_column(column, overflow="fold")
        for row in rows:
            table.add_row(*(escape(cell) for cell in row))
        console.print(table)
        console.print()


def print_scoreboard(run, gabarito, console=None):
    console = console or Console()
    console.print(f"\n[bold]Avaliação {run['run_id']}[/bold]\n")
    _print_sections(console, sections(run, gabarito))


def _markdown_table(columns, rows):
    def cell(text):
        return str(text).replace("|", "\\|").replace("\n", " ")

    header = columns if any(columns) else [" "] * len(columns)
    lines = ["| " + " | ".join(cell(c) for c in header) + " |", "|" + "---|" * len(columns)]
    lines.extend("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)
    return lines


def write_report(run, gabarito, path):
    """Grava o placar e o detalhe de todas as perguntas, com os trechos recuperados (FR-020)."""
    items = gabarito.by_id()
    lines = [f"# Avaliação {run['run_id']}", ""]
    for title, columns, rows in sections(run, gabarito):
        lines += [f"## {title}", "", *_markdown_table(columns, rows), ""]

    lines += ["## Todas as perguntas", ""]
    for result in run["results"]:
        item = items[result["item_id"]]
        status = "certo" if result["passed"] else f"ERRADO ({CAUSE_LABELS.get(result['cause'], '—')})"
        lines += [
            f"### {item.id}: {status}",
            "",
            f"- **Pergunta:** {item.question}",
            f"- **Resposta:** {' '.join(result['answer'].split())}",
            f"- **Esperado:** {describe_expected(item)}",
        ]
        problem = describe_problem(result)
        if problem:
            lines.append(f"- **Detalhe:** {problem}")
        if result["judge"]:
            verdicts = ", ".join(
                f"{CRITERIA[name]['label'].lower()} {'sim' if v['verdict'] else 'não' if v['verdict'] is False else '?'}"
                for name, v in result["judge"].items()
            )
            lines.append(f"- **Juiz:** {verdicts}")
        lines.append(f"- **Tempo:** {result['latency_s']:.1f} s")
        lines += ["", "Trechos enviados ao modelo:", ""]
        for chunk in result["retrieved"]["fused"]:
            lines += [f"{chunk['rank']}.", "", "   ```text", *("   " + line for line in chunk["content"].splitlines()), "   ```"]
        lines.append("")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def print_comparison(comparison, console=None, questions=None):
    """Regressões primeiro, mesmo quando a nota geral subiu."""
    console = console or Console()
    questions = questions or {}
    console.print(f"\n[bold]Comparação[/bold]: {comparison['base']} (base) → {comparison['candidate']}\n")
    if not comparison["comparable"]:
        console.print(f"[red]Não comparável:[/red] {comparison['reason']}")
        return
    for warning in comparison["warnings"]:
        console.print(f"[yellow]Aviso:[/yellow] {warning}\n")

    regressions = comparison["regressions"]
    if regressions:
        table = Table(title=f"REGRESSÕES: {len(regressions)} perguntas passaram de certo para errado",
                      title_justify="left", title_style="bold red", header_style="bold")
        for column in ("Item", "Pergunta", "Causa agora"):
            table.add_column(column, overflow="fold")
        for entry in regressions:
            table.add_row(entry["item_id"], escape(questions.get(entry["item_id"], "")), CAUSE_LABELS.get(entry["cause"], "—"))
        console.print(table)
    else:
        console.print("[green]Nenhuma regressão:[/green] nenhuma pergunta passou de certo para errado.")
    console.print()

    if comparison["config_changes"]:
        table = Table(title="O que mudou no assistente", title_justify="left", header_style="bold")
        for column in ("Parâmetro", "Base", "Agora"):
            table.add_column(column)
        for field, change in comparison["config_changes"].items():
            table.add_row(field, str(change["base"]), str(change["candidate"]))
        console.print(table)
    else:
        console.print("Configuração do assistente: sem mudanças registradas.")
    console.print()

    table = Table(title="Métricas", title_justify="left", header_style="bold")
    for column in ("Métrica", "Base", "Agora", "Diferença", ""):
        table.add_column(column)
    for name, entry in comparison["metric_deltas"].items():
        if name.startswith(("retrieval.vector", "retrieval.bm25")):
            continue
        delta = entry["delta"]
        # diferença menor do que o placar consegue mostrar conta como igual
        tolerance = 0.05 if name.startswith("operational.") else 0.005 if name.endswith(".mrr") else 0.0005
        changed = delta is not None and abs(delta) >= tolerance
        note = ""
        if changed and comparison["within_noise"].get(name):
            note = "dentro da variação"
        elif changed:
            better = (delta < 0) == (name in LOWER_IS_BETTER)
            note = "[green]melhor[/green]" if better else "[red]pior[/red]"
        difference = "—" if delta is None else _delta(name, delta) if changed else "="
        table.add_row(metric_label(name), _value(name, entry["base"]), _value(name, entry["candidate"]),
                      difference, note)
    console.print(table)
    console.print()

    improvements = comparison["improvements"]
    if improvements:
        table = Table(title=f"Melhorias: {len(improvements)} perguntas passaram de errado para certo",
                      title_justify="left", title_style="bold green", header_style="bold")
        for column in ("Item", "Pergunta", "Causa antes"):
            table.add_column(column, overflow="fold")
        for entry in improvements:
            table.add_row(entry["item_id"], escape(questions.get(entry["item_id"], "")),
                          CAUSE_LABELS.get(entry["previous_cause"], "—"))
        console.print(table)
        console.print()


def print_retrieval(summary, misses, console=None):
    console = console or Console()
    labels = {"hit": "Acerto", "recall": "Recall", "mrr": "MRR", "context_precision": "Precisão de contexto",
              "anchored": "Evidência ancorada"}
    table = Table(title="Busca (perguntas com resposta, recorte dev)", title_justify="left", header_style="bold")
    table.add_column("Fonte")
    for label in labels.values():
        table.add_column(label)
    for source, values in summary.items():
        table.add_row(SOURCE_LABELS[source], *(f"{values[name]:.2f}" if name == "mrr" else pct(values[name]) for name in labels))
    console.print(table)
    console.print()
    if not misses:
        console.print("[green]A evidência chegou ao modelo em todas as perguntas.[/green]")
    for miss in misses:
        console.print(f"[red]✗[/red] [bold]{miss['item_id']}[/bold]: {escape(miss['question'])}")
        console.print("    Recuperou: " + escape(" | ".join(title[:40] for title in miss["retrieved"])))


def print_kb_report(report, console=None, strategy=None, stale_reason=None):
    console = console or Console()
    mismatch = report["source_mismatch"]
    name = f" (estratégia {strategy})" if strategy else ""
    console.print(f"\n[bold]Base de conhecimento{name}[/bold]: {report['chunk_count']} trechos na base vetorial\n")
    if stale_reason:
        console.print(f"[yellow]Aviso:[/yellow] {escape(stale_reason)}\n")

    duplicates = report["duplicates"]
    console.print(f"[bold]Trechos duplicados:[/bold] {len(duplicates)}")
    for entry in duplicates:
        console.print(f"  - {entry['count']}x: {escape(_short(entry['content'], 100))}")

    unanchored = report["unanchored"]
    console.print(f"[bold]Fatos sem trecho com o nome do procedimento:[/bold] {len(unanchored)}")
    for entry in unanchored:
        reason = ("nenhum trecho contém a evidência inteira" if entry["kind"] == "missing"
                  else f"nenhum trecho com a evidência cita \"{entry['procedure']}\"")
        console.print(f"  - {entry['item_id']}: \"{escape(entry['evidence'])}\" ({reason})")

    corrupted = report["corrupted"]
    console.print(f"[bold]Trechos com texto corrompido:[/bold] {len(corrupted)}")
    for code in sorted({code for entry in corrupted for code in entry["chars"]}):
        holders = [entry["content"] for entry in corrupted if code in entry["chars"]]
        position = holders[0].index(chr(int(code[2:], 16)))
        excerpt = " ".join(holders[0][max(0, position - 30):position + 30].split())
        console.print(f"  - {code} em {len(holders)} trecho(s), por exemplo: \"…{escape(excerpt)}…\"")

    console.print(
        f"[bold]Base vetorial x arquivo de trechos:[/bold] "
        + ("iguais" if not mismatch["mismatch"] else
           f"DIFERENTES ({mismatch['vector_count']} na base vetorial, {mismatch['file_count']} no arquivo; "
           f"{mismatch['only_in_vector']} só na base, {mismatch['only_in_file']} só no arquivo)")
    )
    console.print()


INDEX_STATE_LABELS = {
    "current": "[green]atual[/green]",
    "stale": "[yellow]desatualizado[/yellow]",
    "missing": "[red]ausente[/red]",
}
SCORE_NOTE = (
    "O Score mede o quanto os trechos se parecem com a pergunta, não se estão certos: quem mede acerto é o True Rate. "
    "Ele só é comparável entre experimentos com o mesmo modelo de embedding e a mesma opção de HyDE."
)


def print_settings(settings, index_states, console=None):
    """Estratégias (com o estado do índice de cada uma) e experimentos declarados."""
    console = console or Console()
    table = Table(title="Estratégias de divisão", title_justify="left", header_style="bold")
    for column in ("Nome", "Tipo", "Parâmetros", "Índice"):
        table.add_column(column)
    for name, strategy in settings.strategies.items():
        state, _ = index_states[name]
        parameters = ", ".join(f"{key} {value}" for key, value in strategy.parameters.items()) or "—"
        table.add_row(name, strategy.type, parameters, INDEX_STATE_LABELS[state])
    console.print(table)
    for name, (state, reason) in index_states.items():
        if reason:
            console.print(f"  {escape(reason)}")

    table = Table(title="Experimentos", title_justify="left", header_style="bold")
    for column in ("Nome", "Estratégia", "Busca", "Trechos", "Threshold", "HyDE", "Assistente"):
        table.add_column(column, no_wrap=True)
    for name, experiment in settings.experiments.items():
        mark = "← em uso" if name == settings.assistant.exp_name else ""
        table.add_row(name, experiment.collection, experiment.search_type, str(experiment.match_count),
                      f"{experiment.match_threshold:.2f}", str(experiment.use_hyde), mark)
    console.print(table)


def experiments_table(results):
    """Linhas de texto da tabela comparativa, com largura fixa: nada é cortado em terminal estreito."""
    header = ("Experiment", "Strategy", "Collection", "Threshold", "Count", "HyDE", "Score", "True Rate", "Anchored", "Time")
    rows = []
    for result in results:
        experiment = result.experiment
        done = result.status == "ok"
        rows.append((
            experiment.exp_name,
            experiment.search_type,
            experiment.collection,
            f"{experiment.match_threshold:.2f}",
            str(experiment.match_count),
            str(experiment.use_hyde),
            f"{result.score:.2f}" if done else "-",
            f"{result.hits}/{result.total}" if done else "-",
            pct(result.anchored_rate) if done else "-",
            f"{result.avg_latency_ms:.0f} ms" if done else "-",
        ))
    widths = [max(len(row[i]) for row in [header, *rows]) + 2 for i in range(len(header))]
    rule = "|" + "|".join("-" * width for width in widths) + "|"
    line = lambda cells: "|" + "|".join(cell.center(width) for cell, width in zip(cells, widths)) + "|"  # noqa: E731
    return [rule, line(header), rule, *(line(row) for row in rows), rule]


def print_experiments(results, console=None):
    """Tabela comparativa da bancada. results já vem ordenado (evaluation.experiments.sort_results)."""
    console = console or Console()
    table = experiments_table(results)
    plain = dict(highlight=False, markup=False, soft_wrap=True)
    console.print()
    console.print("=" * len(table[0]), **plain)
    console.print("COMPARISON OF RETRIEVAL STRATEGIES", **plain)
    console.print("=" * len(table[0]), **plain)
    for row in table:
        console.print(row, **plain)
    console.print("Ordenado por True Rate, depois por Score (no empate, experimentos com HyDE ficam depois).", **plain)

    for result in results:
        if result.status != "ok":
            label = "não executado" if result.status == "not_run" else "incompleto"
            console.print(f"[yellow]{result.experiment.exp_name} ({label}):[/yellow] {escape(result.reason)}")
    console.print(f"\n{SCORE_NOTE}\n", highlight=False)


def print_coverage(summary, console=None):
    console = console or Console()
    console.print(f"{summary['total']} perguntas, {summary['unanswerable']} sem resposta no material, "
                  f"{summary['smoke']} na avaliação reduzida")
    console.print("Por recorte: " + ", ".join(f"{name} {count}" for name, count in summary["by_split"].items()))
    console.print("Por tipo: " + ", ".join(
        f"{CATEGORY_LABELS[name].lower()} {count}" for name, count in summary["by_category"].items()))
    console.print("Por procedimento: " + ", ".join(
        f"{name} {count}" for name, count in summary["by_procedure"].items()))
