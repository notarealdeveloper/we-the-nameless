#!/usr/bin/env python3
"""Strict, dependency-free EPUB package/XHTML/link validator."""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import uuid
import zipfile
from pathlib import PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET

CONTAINER = "META-INF/container.xml"
NS = {
    "c": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub")
    args = parser.parse_args()
    errors: list[str] = []
    with zipfile.ZipFile(args.epub) as archive:
        names = archive.namelist()
        name_set = set(names)
        if not names or names[0] != "mimetype":
            fail(errors, "mimetype must be the first ZIP member")
        if archive.read("mimetype") != b"application/epub+zip":
            fail(errors, "invalid mimetype payload")
        if archive.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            fail(errors, "mimetype must be stored without compression")
        try:
            container = ET.fromstring(archive.read(CONTAINER))
            rootfile = container.find(".//c:rootfile", NS)
            opf_path = rootfile.attrib["full-path"] if rootfile is not None else ""
            package = ET.fromstring(archive.read(opf_path))
        except (KeyError, ET.ParseError) as exc:
            fail(errors, f"invalid container/package XML: {exc}")
            opf_path, package = "", None
        manifest_paths: set[str] = set()
        nav_path = ""
        if package is not None:
            opf_dir = posixpath.dirname(opf_path)
            identifiers = package.findall(".//{http://purl.org/dc/elements/1.1/}identifier")
            unique = package.attrib.get("unique-identifier")
            if not unique or not any(item.attrib.get("id") == unique for item in identifiers):
                fail(errors, "package unique-identifier does not resolve")
            if len(identifiers) != 1 or not (identifiers[0].text or "").strip():
                fail(errors, "package must contain exactly one non-empty publication identifier")
            else:
                identifier = (identifiers[0].text or "").strip()
                if not identifier.startswith("urn:uuid:"):
                    fail(errors, "publication identifier must be a stable urn:uuid")
                else:
                    try:
                        uuid.UUID(identifier.removeprefix("urn:uuid:"))
                    except ValueError:
                        fail(errors, "publication identifier contains an invalid UUID")
            titles = package.findall(".//{http://purl.org/dc/elements/1.1/}title")
            languages = package.findall(".//{http://purl.org/dc/elements/1.1/}language")
            if not any((item.text or "").strip() for item in titles):
                fail(errors, "package has no title")
            if not any((item.text or "").strip() for item in languages):
                fail(errors, "package has no language")
            for item in package.findall(".//opf:manifest/opf:item", NS):
                href = unquote(item.attrib.get("href", ""))
                resolved = posixpath.normpath(posixpath.join(opf_dir, href))
                manifest_paths.add(resolved)
                if resolved not in name_set:
                    fail(errors, f"manifest resource is missing: {resolved}")
                if "nav" in item.attrib.get("properties", "").split():
                    nav_path = resolved
            for name in names:
                if name.startswith(("META-INF/",)) or name == "mimetype" or name.endswith("/"):
                    continue
                if name not in manifest_paths and name != opf_path:
                    fail(errors, f"unmanifested publication resource: {name}")
        document_ids: dict[str, set[str]] = {}
        document_roots: dict[str, ET.Element] = {}
        xhtml_paths = sorted(path for path in manifest_paths if path.endswith((".xhtml", ".html")))
        for path in xhtml_paths:
            try:
                raw_document = archive.read(path).decode("utf-8")
                root = ET.fromstring(raw_document)
            except ET.ParseError as exc:
                fail(errors, f"invalid XHTML {path}: {exc}")
                continue
            # MathML intentionally retains its TeX source annotation. Outside
            # that fallback, TeX commands and layout preambles are conversion
            # debris that readers would expose as ordinary text.
            visible_source = re.sub(
                r"<annotation\b[^>]*encoding=[\"']application/x-tex[\"'][^>]*>.*?</annotation>",
                "", raw_document, flags=re.DOTALL,
            )
            debris = re.search(
                r"\\(?:begin|end|boxed|frac|genfrac|hbox|raisebox|setlength)\b|"
                r"@p\{|\{[+-]?[0-9.]+(?:em|ex|pt)\}|"
                r"\bon background layer\b|\bnode\[|"
                r"\^\[|\{[lcr]\}\{[0-9.]+(?:\\linewidth)?\}|"
                r"\b[0-9.]+pt\{",
                visible_source,
            )
            if debris:
                fail(errors, f"visible TeX/layout debris in {path}: {debris.group(0)!r}")
            document_roots[path] = root
            ids: set[str] = set()
            for element in root.iter():
                element_id = element.attrib.get("id")
                if element_id:
                    if element_id in ids:
                        fail(errors, f"duplicate id {element_id!r} in {path}")
                    ids.add(element_id)
            document_ids[path] = ids
        for path, root in document_roots.items():
            base = posixpath.dirname(path)
            for element in root.iter():
                for attribute in ("href", "src"):
                    value = element.attrib.get(attribute)
                    if not value or urlsplit(value).scheme or value.startswith(("mailto:", "data:")):
                        continue
                    split = urlsplit(value)
                    target_path = posixpath.normpath(posixpath.join(base, unquote(split.path))) if split.path else path
                    if target_path not in name_set:
                        fail(errors, f"broken {attribute} in {path}: {value}")
                    elif split.fragment and target_path in document_ids and split.fragment not in document_ids[target_path]:
                        fail(errors, f"missing fragment in {path}: {value}")
                for value in element.attrib.values():
                    if re.search(r"(?:file:/{2,}|/home/|[A-Za-z]:\\\\)", value):
                        fail(errors, f"absolute filesystem path in {path}: {value}")
        if not nav_path:
            fail(errors, "manifest has no navigation document")
        elif nav_path in name_set:
            nav = ET.fromstring(archive.read(nav_path))
            epub_type = "{http://www.idpf.org/2007/ops}type"
            if not any("toc" in node.attrib.get(epub_type, "").split() for node in nav.iter()):
                fail(errors, "navigation document has no epub:type=toc")
    if errors:
        for error in errors:
            print(f"[validate] ERROR: {error}", file=sys.stderr)
        print(f"[validate] failed with {len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"[validate] valid package: {len(xhtml_paths)} XHTML documents, {len(manifest_paths)} resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
