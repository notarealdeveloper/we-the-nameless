#!/usr/bin/env python3
"""Plot the most frequent marked-English words in Exodus 28--40 by source."""

from __future__ import annotations

import argparse
from collections import Counter
import math
from pathlib import Path
import re

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "exodus-28-40-p-niqqud-counts.md"
OUTPUT = ROOT / "img" / "plots" / "exodus-28-40-word-counts"

CHAPTERS = {
    28: ("P",),
    29: ("P",),
    30: ("P",),
    31: ("P",),
    32: ("E",),
    33: ("E",),
    34: ("J", "P"),
    35: ("P",),
    36: ("P",),
    37: ("P",),
    38: ("P",),
    39: ("P",),
    40: ("P",),
}

SUMMARIES = {
    28: "Priest clothes",
    29: "Priests installed",
    30: "Incense; census; oil",
    31: "Bezalel; Sabbath",
    32: "Golden calf",
    33: "Tent; God's back",
    34: "New tablets",
    35: "Work begins",
    36: "Tabernacle built",
    37: "Ark; furniture made",
    38: "Altar; courtyard; inventory",
    39: "Priest clothes done",
    40: "Tabernacle complete",
}

COLORS = [
    "#C79A2B",  # gold
    "#285F8F",  # blue
    "#B33A3A",  # scarlet
    "#68458C",  # purple
    "#E0B94B",
    "#4E83AD",
    "#D35B4F",
    "#8A68A6",
    "#9B7419",
    "#173E63",
]


def top_words(limit: int = 10) -> list[str]:
    """Read the Markdown table and rank words by its Exodus 28--40 column."""
    rows: list[tuple[str, int]] = []
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 16 or not cells[14].isdigit():
            continue
        rows.append((cells[0], int(cells[14])))
    return [word for word, _count in sorted(rows, key=lambda row: row[1], reverse=True)[:limit]]


def macro_contents(text: str, macro: str) -> list[str]:
    """Return balanced-brace contents for exact ``\\eX`` macros."""
    marker = f"\\e{macro}{{"
    contents: list[str] = []
    start = 0
    while (position := text.find(marker, start)) >= 0:
        content_start = position + len(marker)
        depth = 1
        cursor = content_start
        while cursor < len(text) and depth:
            if text[cursor] == "{" and (cursor == 0 or text[cursor - 1] != "\\"):
                depth += 1
            elif text[cursor] == "}" and (cursor == 0 or text[cursor - 1] != "\\"):
                depth -= 1
            cursor += 1
        if depth:
            raise ValueError(f"Unbalanced {marker} in source")
        contents.append(text[content_start : cursor - 1])
        start = cursor
    return contents


def word_count(text: str, word: str) -> int:
    suffix = r"(?:['\u2019]s)?" if word == "Aaron" else ""
    return len(re.findall(rf"(?<![A-Za-z]){re.escape(word)}{suffix}(?![A-Za-z])", text))


def counts_for(chapter: int, source: str, words: list[str]) -> list[int]:
    chapter_text = (ROOT / "02-exodus" / f"{chapter:02}.tex").read_text(encoding="utf-8")
    source_text = "\n".join(macro_contents(chapter_text, source))
    return [word_count(source_text, word) for word in words]


def source_percentages(chapters: list[int]) -> dict[str, float]:
    """Return verse-weighted J/E/P percentages, splitting mixed verses equally."""
    shares = Counter({source: 0.0 for source in "JEP"})
    verse_count = 0
    for chapter in chapters:
        chapter_text = (ROOT / "02-exodus" / f"{chapter:02}.tex").read_text(encoding="utf-8")
        verses = re.split(r"(?=\\Verse\{\d+\})", chapter_text)[1:]
        for verse in verses:
            tags = re.findall(r"\\e([A-Z]+)\{", verse)
            sources = {source for source in "JEP" if any(source in tag for tag in tags)}
            if not sources:
                continue
            verse_count += 1
            for source in sources:
                shares[source] += 1 / len(sources)
    return {source: 100 * shares[source] / verse_count for source in "JEP"}


def percentage_label(percentages: dict[str, float]) -> str:
    return "  ".join(f"{source}: {percentages[source]:.1f}%" for source in "JEP")


