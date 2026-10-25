@echo off
cd /d "%~dp0\.."
set PYTHONPATH=src
python -m jira_analytics.main --config config.ini
pause