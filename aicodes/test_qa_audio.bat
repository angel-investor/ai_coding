@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo    Test AI Voice QA System
echo ============================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found: %PYTHON_PATH%
    pause
    exit /b 1
)

cd /d "%~dp0"
"%PYTHON_PATH%" test_qa_audio.py

pause

