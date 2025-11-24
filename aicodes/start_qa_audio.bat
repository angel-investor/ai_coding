@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo    AI Voice QA System Startup
echo ============================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

if not exist "%PYTHON_PATH%" (
    echo [ERROR] Python not found: %PYTHON_PATH%
    echo Please check your Python path
    pause
    exit /b 1
)

echo [INFO] Starting Flask server...
echo [INFO] API Endpoint: http://localhost:5000/qa_audio
echo [INFO] Web Interface: http://localhost:5000/web/qa_audio.html
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
"%PYTHON_PATH%" run_server.py

pause

