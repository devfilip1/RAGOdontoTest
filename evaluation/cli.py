"""Linha de comando da avaliação: python -m evaluation <comando> (contracts/cli.md)."""
import argparse
import json
import sys
from datetime import datetime

from rich.console import Console
from rich.markup import escape
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeElapsedColumn

from evaluation import calibrate, history, report
from evaluation.aggregate import aggregate, variance
from evaluation.compare import compare
from evaluation.dataset import GabaritoError, coverage, load_gabarito, load_source_text, select_subset, validate
from assistant.settings import SettingsError

EXIT_OK, EXIT_ERROR, EXIT_USAGE = 0, 1, 2

console = Console()


class UsageError(Exception):
    pass


def _load_valid_gabarito():
    """Carrega e valida o gabarito; mostra os problemas e devolve None se inválido."""
    try:
        gabarito = load_gabarito()
        problems = validate(gabarito, load_source_text())
    except GabaritoError as error:
        gabarito, problems = None, error.problems
    if problems:
        console.print(f"[red]Gabarito inválido:[/red] {len(problems)} problema(s)")
        for problem in problems:
            console.print(f"  - {escape(problem)}")
        return None
    return gabarito


def _experiment(name):
    """Experimento pelo nome, ou o do assistente. Nome inexistente vira erro de uso com a lista dos válidos."""
    from assistant import settings

    if name is None:
        return settings.assistant_experiment()
    try:
        return settings.get_experiment(name)
    except KeyError as error:
        raise UsageError(error.args[0]) from error


def _strategy(name):
    from assistant import settings

    try:
        return settings.get_strategy(name)
    except KeyError as error:
        raise UsageError(error.args[0]) from error


def _require_index(strategy_name):
    """Devolve o motivo se o índice da estratégia não puder ser usado, ou None."""
    from assistant.index import CURRENT, index_state

    state, reason = index_state(_strategy(strategy_name))
    return None if state == CURRENT else reason


def cmd_validate(args):
    from assistant import settings
    from assistant.index import index_state

    loaded = settings.load_settings()  # configuração inválida sai pelo tratamento de SettingsError em main()
    gabarito = _load_valid_gabarito()
    if gabarito is None:
        return EXIT_USAGE
    console.print("[green]Configuração válida[/green] (config/strategies.yaml e config/experiments.yaml)")
    states = {name: index_state(strategy) for name, strategy in loaded.strategies.items()}
    report.print_settings(loaded, states, console)
    console.print(f"\n[green]Gabarito válido[/green] (versão {gabarito.version})")
    report.print_coverage(coverage(gabarito), console)
    return EXIT_OK


def _questions(gabarito):
    return {item.id: item.question for item in gabarito.items}


