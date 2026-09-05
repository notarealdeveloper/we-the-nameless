#!/usr/bin/env python3
"""Focused regression tests for WTN's semantic TeX conversion."""

from __future__ import annotations

import unittest
from pathlib import Path

import build


class ConversionTests(unittest.TestCase):
    def test_wrapped_image_inside_footnote_stays_inline_and_clean(self) -> None:
        source = (
            r"\footnote{Before \begin{wrapfigure}{r}{0.40\linewidth}"
            r"\image{img/brick.png}\end{wrapfigure} after.}"
        )
        rendered = build.tex_to_markdown(source)
        self.assertIn('class="embedded-note-image"', rendered)
        self.assertNotIn("{r}", rendered)
        self.assertNotIn(r"\linewidth", rendered)
        self.assertNotIn("<figure", rendered)

    def test_print_stacking_becomes_accessible_reflowable_text(self) -> None:
        rendered = build.tex_to_markdown(
            r"\Above{3pt}{wo}{\chineseB{我}} \Below{3pt}{men}{\chineseB{們}}"
        )
        self.assertEqual(rendered.count('<ruby class="wtn-ruby'), 2)
        self.assertIn("wo", rendered)
        self.assertIn("我", rendered)
        self.assertIn('class="wtn-ruby ruby-below"', rendered)
        self.assertNotIn("3pt", rendered)

    def test_ruby_command_uses_html5_ruby(self) -> None:
        rendered = build.tex_to_markdown(r"\ruby{字}{reading}")
        self.assertIn('<ruby class="wtn-ruby">字', rendered)
        self.assertIn("<rt>reading</rt>", rendered)

    def test_p_hebrew_keeps_niqqud(self) -> None:
        rendered = build.tex_to_markdown(r"\hP{בְּרֵאשִׁית}")
        self.assertIn("בְּרֵאשִׁית", rendered)

    def test_genesis_49_proto_uses_tel_zayit_encoding(self) -> None:
        rendered = build.tex_to_markdown(r"\hProto{טעשׁת}")
        self.assertIn(">TOst</span>", rendered)
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".hebrew.source-proto", stylesheet)
        self.assertIn('font-family: "WTN Paleo Tel Zayit"', stylesheet)

    def test_genesis_14_other_uses_ascii_moabite_font(self) -> None:
        rendered = build.tex_to_markdown(r"\hOther{אבגד}")
        self.assertIn(">ABGD</span>", rendered)
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".hebrew.source-other", stylesheet)
        self.assertIn('font-family: "WTN Paleo Moabite"', stylesheet)

    def test_genesis_5_records_keeps_hebrew_codepoints_for_block_font(self) -> None:
        rendered = build.tex_to_markdown(r"\hBookOfRecords{אָבג}")
        self.assertIn(">אבג</span>", rendered)
        self.assertNotIn(">ABG</span>", rendered)
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".hebrew.source-records", stylesheet)
        self.assertIn('font-family: "WTN Paleo Mono"', stylesheet)

    def test_english_uses_regular_noto_sans_without_global_smallcaps(self) -> None:
        self.assertFalse(any("english-im-fell-english-sc" in str(font) for font in build.FONT_FILES))
        self.assertTrue(any("noto-sans-regular.ttf" in str(font) for font in build.FONT_FILES))
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn('@font-face { font-family: "WTN Noto Sans";', stylesheet)
        self.assertIn("body {", stylesheet)
        self.assertIn('font-family: "WTN Noto Sans", sans-serif; font-variant: normal;', stylesheet)

    def test_preconverted_math_omits_reparsed_tex_annotation(self) -> None:
        rendered = build.render_complex_math(r"$$\Delta_t = \text{gap}.$$ ")
        self.assertIsNotNone(rendered)
        self.assertIn("<math", rendered)
        self.assertNotIn("<annotation", rendered)

    def test_front_matter_contains_named_alphabet_history_page(self) -> None:
        matter = "\n".join(build.front_matter([], {}))
        self.assertIn("# The History of the Alphabet", matter)
        self.assertIn('class="alphabet-page"', matter)
        self.assertNotIn("we-cover-2.png", Path(build.__file__).read_text())

    def test_raw_tabular_is_semantic_table(self) -> None:
        rendered = build.tex_to_markdown(r"\begin{tabular}{lcr}a&b&c\\d&e&f\end{tabular}")
        self.assertIn('<table class="wtn-table wtn-table-custom">', rendered)
        self.assertEqual(rendered.count("<td"), 6)

    def test_together_options_do_not_leak(self) -> None:
        rendered = build.tex_to_markdown(r"\begin{together}[8][5000]Praise the Lord!\end{together}")
        self.assertEqual(rendered, "Praise the Lord!")

    def test_left_alignment_is_the_default(self) -> None:
        rendered = build.tex_to_markdown(r"\aA{ordinary commentary}")
        self.assertIn("align-start", rendered)
        self.assertNotIn("align-center", rendered)

    def test_red_commentary_is_red_and_left_aligned_without_css_variables(self) -> None:
        rendered = build.tex_to_markdown(r"\aB{Genesis commentary}")
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn("annotation-b align-start", rendered)
        self.assertIn(".annotation-b { color: #820000 !important;", stylesheet)
        self.assertIn(".align-start { text-align: left; text-align: start; }", stylesheet)

    def test_compatibility_palette_has_no_css_variable_dependency(self) -> None:
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertNotIn("var(--", stylesheet)
        self.assertNotIn("prefers-color-scheme", stylesheet)
        self.assertIn("border-top: 1px solid #6e6e6e !important", stylesheet)

    def test_only_explicit_triplet_centers_commentary(self) -> None:
        ordinary = build.tex_to_markdown(r"\aB[c]{optional argument is inert in master.tex}")
        explicit = build.tex_to_markdown(r"\aBc{explicit centering shortcut}")
        self.assertIn("annotation-b align-start", ordinary)
        self.assertIn("annotation-b align-center", explicit)


if __name__ == "__main__":
    unittest.main()
