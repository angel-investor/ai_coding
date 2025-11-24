@echo off
chcp 65001 >nul
echo ========================================
echo 生成数据分析报告
echo ========================================
echo.

set PYTHON_PATH=D:\software\Anaconda\envs\cardioenv\python.exe

echo 使用 Python 解释器: %PYTHON_PATH%
echo.

echo 正在生成报告...
echo.
"%PYTHON_PATH%" scripts/generate_report.py

echo.
echo ========================================
echo 报告生成完成
echo ========================================
echo.
echo 报告位置: analysis\report.html
echo 请用浏览器打开查看
echo.

pause

