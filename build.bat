@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Build GitHub Hotboard

where python >nul 2>nul
if errorlevel 1 goto nopy

echo [1/2] Installing dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 goto nopip

echo [2/2] Building...
python build.py
echo.
pause
exit /b

:nopy
echo.
echo   Python not found.
echo   Install Python 3.10+ and tick "Add python.exe to PATH".
echo   https://www.python.org/downloads/
echo.
pause
exit /b 1

:nopip
echo.
echo   Failed to install dependencies. Check your network or run manually:
echo     python -m pip install -r requirements.txt
echo.
pause
exit /b 1
