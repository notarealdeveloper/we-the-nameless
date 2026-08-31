"""Quantified source attribution from the complete lexical long tail.

The default model is a smoothed multinomial Naive Bayes classifier trained only
on Torah source assignments. It combines every whitespace token with a modest
character n-gram backoff for unseen forms. Reported posteriors are probabilities
*inside this model*, not direct historical probabilities.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .corpus import Corpus, TORAH
from .frequency import SourceFrequencies, frequencies_by_source, words
from .model import Verse
from .normalize import MatresMode
from .sources import DEFAULT_MODEL_SOURCES, DEFAULT_SOURCE_MAP, SourceMap, source_sort_key


def _ngrams(token: str, low: int, high: int) -> tuple[str, ...]:
    bounded = f"^{token}$"
    values: list[str] = []
    for n in range(low, high + 1):
        if len(bounded) >= n:
            values.extend(bounded[i : i + n] for i in range(len(bounded) - n + 1))
    return tuple(values)


def _logsumexp(values: Sequence[float]) -> float:
    if not values:
        return -math.inf
    peak = max(values)
    return peak + math.log(sum(math.exp(value - peak) for value in values))


@dataclass(frozen=True)
class TokenEvidence:
    token: str
    original: str
    known: bool
    source_log_evidence_bits: Mapping[str, float]
    contribution_vs_mean_bits: Mapping[str, float]
    strongest_source: str
    margin_bits: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "original": self.original,
            "known": self.known,
            "source_log_evidence_bits": dict(self.source_log_evidence_bits),
            "contribution_vs_mean_bits": dict(self.contribution_vs_mean_bits),
            "strongest_source": self.strongest_source,
            "margin_bits": self.margin_bits,
        }


@dataclass(frozen=True)
class AttributionResult:
    text: str
    language: str
    winner: str
    runner_up: str | None
    posterior: Mapping[str, float]
    log_evidence_bits: Mapping[str, float]
    posterior_surprisal_bits: Mapping[str, float]
    log2_bayes_factor: float
    token_evidence: tuple[TokenEvidence, ...]
    known_tokens: int
    total_tokens: int
    training_scope: str
    model_fingerprint: str
    caveat: str = (
        "Posterior probabilities are model-relative lexical evidence, not direct historical probabilities."
    )

    @property
    def coverage(self) -> float:
        return self.known_tokens / self.total_tokens if self.total_tokens else 0.0

    def evidence_for(self, source: str) -> float:
        """Log2 Bayes factor for ``source`` versus the strongest alternative."""
        if source not in self.log_evidence_bits:
            raise KeyError(source)
        alternatives = [value for key, value in self.log_evidence_bits.items() if key != source]
        return self.log_evidence_bits[source] - max(alternatives) if alternatives else math.inf

    def strongest_tokens(self, source: str | None = None, limit: int = 10) -> tuple[TokenEvidence, ...]:
        label = self.winner if source is None else source
        ranked = sorted(
            self.token_evidence,
            key=lambda item: item.contribution_vs_mean_bits.get(label, -math.inf),
            reverse=True,
        )
        return tuple(ranked[:limit])

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "language": self.language,
            "winner": self.winner,
            "runner_up": self.runner_up,
            "posterior": dict(self.posterior),
            "log_evidence_bits": dict(self.log_evidence_bits),
            "posterior_surprisal_bits": dict(self.posterior_surprisal_bits),
            "log2_bayes_factor": self.log2_bayes_factor,
            "known_tokens": self.known_tokens,
            "total_tokens": self.total_tokens,
            "coverage": self.coverage,
            "training_scope": self.training_scope,
            "model_fingerprint": self.model_fingerprint,
            "token_evidence": [value.to_dict() for value in self.token_evidence],
            "caveat": self.caveat,
        }

    def plot(self, **kwargs: Any) -> Any:
        from .plotting import plot_attribution

        return plot_attribution(self, **kwargs)

    def __repr__(self) -> str:
        posterior = self.posterior[self.winner]
        return (
            f"<AttributionResult {self.winner} p={posterior:.3f}, "
            f"BF={self.log2_bayes_factor:.2f} bits, coverage={self.coverage:.1%}>"
        )


@dataclass(frozen=True)
class EvaluationResult:
    total: int
    correct: int
    accuracy: float
    confusion: Mapping[str, Mapping[str, int]]
    skipped: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SourceAttributor:
    """Hybrid word/character source model with transparent evidence accounting."""

    FORMAT_VERSION = 1

    def __init__(
        self,
        *,
        language: str,
        source_frequencies: SourceFrequencies,
        sources: Sequence[str],
        char_counts: Mapping[str, Mapping[str, float]],
        char_totals: Mapping[str, float],
        ngram_range: tuple[int, int] = (2, 5),
        alpha_word: float = 0.25,
        alpha_char: float = 0.1,
        char_weight: float = 0.20,
        oov_char_weight: float = 1.0,
        prior: str = "uniform",
        temperature: float = 1.0,
        training_scope: str = "Torah",
        normalization: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.language = language
        self.source_frequencies = source_frequencies
        self.sources = tuple(sources)
        self.char_counts = {source: Counter(values) for source, values in char_counts.items()}
        self.char_totals = {source: float(value) for source, value in char_totals.items()}
        self.ngram_range = tuple(ngram_range)
        self.alpha_word = float(alpha_word)
        self.alpha_char = float(alpha_char)
        self.char_weight = float(char_weight)
        self.oov_char_weight = float(oov_char_weight)
        self.prior = prior
        self.temperature = float(temperature)
        self.training_scope = training_scope
        self.normalization = dict(normalization or {})
        self.metadata = dict(metadata or {})
        self.vocabulary = set(source_frequencies.vocabulary)
        self.char_vocabulary = {
            ngram for values in self.char_counts.values() for ngram in values
        }
        self._fingerprint = self._make_fingerprint()

    @classmethod
    def train(
        cls,
        corpus: Corpus | Iterable[Verse] | None = None,
        *,
        scope: str = "torah",
        language: str = "hebrew",
        sources: Sequence[str] = DEFAULT_MODEL_SOURCES,
        source_map: SourceMap = DEFAULT_SOURCE_MAP,
        ngram_range: tuple[int, int] = (2, 5),
        alpha_word: float = 0.25,
        alpha_char: float = 0.1,
        char_weight: float = 0.20,
        oov_char_weight: float = 1.0,
        prior: str = "uniform",
        temperature: float = 1.0,
        niqqud: bool | None = False,
        matres: MatresMode | str | bool | None = MatresMode.KEEP,
        attribution: str = "fractional",
    ) -> "SourceAttributor":
        if corpus is None:
            corpus = Corpus.from_tex()
        if isinstance(corpus, Corpus):
            scope_key = scope.casefold().replace("_", "-")
            if scope_key in {"torah", "pentateuch", "default"}:
                verses = corpus.select(books=[book for book in TORAH if book in corpus.book_names])
                training_scope = "Torah"
            elif scope_key in {"primary-history", "primary history", "all"}:
                verses = corpus.primary_history() if scope_key != "all" else corpus.verses
                training_scope = "Primary History" if scope_key != "all" else "All available books"
            else:
                names = [part.strip() for part in scope.split(",") if part.strip()]
                verses = corpus.select(books=names)
                training_scope = ", ".join(names)
            corpus_fingerprint = corpus.fingerprint
        else:
            verses = list(corpus)
            training_scope = scope if scope else "custom iterable"
            corpus_fingerprint = None
        frequencies = frequencies_by_source(
            verses,
            language=language,
            sources=sources,
            canonical_sources=True,
            source_map=source_map,
            niqqud=niqqud,
            matres=matres,
            attribution=attribution,
        )
        # Retain requested classes even when a tiny fixture has zero examples.
        for source in sources:
            if source not in frequencies:
                from .frequency import Frequency

                frequencies[source] = Frequency(language=language, metadata={"source": source})
        low, high = ngram_range
        char_counts: dict[str, Counter[str]] = {source: Counter() for source in sources}
        char_totals: dict[str, float] = {source: 0.0 for source in sources}
        for source in sources:
            for token, count in frequencies[source].items():
                grams = _ngrams(str(token), low, high)
                for gram in grams:
                    char_counts[source][gram] += float(count)
                    char_totals[source] += float(count)
        return cls(
            language=language,
            source_frequencies=frequencies,
            sources=sources,
            char_counts=char_counts,
            char_totals=char_totals,
            ngram_range=ngram_range,
            alpha_word=alpha_word,
            alpha_char=alpha_char,
            char_weight=char_weight,
            oov_char_weight=oov_char_weight,
            prior=prior,
            temperature=temperature,
            training_scope=training_scope,
            normalization={
                "niqqud": niqqud,
                "matres": MatresMode.coerce(matres).value,
                "word_boundary": "unicode-whitespace-only",
            },
            metadata={
                "corpus_fingerprint": corpus_fingerprint,
                "attribution": attribution,
                "source_map": "default-canonical",
            },
        )

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    def _make_fingerprint(self) -> str:
        digest = hashlib.sha256()
        digest.update(self.language.encode())
        digest.update(repr(self.sources).encode())
        digest.update(repr(self.ngram_range).encode())
        digest.update(repr((self.alpha_word, self.alpha_char, self.char_weight)).encode())
        for source in self.sources:
            digest.update(source.encode())
            for token, count in sorted(self.source_frequencies[source].items()):
                digest.update(str(token).encode("utf-8"))
                digest.update(repr(float(count)).encode())
        return digest.hexdigest()

    def _log_prior(self, source: str) -> float:
        if self.prior == "uniform":
            return -math.log(len(self.sources))
        if self.prior == "empirical":
            total = sum(self.source_frequencies[label].total_tokens for label in self.sources)
            value = self.source_frequencies[source].total_tokens
            return math.log((value + 1.0) / (total + len(self.sources)))
        raise ValueError("prior must be 'uniform' or 'empirical'")

    def _word_log_probability(self, token: str, source: str) -> float:
        counter = self.source_frequencies[source]
        vocabulary = len(self.vocabulary) + 1  # explicit OOV bucket
        return math.log(
            (float(counter[token]) + self.alpha_word)
            / (counter.total_tokens + self.alpha_word * vocabulary)
        )

    def _char_log_probability(self, token: str, source: str) -> float:
        grams = _ngrams(token, *self.ngram_range)
        if not grams:
            return 0.0
        vocabulary = len(self.char_vocabulary) + 1
        denominator = self.char_totals.get(source, 0.0) + self.alpha_char * vocabulary
        counter = self.char_counts.get(source, Counter())
        # Average rather than sum, preventing a long unknown word from supplying
        # unlimited pseudo-independent evidence solely because it has more grams.
        return sum(
            math.log((float(counter[gram]) + self.alpha_char) / denominator) for gram in grams
        ) / len(grams)

    def _token_scores(self, token: str) -> dict[str, float]:
        known = token in self.vocabulary
        if known:
            return {
                source: self._word_log_probability(token, source)
                + self.char_weight * self._char_log_probability(token, source)
                for source in self.sources
            }
        # The symmetric lexical OOV bucket would mechanically favor a smaller
        # source corpus. It is constant evidence about the spelling's absence,
        # so omit it and let character morphology carry bounded OOV evidence.
        return {
            source: self.oov_char_weight * self._char_log_probability(token, source)
            for source in self.sources
        }

    def attribute(
        self,
        text: str | Verse,
        *,
        temperature: float | None = None,
    ) -> AttributionResult:
        if isinstance(text, Verse):
            raw_text = text.text(self.language)
        else:
            raw_text = text
        token_values = list(
            words(
                raw_text,
                language=self.language,
                niqqud=self.normalization.get("niqqud"),
                matres=self.normalization.get("matres", "keep"),
            )
        )
        if not token_values:
            raise ValueError("Cannot attribute an empty or normalization-empty string")
        scores = {source: self._log_prior(source) for source in self.sources}
        token_evidence: list[TokenEvidence] = []
        known_tokens = 0
        for word, _, _ in token_values:
            token = str(word)
            known = token in self.vocabulary
            known_tokens += int(known)
            token_scores = self._token_scores(token)
            for source, value in token_scores.items():
                scores[source] += value
            bits = {source: value / math.log(2) for source, value in token_scores.items()}
            mean = sum(bits.values()) / len(bits)
            relative = {source: value - mean for source, value in bits.items()}
            ordered = sorted(bits.items(), key=lambda item: item[1], reverse=True)
            token_evidence.append(
                TokenEvidence(
                    token=token,
                    original=word.original,
                    known=known,
                    source_log_evidence_bits=bits,
                    contribution_vs_mean_bits=relative,
                    strongest_source=ordered[0][0],
                    margin_bits=ordered[0][1] - ordered[1][1] if len(ordered) > 1 else math.inf,
                )
            )
        temp = self.temperature if temperature is None else float(temperature)
        if temp <= 0:
            raise ValueError("temperature must be positive")
        scaled = {source: value / temp for source, value in scores.items()}
        normalizer = _logsumexp(list(scaled.values()))
        posterior = {source: math.exp(value - normalizer) for source, value in scaled.items()}
        ranked = sorted(posterior.items(), key=lambda item: item[1], reverse=True)
        winner = ranked[0][0]
        runner_up = ranked[1][0] if len(ranked) > 1 else None
        score_bits = {source: value / math.log(2) for source, value in scores.items()}
        bayes = (
            score_bits[winner] - score_bits[runner_up] if runner_up is not None else math.inf
        )
        return AttributionResult(
            text=raw_text,
            language=self.language,
            winner=winner,
            runner_up=runner_up,
            posterior=posterior,
            log_evidence_bits=score_bits,
            posterior_surprisal_bits={
                source: -math.log2(max(value, 1e-300)) for source, value in posterior.items()
            },
            log2_bayes_factor=bayes,
            token_evidence=tuple(token_evidence),
            known_tokens=known_tokens,
            total_tokens=len(token_values),
            training_scope=self.training_scope,
            model_fingerprint=self.fingerprint,
        )

    predict = attribute

    def evaluate(self, verses: Iterable[Verse], *, minimum_purity: float = 0.8) -> EvaluationResult:
        confusion: dict[str, Counter[str]] = {source: Counter() for source in self.sources}
        total = correct = skipped = 0
        for verse in verses:
            weights = verse.source_weights(self.language, canonical=True)
            eligible = {source: value for source, value in weights.items() if source in self.sources}
            if not eligible:
                skipped += 1
                continue
            gold, purity = max(eligible.items(), key=lambda item: item[1])
            if purity < minimum_purity or not verse.text(self.language).strip():
                skipped += 1
                continue
            prediction = self.attribute(verse).winner
            confusion[gold][prediction] += 1
            total += 1
            correct += int(prediction == gold)
        return EvaluationResult(
            total,
            correct,
            correct / total if total else 0.0,
            {source: dict(values) for source, values in confusion.items()},
            skipped,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_version": self.FORMAT_VERSION,
            "language": self.language,
            "sources": list(self.sources),
            "source_frequencies": self.source_frequencies.to_dict(),
            "char_counts": {
                source: dict(sorted(values.items())) for source, values in self.char_counts.items()
            },
            "char_totals": self.char_totals,
            "ngram_range": list(self.ngram_range),
            "alpha_word": self.alpha_word,
            "alpha_char": self.alpha_char,
            "char_weight": self.char_weight,
            "oov_char_weight": self.oov_char_weight,
            "prior": self.prior,
            "temperature": self.temperature,
            "training_scope": self.training_scope,
            "normalization": self.normalization,
            "metadata": self.metadata,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceAttributor":
        if int(value.get("format_version", 0)) != cls.FORMAT_VERSION:
            raise ValueError("Unsupported attribution model format")
        return cls(
            language=str(value["language"]),
            source_frequencies=SourceFrequencies.from_dict(value["source_frequencies"]),
            sources=tuple(value["sources"]),
            char_counts=value["char_counts"],
            char_totals=value["char_totals"],
            ngram_range=tuple(value.get("ngram_range", (2, 5))),
            alpha_word=float(value.get("alpha_word", 0.25)),
            alpha_char=float(value.get("alpha_char", 0.1)),
            char_weight=float(value.get("char_weight", 0.2)),
            oov_char_weight=float(value.get("oov_char_weight", 1.0)),
            prior=str(value.get("prior", "uniform")),
            temperature=float(value.get("temperature", 1.0)),
            training_scope=str(value.get("training_scope", "unknown")),
            normalization=value.get("normalization", {}),
            metadata=value.get("metadata", {}),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        opener: Any = gzip.open if target.suffix == ".gz" else open
        with opener(target, "wt", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, ensure_ascii=False, separators=(",", ":"))
        return target

    @classmethod
    def load(cls, path: str | Path) -> "SourceAttributor":
        target = Path(path)
        opener: Any = gzip.open if target.suffix == ".gz" else open
        with opener(target, "rt", encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def __repr__(self) -> str:
        return (
            f"<SourceAttributor {self.language}, {self.training_scope}, "
            f"sources={','.join(self.sources)}, vocabulary={len(self.vocabulary)}>"
        )
