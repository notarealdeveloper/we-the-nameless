#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import os
import tarfile
from pathlib import Path

EXCLUDE = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist"}


def include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    return not any(part in EXCLUDE for part in relative.parts) and not path.name.endswith((".pyc", ".pyo"))


def archive(root: Path, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for path in sorted(root.rglob("*")):
                    if not include(path, root):
                        continue
                    arcname = Path("yhwh") / path.relative_to(root)
                    info = tar.gettarinfo(str(path), arcname=str(arcname))
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = 0
                    if path.is_file():
                        with path.open("rb") as handle:
                            tar.addfile(info, handle)
                    else:
                        tar.addfile(info)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args()
    target = args.output / "yhwh-0.1.0.tar.gz"
    print(archive(args.root.resolve(), target.resolve()))


if __name__ == "__main__":
    main()