def cmd_run(args):
    gabarito = _load_valid_gabarito()
    if gabarito is None:
        return EXIT_USAGE

    from assistant.config import OLLAMA_BASE_URL
    from assistant.pipeline import RagConfig

    from evaluation.judge import judge_model_name, make_judge
    from evaluation.runner import eval_config, preflight, run_evaluation, warm_up

    experiment = _experiment(args.experiment)
    unavailable = _require_index(experiment.collection)
    if unavailable:
        console.print(f"[red]Erro:[/red] {escape(unavailable)}")
        return EXIT_ERROR
    config = eval_config(RagConfig.from_experiment(experiment))
    judge_model = None if args.no_judge else judge_model_name(config.chat_model)

    problems = preflight([config.chat_model, config.embedding_model, *([judge_model] if judge_model else [])],
                         OLLAMA_BASE_URL)
    if problems:
        for problem in problems:
            console.print(f"[red]Erro:[/red] {problem}")
        return EXIT_ERROR

    try:
        warm_up(config)
    except Exception as error:
        console.print(f"[red]Erro:[/red] o assistente não respondeu: {escape(f'{type(error).__name__}: {error}')}")
        return EXIT_ERROR

    subset = "smoke" if args.smoke else "holdout" if args.holdout else "dev"
    items = select_subset(gabarito, subset)
    judge_fn = make_judge(judge_model, OLLAMA_BASE_URL) if judge_model else None
    started_at = datetime.now().astimezone()

    with Progress(TextColumn("{task.description}"), BarColumn(), MofNCompleteColumn(), TimeElapsedColumn(),
                  console=console) as progress:
        task = progress.add_task(f"Avaliando ({report.SUBSET_LABELS[subset]})", total=len(items) * args.repeat)
        outcome = run_evaluation(items, gabarito, config, judge_fn, args.repeat, lambda: progress.advance(task))

    items_by_id = gabarito.by_id()
    agreement = calibrate.load_agreement(judge_model) if judge_model else {}
    repetitions = outcome["repetitions"]
    complete = outcome["status"] == "complete"
    run = {
        "run_id": history.new_run_id(args.label, started_at),
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": outcome["status"],
        "subset": subset,
        "gabarito_version": gabarito.version,
        "gabarito_hash": gabarito.hash,
        "config": history.snapshot_config(config, judge_model),
        "repeat": args.repeat,
        "results": repetitions[0],
        "metrics": aggregate(repetitions[0], items_by_id, agreement),
        "skipped": outcome["skipped"],
    }
    if complete and args.repeat > 1:
        run["variance"] = variance([aggregate(results, items_by_id) for results in repetitions])

    folder = history.save_run(run)
    if not complete:
        console.print(f"\n[red]Avaliação incompleta:[/red] {escape(outcome['error'])}")
        console.print(f"{len(run['skipped'])} pergunta(s) não avaliada(s): {', '.join(run['skipped'])}")
        console.print(f"Resultado parcial gravado em {folder} (fora do histórico).")
        return EXIT_ERROR

    report.write_report(run, gabarito, folder / "report.md")
    report.print_scoreboard(run, gabarito, console)
    console.print(f"Gravado em {folder}\n")

    baseline_id = history.get_baseline(subset)
    if baseline_id and baseline_id != run["run_id"]:
        try:
            base = history.load_run(baseline_id)
        except FileNotFoundError:
            console.print(f"[yellow]Aviso:[/yellow] a referência {baseline_id} não foi encontrada.")
        else:
            report.print_comparison(compare(base, run), console, _questions(gabarito))
    elif subset in history.BASELINE_SUBSETS and not baseline_id:
        console.print("Ainda não há referência para este recorte. Para marcar esta execução: "
                      "python -m evaluation baseline set")
    return EXIT_OK


def cmd_retrieval(args):
    from evaluation import experiments as bench

    experiment = _experiment(args.experiment)
    gabarito = _load_valid_gabarito()
    if gabarito is None:
        return EXIT_USAGE

    result = bench.run_experiment(experiment, bench.select_items(gabarito), gabarito)
    if result.status != bench.OK:
        console.print(f"[red]Erro:[/red] {escape(result.reason)}")
        return EXIT_ERROR
    console.print(f"Experimento [bold]{experiment.exp_name}[/bold] (estratégia {experiment.collection}, "
                  f"busca {experiment.search_type}, até {experiment.match_count} trechos)\n")
    report.print_retrieval(bench.source_summary(result), bench.misses(result), console)
    return EXIT_OK


def cmd_experiments(args):
    from assistant import settings
    from assistant.config import OLLAMA_BASE_URL, OLLAMA_CHAT_MODEL, OLLAMA_EMBEDDING_MODEL

    from evaluation import experiments as bench
    from evaluation.runner import preflight

    chosen = [_experiment(name) for name in args.names] if args.names else settings.experiments()
    gabarito = _load_valid_gabarito()
    if gabarito is None:
        return EXIT_USAGE

    models = [OLLAMA_EMBEDDING_MODEL] + ([OLLAMA_CHAT_MODEL] if any(e.use_hyde for e in chosen) else [])
    problems = preflight(models, OLLAMA_BASE_URL)
    if problems:
        for problem in problems:
            console.print(f"[red]Erro:[/red] {problem}")
        return EXIT_ERROR

    items = bench.select_items(gabarito)
    started_at = datetime.now()
    results = []
    for experiment in chosen:
        with Progress(TextColumn("{task.description}"), BarColumn(), MofNCompleteColumn(), TimeElapsedColumn(),
                      console=console) as progress:
            task = progress.add_task(f"Retrieving and evaluating ({experiment.exp_name})", total=len(items))
            on_question = None
            if args.verbose:
                on_question = lambda question: progress.console.print(  # noqa: E731
                    escape(bench.format_question_line(question)), highlight=False, soft_wrap=True)
            results.append(bench.run_experiment(
                experiment, items, gabarito, on_progress=lambda: progress.advance(task), on_question=on_question))

    ordered = bench.sort_results(results)
    report.print_experiments(ordered, console)
    summary_path, questions_path = bench.write_csv(ordered, started_at, gabarito.version, OLLAMA_EMBEDDING_MODEL)
    console.print(f"Resultados gravados em:\n  {summary_path}\n  {questions_path}\n")
    return EXIT_OK if any(result.status == bench.OK for result in results) else EXIT_ERROR


