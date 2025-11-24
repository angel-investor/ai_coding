@echo off
title Cardiovascular Disease Prediction System

set PY=D:\software\Anaconda\envs\cardioenv\python.exe

:menu
cls
echo.
echo ========================================
echo   Cardiovascular Disease Prediction
echo ========================================
echo.
echo   1. Install Dependencies
echo   2. Configure API Keys
echo   3. Train XGBoost Model
echo   4. Start Prediction Server
echo   5. Generate Analysis Report
echo   6. Start Voice QA System
echo   7. Test Voice QA
echo   8. Check Environment
echo   0. Exit
echo.
echo ========================================
echo.

set /p choice=Enter number: 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto config
if "%choice%"=="3" goto train
if "%choice%"=="4" goto server
if "%choice%"=="5" goto report
if "%choice%"=="6" goto voiceqa
if "%choice%"=="7" goto testqa
if "%choice%"=="8" goto check
if "%choice%"=="0" goto end

echo Invalid option
timeout /t 2 >nul
goto menu

:install
cls
echo.
echo Installing dependencies...
echo.
"%PY%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo Done
pause
goto menu

:config
cls
echo.
echo Configuring API Keys...
echo.
call 配置API_KEY.bat
goto menu

:train
cls
echo.
echo Training XGBoost model...
echo This may take a few minutes...
echo.
"%PY%" model/train_xgb.py
echo.
echo Done
pause
goto menu

:server
cls
echo.
echo Starting prediction server...
echo Prediction page: http://localhost:5000/web/predict.html
echo Press Ctrl+C to stop
echo.
"%PY%" run_server.py
pause
goto menu

:report
cls
echo.
echo Generating report...
echo.
"%PY%" scripts/generate_report.py
echo.
echo Done
pause
goto menu

:voiceqa
cls
echo.
echo Starting Voice QA System...
echo Web page: http://localhost:5000/web/qa_audio.html
echo Press Ctrl+C to stop
echo.
"%PY%" run_server.py
pause
goto menu

:testqa
cls
echo.
echo Testing Voice QA System...
echo.
"%PY%" test_qa_audio.py
echo.
echo Done
pause
goto menu

:check
cls
echo.
echo Checking environment...
echo.
echo Python version:
"%PY%" --version
echo.
echo Checking packages:
"%PY%" -c "import flask" 2>nul && echo Flask OK || echo Flask not installed
"%PY%" -c "import xgboost" 2>nul && echo XGBoost OK || echo XGBoost not installed
"%PY%" -c "import sklearn" 2>nul && echo sklearn OK || echo sklearn not installed
"%PY%" -c "import pandas" 2>nul && echo pandas OK || echo pandas not installed
echo.
echo Checking files:
if exist .env (echo .env exists) else (echo .env not found)
if exist model\xgb_model.pkl (echo Model exists) else (echo Model not found)
echo.
pause
goto menu

:end
cls
echo.
echo Thank you
timeout /t 2 >nul
exit

