@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Drag your BCAT *-bcat-blacklist.json file onto this .bat file.
  echo For safest version selection, use the Python command in README.md with --system.
  pause
  exit /b 1
)
py -3 "%~dp0patch_blacklist.py" "%~1" --output "%~dp0payload.json"
if errorlevel 1 (
  echo.
  echo Python 3 must be installed, and payload.json must not already exist.
)
echo.
pause
