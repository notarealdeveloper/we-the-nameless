from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import requests

from .models import TextResult, TextVersion, Version, VersionsResult


LANG_ALIASES = {
    "hebrew": "he",
    "he": "he",
    "english": "en",
    "en": "en",
    "spanish": "es",
    "es": "es",
    "french": "fr",
    "fr": "fr",
    "german": "de",
    "de": "de",
    "russian": "ru",
    "ru": "ru",
    "yiddish": "yi",
    "yi": "yi",
    "ladino": "lad",
    "lad": "lad",
}

SEFARIA_LANG_NAMES = {
    "he": "hebrew",
    "en": "english",
    "es": "spanish",
    "fr": "french",
    "de": "german",
    "ru": "russian",
    "yi": "yiddish",
    "lad": "ladino",
}


_REF_HAS_SECTION = re.compile(r"\d")


def normalize_lang(lang: str) -> str:
    return LANG_ALIASES.get(lang.lower(), lang.lower())


def sefaria_lang_name(lang: str) -> str:
    lang = normalize_lang(lang)
    return SEFARIA_LANG_NAMES.get(lang, lang)


def looks_like_book_ref(ref: str) -> bool:
    return _REF_HAS_SECTION.search(ref) is None


class SefariaError(RuntimeError):
    pass


class SefariaClient:
    def __init__(self, base_url: str = "https://www.sefaria.org", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "sefaria/0.1"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as e:
            raise SefariaError(f"Sefaria request failed: {e}") from e
        try:
            return response.json()
        except ValueError as e:
            raise SefariaError(f"Sefaria returned non-JSON response from {url}") from e

    def get_text(
        self,
        ref: str,
        *,
        lang: str = "en",
        version_title: str | None = None,
        version: str | None = None,
        fill_missing_segments: bool = False,
        return_format: str = "text_only",
        expand_book: bool = True,
    ) -> TextResult:
        """Fetch text for a Sefaria ref.

        `ref` may be a verse, chapter, range, or bare book title.

        Sefaria v3 resolves a bare book title like ``Genesis`` to its first
        chapter. When ``expand_book`` is true, this client expands bare book
        refs itself by using the index lengths and fetching every chapter.
        """
        if expand_book and looks_like_book_ref(ref):
            return self.get_book(
                ref,
                lang=lang,
                version_title=version_title,
                version=version,
                fill_missing_segments=fill_missing_segments,
                return_format=return_format,
            )

        return self._get_text_ref(
            ref,
            lang=lang,
            version_title=version_title,
            version=version,
            fill_missing_segments=fill_missing_segments,
            return_format=return_format,
        )

    def _version_param(
        self,
        *,
        lang: str,
        version_title: str | None = None,
        version: str | None = None,
        source: bool = False,
    ) -> str:
        if version:
            return version
        if source:
            return "source"
        language = sefaria_lang_name(lang)
        if version_title:
            return f"{language}|{version_title}"
        return language

    def _get_text_ref(
        self,
        ref: str,
        *,
        lang: str = "en",
        version_title: str | None = None,
        version: str | None = None,
        fill_missing_segments: bool = False,
        return_format: str = "text_only",
        source: bool = False,
    ) -> TextResult:
        params: dict[str, Any] = {
            "version": self._version_param(
                lang=lang,
                version_title=version_title,
                version=version,
                source=source,
            ),
            "fill_in_missing_segments": int(fill_missing_segments),
            "return_format": return_format,
        }

        data = self._get(f"/api/v3/texts/{quote(ref, safe='')}", params=params)
        if not isinstance(data, dict):
            raise SefariaError("Unexpected response for text lookup")

        versions = [
            TextVersion(
                language=item.get("language"),
                version_title=item.get("versionTitle"),
                text=item.get("text", []),
                raw=item,
            )
            for item in data.get("versions", []) or []
        ]
        return TextResult(ref=data.get("ref", ref), versions=versions, raw=data)

    def get_hebrew(self, ref: str, *, version_title: str | None = None) -> TextResult:
        if version_title:
            return self.get_text(ref, lang="he", version_title=version_title)
        if looks_like_book_ref(ref):
            return self.get_book(ref, version="source")
        return self._get_text_ref(ref, lang="he", source=True)

    def get_book(
        self,
        title: str,
        *,
        lang: str = "en",
        version_title: str | None = None,
        version: str | None = None,
        fill_missing_segments: bool = False,
        return_format: str = "text_only",
    ) -> TextResult:
        index = self.index(title)
        chapter_count = self._chapter_count(index)
        if chapter_count is None:
            raise SefariaError(f"Could not determine chapter count for {title!r}")

        chapters = [
            self._get_text_ref(
                f"{title} {chapter}",
                lang=lang,
                version_title=version_title,
                version=version,
                fill_missing_segments=fill_missing_segments,
                return_format=return_format,
                source=version == "source",
            )
            for chapter in range(1, chapter_count + 1)
        ]
        return self._combine_chapters(title, chapters)

    def _chapter_count(self, index: dict[str, Any]) -> int | None:
        lengths = index.get("lengths") or index.get("schema", {}).get("lengths")
        if isinstance(lengths, list) and lengths and isinstance(lengths[0], int):
            return lengths[0]
        alts = index.get("alts", {})
        chapters = alts.get("Chapters", {}) if isinstance(alts, dict) else {}
        nodes = chapters.get("nodes", []) if isinstance(chapters, dict) else []
        if nodes:
            return len(nodes)
        return None

    def _combine_chapters(self, title: str, chapters: list[TextResult]) -> TextResult:
        if not chapters:
            raise SefariaError(f"No chapters returned for {title!r}")
        first = chapters[0].first
        text = [chapter.first.text for chapter in chapters]
        raw = {
            "ref": title,
            "isClientAssembledBook": True,
            "chapters": [chapter.raw for chapter in chapters],
        }
        return TextResult(
            ref=title,
            versions=[
                TextVersion(
                    language=first.language,
                    version_title=first.version_title,
                    text=text,
                    raw=first.raw,
                )
            ],
            raw=raw,
        )

    def versions(self, index: str) -> VersionsResult:
        data = self._get(f"/api/texts/versions/{quote(index, safe='')}")
        if not isinstance(data, dict):
            raise SefariaError("Unexpected response for versions lookup")

        versions = [
            Version(
                language=v.get("language"),
                version_title=v.get("versionTitle"),
                version_source=v.get("versionSource"),
                status=v.get("status"),
                priority=v.get("priority"),
                raw=v,
            )
            for v in data.get("versions", []) or []
        ]
        return VersionsResult(index=index, versions=versions, raw=data)

    def index(self, title: str) -> dict[str, Any]:
        data = self._get(f"/api/v2/raw/index/{quote(title, safe='')}")
        if not isinstance(data, dict):
            raise SefariaError("Unexpected response for index lookup")
        return data

    def toc(self) -> list[Any]:
        data = self._get("/api/index")
        if not isinstance(data, list):
            raise SefariaError("Unexpected response for table of contents")
        return data

    def related(self, ref: str) -> dict[str, Any]:
        data = self._get(f"/api/related/{quote(ref, safe='')}")
        if not isinstance(data, dict):
            raise SefariaError("Unexpected response for related lookup")
        return data
