from bible import plot


def _bar_heights(ax):
    return [patch.get_height() for patch in ax.patches]


def test_chapters_plots_one_bar_per_chapter_not_remaining_books():
    fig, ax = plot.chapters("exodus", show=False)

    try:
        heights = _bar_heights(ax)
        assert len(heights) == 40
        assert heights[:3] == [22, 25, 22]
    finally:
        fig.clear()


def test_chapters_can_plot_english_word_totals_by_chapter():
    fig, ax = plot.chapters("exodus", measure="words", show=False)

    try:
        heights = _bar_heights(ax)
        assert len(heights) == 40
        assert heights[0] > 0
        assert ax.get_ylabel() == "English Words per chapter"
    finally:
        fig.clear()


def test_chapter_can_plot_hebrew_chars_by_verse_without_niqqud():
    fig, ax = plot.chapter("exodus 1", measure="chars", language="heb", show=False)

    try:
        heights = _bar_heights(ax)
        assert len(heights) == 22
        assert heights[0] == 45
        assert ax.get_ylabel() == "Hebrew Characters, niqqud stripped per verse"
    finally:
        fig.clear()
