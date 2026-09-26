"""Expose the print assembly to source readers without executing any TeX."""
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expand_history(body, root):
    marker = r"\input{10-dudetheyreontome/contents}"
    if marker not in body:
        return body
    return body.replace(marker, (root / "10-dudetheyreontome/contents.tex").read_text())


def history_layers_as_parts(body):
    return re.sub(r"\\History(?:Addition|Source)\{([^}]+)\}",
                  lambda m: r"\BookPart{" + m[1] + "}", body)


def prepare_include_dirs(master, output_dir):
    body = expand_history(master.read_text(), ROOT)
    for include in re.findall(r"^[ \t]*\\include\{([^}]+)\}", body, re.MULTILINE):
        (output_dir / Path(include).parent).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Prepare chapter aux directories without running TeX.")
    parser.add_argument("master", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    prepare_include_dirs(args.master, args.output_dir)
