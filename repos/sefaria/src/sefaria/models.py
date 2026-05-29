from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TextTree = str | list["TextTree"]


def flatten_text(value: Any) -> list[str]:
    """Flatten Sefaria's nested text arrays into printable lines."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        out: list[str] = []
        for item in value:
            out.extend(flatten_text(item))
        return out
    return [str(value)]


@dataclass(frozen=True)
class TextVersion:
    language: str | None
    version_title: str | None
    text: Any
    raw: dict[str, Any]

    def lines(self) -> list[str]:
        return flatten_text(self.text)

    def plain(self, sep: str = "\n") -> str:
        return sep.join(x for x in self.lines() if x != "")


@dataclass(frozen=True)
class TextResult:
    ref: str
    versions: list[TextVersion]
    raw: dict[str, Any]

    @property
    def first(self) -> TextVersion:
        if not self.versions:
            raise ValueError(f"No text versions returned for {self.ref!r}")
        return self.versions[0]

    def lines(self) -> list[str]:
        return self.first.lines()

    def plain(self, sep: str = "\n") -> str:
        return self.first.plain(sep=sep)


@dataclass(frozen=True)
class Version:
    language: str | None
    version_title: str | None
    version_source: str | None
    status: str | None
    priority: float | int | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class VersionsResult:
    index: str
    versions: list[Version]
    raw: dict[str, Any]

    def for_lang(self, lang: str) -> list[Version]:
        lang = lang.lower()
        return [v for v in self.versions if (v.language or "").lower() == lang]
