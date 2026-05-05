@echo off
setlocal
cd /d "%~dp0"

set "PY_CMD="

py -3.12 -c "import sys" >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3.12"

if not defined PY_CMD (
    py -3.11 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py -3.11"
)

if not defined PY_CMD (
    py -3.10 -c "import sys" >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py -3.10"
)

if not defined PY_CMD (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo Python 3.10.8 or newer is required on the build PC.
    exit /b 1
)

%PY_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10, 8) else 1)"
if errorlevel 1 (
    echo Python 3.10.8 or newer is required on the build PC.
    exit /b 1
)

%PY_CMD% -m venv .venv-build
call .venv-build\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python installer\build_app.py
