#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -d "$ROOT/src" ] || ROOT="$(dirname "$ROOT")"
cd "$ROOT"

if [ ! -x .venv/bin/python ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
fi

PYTHONPATH=src .venv/bin/python -m jira_analytics.main --config config.ini "$@"