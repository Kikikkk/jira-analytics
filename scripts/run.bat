@echo off
setlocal
set "ROOT=%~dp0"
if not exist "%ROOT%src" set "ROOT=%~dp0..\"
cd /d "%ROOT%"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv || goto :error
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)

set "PYTHONPATH=src"
".venv\Scripts\python.exe" -m jira_analytics.main --config config.ini %*
exit /b %ERRORLEVEL%

:error
echo Setup failed. Check that Python 3.10+ is installed and available in PATH.
exit /b 1