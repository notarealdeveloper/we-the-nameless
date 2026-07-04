#!/usr/bin/env -S fontforge -script
"""Compatibility wrapper for the old chronology renamer.

The chronology manifest now also owns fontconfig metadata, so the real
implementation lives in update_fonts_ascii_metadata.py.
"""

from __future__ import annotations

import os
import runpy


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "tools", "update_fonts_ascii_metadata.py")

runpy.run_path(SCRIPT, run_name="__main__")
