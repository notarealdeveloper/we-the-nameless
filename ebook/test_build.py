#!/usr/bin/env python3
"""Focused regression tests for WTN's semantic TeX conversion."""

from __future__ import annotations

import unittest
import tempfile
import json
import re
import shutil
from unittest.mock import patch
import subprocess
from pathlib import Path

from fontTools.ttLib import TTFont

import build


class ConversionTests(unittest.TestCase):
    def test_genesis_48_artwork_replaces_scenes_and_preserves_prose(self):
        source = (build.ROOT / "01-genesis/48.tex").read_text(encoding="utf-8")
        rendered = {}
        for number, _, _, commentary in build.parse_verses(source):
            rendered[number] = build.render_verse_commentary("Genesis", "48", number, commentary)
            if number not in {"11", "12", "13", "14", "17", "18", "19"}:
                self.assertEqual(rendered[number], build.tex_to_markdown(commentary))
            self.assertEqual(
                build.render_verse_commentary("Exodus", "48", number, commentary),
                build.tex_to_markdown(commentary),
            )
        for asset in (build.HERE / "img").glob("genesis-48-*.png"):
            number = asset.stem.split("-")[2]
            self.assertEqual(rendered[number].count(f'src="ebook/img/{asset.name}"'), 1)
        for number in ("11", "12", "13", "14", "17", "18", "19"):
            for obsolete in ("family-diagram", "glyph-overlap", "tikzpicture", 'class="egyptian"'):
                self.assertNotIn(obsolete, rendered[number])
        verse = rendered["18"]
        self.assertLess(verse.index("Not good dad."), verse.index("genesis-48-18-1.png"))
        self.assertLess(verse.index("genesis-48-18-1.png"), verse.index("Set your right hand on his head."))
        self.assertLess(verse.index("Set your right hand on his head."), verse.index("genesis-48-18-2.png"))
        self.assertIn("For the book.", rendered["19"])

    def test_new_genesis_redactors_and_inline_commands(self):
        for key in ("RA", "RB", "RC"):
            rendered = build.tex_to_markdown("\\e" + key + "{English}\\h" + key + "{אב}")
            self.assertEqual(rendered.count("source-" + key.lower()), 2)
            self.assertIn('dir="rtl"', rendered)
        self.assertIn('class="proto-sinaitic"', build.tex_to_markdown(r"\proto{נח}"))
        self.assertNotIn("black!4", build.tex_to_markdown(r"\textcolor{black!4}{S}laughter"))
        self.assertNotIn("[4]", build.tex_to_markdown(r"before\nopagebreak[4]after"))

    def test_current_publication_notices_and_legend(self):
        matter = "\n".join(build.front_matter([], {}, "Genesis"))
        self.assertIn("Publication Notice One", matter)
        self.assertIn("Publication Notice Two", matter)
        self.assertIn("Genesis 1 is written in a different style", matter)
        self.assertIn("empowering of Zadok and the Aaronids", matter)
        self.assertIn("We the people. We write regular.", matter)
        self.assertIn("Named J, or the Yahwist", matter)
        self.assertIn("We have complied, reluctantly.", matter)
        self.assertIn("Ketef Hinnom", matter)
        self.assertNotIn("SourceLegendFootnote", matter)

    def test_midrash_boundaries_and_helper_glyphs_survive(self):
        source = r"Before \begin{midrash}Abe: Which son?\end{midrash} After"
        for compact in (False, True):
            rendered = build.tex_to_markdown(source, compact=compact)
            self.assertIn("(Begin Midrash)", rendered)
            self.assertIn("(End Midrash)", rendered)
            self.assertLess(rendered.index("(Begin Midrash)"), rendered.index("Abe:"))
        self.assertIn("ᗺ", build.tex_to_markdown(r"{\Er}"))
        self.assertIn("𓂋", build.tex_to_markdown(r"{\reubenface}"))
        self.assertIn('class="canadian-syllabics"', build.tex_to_markdown(r"{\Er}"))

    def test_apocrypha_selection_follows_print(self):
        for selection in ("genesis", "exodus"):
            enabled = build.subset_content(selection, apocrypha="apocryphal")[0]
            disabled = build.subset_content(selection, apocrypha="canonical")[0]
            self.assertTrue(any(rel.endswith("/apocrypha.tex") for _, rel in enabled))
            self.assertFalse(any(rel.endswith("/apocrypha.tex") for _, rel in disabled))
        self.assertFalse(any(rel.endswith("/apocrypha.tex") for _, rel in build.subset_content("J")[0]))
        self.assertFalse(any(rel.endswith("/apocrypha.tex") for _, rel in build.master_sequence(apocrypha="canonical")))

    def test_apocrypha_preserves_intro_titles_fragments_and_trailing_prose(self):
        rendered = build.tex_to_markdown(
            r"\Apocrypha{Genesis}Publisher intro. \Apocryphon[Short]{Long title}"
            r"\ApocryphonVerse{1}{}{}{Fragment prose.} Trailing dialogue.")
        for text in ("Publisher intro.", "### Long title", "#### Fragment 1", "Fragment prose.", "Trailing dialogue."):
            self.assertIn(text, rendered)
        self.assertNotIn("Short", rendered)

    def test_sentence_numbering_is_independent_of_verses(self):
        self.assertEqual([v[0] for v in build.parse_verses(
            r"\Verse{7}{}{}{}\Sentence{}{One}{}\Verse{9}{}{}{}\Sentence{}{Two}{}")],
            ["7", "1", "9", "2"])

    def test_genesis_apocrypha_print_pages_become_linked_contents(self):
        source = (build.ROOT / "01-genesis/apocrypha.tex").read_text(encoding="utf-8")
        rendered = build.render_apocrypha(source)
        self.assertTrue(rendered.startswith("### Contents\n\n::: {.apocrypha-contents}\n\n- [Publisher's Introduction]"))
        import re
        targets = re.findall(r"\]\(#(gen-apoc:[^)]+)\)", rendered)
        self.assertEqual(len(targets), 6)
        for target in targets:
            self.assertEqual(rendered.count("{#" + target), 1)
        for debris in ("RuleColor", "4248", "0.75pt", "0.4pt", "=0pt", "[2]0.84", "#2[r]#1", "\nempty\n", "\nplain\n"):
            self.assertNotIn(debris, rendered)
        self.assertIn("### Publisher's Introduction", rendered)
        self.assertIn("### Genesis 1 Apocryphon — Infinite J Est", rendered)
        self.assertIn("### Genesis 22 Apocryphon — The Son of J", rendered)
        self.assertIn("Ever since the discovery", rendered)
        self.assertIn('Comet is short for', rendered)
        self.assertIn("#### Fragment 1", rendered)
        for number in range(1, 5):
            self.assertIn(f'src="img/comics/the-twelve-tribes-of-israel-comic-{number}.png"', rendered)
        # Only print preliminaries and label/heading markup may be replaced.
        body = source[source.index(r"\Apocrypha{Genesis}"):]
        plain = lambda value: re.sub(r"<[^>]+>|\s+|[#*]", "", re.sub(r" \{[#.][^}]+\}", "", value))
        original = build.tex_to_markdown(body)
        for target in targets:
            original = original.replace(target, "")
        content = "Publisher" + rendered.split("### Publisher", 1)[1]
        self.assertEqual(plain(original), plain(content))

    def test_exodus_apocrypha_without_print_index_is_preserved(self):
        source = (build.ROOT / "02-exodus/apocrypha.tex").read_text(encoding="utf-8")
        self.assertEqual(build.render_apocrypha(source), build.tex_to_markdown(source))

    def test_new_script_fonts_and_nested_image_paths(self):
        rendered = build.tex_to_markdown(r"\anatolian{𔔉}")
        self.assertIn('class="anatolian" lang="hlu" dir="ltr"', rendered)
        for filename in ("noto-sans-anatolian-hieroglyphs.ttf", "noto-sans-canadian-aboriginal.ttf"):
            font = build.ROOT / "fonts" / filename
            self.assertIn(font, build.FONT_FILES)
            self.assertTrue(font.is_file())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            asset = root / "history/book/include/fixture.png"
            asset.parent.mkdir(parents=True)
            asset.touch()
            with patch.object(build, "ROOT", root):
                self.assertEqual(build.resolve_image_path("fixture"), asset)

    def test_subset_alias_identity_and_case(self):
        aliases = [build.subset_edition(name) for name in ("genesis", "1-genesis", "01-genesis")]
        self.assertEqual({item[1] for item in aliases}, {"genesis"})
        self.assertTrue(all(item[3] == build.publication_metadata("Genesis") for item in aliases))
        self.assertNotEqual(build.subset_edition("J")[3]["identifier"], build.subset_edition("j")[3]["identifier"])
        self.assertEqual(build.subset_edition("J")[1], "J")
        self.assertEqual([build.subset_edition(name)[1] for name in ("samuel", "1-samuel", "2-samuel")],
                         ["samuel", "1-samuel", "2-samuel"])

    def test_subset_filtering_and_navigation_on_fixture(self):
        selector = build.subset_module()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "01-genesis").mkdir()
            (root / "01-genesis/01.tex").write_text(
                r"\Chapter{1}" + "\n" + r"\Verse{1}{\hP{אב}}{\eP{Priestly}}{}" + "\n"
                + r"\Verse{2}{\hJ{אב}}{\eJ{Yahwist}}{}" + "\n")
            body = r"\Book{Genesis}\include{01-genesis/01}"
            with patch.object(build, "ROOT", root), patch.object(selector, "read_master", return_value=("", body)):
                content = build.subset_content("P")
            self.assertIn("Priestly", content[1]["01-genesis/01.tex"])
            self.assertNotIn("Yahwist", content[1]["01-genesis/01.tex"])
            manuscript = root / "fixture.md"
            with patch.object(build, "chapter_summaries", return_value={}), patch.object(build, "top_level_books", return_value=["Genesis", "Exodus"]):
                build.make_markdown(manuscript, "P", content=content)
            rendered = manuscript.read_text()
            self.assertIn('href="#contents-genesis"', rendered)
            self.assertNotIn('href="#contents-exodus"', rendered)
            self.assertIn("Priestly", rendered)
            self.assertNotIn("Yahwist", rendered.split("# [Genesis]", 1)[1])

    def test_all_subset_targets_have_ebook_commands(self):
        names = subprocess.check_output([str(build.ROOT / "bin/book-subset"), "--make-targets"], text=True).split()
        names += subprocess.check_output([str(build.ROOT / "bin/book-subset"), "--make-chapter-targets"], text=True).split()
        database = subprocess.run(["make", "-qp"], cwd=build.ROOT, text=True, capture_output=True)
        self.assertIn(database.returncode, (0, 1))
        outputs = {}
        for name in names:
            for suffix in ("ebook", "ebook-release", "ebook-check"):
                self.assertIn("\n" + name + "-" + suffix + ":", database.stdout)
            target, output, _, _ = build.subset_edition(name)
            canonical = build.subset_module().target_output_name(target)
            self.assertEqual(outputs.setdefault(output, canonical), canonical)

    def test_sentence_prose_is_not_dropped(self):
        self.assertEqual(build.parse_verses(r"\Sentence{original}{English}{commentary}"),
                         [("1", "original", "English", "commentary")])

    def test_epubcheck_failure_is_not_swallowed(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            for name, code in (("epubcheck", 7), ("validate.py", 0)):
                script = temp / name
                script.write_text(f"#!/bin/sh\nexit {code}\n")
                script.chmod(0o755)
            import os
            result = subprocess.run(["make", "-f", str(build.HERE / "Makefile"), "validate"], cwd=temp,
                env={**os.environ, "PATH": str(temp) + ":" + os.environ["PATH"]},
                text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Error 7", result.stderr)

    def test_failed_release_preserves_previous_epub(self):
        import sys
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "edition.epub"
            output.write_bytes(b"previous release")
            def fake_run(command, **kwargs):
                if command[0] == "pandoc":
                    Path(command[command.index("--output") + 1]).write_bytes(b"candidate")
                return subprocess.CompletedProcess(command, 7 if command[0] == "epubcheck" else 0, "", "")
            with patch.object(sys, "argv", ["build.py", "--output", str(output), "--require-epubcheck"]), \
                 patch.object(build.shutil, "which", side_effect=lambda name: name), \
                 patch.object(build, "master_sequence", return_value=[]), \
                 patch.object(build, "make_markdown", side_effect=lambda path, *a, **kw: (path.write_text("fixture") and (1, 1))), \
                 patch.object(build, "postprocess_epub"), \
                 patch.object(build.subprocess, "run", side_effect=fake_run):
                self.assertEqual(build.main(), 7)
            self.assertEqual(output.read_bytes(), b"previous release")

    def test_babeled_j_font_aliases_original_phoenician_glyphs(self) -> None:
        original = TTFont(Path(build.ROOT) / "fonts/paleo-hebrew-phoenician.ttf")
        babeled_path = Path(build.ROOT) / "fonts/babel-paleo-hebrew-phoenician.ttf"
        babeled = TTFont(babeled_path)
        original_cmap = original.getBestCmap()
        cmap = babeled.getBestCmap()
        for hebrew, phoenician, ascii_aliases in zip(
            "אבגדהוזחטיכלמנסעפצקרשת",
            "𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕",
            ("a", "bv", "g", "d", "eh", "w", "z", "xH", "T0", "ijy", "k", "l", "m", "n", "S", "oA", "p", "c", "q", "r", "s", "t"),
        ):
            source_glyph = original_cmap[ord(phoenician)]
            self.assertEqual(cmap[ord(phoenician)], source_glyph)
            self.assertEqual(cmap[ord(hebrew)], source_glyph)
            for alias in ascii_aliases:
                self.assertEqual(cmap[ord(alias)], source_glyph)
            self.assertEqual(babeled["hmtx"][source_glyph], original["hmtx"][source_glyph])

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
        self.assertIn(">TOst</bdo>", rendered)
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".hebrew.source-proto", stylesheet)
        self.assertIn('font-family: "WTN Paleo Tel Zayit"', stylesheet)

    def test_genesis_14_other_uses_ascii_moabite_font(self) -> None:
        rendered = build.tex_to_markdown(r"\hOther{אבגד}")
        self.assertIn(">ABGD</bdo>", rendered)
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

    def test_source_span_preserves_trailing_space_inside_its_argument(self) -> None:
        rendered = build.tex_to_markdown(r"c\eR{hildren }o\eR{h my oh }me")
        self.assertIn(">hildren </span>o", rendered)
        self.assertIn(">h my oh </span>me", rendered)

    def test_commentary_indentation_preserves_each_authored_level(self) -> None:
        rendered = build.tex_to_markdown(
            r"\hspace{1em}one \hspace{2em}two \hspace{3em}three"
        )
        self.assertIn('class="indent-1"', rendered)
        self.assertIn('class="indent-2"', rendered)
        self.assertIn('class="indent-3"', rendered)
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".indent-1 { width: 1em; }", stylesheet)
        self.assertIn(".indent-3 { width: 3em; }", stylesheet)

    def test_multiline_annotation_keeps_paragraphs_without_footnotes(self) -> None:
        rendered = build.tex_to_markdown("\\aB{First.\n\nSecond.\n\nThird.}")
        self.assertEqual(rendered.count('class="annotation-paragraph"'), 3)

    def test_tex_single_quotes_become_unicode_typographic_quotes(self) -> None:
        rendered = build.tex_to_markdown(r"Putting an `i' at the end.")
        self.assertEqual(rendered, "Putting an ‘i’ at the end.")

    def test_reusable_zero_argument_tex_macros_are_expanded(self) -> None:
        rje = build.tex_to_markdown(r"infinite {\pussyb}")
        redactor = build.tex_to_markdown(r"infinite {\pussyc}")
        self.assertIn('class="source source-rje english"', rje)
        self.assertIn(">atriarch</span>y", rje)
        self.assertIn('class="source source-r english"', redactor)
        self.assertIn(">rity and blessing", redactor)
        self.assertTrue(redactor.endswith("ssy"))

    def test_j_e_rje_and_generic_paleo_are_right_to_left(self) -> None:
        j = build.tex_to_markdown(r"\hJ{אבג}")
        self.assertIn('<span class="source source-j hebrew" lang="he" dir="rtl"', j)
        self.assertIn('>אבג</span>', j)
        self.assertNotRegex(j, r"[𐤀-𐤟]")
        self.assertIn('<bdo class="source source-e hebrew" lang="he" dir="rtl"', build.tex_to_markdown(r"\hE{אבג}"))
        self.assertIn('>ABG</bdo>', build.tex_to_markdown(r"\hE{אבג}"))
        self.assertIn('<bdo class="source source-rje hebrew" lang="he" dir="rtl"', build.tex_to_markdown(r"\hRJE{אבג}"))
        self.assertIn('class="paleo" lang="he" dir="rtl"', build.tex_to_markdown(r"\paleo{אבג}"))
        self.assertIn('lang="he" dir="rtl"', build.tex_to_markdown(r"\hP{אָבג}"))

    def test_e_bidi_override_preserves_logical_order_and_inline_markup(self) -> None:
        rendered = build.tex_to_markdown(r"\hE{אב \hlB{גד} הו}")
        self.assertIn(
            '>AB <span class="highlight-b">GD</span> HW</bdo>',
            rendered,
        )

    def test_mixed_j_e_rje_sequence_remains_in_authored_order(self) -> None:
        rendered = build.tex_to_markdown(r"\hJ{אב} \hE{גד} \hRJE{הו}")
        j = rendered.index('source-j hebrew')
        e = rendered.index('source-e hebrew')
        rje = rendered.index('source-rje hebrew')
        self.assertLess(j, e)
        self.assertLess(e, rje)
        self.assertIn('dir="rtl"', rendered[j:e])
        self.assertIn('dir="rtl"', rendered[e:rje])
        self.assertIn('dir="rtl"', rendered[rje:])

    def test_genesis_49_proto_forces_rtl_despite_ascii_font_slots(self) -> None:
        rendered = build.tex_to_markdown(r"\hProto{טעשׁת}")
        self.assertIn('<bdo class="source source-proto hebrew" lang="he" dir="rtl"', rendered)
        self.assertIn('>TOst</bdo>', rendered)

    def test_print_style_image_name_resolves_to_book_include_asset(self) -> None:
        rendered = build.tex_to_markdown(r"\image{seir}")
        self.assertIn('src="01-genesis/include/seir.jpg"', rendered)

    def test_chapter_summaries_are_toc_only(self) -> None:
        self.assertEqual(build.chapter_heading("Genesis", "46"), "Genesis 46")
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn("h1.book-title", stylesheet)
        self.assertIn("h2.chapter-title", stylesheet)
        self.assertNotIn("\n.book-title {", stylesheet)
        self.assertNotIn("\n.chapter-title {", stylesheet)
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
        self.assertIn('class="alphabet paleo" lang="he" dir="rtl"', matter)
        self.assertIn('class="source source-j hebrew" lang="he" dir="rtl"', matter)
        self.assertIn('class="source source-e hebrew" lang="he" dir="rtl"', matter)
        self.assertEqual(build.cover_path("none"), None)
        self.assertEqual(build.cover_path("we-cover-8"), build.COVERS / "we-cover-8.png")

    def test_cover_rejects_paths_and_unknown_basenames(self) -> None:
        with self.assertRaises(ValueError):
            build.cover_path("../we-cover-8")
        with self.assertRaises(ValueError):
            build.cover_path("not-a-cover")

    def test_partial_front_matter_keeps_full_book_list_but_links_only_selection(self) -> None:
        matter = "\n".join(build.front_matter(build.master_sequence("Genesis"), {}, "Genesis"))
        self.assertIn('<a href="#contents-genesis">Genesis</a>', matter)
        self.assertIn('<span>Exodus</span>', matter)
        self.assertNotIn('href="#contents-exodus"', matter)
        self.assertIn('<h2><a href="#tableofcontents">Genesis</a></h2>', matter)

    def test_body_navigation_mirrors_print_hierarchy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manuscript = Path(temp) / "manuscript.md"
            build.make_markdown(manuscript, "Genesis")
            rendered = manuscript.read_text(encoding="utf-8")
        self.assertIn("# [Genesis](#tableofcontents) {#book-genesis .book-title}", rendered)
        self.assertIn("## [Genesis 1](#contents-genesis) {#genesis-1 .chapter-title}", rendered)
        self.assertIn('<a href="#genesis-1">Genesis 1:1</a>', rendered)

    def test_front_matter_prose_matches_body_scale(self) -> None:
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertIn(".verse { font-size: .82em", stylesheet)
        self.assertIn(".contents-list { font-size: .82em", stylesheet)
        self.assertIn(".source-legend {", stylesheet)
        self.assertIn("font-size: .82em;", stylesheet)
        # The nested wrapper must not shrink an already scaled source legend.
        self.assertIn(".font-legend { font-size: 1em; }", stylesheet)
        self.assertIn(".book-list { font-size: 1em; }", stylesheet)
        self.assertIn(".apocrypha { font-size: .82em;", stylesheet)

    def test_source_keys_reflow_without_print_line_breaks(self):
        for command in ("SourceLegendPage", "PrimarySourceFontsPage", "PrimevalSourceFontsPage"):
            rendered = "\n".join(build.author_legend(command))
            self.assertNotIn("<br/>", rendered)
            self.assertNotIn("align-center", rendered)
        rendered = "\n".join(build.author_legend())
        self.assertIn('same event </span> <span class="source source-rje english"', rendered)
        self.assertIn("while others prefer to choose one", rendered)

    def test_primeval_specimens_have_embedded_fonts_and_correct_glyph_slots(self):
        rendered = "\n".join(build.author_legend("PrimevalSourceFontsPage"))
        self.assertIn("Archaic songs, poetry, and blessings", rendered)
        self.assertEqual(rendered.count('class="legend-label" dir="rtl"'), 6)
        for profile, filename in {
            "ProtoA": "proto-sinaitic-15.ttf", "ProtoC": "proto-sinaitic-15.ttf",
            "ProtoE": "proto-sinaitic-13.ttf", "Proto": "08-bc10c-paleo-hebrew-tel-zayit.ttf",
            "Records": "paleo-hebrew-mono.ttf", "PaleoM": "paleo-hebrew-ketef-hinnom-1.ttf",
        }.items():
            sample = build.legend_alphabet(profile)
            self.assertIn(sample, rendered)
            self.assertIn('lang="he" dir="rtl"', sample)
            font = build.ROOT / "fonts" / filename
            self.assertIn(font, build.FONT_FILES)
            cmap = TTFont(font).getBestCmap()
            text = re.sub(r"<[^>]+>", "", sample)
            for char in text:
                self.assertIn(ord(char), cmap, (profile, char))
                self.assertNotEqual(cmap[ord(char)], ".notdef")

    def test_heading_styles_do_not_scale_or_hide_enclosing_sections(self):
        stylesheet = (build.HERE / "epub.css").read_text()
        for cls in ("front-heading", "alphabet-heading", "visually-hidden", "apocryphon-title"):
            self.assertNotRegex(stylesheet, r"(?m)^\." + cls + r"\s*\{")
        self.assertIn("h1, h2, h3, h4, h5, h6 { font-family: serif; }", stylesheet)
        self.assertIn(".title-we, .title-nameless, .title-book { font-family: serif;", stylesheet)
        title_rule = re.search(r"h3\.apocryphon-title\s*\{([^}]+)\}", stylesheet)[1]
        self.assertIn("page-break-before: always", title_rule)
        self.assertIn("margin-top: 0", title_rule)

    def test_apocryphon_titles_have_scroll_ornaments_and_page_destinations(self):
        rendered = build.render_apocrypha((build.ROOT / "01-genesis/apocrypha.tex").read_text())
        titles = re.findall(r"(?m)^### .*\{#(gen-apoc:[^ ]+) \.apocryphon-title\}", rendered)
        self.assertEqual(len(titles), 5)
        self.assertEqual(rendered.count('class="apocryphon-alphabet"'), len(titles))
        self.assertNotIn('<span id="gen-apoc:', rendered)
        decoration = build.apocryphon_alphabet()
        self.assertIn('aria-hidden="true"', decoration)
        font = build.ROOT / "fonts/dead-sea-scrolls-isaiah.ttf"
        self.assertIn(font, build.FONT_FILES)
        cmap = TTFont(font).getBestCmap()
        for char in re.sub(r"<[^>]+>", "", decoration):
            self.assertIn(ord(char), cmap)

    def test_stylesheet_fonts_are_packaged_and_alphabets_can_wrap(self):
        stylesheet = (build.HERE / "epub.css").read_text()
        for filename in re.findall(r'url\("\.\./fonts/([^\"]+)"\)', stylesheet):
            self.assertIn(build.ROOT / "fonts" / filename, build.FONT_FILES)
        wrapping = re.search(r"\.legend-label, \.apocryphon-alphabet, \.alphabet\s*\{([^}]+)\}", stylesheet)[1]
        self.assertIn("word-wrap: break-word", wrapping)
        self.assertIn("overflow-wrap: anywhere", wrapping)

    @unittest.skipUnless(shutil.which("pandoc"), "Pandoc is needed for note parsing fixtures")
    def test_adjacent_footnotes_throughout_manuscript_are_real_notes(self):
        # Parse only affected verse fragments, never compile a book or EPUB.
        fixtures, expected_notes, locations = [], 0, []
        for directory in sorted(build.ROOT.glob("[0-9][0-9]-*")):
            for path in sorted(directory.rglob("*.tex")):
                for number, hebrew, english, commentary in build.parse_verses(path.read_text()):
                    for region in (hebrew, english, commentary):
                        if not re.search(r"\\(?:footnote|recursivefootnote|hangingfootnote|f[ABC]X?)\b", region):
                            continue
                        rendered = build.tex_to_markdown(region)
                        if re.search(r"\]\s*\^\[", rendered):
                            fixtures.append(rendered)
                            expected_notes += rendered.count("^[")
                            locations.append((path.relative_to(build.ROOT).as_posix(), number))
        self.assertIn(("01-genesis/26.tex", "22"), locations)
        result = subprocess.run(["pandoc", "--from=" + build.PANDOC_READER, "--to=json"],
                                input="\n\n---\n\n".join(fixtures), capture_output=True, text=True, check=True)
        def nodes(value):
            if isinstance(value, dict):
                yield value
                for child in value.values():
                    yield from nodes(child)
            elif isinstance(value, list):
                for child in value:
                    yield from nodes(child)
        ast = list(nodes(json.loads(result.stdout)))
        self.assertEqual(sum(node.get("t") == "Note" for node in ast), expected_notes)
        self.assertFalse(any(node.get("t") == "Superscript" for node in ast))

    @unittest.skipUnless(shutil.which("pandoc"), "Pandoc is needed for note parsing fixtures")
    def test_adjacent_notes_keep_voices_and_explicit_superscripts(self):
        rendered = build.tex_to_markdown(r"Word\footnote{First.}\fB{Second.}\fC{Third.} x\textsuperscript{2}")
        result = subprocess.run(["pandoc", "--from=" + build.PANDOC_READER, "--to=html5"],
                                input=rendered, capture_output=True, text=True, check=True).stdout
        self.assertEqual(result.count('class="footnote-ref"'), 3)
        self.assertIn('class="footnote-voice annotation-b"', result)
        self.assertIn('class="footnote-voice annotation-c"', result)
        self.assertIn("x<sup>2</sup>", result)

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
