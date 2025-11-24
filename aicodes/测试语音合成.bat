@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo    Test CosyVoice Speech Synthesis
echo ============================================
echo.

set PY=D:\software\Anaconda\envs\cardioenv\python.exe

echo Running tests...
echo.

"%PY%" test_cosyvoice.py

echo.
echo ============================================
pause

