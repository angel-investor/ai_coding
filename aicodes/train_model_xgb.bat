@echo off
chcp 65001 >nul
echo ========================================
echo 训练 XGBoost 模型
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 使用 Python: %PYTHON_PATH%
echo.

echo 开始训练模型...
echo 这可能需要几分钟，请耐心等待...
echo.

"%PYTHON_PATH%" model/train_xgb.py

echo.
echo ========================================
echo 训练完成
echo ========================================
echo.

pause

