@echo off
chcp 65001 > NUL
set PYTHONUTF8=1
set PYTHONIOENCODING=utf8
cd "%~dp0"
setlocal enabledelayedexpansion

set DEBUG_MODE=0

call src\variables.bat

python src\start.py
if "%DEBUG_MODE%"=="1" (
    echo Script finished. Press any key to exit...
    pause > nul
)
