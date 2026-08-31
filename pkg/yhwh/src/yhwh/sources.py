"""Raw source labels, configurable canonical groupings, and source arithmetic."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Mapping

DEFAULT_MODEL_SOURCES = ("J", "E", "P", "R", "D")

# Exact rules precede regex rules. Raw labels are *never* discarded from the dataset.
DEFAULT_EXACT: dict[str, str] = {
    "J": "J",
    "E": "E",
    "P": "P",
    "R": "R",
    "RJE": "R",
    "RE": "R",
    "RJ": "R",
    "RP": "R",
    "D": "D",
    "Dtn": "D",
    "Dtr": "D",
    "Dtr1": "D",
    "Dtr2": "D",
    "DH": "D",
    "DHist": "D",
    "Deuteronomist": "D",
    "Other": "Other",
    "Proto": "Proto",
}

DEFAULT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"^D(?:tn|tr|H|Hist|eut|[0-9]|[_-])", "D"),
    (r"^R(?:JE|J|E|P|D|[0-9]|[_-])", "R"),
    (r"^J(?:[0-9]|[_-])", "J"),
    (r"^E(?:[0-9]|[_-])", "E"),
    (r"^P(?:[0-9]|g|s|h|riest|[_-])", "P"),
    (r"^Proto", "Proto"),
    (r"^Poem|^Song|^Oracle", "Proto"),
    (r"^Other|^Anom", "Other"),
)


@dataclass(frozen=True)
class SourceMap:
    """Map literal corpus labels to analysis groups without mutating raw evidence."""

    exact: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_EXACT))
    patterns: tuple[tuple[str, str], ...] = DEFAULT_PATTERNS
    unknown: str = "keep"

    def canonical(self, label: str | None) -> str | None:
        if label is None:
            return None
        clean = label.strip()
        if clean in self.exact:
            return self.exact[clean]
        for pattern, replacement in self.patterns:
            if re.search(pattern, clean, flags=re.IGNORECASE):
                return replacement
        if self.unknown == "other":
            return "Other"
        if self.unknown == "drop":
            return None
        return clean

    def map_weights(self, weights: Mapping[str, float]) -> Counter[str]:
        result: Counter[str] = Counter()
        for raw, weight in weights.items():
            label = self.canonical(raw)
            if label is not None:
                result[label] += float(weight)
        return result

    def map_many(self, labels: Iterable[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(x for x in (self.canonical(v) for v in labels) if x))


DEFAULT_SOURCE_MAP = SourceMap()


def canonical_source(label: str | None, source_map: SourceMap = DEFAULT_SOURCE_MAP) -> str | None:
    return source_map.canonical(label)


def source_sort_key(label: str) -> tuple[int, str]:
    order = {"J": 0, "E": 1, "P": 2, "R": 3, "D": 4, "Proto": 5, "Other": 6}
    return order.get(label, 99), label
