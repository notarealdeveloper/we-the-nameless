#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


BOOK_NAMES = {
    "01-genesis": "Genesis",
    "02-exodus": "Exodus",
    "03-leviticus": "Leviticus",
    "04-numbers": "Numbers",
    "05-deuteronomy": "Deuteronomy",
    "06-joshua": "Joshua",
    "07-judges": "Judges",
    "08-samuel": "Samuel",
    "09-kings": "Kings",
    "10-ezra": "Ezra",
    "11-nehemiah": "Nehemiah",
    "12-esther": "Esther",
    "10-dudetheyreontome": "Dude, They’re On To Me",
}

SUPER_DIGITS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def chapter_sort_key(path):
    stem = path.stem
    if "-" in stem and stem.split("-", 1)[0].isdigit():
        left, right = stem.split("-", 1)
        return (int(left), int(right) if right.isdigit() else right)
    return (0, int(stem) if stem.isdigit() else stem)


def find_files(path, suffix):
    path = Path(path)
    if path.is_file():
        if path.suffix == suffix:
            return [path]
        raise ValueError(f"{path} is not a {suffix} file")
    return sorted(
        (p for p in path.rglob(f"*{suffix}") if p.is_file()),
        key=lambda p: tuple(p.parts),
    )


def book_id_for(path):
    for part in path.parts:
        if re.fullmatch(r"\d\d-.+", part):
            return part
    return path.parent.name if path.is_file() else path.name


def book_name_for(book_id):
    if book_id in BOOK_NAMES:
        return BOOK_NAMES[book_id]
    return re.sub(r"^\d\d-", "", book_id).replace("-", " ").title()


def chapter_id_for(path):
    return path.stem


def chapter_number_for(chapter_id):
    if "-" in chapter_id:
        chapter_id = chapter_id.split("-", 1)[1]
    return int(chapter_id) if chapter_id.isdigit() else chapter_id


def chapter_part_for(chapter_id):
    if "-" in chapter_id and chapter_id.split("-", 1)[0].isdigit():
        return int(chapter_id.split("-", 1)[0])
    return None


def apply_strip(value, strip):
    return value.strip() if strip and isinstance(value, str) else value


def parse_markdown_file(path, strip=False):
    text = Path(path).read_text(encoding="utf-8").translate(SUPER_DIGITS)
    pattern = re.compile(
        r"(?ms)^##\s+(.+?)\s+(\d+):(\d+)\s*$"
        r".*?^-{8,}\s*$\n(?P<body>.*?)(?=^-{8,}\s*$\n\n##\s+|\Z)"
    )
    verses = []
    for match in pattern.finditer(text):
        body = match.group("body")
        verse_text = body
        note_text = ""
        if re.search(r"(?m)^---\s*$", body):
            verse_text, note_text = re.split(r"(?m)^---\s*$", body, maxsplit=1)
        notes = []
        for block in re.split(r"(?m)(?=^Footnote\s+)", note_text):
            block = block.strip("\n")
            if block:
                notes.append(apply_strip(block, strip))
        verses.append(
            {
                "number": int(match.group(3)),
                "text": apply_strip(verse_text, strip),
                "notes": notes,
            }
        )
    if not verses:
        raise ValueError(f"no markdown verses found in {path}")
    return {
        "id": chapter_id_for(Path(path)),
        "number": chapter_number_for(chapter_id_for(Path(path))),
        "part": chapter_part_for(chapter_id_for(Path(path))),
        "verses": verses,
    }


def parse_markdown(path, strip=False):
    return collect_books(find_files(path, ".md"), parse_markdown_file, strip)


def strip_tex_comments(text):
    out = []
    for line in text.splitlines():
        i = 0
        while True:
            pos = line.find("%", i)
            if pos == -1:
                out.append(line)
                break
            backslashes = 0
            j = pos - 1
            while j >= 0 and line[j] == "\\":
                backslashes += 1
                j -= 1
            if backslashes % 2:
                i = pos + 1
                continue
            out.append(line[:pos])
            break
    return "\n".join(out)


