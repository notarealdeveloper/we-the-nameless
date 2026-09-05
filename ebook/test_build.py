#!/usr/bin/env python3
"""Focused regression tests for WTN's semantic TeX conversion."""

from __future__ import annotations

import unittest
from pathlib import Path

import build


class ConversionTests(unittest.TestCase):
    def test_publication_identity_is_stable_and_scoped_per_edition(self) -> None:
        complete = build.publication_metadata(None)
        genesis = build.publication_metadata("Genesis")
        self.assertEqual(complete, build.publication_metadata(None))
        self.assertTrue(complete["identifier"].startswith("urn:uuid:"))
        self.assertNotEqual(complete["identifier"], genesis["identifier"])
        self.assertEqual(complete["title"], "We The Nameless")
        self.assertEqual(genesis["title"], "We The Nameless: Genesis")
        self.assertEqual(complete["publisher"], "LD LLC")

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

    def test_english_defaults_to_serif_without_global_smallcaps(self) -> None:
        self.assertFalse(any("english-im-fell-english-sc" in str(font) for font in build.FONT_FILES))
        self.assertFalse(any("noto-sans-regular.ttf" in str(font) for font in build.FONT_FILES))
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertNotIn("noto-sans-regular.ttf", stylesheet)
        self.assertNotIn('font-family: "Noto Sans"', stylesheet)
        self.assertNotIn('font-family: "WTN Noto Sans"', stylesheet)
        self.assertIn("body {", stylesheet)
        self.assertIn("font-family: serif; font-size: 100%;", stylesheet)
        self.assertIn("body, body * { font-variant: normal; font-variant-caps: normal; }", stylesheet)

    def test_only_textsc_generates_smallcaps(self) -> None:
        rendered = build.tex_to_markdown(
            r"\eJ{Ordinary English}\fC{Ordinary note and \textsc{Small Caps}}"
        )
        self.assertEqual(rendered.count('class="smallcaps"'), 1)
        self.assertIn('<span class="smallcaps">Small Caps</span>', rendered)

    def test_uncommented_source_transition_has_tex_interword_space(self) -> None:
        rendered = build.tex_to_markdown("\\eJ{first}\n    \\eE{second}")
        self.assertIn("first</span> <span", rendered)

    def test_commented_source_transition_has_no_interword_space(self) -> None:
        rendered = build.tex_to_markdown("\\eJ{first}% comment\n    \\eE{second}")
        self.assertIn("first</span><span", rendered)

    def test_source_transition_preserves_authored_horizontal_space(self) -> None:
        rendered = build.tex_to_markdown(r"\eJ{first} \eE{second}")
        self.assertIn("first</span> <span", rendered)

    def test_paleo_sources_are_left_to_right(self) -> None:
        self.assertIn('lang="he" dir="ltr"', build.tex_to_markdown(r"\hJ{אבג}"))
        self.assertIn('lang="he" dir="ltr"', build.tex_to_markdown(r"\hE{אבג}"))
        self.assertIn('class="paleo" lang="he" dir="ltr"', build.tex_to_markdown(r"\paleo{אבג}"))
        self.assertIn('lang="he" dir="rtl"', build.tex_to_markdown(r"\hP{אָבג}"))

    def test_chapter_summaries_are_toc_only(self) -> None:
        self.assertEqual(build.chapter_heading("Genesis", "46"), "Genesis 46")
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".chapter-title", stylesheet)
        self.assertIn("font-family: serif", stylesheet)
        self.assertIn("font-size: 2.2em", stylesheet)

    def test_footnote_marker_is_attached_to_preceding_annotation(self) -> None:
        rendered = build.tex_to_markdown(r"\aB{Blah.}\fC{Footnote}")
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn("Blah.</span>^[", rendered)
        self.assertNotIn("Blah.</span> ^[", rendered)
        self.assertNotIn(".verse-commentary > p > .annotation { display: block; }", stylesheet)

    def test_preconverted_math_omits_reparsed_tex_annotation(self) -> None:
        rendered = build.render_complex_math(r"$$\Delta_t = \text{gap}.$$ ")
        self.assertIsNotNone(rendered)
        self.assertIn("<math", rendered)
        self.assertNotIn("<annotation", rendered)

    def test_front_matter_contains_named_alphabet_history_page(self) -> None:
        matter = "\n".join(build.front_matter([], {}, "Genesis"))
        self.assertIn("# The History of the Alphabet", matter)
        self.assertIn('class="alphabet-page"', matter)
        self.assertIn('<div class="title-book">Genesis</div>', matter)
        self.assertIn('class="alphabet paleo" dir="ltr"', matter)
        self.assertIn('class="source source-j hebrew" dir="ltr"', matter)
        self.assertNotIn("we-cover-2.png", Path(build.__file__).read_text())

    def test_definition_list_has_markdown_block_boundaries(self) -> None:
        rendered = build.tex_to_markdown(
            r"\Def{term}[name]{\begin{enumerate}\item First.\item Second.\end{enumerate}}"
        )
        self.assertIn('<div class="definition-body">\n\n-  First.', rendered)
        self.assertIn('Second.\n\n</div>\n\n</section>', rendered)

    def test_recursive_footnote_is_inlined_inside_parent_note(self) -> None:
        rendered = build.tex_to_markdown(
            r"Text\footnote{Outer\recursivefootnote{Inner}}"
        )
        self.assertEqual(rendered.count("^["), 1)
        self.assertIn('<span class="nested-footnote">[Inner]</span>', rendered)

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
