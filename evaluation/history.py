"""Histórico das execuções: gravar, listar e marcar a referência."""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import jsonschema

PACKAGE_DIR = Path(__file__).parent
RUNS_DIR = PACKAGE_DIR / "runs"
RUN_SCHEMA_PATH = PACKAGE_DIR / "schemas" / "run.schema.json"
INCOMPLETE_DIR = "_incomplete"
BASELINE_FILE = "baseline.json"
BASELINE_SUBSETS = ("dev", "holdout")


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _git(*args):
    try:
        done = subprocess.run(["git", *args], capture_output=True, text=True, cwd=PACKAGE_DIR.parent, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout.strip() if done.returncode == 0 else None


def snapshot_config(rag_config, judge_model=None):
    """Configuração do assistente gravada junto com cada execução (data-model)."""
    from assistant.index import chunks_path
    from assistant.settings import get_strategy

    parameters = get_strategy(rag_config.strategy).parameters
    with open(chunks_path(rag_config.strategy), "r", encoding="utf-8") as f:
        chunks = [chunk["content"] for chunk in json.load(f)]
    status = _git("status", "--porcelain")
    return {
        "experiment": rag_config.experiment,
        "strategy": rag_config.strategy,
        "search_type": rag_config.search_type,
        "match_count": rag_config.match_count,
        "match_threshold": rag_config.match_threshold,
        "use_hyde": rag_config.use_hyde,
        # tamanho máximo e sobreposição dos trechos, quando a estratégia tem esses parâmetros
        "chunk_size": parameters.get("chunk_size", parameters.get("max_chars")),
        "chunk_overlap": parameters.get("chunk_overlap", parameters.get("overlap")),
        "vector_k": rag_config.vector_k,
        "bm25_k": rag_config.bm25_k,
        "final_k": rag_config.final_k,
        "chat_model": rag_config.chat_model,
        "embedding_model": rag_config.embedding_model,
        "temperature": rag_config.temperature,
        "seed": rag_config.seed,
        "num_ctx": None,
        "prompt_hash": _sha(rag_config.prompt_template + rag_config.user_template),
        "kb_hash": _sha("\n\x00".join(chunks)),
        "kb_chunk_count": len(chunks),
        "judge_model": judge_model,
        "git_commit": _git("rev-parse", "--short", "HEAD"),
        "git_dirty": bool(status),
    }


def new_run_id(label=None, now=None):
    run_id = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    if label:
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
        if slug:
            run_id += f"-{slug}"
    return run_id


def save_run(run, runs_dir=RUNS_DIR):
    """Grava a execução. Incompletas vão para _incomplete/ e ficam fora do histórico (FR-022)."""
    schema = json.loads(RUN_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(run, schema)

    folder = Path(runs_dir)
    if run["status"] != "complete":
        folder = folder / INCOMPLETE_DIR
    folder = folder / run["run_id"]
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
    return folder


def load_run(run_id, runs_dir=RUNS_DIR):
    path = Path(runs_dir) / run_id / "run.json"
    if run_id == INCOMPLETE_DIR or not path.is_file():
        raise FileNotFoundError(f"execução \"{run_id}\" não encontrada em {runs_dir}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_runs(runs_dir=RUNS_DIR):
    """Execuções completas, da mais recente para a mais antiga."""
    folder = Path(runs_dir)
    if not folder.is_dir():
        return []
    ids = sorted(
        (p.name for p in folder.iterdir() if p.name != INCOMPLETE_DIR and (p / "run.json").is_file()),
        reverse=True,
    )
    return [load_run(run_id, runs_dir) for run_id in ids]


def latest_run(subset, runs_dir=RUNS_DIR):
    return next((run for run in list_runs(runs_dir) if run["subset"] == subset), None)


def _read_baseline(runs_dir):
    path = Path(runs_dir) / BASELINE_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def get_baseline(subset, runs_dir=RUNS_DIR):
    """Id da execução de referência do recorte, ou None."""
    return _read_baseline(runs_dir).get(subset)


def set_baseline(run_id, runs_dir=RUNS_DIR):
    """Marca a execução como referência do recorte dela. Só aceita execução completa."""
    run = load_run(run_id, runs_dir)
    if run["status"] != "complete":
        raise ValueError(f"a execução \"{run_id}\" está incompleta e não pode ser referência")
    if run["subset"] not in BASELINE_SUBSETS:
        raise ValueError(f"a execução \"{run_id}\" é do recorte {run['subset']}; a referência é por dev ou holdout")

    baseline = _read_baseline(runs_dir)
    baseline[run["subset"]] = run_id
    baseline["set_at"] = datetime.now().isoformat(timespec="seconds")
    (Path(runs_dir) / BASELINE_FILE).write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return run