def _resolve_pair(args):
    if args.base and args.candidate:
        return history.load_run(args.base), history.load_run(args.candidate)
    if args.base:
        candidate = history.load_run(args.base)
    else:
        candidate = history.latest_run("dev")
        if candidate is None:
            raise UsageError("não há nenhuma avaliação completa do recorte dev")
    baseline_id = history.get_baseline(candidate["subset"])
    if not baseline_id:
        raise UsageError(f"não há referência para o recorte {candidate['subset']}; "
                         "marque uma com: python -m evaluation baseline set")
    if baseline_id == candidate["run_id"]:
        raise UsageError(f"a avaliação mais recente ({baseline_id}) é a própria referência; "
                         "rode uma nova avaliação ou informe as duas execuções")
    return history.load_run(baseline_id), candidate


def cmd_compare(args):
    base, candidate = _resolve_pair(args)
    comparison = compare(base, candidate)
    try:
        questions = _questions(load_gabarito())
    except (GabaritoError, OSError):
        questions = {}
    report.print_comparison(comparison, console, questions)
    return EXIT_OK if comparison["comparable"] else EXIT_USAGE


def cmd_baseline(args):
    if args.action == "show":
        found = False
        for subset in history.BASELINE_SUBSETS:
            run_id = history.get_baseline(subset)
            if run_id:
                found = True
                console.print(f"Referência ({subset}): {run_id}")
        if not found:
            console.print("Nenhuma referência marcada.")
        return EXIT_OK

    run_id = args.run_id
    if run_id is None:
        runs = [run for run in history.list_runs() if run["subset"] in history.BASELINE_SUBSETS]
        if not runs:
            raise UsageError("não há nenhuma avaliação completa para marcar como referência")
        run_id = runs[0]["run_id"]
    try:
        run = history.set_baseline(run_id)
    except ValueError as error:
        raise UsageError(str(error)) from error
    console.print(f"Referência do recorte {run['subset']}: {run_id} "
                  f"(nota geral {report.pct(run['metrics']['overall']['pass_rate'])})")
    return EXIT_OK


def cmd_list(args):
    runs = history.list_runs()
    if not runs:
        console.print("Nenhuma avaliação completa gravada.")
        return EXIT_OK
    baselines = {history.get_baseline(subset) for subset in history.BASELINE_SUBSETS}
    for run in runs:
        mark = "  ← referência" if run["run_id"] in baselines else ""
        console.print(f"{run['run_id']:<45} {run['subset']:<8} gabarito {run['gabarito_version']:<14} "
                      f"nota {report.pct(run['metrics']['overall']['pass_rate']):>6}{mark}")
    return EXIT_OK


def cmd_kb_check(args):
    from evaluation import kb_checks

    from assistant.index import MISSING, index_state

    strategy = _strategy(args.strategy or _experiment(None).collection)
    state, reason = index_state(strategy)
    if state == MISSING:
        console.print(f"[red]Erro:[/red] {escape(reason)}")
        return EXIT_ERROR
    try:
        gabarito = load_gabarito()
        vector_chunks, file_chunks = kb_checks.load_kb(strategy.name)
    except (GabaritoError, OSError, ValueError) as error:
        console.print(f"[red]Erro:[/red] não foi possível ler a base de conhecimento: {escape(str(error))}")
        return EXIT_ERROR
    checks = kb_checks.run_checks(gabarito, vector_chunks, file_chunks)
    report.print_kb_report(checks, console, strategy=strategy.name, stale_reason=reason)
    return EXIT_OK


