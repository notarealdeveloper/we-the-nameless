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
import zipfile
from pathlib import Path

from fontTools.ttLib import TTFont

import build


class ConversionTests(unittest.TestCase):
    def css_properties(self, selector):
        """Read the author's simple class rules, including shared declarations."""
        stylesheet = (build.HERE / "epub.css").read_text()
        stylesheet = re.sub(r"/\*.*?\*/", "", stylesheet, flags=re.DOTALL)
        properties = {}
        for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", stylesheet):
            if selector in [value.strip() for value in selectors.split(",")]:
                properties.update(declaration.strip().split(":", 1)
                                  for declaration in body.split(";") if ":" in declaration)
        return {key.strip(): value.strip() for key, value in properties.items()}

    def test_apocryphon_dialogue_uses_inks_without_priest_or_redactor_profiles(self):
        for compact in (False, True):
            with self.subTest(compact=compact):
                yhwh = build.tex_to_markdown(
                    r"\ApocryphonYHWHDialogue{Yahweh: Words \eR{edited} here.}", compact=compact)
                self.assertEqual(yhwh, build.tex_to_markdown(
                    r"\aB{Yahweh: Words \eR{edited} here.}", compact=compact))
                # Explicit redactor edits inside dialogue retain their own style.
                self.assertEqual(yhwh.count('data-source="R"'), 1)
                moses = build.tex_to_markdown(
                    r"\ApocryphonMosesDialogue{Moses: \textsl{(whispering)} Words.}", compact=compact)
                self.assertIn("yellow dialogue-moses", moses)
                self.assertNotIn("source-e", moses)
                self.assertNotIn("<strong>", moses)
                self.assertIn("<em>(whispering)</em>", moses)
        self.assertEqual(self.css_properties(".yellow")["color"],
                         self.css_properties(".source-e")["color"])
        self.assertEqual(self.css_properties(".dialogue-moses")["font-weight"], "400")
        self.assertEqual(self.css_properties(".english.source-e")["font-weight"], "700")
        # Exercise every dialogue wrapper in the current manuscript, including
        # multiline speeches and the dialogue after the numbered fragments.
        source = build.strip_comments((build.ROOT / "01-genesis/apocrypha.tex").read_text())
        for name, cls in (("ApocryphonMosesDialogue", "yellow dialogue-moses"),
                          ("ApocryphonYHWHDialogue", "annotation-b")):
            for match in re.finditer(r"\\" + name + r"\s*(?=\{)", source):
                body, _ = build.group(source, match.end())
                self.assertIn(cls, build.tex_to_markdown("\\" + name + "{" + body + "}"))

    def test_generic_paleo_inherits_foreground_and_explicit_sources_keep_colour(self):
        source = (build.ROOT / "01-genesis/apocrypha.tex").read_text()
        intro = build.render_apocrypha(source).split("### Apocryphon", 1)[0]
        for letter in ("ה", "א"):
            self.assertIn(f'<span class="paleo" lang="he" dir="rtl">{letter}</span>', intro)
        self.assertNotIn("color", self.css_properties(".paleo"))
        for command in ("paleo", "Paleo"):
            rendered = build.tex_to_markdown("\\" + command + "{אב}")
            self.assertIn('class="paleo" lang="he" dir="rtl"', rendered)
            self.assertNotIn("source-j", rendered)
        self.assertIn("color", self.css_properties(".source-j"))
        self.assertIn("source-j", build.tex_to_markdown(r"\hJ{אב}"))

    def test_source_traits_do_not_imply_priesthood_and_options_compose_in_order(self):
        for macro, color in (("Mushite", "yellow"), ("Aaronid", "blue")):
            plain = build.tex_to_markdown("\\" + macro + "{Words}")
            self.assertIn(f'class="source-decoration {color}"', plain)
            self.assertNotIn("font-weight", plain)
            self.assertNotIn("font-weight", self.css_properties("." + color))
            self.assertNotIn("data-source", plain)
            priest = build.tex_to_markdown("\\" + macro + "[priest]{Words}")
            self.assertIn('style="font-weight: 700"', priest)
            regular = build.tex_to_markdown("\\" + macro + "[priest,nopriest]{Words}")
            self.assertIn('style="font-weight: 400"', regular)
        for options, weight in (("priest,nopriest", "400"), ("nopriest,priest", "700")):
            rendered = build.tex_to_markdown("\\SourceDecorate[mushite," + options + "]{Words}")
            self.assertIn("yellow", rendered)
            self.assertIn(f'font-weight: {weight}', rendered)
        self.assertIn("font-weight: 700", build.tex_to_markdown(r"\DeuterA{Dtr1}"))
        self.assertIn("font-weight: 400", build.tex_to_markdown(r"\DeuterB[nopriest]{Dtr2}"))
        redactor = build.tex_to_markdown(r"\Aaronid[redactor,nopriest]{R}")
        self.assertIn("blue decorator-redactor", redactor)
        self.assertIn("font-weight: 400", redactor)
        self.assertIn("decorator-ezekiel", build.tex_to_markdown(r"\Aaronid[ezekiel]{Ezekiel}"))
        nested = build.tex_to_markdown(r"\Priest{\Mushite{E}}")
        self.assertIn('style="font-weight: 700"', nested)
        self.assertIn('class="source-decoration yellow"', nested)
        paragraphs = build.tex_to_markdown("\\Mushite{First.\n\nSecond.}")
        self.assertIn('<div class="source-decoration yellow">', paragraphs)
        self.assertNotIn('<span class="source-decoration', paragraphs)

    def test_detached_and_recursive_notes_share_body_prose_size(self):
        body = self.css_properties(".verse")
        for selector in (".apocrypha", "section.footnotes"):
            props = self.css_properties(selector)
            self.assertEqual(props["font-size"], body["font-size"])
            self.assertEqual(props["line-height"], body["line-height"])
        for selector in (".footnote-voice", ".nested-footnote"):
            self.assertNotIn("font-size", self.css_properties(selector))

    @unittest.skipUnless(shutil.which("pandoc"), "Pandoc is needed for note section fixtures")
    def test_pandoc_detaches_note_sections_from_scaled_prose_containers(self):
        manuscript = ("::: {.verse}\n\n" + build.tex_to_markdown(
            r"Verse\footnote{Ordinary note.}\fB{Red note.}") + "\n\n:::\n\n"
            "::: {.apocrypha}\n\n" + build.tex_to_markdown(
            r"Apocryphon\fC{Blue note.\recursivefootnote{Recursive note.}}") + "\n\n:::")
        result = subprocess.run(
            ["pandoc", "--from=" + build.PANDOC_READER, "--to=html5"],
            input=manuscript, text=True, capture_output=True, check=True,
        ).stdout
        root = build.ET.fromstring("<body>" + result + "</body>")
        notes = [node for node in root if "footnotes" in node.get("class", "").split()]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].tag, "section")
        self.assertEqual(len(notes[0].findall(".//li")), 3)
        for container in root:
            if {"verse", "apocrypha"} & set(container.get("class", "").split()):
                self.assertFalse(any("footnotes" in node.get("class", "").split()
                                     for node in container.iter()))
        self.assertIn("Recursive note.", "".join(notes[0].itertext()))

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
        self.assertNotIn('publisher-page-', matter)
        self.assertEqual(matter.count('class="publication-logo"'), 2)
        self.assertEqual(matter.count('<rect '), 8)
        self.assertIn("Genesis 1 is written in a different style", matter)
        self.assertIn("empowering of Zadok and the Aaronids", matter)
        self.assertIn("We the people. We write regular.", matter)
        self.assertIn("Named J, or the Yahwist", matter)
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

    def test_reader_navigation_lists_only_flat_numbered_chapters(self):
        ids = {f"genesis-{i}" for i in range(1, 51)}
        links = ''.join(f'<li><a href="body.xhtml#{key}">{key}</a></li>' for key in sorted(ids))
        nav = ('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
               '<nav epub:type="toc"><ol><li><a href="front.xhtml#authors">Authors</a><ol>'
               + links + '<li><a href="body.xhtml#genesis-apocrypha">Apocrypha</a></li></ol></li></ol></nav></html>')
        rendered = build.chapter_navigation(nav, ids)
        self.assertEqual(rendered.count('<ol'), 1)
        self.assertEqual(rendered.count('<a '), 50)
        self.assertNotIn('Authors', rendered)
        self.assertNotIn('Apocrypha', rendered)
        points = ''.join(f'<navPoint><navLabel><text>{key}</text></navLabel><content src="body.xhtml#{key}"/></navPoint>' for key in sorted(ids))
        ncx = ('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"><navMap><navPoint>'
               '<navLabel><text>Genesis</text></navLabel><content src="body.xhtml#book-genesis"/>'
               + points + '</navPoint></navMap></ncx>')
        rendered = build.chapter_navigation(ncx, ids, ncx=True)
        root = build.ET.fromstring(rendered)
        navmap = root.find('{http://www.daisy.org/z3986/2005/ncx/}navMap')
        self.assertEqual(len(navmap), 50)
        self.assertEqual(rendered.count('<navPoint '), 50)

    @unittest.skipUnless(shutil.which("pandoc"), "Pandoc is needed for section fixtures")
    def test_packaged_navigation_reads_real_pandoc_sections_without_building_an_epub(self):
        # Generate only a small HTML fixture. This never invokes the book
        # builder or Pandoc's EPUB writer.
        manuscript = ("# Authors {.front-heading}\n\nFront matter.\n\n"
                      "# Genesis {#book-genesis .book-title}\n\n"
                      "## Genesis 1 {#genesis-1 .chapter-title}\n\nVerse.\n\n"
                      "## Genesis 2 {#genesis-2 .chapter-title}\n\nVerse.\n\n"
                      "## Apocrypha {#genesis-apocrypha .chapter-title}\n\nProse.")
        body = subprocess.run(
            ["pandoc", "--from=" + build.PANDOC_READER, "--to=html5", "--standalone",
             "--section-divs", "--metadata=title:Fixture"],
            input=manuscript, text=True, capture_output=True, check=True,
        ).stdout
        expected = {"genesis-1", "genesis-2"}
        self.assertEqual(build.numbered_chapter_ids(body), expected)
        ns = "{http://www.w3.org/1999/xhtml}"
        parsed = build.ET.fromstring(body)
        self.assertTrue(all("id" not in node.attrib for node in parsed.iter(ns + "h2")))
        links = ''.join(f'<li><a href="body.xhtml#{key}">{label}</a></li>' for key, label in (
            ("authors", "Authors"), ("genesis-1", "Genesis 1"),
            ("genesis-2", "Genesis 2"), ("genesis-apocrypha", "Apocrypha")))
        # Tokens, quote style, namespace prefix, attribute order and multiple
        # nav elements must not affect discovery or erase unrelated nav.
        nav = ("<html xmlns='http://www.w3.org/1999/xhtml' xmlns:e='http://www.idpf.org/2007/ops'>"
               "<body><nav e:type='landmarks'><ol><li><a href='body.xhtml'>Start</a></li></ol></nav>"
               "<nav id='reader-toc' e:type='frontmatter toc'><h1>Contents</h1><ol><li>Genesis<ol>"
               + links + "</ol></li></ol></nav>"
               "<nav e:type='page-list'><ol><li><a href='body.xhtml#genesis-1'>1</a></li></ol></nav>"
               "</body></html>")
        ncx = ('<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/"><head>'
               '<meta name="dtb:depth" content="2"/></head><navMap><navPoint>'
               '<navLabel><text>Genesis</text></navLabel><content src="body.xhtml#book-genesis"/>'
               + ''.join(f'<navPoint><navLabel><text>Genesis {i}</text></navLabel>'
                         f'<content src="body.xhtml#genesis-{i}"/></navPoint>' for i in (1, 2))
               + '</navPoint></navMap></ncx>')
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "navigation-fixture.zip"
            with zipfile.ZipFile(fixture, "w") as archive:
                archive.writestr("EPUB/body.xhtml", body)
                archive.writestr("EPUB/nav.xhtml", nav)
                archive.writestr("EPUB/toc.ncx", ncx)
            build.postprocess_epub(fixture)
            with zipfile.ZipFile(fixture) as archive:
                rewritten = archive.read("EPUB/nav.xhtml").decode()
                reader_nav = build.ET.fromstring(rewritten).find(".//" + ns + "nav[@id='reader-toc']")
                self.assertEqual(len(list(reader_nav.iter(ns + "ol"))), 1)
                self.assertEqual([a.get("href") for a in reader_nav.iter(ns + "a")],
                                 ["body.xhtml#genesis-1", "body.xhtml#genesis-2"])
                self.assertNotIn("Authors", rewritten)
                self.assertNotIn("Apocrypha", rewritten)
                self.assertIn("Start", rewritten)
                self.assertIn('epub:type="page-list"', rewritten)
                self.assertIn("Contents", rewritten)
                self.assertEqual(archive.read("EPUB/body.xhtml").decode(), body)
                legacy = archive.read("EPUB/toc.ncx").decode()
                self.assertEqual(legacy.count('<navPoint '), 2)
                self.assertIn('name="dtb:depth" content="1"', legacy)
            # Running cleanup again must leave navigation unchanged.
            build.postprocess_epub(fixture)
            with zipfile.ZipFile(fixture) as archive:
                self.assertEqual(archive.read("EPUB/nav.xhtml").decode(), rewritten)
                self.assertEqual(archive.read("EPUB/toc.ncx").decode(), legacy)

    def test_reader_navigation_rejects_missing_or_duplicate_chapters(self):
        for targets in ([], ["genesis-1"], ["genesis-1", "genesis-1", "genesis-2"]):
            with self.subTest(targets=targets):
                links = ''.join(f'<li><a href="body.xhtml#{key}">{key}</a></li>' for key in targets)
                nav = ('<html xmlns="http://www.w3.org/1999/xhtml" xmlns:e="http://www.idpf.org/2007/ops">'
                       '<nav e:type="toc"><ol>' + links + '</ol></nav></html>')
                with self.assertRaisesRegex(ValueError, "every numbered chapter exactly once"):
                    build.chapter_navigation(nav, {"genesis-1", "genesis-2"})

    def test_chapter_discovery_supports_bare_headings_and_rejects_no_destinations(self):
        body = ('<html xmlns="http://www.w3.org/1999/xhtml"><body>'
                '<h2 class="chapter-title" id="genesis-1">Genesis 1</h2>'
                '<h2 class="chapter-title" id="genesis-apocrypha">Apocrypha</h2>'
                '<h1 class="front-heading" id="notice-2">Notice</h1></body></html>')
        self.assertEqual(build.numbered_chapter_ids(body), {"genesis-1"})
        with tempfile.TemporaryDirectory() as temp:
            fixture = Path(temp) / "missing-chapters.zip"
            with zipfile.ZipFile(fixture, "w") as archive:
                archive.writestr("EPUB/body.xhtml", '<html xmlns="http://www.w3.org/1999/xhtml"/>')
            before = fixture.read_bytes()
            with self.assertRaisesRegex(ValueError, "no numbered chapter destinations"):
                build.postprocess_epub(fixture)
            self.assertEqual(fixture.read_bytes(), before)

    def test_front_matter_omits_alphabet_history_page(self) -> None:
        matter = "\n".join(build.front_matter([], {}, "Genesis"))
        self.assertNotIn("The History of the Alphabet", matter)
        self.assertNotIn('class="alphabet-page"', matter)
        self.assertIn('<div class="title-book">Genesis</div>', matter)
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

    def test_displaced_genesis_verse_keeps_reference_and_order(self):
        with tempfile.TemporaryDirectory() as temp:
            manuscript = Path(temp) / "manuscript.md"
            build.make_markdown(manuscript, "Genesis")
            rendered = manuscript.read_text()
        heading = rendered.index("{#genesis-3 .chapter-title}")
        displaced = rendered.index("{.verse #genesis-2-25}")
        first = rendered.index("{.verse #genesis-3-1}")
        self.assertLess(heading, displaced)
        self.assertLess(displaced, first)
        self.assertIn('>Genesis 2:25</a>', rendered)
        self.assertNotIn('>Genesis 3:25</a>', rendered)

    def test_genesis_day_commentary_is_unpointed(self):
        source = (build.ROOT / "01-genesis/02.tex").read_text()
        number, hebrew, _, commentary = next(v for v in build.parse_verses(source) if v[0] == "4")
        rendered = build.render_verse_commentary("Genesis", "2", number, commentary)
        self.assertIn("ביום", rendered)
        self.assertNotIn("בְּיוֹם", rendered)
        self.assertIn("בְּיוֹם", hebrew)

    def test_highlights_use_lite_screens_and_preserve_ink(self):
        for selector, color in ((".highlight-a", "#e0e0e0"),
                                (".highlight-b", "#f0e0e0"),
                                (".highlight-c", "#e0e9f5")):
            properties = self.css_properties(selector)
            self.assertEqual(properties["background-color"], color + " !important")
            self.assertNotIn("color", properties)

    def test_front_matter_prose_matches_body_scale(self) -> None:
        stylesheet = (Path(build.HERE) / "epub.css").read_text()
        self.assertEqual(self.css_properties(".verse")["font-size"], ".82em")
        self.assertIn(".contents-list { font-size: .82em", stylesheet)
        self.assertIn(".source-legend {", stylesheet)
        self.assertIn("font-size: .82em;", stylesheet)
        # The nested wrapper must not shrink an already scaled source legend.
        self.assertIn(".font-legend { font-size: 1em; }", stylesheet)
        self.assertIn(".book-list { font-size: 1em; }", stylesheet)
        self.assertEqual(self.css_properties(".apocrypha")["font-size"], ".82em")

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
