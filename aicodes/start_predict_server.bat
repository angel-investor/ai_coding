@echo off
chcp 65001 >nul
echo ========================================
echo 启动预测服务器
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 使用 Python: %PYTHON_PATH%
echo.

echo 启动服务器...
echo 访问地址: http://localhost:5000/web/predict.html
echo 按 Ctrl+C 停止服务器
echo.

"%PYTHON_PATH%" run_server.py

pause