def read_braced(text, pos):
    while pos < len(text) and text[pos].isspace():
        pos += 1
    if pos >= len(text) or text[pos] != "{":
        raise ValueError("expected braced TeX group")
    start = pos + 1
    depth = 1
    pos += 1
    while pos < len(text):
        c = text[pos]
        if c == "\\":
            pos += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos], pos + 1
        pos += 1
    raise ValueError("unterminated TeX group")


def iter_tex_commands(text, command):
    needle = "\\" + command
    pos = 0
    while True:
        pos = text.find(needle, pos)
        if pos == -1:
            return
        after = pos + len(needle)
        if after < len(text) and (text[after].isalpha() or text[after] == "*"):
            pos = after
            continue
        yield pos, after
        pos = after


def compact_text(text, strip=False):
    text = text.translate(SUPER_DIGITS)
    text = text.replace("``", '"').replace("''", '"')
    text = text.replace("—", "—")
    text = re.sub(r"\\(?:nl|par)\b", "\n", text)
    text = re.sub(r"\\(?:God|LORD)\b", lambda m: m.group(0)[1:], text)
    text = re.sub(r"\\begin\{[^}]+\}|\\end\{[^}]+\}", "\n", text)
    previous = None
    while previous != text:
        previous = text
        text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)
        text = re.sub(r"\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\([{}%&#_$])", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\s+|$)", " ", text)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return apply_strip(text, strip)


def parse_tex_file(path, strip=False):
    raw = Path(path).read_text(encoding="utf-8")
    text = strip_tex_comments(raw)
    chapter_matches = list(iter_tex_commands(text, "Chapter"))
    if not chapter_matches:
        raise ValueError(f"no TeX chapter found in {path}")
    chapter_value, chapter_end = read_braced(text, chapter_matches[0][1])
    verses = []
    for _, after in iter_tex_commands(text[chapter_end:], "Verse"):
        offset_after = chapter_end + after
        number_value, pos = read_braced(text, offset_after)
        groups = []
        for _ in range(3):
            group, pos = read_braced(text, pos)
            groups.append(group)
        try:
            number = int(number_value.strip())
        except ValueError:
            number = compact_text(number_value, strip=True)
        hebrew, english, commentary = groups
        verses.append(
            {
                "number": number,
                "text": compact_text(english, strip),
                "hebrew": compact_text(hebrew, strip),
                "commentary": compact_text(commentary, strip),
            }
        )
    if not verses:
        raise ValueError(f"no TeX verses found in {path}")
    chapter_id = chapter_id_for(Path(path))
    chapter_number = chapter_number_for(chapter_id)
    if isinstance(chapter_number, str):
        stripped_chapter = compact_text(chapter_value, strip=True)
        chapter_number = int(stripped_chapter) if stripped_chapter.isdigit() else stripped_chapter
    return {
        "id": chapter_id,
        "number": chapter_number,
        "part": chapter_part_for(chapter_id),
        "verses": verses,
    }


def parse_tex(path, strip=False):
    return collect_books(find_files(path, ".tex"), parse_tex_file, strip)


def collect_books(files, parser, strip):
    books = {}
    errors = []
    for path in files:
        try:
            chapter = parser(path, strip=strip)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        book_id = book_id_for(path)
        books.setdefault(
            book_id,
            {"id": book_id, "name": book_name_for(book_id), "chapters": []},
        )["chapters"].append(chapter)
    if not books:
        detail = "\n".join(errors[:10])
        raise ValueError("no parseable files found" + (f":\n{detail}" if detail else ""))
    for book in books.values():
        book["chapters"].sort(key=lambda ch: chapter_sort_key(Path(ch["id"])))
    return {"books": [books[k] for k in sorted(books)]}


def dump_json(data):
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
