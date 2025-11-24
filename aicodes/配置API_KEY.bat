@echo off
chcp 65001 >nul
setlocal

echo ============================================
echo    Configure API Keys
echo ============================================
echo.

set ENV_FILE=.env

echo Checking .env file...
if exist "%ENV_FILE%" (
    echo .env file already exists
    echo.
    choice /C YN /M "Do you want to overwrite it?"
    if errorlevel 2 goto end
    echo.
)

echo Creating .env file...
echo.

(
echo # DeepSeek API Configuration
echo DEEPSEEK_API_KEY=sk-52e226ac3cac46838cb282b45b1a648e
echo DEEPSEEK_API_URL=https://api.deepseek.com/v1
echo MODEL=deepseek-chat
echo.
echo # CosyVoice Configuration
echo COSYVOICE_APPKEY=your_cosyvoice_appkey_here
echo COSYVOICE_TOKEN=your_cosyvoice_token_here
echo COSYVOICE_TIMEOUT=30
echo COSYVOICE_MAX_RETRIES=3
echo.
echo # Model Configuration
echo MODEL_PATH=./model/xgb_model.pkl
echo DATA_PATH=D:/project/workspace/ai_coding/data/心血管疾病.xlsx
echo.
echo # Flask Configuration
echo FLASK_HOST=0.0.0.0
echo FLASK_PORT=5000
echo FLASK_DEBUG=False
echo.
echo # Logging Configuration
echo LOG_LEVEL=INFO
echo LOG_DIR=./logs
) > "%ENV_FILE%"

echo.
echo [SUCCESS] .env file created successfully!
echo.
echo File location: %CD%\%ENV_FILE%
echo.
echo IMPORTANT:
echo 1. The DeepSeek API Key is already configured
echo 2. If you need CosyVoice, please edit .env and add your keys
echo 3. You can edit .env with any text editor
echo.
echo Next steps:
echo 1. Restart the server: start_predict_server.bat
echo 2. Test voice QA: http://localhost:5000/web/qa_audio.html
echo.

:end
pause

