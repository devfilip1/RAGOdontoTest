"""Estratégias de divisão e experimentos de busca, lidos de config/strategies.yaml e config/experiments.yaml."""
import hashlib
import json
from dataclasses import dataclass, field
from functools import lru_cache

import jsonschema
import yaml

from assistant.config import EXPERIMENTS_PATH, SCHEMAS_DIR, STRATEGIES_PATH

STRATEGY_TYPES = ("section", "split", "page")
SEARCH_TYPES = ("hybrid", "vector", "bm25")
TYPE_DEFAULTS = {"section": {"max_chars": 1200, "overlap": 100}, "split": {}, "page": {}}
# par (tamanho, sobreposição) de cada tipo: a sobreposição precisa ser menor que o tamanho
SIZE_AND_OVERLAP = {"section": ("max_chars", "overlap"), "split": ("chunk_size", "chunk_overlap")}


class SettingsError(Exception):
    """Configuração inválida. problems traz uma mensagem por problema, dizendo o que corrigir."""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Strategy:
    name: str
    type: str
    parameters: dict = field(default_factory=dict, hash=False)

    def definition_hash(self):
        """Muda quando o tipo ou os parâmetros mudam: é o que diz se um índice está desatualizado."""
        definition = json.dumps({"type": self.type, "parameters": self.parameters}, sort_keys=True)
        return hashlib.sha256(definition.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Experiment:
    exp_name: str
    collection: str
    search_type: str
    match_count: int
    match_threshold: float = 0.0
    use_hyde: bool = False


@dataclass(frozen=True)
class Settings:
    strategies: dict  # nome -> Strategy, na ordem do arquivo
    experiments: dict  # nome -> Experiment, na ordem do arquivo
    assistant: Experiment


def _schema(name):
    return json.loads((SCHEMAS_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def _load_yaml(text, file_name, problems):
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        problems.append(f"{file_name}: YAML inválido: {' '.join(str(error).split())}")
        return None
    if not isinstance(data, dict):
        problems.append(f"{file_name}: o arquivo está vazio ou não tem a estrutura esperada")
        return None
    return data


def _item_label(data, error, list_key, name_key):
    """Nome do item em que o erro aconteceu, para a mensagem apontar o lugar certo."""
    path = list(error.absolute_path)
    if len(path) >= 2 and path[0] == list_key and isinstance(path[1], int):
        item = data[list_key][path[1]]
        name = item.get(name_key) if isinstance(item, dict) else None
        label = f"\"{name}\"" if isinstance(name, str) else f"item {path[1] + 1}"
        return label, [str(part) for part in path[2:]]
    return None, [str(part) for part in path]


def _describe(error, label, where):
    """Traduz um erro do esquema em uma instrução do que corrigir."""
    target = f"{label}: " if label else ""
    name = where[-1] if where else None
    validator = error.validator

    if validator == "required":
        missing = [key for key in error.validator_value if key not in error.instance]
        if where and where[-1] == "parameters":
            return f"{target}faltam os parâmetros obrigatórios: {', '.join(missing)}"
        return f"{target}falta o campo obrigatório: {', '.join(missing)}"
    if validator == "additionalProperties":
        allowed = set(error.schema.get("properties", {}))
        unknown = [key for key in error.instance if key not in allowed]
        kind = "parâmetro desconhecido" if where and where[-1] == "parameters" else "campo desconhecido"
        hint = f" (aceitos: {', '.join(sorted(allowed))})" if allowed else ""
        return f"{target}{kind}: {', '.join(unknown)}{hint}"
    if validator == "maxProperties":
        return f"{target}este tipo não aceita parâmetros; remova: {', '.join(error.instance)}"
    if validator == "enum":
        options = ", ".join(str(option) for option in error.validator_value)
        return f"{target}{name} \"{error.instance}\" não existe; use um de: {options}"
    if validator in ("minimum", "maximum"):
        schema = error.schema
        if "minimum" in schema and "maximum" in schema:
            limits = f"de {schema['minimum']} a {schema['maximum']}"
        elif "minimum" in schema:
            limits = f"no mínimo {schema['minimum']}"
        else:
            limits = f"no máximo {schema['maximum']}"
        return f"{target}{name} é {error.instance}; o valor precisa ser {limits}"
    if validator == "pattern":
        return f"{target}nome \"{error.instance}\" inválido: use só letras minúsculas, dígitos e _"
    if validator == "minItems":
        return f"{name or where}: declare ao menos um item"
    if validator == "type":
        return f"{target}{name} tem o valor {error.instance!r}, que não é do tipo esperado ({error.validator_value})"
    return f"{target}{'/'.join(where)}: {error.message}"


def _schema_problems(data, schema_name, list_key, name_key, file_name):
    problems = []
    validator = jsonschema.Draft202012Validator(_schema(schema_name))
    for error in sorted(validator.iter_errors(data), key=lambda e: [str(part) for part in e.absolute_path]):
        label, where = _item_label(data, error, list_key, name_key)
        problems.append(f"{file_name}: {_describe(error, label, where)}")
    return problems


def _duplicates(items, name_key):
    seen, repeated = set(), []
    for item in items:
        name = item.get(name_key) if isinstance(item, dict) else None
        if isinstance(name, str):
            if name in seen and name not in repeated:
                repeated.append(name)
            seen.add(name)
    return repeated


def parse_settings(strategies_text, experiments_text):
    """Valida os dois arquivos e devolve Settings. Levanta SettingsError com todos os problemas encontrados."""
    problems = []
    strategies_file, experiments_file = "config/strategies.yaml", "config/experiments.yaml"
    strategies_data = _load_yaml(strategies_text, strategies_file, problems)
    experiments_data = _load_yaml(experiments_text, experiments_file, problems)

    strategies = {}
    if strategies_data is not None:
        problems += _schema_problems(strategies_data, "strategies", "strategies", "name", strategies_file)
        raw_strategies = strategies_data.get("strategies")
        raw_strategies = raw_strategies if isinstance(raw_strategies, list) else []
        for name in _duplicates(raw_strategies, "name"):
            problems.append(f"{strategies_file}: nome de estratégia repetido: \"{name}\"; cada estratégia precisa de um nome único")
        for raw in raw_strategies:
            if not isinstance(raw, dict) or raw.get("type") not in STRATEGY_TYPES or not isinstance(raw.get("name"), str):
                continue
            given = raw.get("parameters") if isinstance(raw.get("parameters"), dict) else {}
            parameters = {**TYPE_DEFAULTS[raw["type"]], **given}
            pair = SIZE_AND_OVERLAP.get(raw["type"])
            if pair and all(isinstance(parameters.get(key), int) for key in pair):
                size, overlap = pair
                if parameters[overlap] >= parameters[size]:
                    problems.append(
                        f"{strategies_file}: \"{raw['name']}\": {overlap} ({parameters[overlap]}) precisa ser menor "
                        f"que {size} ({parameters[size]})"
                    )
            strategies.setdefault(raw["name"], Strategy(raw["name"], raw["type"], parameters))

    experiments = {}
    assistant = None
    if experiments_data is not None:
        problems += _schema_problems(experiments_data, "experiments", "experiments", "exp_name", experiments_file)
        raw_experiments = experiments_data.get("experiments")
        raw_experiments = raw_experiments if isinstance(raw_experiments, list) else []
        for name in _duplicates(raw_experiments, "exp_name"):
            problems.append(f"{experiments_file}: nome de experimento repetido: \"{name}\"; cada experimento precisa de um nome único")
        for raw in raw_experiments:
            if not isinstance(raw, dict) or not isinstance(raw.get("exp_name"), str):
                continue
            name = raw["exp_name"]
            collection = raw.get("collection")
            if strategies_data is not None and isinstance(collection, str) and collection not in strategies:
                problems.append(
                    f"{experiments_file}: \"{name}\": a estratégia \"{collection}\" não existe em {strategies_file}; "
                    f"use uma de: {', '.join(strategies) or '(nenhuma válida)'}"
                )
            if raw.get("use_hyde") is True and raw.get("search_type") == "bm25":
                problems.append(
                    f"{experiments_file}: \"{name}\": use_hyde só funciona com busca vetorial; "
                    "troque search_type bm25 por hybrid ou vector, ou desligue use_hyde"
                )
            try:
                experiments.setdefault(name, Experiment(
                    exp_name=name,
                    collection=raw["collection"],
                    search_type=raw["search_type"],
                    match_count=raw["match_count"],
                    match_threshold=float(raw.get("match_threshold", 0.0)),
                    use_hyde=raw.get("use_hyde", False),
                ))
            except (KeyError, TypeError, ValueError):
                pass  # o problema já foi listado pelo esquema
        chosen = experiments_data.get("assistant")
        if isinstance(chosen, str):
            assistant = experiments.get(chosen)
            declared = [raw.get("exp_name") for raw in raw_experiments if isinstance(raw, dict)]
            if chosen not in declared:
                problems.append(
                    f"{experiments_file}: assistant aponta para \"{chosen}\", que não é um experimento declarado; "
                    f"use um de: {', '.join(str(name) for name in declared) or '(nenhum)'}"
                )

    if problems:
        raise SettingsError(problems)
    return Settings(strategies=strategies, experiments=experiments, assistant=assistant)


@lru_cache(maxsize=1)
def load_settings():
    """Lê e valida os dois arquivos de configuração. O resultado fica em cache durante a execução."""
    problems = []
    texts = []
    for path in (STRATEGIES_PATH, EXPERIMENTS_PATH):
        try:
            texts.append(path.read_text(encoding="utf-8"))
        except OSError:
            problems.append(f"config/{path.name}: arquivo não encontrado em {path}")
    if problems:
        raise SettingsError(problems)
    return parse_settings(*texts)


def strategies():
    return list(load_settings().strategies.values())


def experiments():
    return list(load_settings().experiments.values())


def get_strategy(name):
    """Estratégia pelo nome. KeyError com a lista das válidas se não existir."""
    found = load_settings().strategies
    if name not in found:
        raise KeyError(f"a estratégia \"{name}\" não existe; use uma de: {', '.join(found)}")
    return found[name]


def get_experiment(name):
    """Experimento pelo nome. KeyError com a lista dos válidos se não existir."""
    found = load_settings().experiments
    if name not in found:
        raise KeyError(f"o experimento \"{name}\" não existe; use um de: {', '.join(found)}")
    return found[name]


def assistant_experiment():
    """O experimento que o chat e a avaliação da resposta usam."""
    return load_settings().assistant
