"""Small, dependency-free ANSI helpers used by object reprs."""
from __future__ import annotations

import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

_COLOR: ContextVar[bool] = ContextVar(
    "yhwh_color",
    default=os.environ.get("NO_COLOR") is None and os.environ.get("YHWH_COLOR", "1") != "0",
)

RESET = "\x1b[0m"
LIGHT_GREY = "\x1b[90m"
RED = "\x1b[31m"
BLUE = "\x1b[34m"
CYAN = "\x1b[36m"


def color_enabled() -> bool:
    return _COLOR.get()


def set_color(enabled: bool) -> bool:
    """Set repr coloring for the current context and return the previous value."""
    old = _COLOR.get()
    _COLOR.set(bool(enabled))
    return old


@contextmanager
def color(enabled: bool) -> Iterator[None]:
    token = _COLOR.set(bool(enabled))
    try:
        yield
    finally:
        _COLOR.reset(token)


def paint(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if color_enabled() else text
