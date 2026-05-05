#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON_BIN:-python3}"
"$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10, 8) else 1)' || {
    echo "Python 3.10.8 or newer is required on the build Mac."
    exit 1
}

"$PYTHON_BIN" -m venv .venv-build
. .venv-build/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python installer/build_app.py

if command -v open >/dev/null 2>&1; then
    open release
fi
