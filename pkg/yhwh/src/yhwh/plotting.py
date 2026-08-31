"""Optional matplotlib visualizations. Every function returns ``(figure, axes)``."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Sequence


def _plt() -> Any:
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:  # pragma: no cover - depends on optional extra
        raise ImportError("Plotting requires `pip install yhwh[plots]`") from error
    return plt


def _finish(fig: Any, *, save: str | Path | None = None, show: bool = False) -> None:
    fig.tight_layout()
    if save is not None:
        target = Path(save)
        target.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(target, bbox_inches="tight")
    if show:
        fig.show()


def plot_frequency(
    frequency: Any,
    *,
    top: int = 30,
    title: str | None = None,
    horizontal: bool = True,
    save: str | Path | None = None,
    show: bool = False,
) -> tuple[Any, Any]:
    plt = _plt()
    values = frequency.most_common(top)
    labels = [str(word) for word, _ in values][::-1] if horizontal else [str(w) for w, _ in values]
    counts = [float(count) for _, count in values][::-1] if horizontal else [float(c) for _, c in values]
    fig, ax = plt.subplots(figsize=(10, max(4, top * 0.24) if horizontal else 6))
    if horizontal:
        ax.barh(labels, counts)
        ax.set_xlabel("Count")
    else:
        ax.bar(labels, counts)
        ax.tick_params(axis="x", rotation=70)
        ax.set_ylabel("Count")
    ax.set_title(title or f"Most frequent {frequency.language} tokens")
    _finish(fig, save=save, show=show)
    return fig, ax


def plot_source_profile(
    profile: Any,
    *,
    metric: str = "rate_per_million",
    title: str | None = None,
    save: str | Path | None = None,
    show: bool = False,
) -> tuple[Any, Any]:
    plt = _plt()
    if not profile.evidence:
        raise ValueError("Profile has no source evidence")
    labels = [value.source for value in profile.evidence]
    values = [float(getattr(value, metric)) for value in profile.evidence]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title or f"{profile.query!r} by source")
    _finish(fig, save=save, show=show)
    return fig, ax


def plot_attribution(
    result: Any,
    *,
    title: str | None = None,
    save: str | Path | None = None,
    show: bool = False,
) -> tuple[Any, Any]:
    plt = _plt()
    ranked = sorted(result.posterior.items(), key=lambda item: item[1], reverse=True)
    labels = [item[0] for item in ranked]
    values = [item[1] for item in ranked]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Model posterior")
    ax.set_title(title or f"Source attribution: {result.winner}")
    _finish(fig, save=save, show=show)
    return fig, ax


def plot_characteristic_words(
    values: Sequence[Any],
    *,
    metric: str = "log_odds_z",
    top: int = 30,
    title: str | None = None,
    save: str | Path | None = None,
    show: bool = False,
) -> tuple[Any, Any]:
    plt = _plt()
    selected = list(values[:top])[::-1]
    labels = [f"{value.word} ({value.source})" for value in selected]
    numbers = [float(getattr(value, metric)) for value in selected]
    fig, ax = plt.subplots(figsize=(10, max(4, top * 0.27)))
    ax.barh(labels, numbers)
    ax.set_xlabel(metric.replace("_", " ").title())
    ax.set_title(title or "Characteristic words")
    _finish(fig, save=save, show=show)
    return fig, ax


def plot_source_heatmap(
    rows: Sequence[str],
    sources: Sequence[str],
    matrix: Sequence[Sequence[float]],
    *,
    title: str = "Source evidence",
    save: str | Path | None = None,
    show: bool = False,
) -> tuple[Any, Any]:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(max(6, len(sources) * 1.2), max(4, len(rows) * 0.35)))
    image = ax.imshow(matrix, aspect="auto")
    ax.set_xticks(range(len(sources)), labels=sources)
    ax.set_yticks(range(len(rows)), labels=rows)
    ax.set_title(title)
    fig.colorbar(image, ax=ax, label="Evidence")
    _finish(fig, save=save, show=show)
    return fig, ax
