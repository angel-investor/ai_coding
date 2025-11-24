@echo off
chcp 65001 >nul
echo ========================================
echo 训练心血管疾病预测模型
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 使用 Python 解释器: %PYTHON_PATH%
echo.

echo 开始训练模型...
"%PYTHON_PATH%" scripts/train_model.py

echo.
echo ========================================
echo 训练完成！
echo ========================================
echo.

pause

