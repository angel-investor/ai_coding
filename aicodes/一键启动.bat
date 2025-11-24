@echo off
chcp 65001 >nul
title 心血管疾病预测系统 - 一键启动

:menu
cls
echo ========================================
echo   心血管疾病预测系统 - 控制面板
echo ========================================
echo.
echo   Python 环境: cardioenv
echo   解释器路径: D:\software\Anaconda\envs\cardioenv\python.exe
echo.
echo ========================================
echo   请选择操作：
echo ========================================
echo.
echo   1. 安装依赖包
echo   2. 训练模型
echo   3. 启动服务器
echo   4. 生成数据分析报告
echo   5. 检查环境
echo   0. 退出
echo.
echo ========================================

set /p choice=请输入选项 0-5: 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto train
if "%choice%"=="3" goto server
if "%choice%"=="4" goto report
if "%choice%"=="5" goto check
if "%choice%"=="0" goto end

echo 无效的选项，请重新选择！
timeout /t 2 >nul
goto menu

:install
cls
echo ========================================
echo 安装依赖包
echo ========================================
call install_dependencies.bat
goto menu

:train
cls
echo ========================================
echo 训练模型
echo ========================================
call train_model.bat
goto menu

:server
cls
echo ========================================
echo 启动服务器
echo ========================================
call start_server.bat
goto menu

:report
cls
echo ========================================
echo 生成数据分析报告
echo ========================================
call generate_report.bat
goto menu

:check
cls
echo ========================================
echo 检查环境
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 检查 Python 版本...
"%PYTHON_PATH%" --version
echo.

echo 检查 Python 路径...
"%PYTHON_PATH%" -c "import sys; print('Python 路径:', sys.executable)"
echo.

echo 检查关键依赖包...
"%PYTHON_PATH%" -c "import flask; print('Flask 已安装')" 2>nul || echo Flask 未安装
"%PYTHON_PATH%" -c "import xgboost; print('XGBoost 已安装')" 2>nul || echo XGBoost 未安装
"%PYTHON_PATH%" -c "import sklearn; print('scikit-learn 已安装')" 2>nul || echo scikit-learn 未安装
"%PYTHON_PATH%" -c "import pandas; print('pandas 已安装')" 2>nul || echo pandas 未安装
"%PYTHON_PATH%" -c "import plotly; print('plotly 已安装')" 2>nul || echo plotly 未安装
echo.

echo 检查配置文件...
if exist .env (
    echo .env 文件存在
) else (
    echo .env 文件不存在，请从 env_template.txt 复制并重命名
)
echo.

echo 检查模型文件...
if exist model\xgb_model.pkl (
    echo 模型文件存在
) else (
    echo 模型文件不存在，请先训练模型
)
echo.

echo ========================================
pause
goto menu

:end
echo.
echo 感谢使用！再见！
timeout /t 2 >nul
exit