def cmd_calibrate(args):
    if args.action == "export":
        run = history.load_run(args.run_id) if args.run_id else next(
            (run for run in history.list_runs() if run["config"]["judge_model"]), None)
        if run is None or not run["config"]["judge_model"]:
            raise UsageError("não há avaliação com juiz; rode: python -m evaluation run")
        sample = calibrate.export_sample(run, load_gabarito().by_id(), args.size)
        console.print(f"{len(sample['samples'])} respostas de {run['run_id']} gravadas em {calibrate.LABELS_PATH}")
        console.print("Preencha os campos \"human\" com true ou false e rode: python -m evaluation calibrate score")
        return EXIT_OK

    if not calibrate.LABELS_PATH.is_file():
        raise UsageError("não há amostra; rode: python -m evaluation calibrate export")
    labels = json.loads(calibrate.LABELS_PATH.read_text(encoding="utf-8"))
    agreement = calibrate.score_agreement(labels, history.load_run(labels["run_id"]))
    if not any(entry["compared"] for entry in agreement["criteria"].values()):
        raise UsageError(f"nenhum campo \"human\" preenchido em {calibrate.LABELS_PATH}")
    calibrate.save_agreement(agreement)
    console.print(f"Concordância entre a pessoa e o juiz ({agreement['judge_model']}):")
    for name, entry in agreement["criteria"].items():
        status = "[green]confiável[/green]" if entry["reliable"] else "[red]NÃO CONFIÁVEL[/red]"
        pending = f", {entry['unfilled']} sem preencher" if entry["unfilled"] else ""
        console.print(f"  {report.CRITERIA[name]['label']:<28} {report.pct(entry['agreement']):>6} "
                      f"em {entry['compared']} respostas{pending}  {status}")
    return EXIT_OK


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m evaluation", description="Avaliação do assistente OdontoTest")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="roda a avaliação e grava o resultado")
    subset = run.add_mutually_exclusive_group()
    subset.add_argument("--smoke", action="store_true", help="só os itens da avaliação reduzida")
    subset.add_argument("--holdout", action="store_true", help="só a parte reservada")
    run.add_argument("--repeat", type=int, default=1, metavar="N", help="roda N vezes e informa a variação")
    run.add_argument("--no-judge", action="store_true", help="pula as métricas de juiz")
    run.add_argument("--label", metavar="TEXTO", help="rótulo acrescentado ao id da execução")
    run.add_argument("--experiment", metavar="NOME",
                     help="experimento de config/experiments.yaml a avaliar (padrão: o do assistente)")
    run.set_defaults(handler=cmd_run)

    comparison = commands.add_parser("compare", help="compara duas avaliações")
    comparison.add_argument("base", nargs="?")
    comparison.add_argument("candidate", nargs="?")
    comparison.set_defaults(handler=cmd_compare)

    baseline = commands.add_parser("baseline", help="marca ou mostra a avaliação de referência")
    baseline.add_argument("action", choices=("set", "show"))
    baseline.add_argument("run_id", nargs="?")
    baseline.set_defaults(handler=cmd_baseline)

    retrieval = commands.add_parser("retrieval", help="mede só a busca, sem gerar respostas")
    retrieval.add_argument("--experiment", metavar="NOME", help="experimento a detalhar (padrão: o do assistente)")
    retrieval.set_defaults(handler=cmd_retrieval)

    bench = commands.add_parser("experiments", help="roda os experimentos de busca e mostra a tabela comparativa")
    bench.add_argument("names", nargs="*", metavar="NOME", help="experimentos a rodar (padrão: todos)")
    bench.add_argument("--verbose", action="store_true", help="mostra uma linha por pergunta: pergunta;acertou;nota")
    bench.set_defaults(handler=cmd_experiments)

    commands.add_parser("list", help="lista as avaliações completas").set_defaults(handler=cmd_list)
    kb_check = commands.add_parser("kb-check", help="verifica a base de conhecimento")
    kb_check.add_argument("--strategy", metavar="NOME", help="estratégia a verificar (padrão: a do assistente)")
    kb_check.set_defaults(handler=cmd_kb_check)
    commands.add_parser("validate", help="valida a configuração e o gabarito").set_defaults(handler=cmd_validate)

    calibration = commands.add_parser("calibrate", help="confere o juiz contra uma pessoa")
    calibration.add_argument("action", choices=("export", "score"))
    calibration.add_argument("run_id", nargs="?")
    calibration.add_argument("--size", type=int, default=20)
    calibration.set_defaults(handler=cmd_calibrate)
    return parser


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    if getattr(args, "repeat", 1) < 1:
        console.print("[red]Erro:[/red] --repeat precisa ser 1 ou mais")
        return EXIT_USAGE
    try:
        return args.handler(args)
    except SettingsError as error:
        console.print(f"[red]Configuração inválida:[/red] {len(error.problems)} problema(s)")
        for problem in error.problems:
            console.print(f"  - {escape(problem)}")
        return EXIT_USAGE
    except (UsageError, FileNotFoundError) as error:
        console.print(f"[red]Erro:[/red] {escape(str(error))}")
        return EXIT_USAGE
