"""Source profiles and corpus-wide lexical distinctiveness metrics."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from .frequency import SourceFrequencies, frequencies_by_source, normalize_token
from .model import Verse
from .normalize import MatresMode, find_english, find_hebrew
from .sources import DEFAULT_SOURCE_MAP, SourceMap, source_sort_key


@dataclass(frozen=True)
class SourceWordEvidence:
    source: str
    count: float
    source_tokens: float
    rate_per_million: float
    conditional_probability: float
    source_given_word: float
    surprisal_bits: float
    enrichment_log2: float
    log_odds_z: float
    pmi_bits: float
    information_bits: float


@dataclass(frozen=True)
class SourceProfile:
    query: str
    normalized_query: str
    language: str
    total_occurrences: float
    total_tokens: float
    evidence: tuple[SourceWordEvidence, ...]
    metadata: Mapping[str, Any]

    def __getitem__(self, source: str) -> SourceWordEvidence:
        for value in self.evidence:
            if value.source == source:
                return value
        raise KeyError(source)

    @property
    def counts(self) -> dict[str, float]:
        return {value.source: value.count for value in self.evidence}

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "normalized_query": self.normalized_query,
            "language": self.language,
            "total_occurrences": self.total_occurrences,
            "total_tokens": self.total_tokens,
            "evidence": [asdict(value) for value in self.evidence],
            "metadata": dict(self.metadata),
        }

    def plot(self, **kwargs: Any) -> Any:
        from .plotting import plot_source_profile

        return plot_source_profile(self, **kwargs)


@dataclass(frozen=True)
class DistinctiveWord:
    word: str
    source: str
    count: float
    rate_per_million: float
    log_odds_z: float
    enrichment_log2: float
    information_bits: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _profile_values(
    frequencies: SourceFrequencies,
    word: str,
    *,
    prior_strength: float = 20.0,
) -> SourceProfile:
    counts = {source: float(counter[word]) for source, counter in frequencies.items()}
    totals = {source: counter.total_tokens for source, counter in frequencies.items()}
    grand_count = sum(counts.values())
    grand_tokens = sum(totals.values())
    pooled_rate = (grand_count / grand_tokens) if grand_tokens else 0.0
    # Informative beta prior for word-vs-all-other-tokens.
    alpha_word = max(prior_strength * pooled_rate, 1e-9)
    alpha_rest = max(prior_strength * (1.0 - pooled_rate), 1e-9)
    values: list[SourceWordEvidence] = []
    for source in sorted(frequencies, key=source_sort_key):
        count = counts[source]
        total = totals[source]
        other_count = grand_count - count
        other_total = grand_tokens - total
        conditional = (count + alpha_word) / (total + prior_strength) if total else 0.0
        other_conditional = (
            (other_count + alpha_word) / (other_total + prior_strength) if other_total else conditional
        )
        source_given = count / grand_count if grand_count else 0.0
        source_prior = total / grand_tokens if grand_tokens else 0.0
        enrichment = math.log2(conditional / other_conditional) if conditional and other_conditional else 0.0
        odds_source = (count + alpha_word) / max(total - count + alpha_rest, 1e-12)
        odds_other = (other_count + alpha_word) / max(
            other_total - other_count + alpha_rest, 1e-12
        )
        delta = math.log(odds_source) - math.log(odds_other)
        variance = 1.0 / (count + alpha_word) + 1.0 / (other_count + alpha_word)
        z = delta / math.sqrt(variance) if variance > 0 else 0.0
        pmi = math.log2(source_given / source_prior) if source_given and source_prior else 0.0
        values.append(
            SourceWordEvidence(
                source=source,
                count=count,
                source_tokens=total,
                rate_per_million=(count / total * 1_000_000) if total else 0.0,
                conditional_probability=conditional,
                source_given_word=source_given,
                surprisal_bits=-math.log2(conditional) if conditional else math.inf,
                enrichment_log2=enrichment,
                log_odds_z=z,
                pmi_bits=pmi,
                information_bits=count * enrichment,
            )
        )
    return SourceProfile(
        query=word,
        normalized_query=word,
        language=frequencies.language,
        total_occurrences=grand_count,
        total_tokens=grand_tokens,
        evidence=tuple(values),
        metadata={**frequencies.metadata, "prior_strength": prior_strength},
    )


def profile_from_frequencies(
    frequencies: SourceFrequencies,
    word: str,
    *,
    prior_strength: float = 20.0,
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
) -> SourceProfile:
    normalized = normalize_token(
        word,
        language=frequencies.language,
        case_sensitive=case_sensitive,
        niqqud=niqqud,
        matres=matres,
    )
    profile = _profile_values(frequencies, normalized, prior_strength=prior_strength)
    return SourceProfile(
        query=word,
        normalized_query=normalized,
        language=profile.language,
        total_occurrences=profile.total_occurrences,
        total_tokens=profile.total_tokens,
        evidence=profile.evidence,
        metadata=profile.metadata,
    )


def _query_counts(
    verses: Iterable[Verse],
    query: str,
    *,
    language: str,
    regex: bool,
    case_sensitive: bool,
    niqqud: bool | None,
    spaces: bool,
    matres: MatresMode | str | bool | None,
    source_map: SourceMap,
    canonical_sources: bool,
) -> dict[str, float]:
    counts: dict[str, float] = {}
    for verse in verses:
        matches = (
            find_hebrew(
                verse.hebrew,
                query,
                regex=regex,
                niqqud=niqqud,
                spaces=spaces,
                matres=matres,
            )
            if language.lower().startswith(("h", "heb"))
            else find_english(
                verse.english,
                query,
                regex=regex,
                case_sensitive=case_sensitive,
                whole_word="auto",
            )
        )
        for match in matches:
            weights = verse.source_weights(
                language,
                match.start,
                match.end,
                canonical=canonical_sources,
                source_map=source_map,
            )
            for source, weight in weights.items():
                counts[source] = counts.get(source, 0.0) + weight
    return counts


def source_profile(
    verses: Iterable[Verse],
    query: str,
    *,
    language: str = "english",
    regex: bool = False,
    case_sensitive: bool = False,
    niqqud: bool | None = None,
    spaces: bool = False,
    matres: MatresMode | str | bool | None = MatresMode.KEEP,
    sources: Iterable[str] | None = None,
    canonical_sources: bool = True,
    source_map: SourceMap = DEFAULT_SOURCE_MAP,
    prior_strength: float = 20.0,
) -> SourceProfile:
    values = list(verses)
    frequencies = frequencies_by_source(
        values,
        language=language,
        sources=sources,
        canonical_sources=canonical_sources,
        source_map=source_map,
        case_sensitive=case_sensitive,
        niqqud=niqqud,
        matres=matres,
        attribution="fractional",
    )
    # A single whitespace token can use the counters directly. Phrases, regexes,
    # and cross-boundary Hebrew require occurrence matching against the stream.
    is_phrase = regex or (" " in query) or (language.lower().startswith(("h", "heb")) and not spaces)
    if not is_phrase:
        return profile_from_frequencies(
            frequencies,
            query,
            prior_strength=prior_strength,
            case_sensitive=case_sensitive,
            niqqud=niqqud,
            matres=matres,
        )
    counts = _query_counts(
        values,
        query,
        language=language,
        regex=regex,
        case_sensitive=case_sensitive,
        niqqud=niqqud,
        spaces=spaces,
        matres=matres,
        source_map=source_map,
        canonical_sources=canonical_sources,
    )
    pseudo = SourceFrequencies(language=language, metadata=frequencies.metadata)
    marker = "__QUERY__"
    for source, counter in frequencies.items():
        from .frequency import Frequency

        copy = Frequency(language=language, metadata=counter.metadata)
        copy[marker] = counts.get(source, 0.0)
        # Add a synthetic remainder so totals remain the source token totals.
        copy["__OTHER__"] = max(0.0, counter.total_tokens - copy[marker])
        pseudo[source] = copy
    result = _profile_values(pseudo, marker, prior_strength=prior_strength)
    return SourceProfile(
        query=query,
        normalized_query=query,
        language=language,
        total_occurrences=result.total_occurrences,
        total_tokens=result.total_tokens,
        evidence=result.evidence,
        metadata={**result.metadata, "regex": regex, "spaces": spaces},
    )


def characteristic_words(
    frequencies: SourceFrequencies,
    *,
    source: str | None = None,
    min_count: float = 2.0,
    limit: int | None = 100,
    prior_strength: float = 20.0,
    rank_by: str = "log_odds_z",
) -> list[DistinctiveWord]:
    """Rank the complete vocabulary, including its long tail, by source evidence."""
    results: list[DistinctiveWord] = []
    wanted = [source] if source is not None else list(frequencies)
    for word in frequencies.vocabulary:
        profile = _profile_values(frequencies, word, prior_strength=prior_strength)
        for label in wanted:
            try:
                evidence = profile[label]
            except KeyError:
                continue
            if evidence.count < min_count:
                continue
            results.append(
                DistinctiveWord(
                    word,
                    label,
                    evidence.count,
                    evidence.rate_per_million,
                    evidence.log_odds_z,
                    evidence.enrichment_log2,
                    evidence.information_bits,
                )
            )
    if rank_by not in DistinctiveWord.__dataclass_fields__:
        raise ValueError(f"Unknown rank field {rank_by!r}")
    results.sort(key=lambda value: getattr(value, rank_by), reverse=True)
    return results if limit is None else results[:limit]
