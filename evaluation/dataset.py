"""Gabarito de perguntas: carga, validação e recortes."""
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import jsonschema

from evaluation.normalize import FACT_UNITS, extract_values, normalize_text

PACKAGE_DIR = Path(__file__).parent
GABARITO_PATH = PACKAGE_DIR / "data" / "gabarito.json"
SCHEMA_PATH = PACKAGE_DIR / "schemas" / "gabarito.schema.json"

MIN_ITEMS = 40
MIN_UNANSWERABLE = 6
REQUIRED_CATEGORIES_PER_PROCEDURE = ("price", "duration", "result")
SUBSETS = ("dev", "holdout", "smoke")


class GabaritoError(Exception):
    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Fact:
    type: str
    label: str
    values: tuple = ()
    unit: str | None = None
    alternatives: tuple = ()

    def targets(self):
        """Chaves (kind, valor, unidade) no mesmo formato de normalize.Value.key."""
        if self.type == "money":
            return [("money", round(float(v), 2), None) for v in self.values]
        if self.type == "duration":
            factor, unit = FACT_UNITS[self.unit]
            return [("duration", round(float(v) * factor, 2), unit) for v in self.values]
        return []


@dataclass(frozen=True)
class Item:
    id: str
    question: str
    category: str
    procedure: str | None
    answerable: bool
    split: str
    smoke: bool
    expected_facts: tuple = ()
    allowed_facts: tuple = ()
    evidence: tuple = ()
    variant_of: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class Gabarito:
    version: str
    hash: str
    procedures: dict = field(default_factory=dict)  # nome -> lista de âncoras
    items: tuple = ()

    def by_id(self):
        return {item.id: item for item in self.items}

    def anchors(self, procedure):
        return self.procedures.get(procedure, []) if procedure else []


def _fact(raw):
    return Fact(
        type=raw["type"],
        label=raw["label"],
        values=tuple(raw.get("values", ())),
        unit=raw.get("unit"),
        alternatives=tuple(raw.get("alternatives", ())),
    )


def parse_gabarito(data, file_hash=""):
    """Monta o gabarito a partir do JSON já lido. Levanta GabaritoError se fugir do esquema."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        raise GabaritoError([f"esquema: {'/'.join(map(str, e.path)) or '(raiz)'}: {e.message}" for e in errors])

    items = tuple(
        Item(
            id=raw["id"],
            question=raw["question"],
            category=raw["category"],
            procedure=raw["procedure"],
            answerable=raw["answerable"],
            split=raw["split"],
            smoke=raw["smoke"],
            expected_facts=tuple(_fact(f) for f in raw.get("expected_facts", ())),
            allowed_facts=tuple(_fact(f) for f in raw.get("allowed_facts", ())),
            evidence=tuple(raw.get("evidence", ())),
            variant_of=raw.get("variant_of"),
            notes=raw.get("notes"),
        )
        for raw in data["items"]
    )
    procedures = {name: list(value["anchors"]) for name, value in data["procedures"].items()}
    return Gabarito(version=data["version"], hash=file_hash, procedures=procedures, items=items)


def load_gabarito(path=GABARITO_PATH):
    raw = Path(path).read_bytes()
    return parse_gabarito(json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest())


@lru_cache(maxsize=1)
def load_source_text():
    """Texto completo do material da clínica, página a página."""
    from pypdf import PdfReader

    from assistant.config import SOURCE_PDF

    return "\n".join(page.extract_text() for page in PdfReader(SOURCE_PDF).pages)


def validate(gabarito, source_text, check_coverage=True):
    """Aplica as regras de validação do data-model. Devolve a lista de problemas."""
    problems = []
    source = normalize_text(source_text)
    by_id = gabarito.by_id()

    for item_id, count in Counter(item.id for item in gabarito.items).items():
        if count > 1:
            problems.append(f"{item_id}: id repetido {count} vezes")

    for item in gabarito.items:
        if item.answerable:
            if not item.expected_facts:
                problems.append(f"{item.id}: pergunta com resposta precisa de ao menos um fato esperado")
            if not item.evidence:
                problems.append(f"{item.id}: pergunta com resposta precisa de ao menos uma evidência")
        elif item.expected_facts or item.evidence:
            problems.append(f"{item.id}: pergunta sem resposta não pode ter fatos esperados nem evidência")

        for evidence in item.evidence:
            occurrences = source.count(normalize_text(evidence))
            if occurrences != 1:
                problems.append(
                    f"{item.id}: a evidência \"{evidence}\" aparece {occurrences} vezes no material (precisa ser 1)"
                )

        evidence_values = {v.key for evidence in item.evidence for v in extract_values(evidence)}
        for fact in item.expected_facts:
            for target in fact.targets():
                if target not in evidence_values:
                    problems.append(
                        f"{item.id}: o valor {target[1]:g} do fato \"{fact.label}\" não está em nenhuma evidência do item"
                    )

        if item.procedure is not None and item.procedure not in gabarito.procedures:
            problems.append(f"{item.id}: procedimento \"{item.procedure}\" não existe em procedures")

        if item.variant_of is not None:
            original = by_id.get(item.variant_of)
            if original is None:
                problems.append(f"{item.id}: variant_of aponta para \"{item.variant_of}\", que não existe")
            elif original.split != item.split:
                problems.append(f"{item.id}: variant_of aponta para item de outro split ({original.split})")

    if check_coverage:
        if len(gabarito.items) < MIN_ITEMS:
            problems.append(f"cobertura: {len(gabarito.items)} itens (mínimo {MIN_ITEMS})")
        for procedure in gabarito.procedures:
            categories = {item.category for item in gabarito.items if item.procedure == procedure}
            for category in REQUIRED_CATEGORIES_PER_PROCEDURE:
                if category not in categories:
                    problems.append(f"cobertura: procedimento \"{procedure}\" sem item de {category}")
        unanswerable = sum(1 for item in gabarito.items if not item.answerable)
        if unanswerable < MIN_UNANSWERABLE:
            problems.append(f"cobertura: {unanswerable} itens sem resposta no material (mínimo {MIN_UNANSWERABLE})")

    return problems


def select_subset(gabarito, subset):
    """dev e holdout são os dois recortes; smoke é a amostra pequena do dev."""
    if subset == "smoke":
        return [item for item in gabarito.items if item.smoke and item.split == "dev"]
    if subset in ("dev", "holdout"):
        return [item for item in gabarito.items if item.split == subset]
    raise ValueError(f"recorte desconhecido: {subset}")


def coverage(gabarito):
    return {
        "total": len(gabarito.items),
        "unanswerable": sum(1 for item in gabarito.items if not item.answerable),
        "by_category": dict(Counter(item.category for item in gabarito.items)),
        "by_procedure": dict(Counter(item.procedure or "(geral)" for item in gabarito.items)),
        "by_split": dict(Counter(item.split for item in gabarito.items)),
        "smoke": len(select_subset(gabarito, "smoke")),
    }
