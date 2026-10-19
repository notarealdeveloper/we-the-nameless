#!/usr/bin/env python3
"""Run LaTeX until its cross-references settle, without hiding compiler errors."""
import argparse
import re
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command:
        parser.error("a LaTeX command is required")
    for attempt in range(1, 6):
        result = subprocess.run(args.command)
        if result.returncode:
            return result.returncode
        log = args.log.read_text()
        # TeX can wrap warning text at max_print_line; normalize whitespace.
        log = re.sub(r"-\s*\n\s*", "-", log)
        log = " ".join(log.split())
        rerun = any(message in log for message in (
            "Rerun to get cross-references right",
            "Rerun to get outlines right",
            "There were undefined references",
            "Rerun to get /PageLabels entry",
        ))
        if not rerun:
            return 0
        if attempt < 5:
            print("LaTeX references need another pass; rerunning.", flush=True)
    print("LaTeX references did not settle after 5 passes; see " + str(args.log),
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
