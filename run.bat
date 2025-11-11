@echo off
REM EHR Chatbot Run Script for Windows

echo 🩺 Starting EHR Medical Chatbot...
echo.

REM Check if .env file exists
if not exist .env (
    echo ⚠️  Warning: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo 📝 Please edit .env file and add your OPENAI_API_KEY
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python3 -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python3 -m pip install -q -r requirements.txt

REM Run API server in background
echo.
echo 🚀 Starting API server...
start "EHR Chatbot API" cmd /k "python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 2 /nobreak >nul

REM Run Streamlit app
echo.
echo ✅ Starting Streamlit application...
echo 🌐 Streamlit UI: http://localhost:8501
echo 🔌 API Server: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.

streamlit run main.py
