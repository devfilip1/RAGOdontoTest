"""Onde fica o índice de cada estratégia e se ele ainda corresponde à estratégia declarada e ao material."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

from assistant.config import INDEX_DIR, OLLAMA_EMBEDDING_MODEL, SOURCE_PDF

CURRENT, STALE, MISSING = "current", "stale", "missing"


class IndexUnavailable(Exception):
    """O índice de uma estratégia está ausente ou desatualizado. A mensagem traz o comando que resolve."""


def index_dir(name, base=None):
    return Path(base or INDEX_DIR) / name


def chroma_dir(name, base=None):
    return index_dir(name, base) / "chroma"


def chunks_path(name, base=None):
    return index_dir(name, base) / "chunks.json"


def manifest_path(name, base=None):
    return index_dir(name, base) / "manifest.json"


def source_hash(path=SOURCE_PDF):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def ingest_command(name):
    return f"python -m assistant.ingest {name}"


def write_manifest(strategy, chunk_count, base=None, source=None, embedding_model=None):
    """Registra com que definição, material e modelo o índice foi criado."""
    manifest = {
        "strategy": strategy.name,
        "definition_hash": strategy.definition_hash(),
        "source_hash": source or source_hash(),
        "embedding_model": embedding_model or OLLAMA_EMBEDDING_MODEL,
        "chunk_count": chunk_count,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    path = manifest_path(strategy.name, base)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def read_manifest(name, base=None):
    path = manifest_path(name, base)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def index_state(strategy, base=None, source=None, embedding_model=None):
    """Devolve (estado, motivo). O motivo é None quando o índice está atual."""
    manifest = read_manifest(strategy.name, base)
    command = ingest_command(strategy.name)
    if manifest is None or not chunks_path(strategy.name, base).is_file():
        return MISSING, f"o índice da estratégia \"{strategy.name}\" ainda não foi criado; rode: {command}"

    changed = []
    if manifest.get("definition_hash") != strategy.definition_hash():
        changed.append("a definição da estratégia mudou")
    if manifest.get("source_hash") != (source or source_hash()):
        changed.append("o material da clínica mudou")
    if manifest.get("embedding_model") != (embedding_model or OLLAMA_EMBEDDING_MODEL):
        changed.append("o modelo de embedding mudou")
    if changed:
        return STALE, (
            f"o índice da estratégia \"{strategy.name}\" está desatualizado ({' e '.join(changed)}); rode: {command}"
        )
    return CURRENT, None


def require_index(strategy, base=None):
    """Levanta IndexUnavailable se o índice não puder ser usado."""
    state, reason = index_state(strategy, base)
    if state != CURRENT:
        raise IndexUnavailable(reason)
