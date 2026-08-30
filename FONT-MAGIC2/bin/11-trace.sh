#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); PYTHONPATH="$ROOT" python3 "$ROOT/bin/run-stage.py" trace "$@"
