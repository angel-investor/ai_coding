@echo off
chcp 65001 >nul
title 心血管疾病预测系统

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

:menu
cls
echo ==========================================
echo   心血管疾病预测系统
echo ==========================================
echo.
echo   Python: cardioenv
echo.
echo ==========================================
echo   请选择操作
echo ==========================================
echo.
echo   1 - 安装依赖包
echo   2 - 训练模型
echo   3 - 启动服务器
echo   4 - 生成报告
echo   5 - 检查环境
echo   0 - 退出
echo.
echo ==========================================
echo.

set /p choice=请输入数字: 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto train
if "%choice%"=="3" goto server
if "%choice%"=="4" goto report
if "%choice%"=="5" goto check
if "%choice%"=="0" goto end

echo 无效选项！
timeout /t 2 >nul
goto menu

:install
cls
echo ==========================================
echo 安装依赖包
echo ==========================================
echo.
"%PYTHON_PATH%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo 安装完成！
pause
goto menu

:train
cls
echo ==========================================
echo 训练模型
echo ==========================================
echo.
"%PYTHON_PATH%" scripts/train_model.py
echo.
echo 训练完成！
pause
goto menu

:server
cls
echo ==========================================
echo 启动服务器
echo ==========================================
echo.
echo 访问地址: http://localhost:5000/web
echo 按 Ctrl+C 停止服务器
echo.
"%PYTHON_PATH%" scripts/run_server.py
pause
goto menu

:report
cls
echo ==========================================
echo 生成数据分析报告
echo ==========================================
echo.
"%PYTHON_PATH%" scripts/generate_report.py
echo.
echo 报告生成完成！
pause
goto menu

:check
cls
echo ==========================================
echo 检查环境
echo ==========================================
echo.

echo Python 版本:
"%PYTHON_PATH%" --version
echo.

echo Python 路径:
"%PYTHON_PATH%" -c "import sys; print(sys.executable)"
echo.

echo 检查依赖包:
"%PYTHON_PATH%" -c "import flask" 2>nul && echo Flask - OK || echo Flask - 未安装
"%PYTHON_PATH%" -c "import xgboost" 2>nul && echo XGBoost - OK || echo XGBoost - 未安装
"%PYTHON_PATH%" -c "import sklearn" 2>nul && echo scikit-learn - OK || echo scikit-learn - 未安装
"%PYTHON_PATH%" -c "import pandas" 2>nul && echo pandas - OK || echo pandas - 未安装
"%PYTHON_PATH%" -c "import plotly" 2>nul && echo plotly - OK || echo plotly - 未安装
echo.

echo 检查配置文件:
if exist .env (echo .env - 存在) else (echo .env - 不存在)
echo.

echo 检查模型文件:
if exist model\xgb_model.pkl (echo 模型文件 - 存在) else (echo 模型文件 - 不存在)
echo.

echo ==========================================
pause
goto menu

:end
cls
echo.
echo 感谢使用！
echo.
timeout /t 2 >nul
exit

