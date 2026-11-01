#!/usr/bin/env bash
# First-time setup: create the project venv and install dependencies.
# Idempotent — safe to re-run; existing venv is reused.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x venv/bin/python ]; then
    echo "Creating virtualenv in ./venv ..."
    python3 -m venv venv
fi

venv/bin/pip install --upgrade pip
venv/bin/pip install "matchering==2.0.6"

echo "Done. Run: ./venv/bin/python master.py <file> <genre> [-f {24bit,16bit,mp3}]"
