"""Expose the print assembly to source readers without executing any TeX."""
import re


def expand_history(body, root):
    marker = r"\input{10-dudetheyreontome/contents}"
    if marker not in body:
        return body
    return body.replace(marker, (root / "10-dudetheyreontome/contents.tex").read_text())


def history_layers_as_parts(body):
    return re.sub(r"\\History(?:Addition|Source)\{([^}]+)\}",
                  lambda m: r"\BookPart{" + m[1] + "}", body)