def style_count_axis(ax: plt.Axes, ymax: int | None = None) -> None:
    if ymax is not None:
        ax.set_ylim(0, ymax)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    labels = [label.get_text() for label in ax.get_xticklabels()]
    ax.set_xticks(
        ax.get_xticks(),
        ["Tent of\nMeeting" if label == "Tent of Meeting" else label for label in labels],
    )
    for label in ax.get_xticklabels():
        if label.get_text() == "Tent of\nMeeting":
            label.set(rotation=0, ha="center")
        else:
            label.set(rotation=35, ha="right", rotation_mode="anchor")


def set_theme() -> None:
    sns.set_theme(
        context="talk",
        style="whitegrid",
        rc={
            "axes.facecolor": "#FBF8F0",
            "figure.facecolor": "#FBF8F0",
            "grid.color": "#DDD4C2",
            "axes.edgecolor": "#5C554B",
            "text.color": "#29251F",
        },
    )


def chapter_plot(chapter: int, source: str, words: list[str], counts: list[int]) -> None:
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(x=words, y=counts, hue=words, palette=COLORS, legend=False, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Appearances")
    ax.set_title(SUMMARIES[chapter], fontsize=17, pad=10)
    style_count_axis(ax, ymax=20)
    ax.legend(
        handles=[Patch(facecolor=color, label=word) for word, color in zip(words, COLORS)],
        title="Words",
        ncol=1,
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        frameon=True,
    )
    composition = percentage_label(source_percentages([chapter]))
    ax.text(0.01, 0.98, f"Source: {source}", transform=ax.transAxes, va="top", fontsize=12)
    ax.text(0.99, 0.98, composition, transform=ax.transAxes, va="top", ha="right", fontsize=12)
    fig.suptitle(f"Exodus {chapter}", fontsize=23, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUTPUT / f"exodus-{chapter:02}-{source.lower()}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def total_plot(words: list[str], all_counts: dict[tuple[int, str], list[int]]) -> None:
    totals = [sum(counts[index] for counts in all_counts.values()) for index in range(len(words))]
    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(x=words, y=totals, hue=words, palette=COLORS, legend=False, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("Appearances")
    ax.set_title("Selected-source totals across chapters 28--40", fontsize=17, pad=10)
    style_count_axis(ax)
    ax.legend(
        handles=[Patch(facecolor=color, label=word) for word, color in zip(words, COLORS)],
        title="Words",
        ncol=1,
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        frameon=True,
    )
    fig.suptitle("Exodus 28--40", fontsize=23, y=0.99)
    ax.text(0.99, 0.98, percentage_label(source_percentages(list(CHAPTERS))), transform=ax.transAxes, va="top", ha="right", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUTPUT / "exodus-28-40-total.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def source_total_plots(words: list[str]) -> None:
    totals = {
        source: [
            sum(counts_for(chapter, source, words)[index] for chapter in CHAPTERS)
            for index in range(len(words))
        ]
        for source in "JEP"
    }
    ymax = math.ceil(max(totals["P"]) / 10) * 10
    composition = percentage_label(source_percentages(list(CHAPTERS)))
    for source in "JEP":
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.barplot(x=words, y=totals[source], hue=words, palette=COLORS, legend=False, ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Appearances")
        ax.set_title(f"All selected terms in source {source}", fontsize=17, pad=10)
        style_count_axis(ax, ymax=ymax)
        ax.legend(
            handles=[Patch(facecolor=color, label=word) for word, color in zip(words, COLORS)],
            title="Words",
            ncol=1,
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
            frameon=True,
        )
        ax.text(0.99, 0.98, composition, transform=ax.transAxes, va="top", ha="right", fontsize=12)
        fig.suptitle("Exodus 28--40", fontsize=23, y=0.99)
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(OUTPUT / f"exodus-28-40-{source.lower()}-total.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, choices=range(5, 11))
    args = parser.parse_args()

    set_theme()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    words = top_words(args.limit)
    all_counts: dict[tuple[int, str], list[int]] = {}
    for chapter, sources in CHAPTERS.items():
        for source in sources:
            counts = counts_for(chapter, source, words)
            all_counts[(chapter, source)] = counts
            chapter_plot(chapter, source, words, counts)
    total_plot(words, all_counts)
    source_total_plots(words)
    print(f"Plotted {', '.join(words)}")
    print(f"Wrote {len(all_counts) + 4} graphs to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
