@echo off
title 心血管疾病预测系统

set PYTHON=D:\software\Anaconda\envs\cardioenv\python.exe

:menu
cls
echo.
echo ========================================
echo   心血管疾病预测系统
echo ========================================
echo.
echo   1. 安装依赖包
echo   2. 训练模型
echo   3. 启动服务器
echo   4. 生成报告
echo   5. 检查环境
echo   0. 退出
echo.
echo ========================================
echo.

set /p choice=请输入数字: 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto train
if "%choice%"=="3" goto server
if "%choice%"=="4" goto report
if "%choice%"=="5" goto check
if "%choice%"=="0" goto end

echo 无效选项
timeout /t 2 >nul
goto menu

:install
cls
echo.
echo 正在安装依赖包...
echo.
"%PYTHON%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo 完成
pause
goto menu

:train
cls
echo.
echo 正在训练模型...
echo.
"%PYTHON%" scripts/train_model.py
echo.
echo 完成
pause
goto menu

:server
cls
echo.
echo 正在启动服务器...
echo 访问地址: http://localhost:5000/web
echo 按 Ctrl+C 停止
echo.
"%PYTHON%" scripts/run_server.py
pause
goto menu

:report
cls
echo.
echo 正在生成报告...
echo.
"%PYTHON%" scripts/generate_report.py
echo.
echo 完成
pause
goto menu

:check
cls
echo.
echo 检查环境...
echo.
echo Python版本:
"%PYTHON%" --version
echo.
echo 检查依赖:
"%PYTHON%" -c "import flask" 2>nul && echo Flask OK || echo Flask 未安装
"%PYTHON%" -c "import xgboost" 2>nul && echo XGBoost OK || echo XGBoost 未安装
"%PYTHON%" -c "import sklearn" 2>nul && echo sklearn OK || echo sklearn 未安装
"%PYTHON%" -c "import pandas" 2>nul && echo pandas OK || echo pandas 未安装
echo.
echo 检查文件:
if exist .env (echo .env 存在) else (echo .env 不存在)
if exist model\xgb_model.pkl (echo 模型存在) else (echo 模型不存在)
echo.
pause
goto menu

:end
cls
echo.
echo 谢谢使用
timeout /t 2 >nul
exit

