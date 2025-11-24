@echo off
chcp 65001 >nul
echo ========================================
echo 安装项目依赖包
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 使用 Python 解释器: %PYTHON_PATH%
echo.

echo 正在安装依赖包...
"%PYTHON_PATH%" -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.

pause

