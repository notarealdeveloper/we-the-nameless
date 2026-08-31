"""Runtime settings and path discovery."""
from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Iterator

_NIQQUD: ContextVar[bool] = ContextVar("yhwh_niqqud", default=False)


def get_niqqud() -> bool:
    """Whether Hebrew operations currently distinguish niqqud (default: False)."""
    return _NIQQUD.get()


def set_niqqud(enabled: bool) -> bool:
    """Set global/context-local niqqud behavior and return the previous value."""
    old = _NIQQUD.get()
    _NIQQUD.set(bool(enabled))
    return old


@contextmanager
def niqqud(enabled: bool = True) -> Iterator[None]:
    """Temporarily change niqqud sensitivity."""
    token = _NIQQUD.set(bool(enabled))
    try:
        yield
    finally:
        _NIQQUD.reset(token)


def cache_dir(path: str | os.PathLike[str] | None = None) -> Path:
    if path is not None:
        result = Path(path).expanduser()
    elif value := os.environ.get("YHWH_CACHE_DIR"):
        result = Path(value).expanduser()
    elif value := os.environ.get("XDG_CACHE_HOME"):
        result = Path(value).expanduser() / "yhwh"
    else:
        result = Path.home() / ".cache" / "yhwh"
    result.mkdir(parents=True, exist_ok=True)
    return result


def clean_cache(path: str | os.PathLike[str] | None = None) -> Path:
    target = cache_dir(path)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    return target


def find_corpus(path: str | os.PathLike[str] | None = None) -> Path:
    """Find a TeX corpus root.

    Resolution order: explicit argument, ``WE_THE_NAMELESS``, ``YHWH_CORPUS``,
    then the current directory. A root is accepted when it contains at least one
    book chapter matching ``[01][0-9]-*/*.tex``.
    """
    candidates: list[Path] = []
    if path is not None:
        candidates.append(Path(path).expanduser())
    if value := os.environ.get("WE_THE_NAMELESS"):
        candidates.append(Path(value).expanduser())
    if value := os.environ.get("YHWH_CORPUS"):
        candidates.append(Path(value).expanduser())
    cwd = Path.cwd()
    candidates.append(cwd)
    checked: list[str] = []
    for candidate in candidates:
        candidate = candidate.resolve()
        if str(candidate) in checked:
            continue
        checked.append(str(candidate))
        if candidate.is_file() and candidate.suffix == ".tex":
            return candidate
        if candidate.is_dir() and next(candidate.glob("[01][0-9]-*/*.tex"), None) is not None:
            return candidate
    raise FileNotFoundError(
        "Could not find [01][0-9]-*/*.tex. Pass a path or set WE_THE_NAMELESS. Checked: "
        + ", ".join(checked)
    )


def find_dataset(path: str | os.PathLike[str] | None = None) -> Path:
    candidates: list[Path] = []
    if path is not None:
        candidates.append(Path(path).expanduser())
    if value := os.environ.get("YHWH_DATASET"):
        candidates.append(Path(value).expanduser())
    cwd = Path.cwd()
    candidates.extend(
        [cwd / "dataset" / "primary-history.jsonl.gz", cwd / "primary-history.jsonl.gz"]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError("Could not find a built dataset; pass a path or set YHWH_DATASET")
