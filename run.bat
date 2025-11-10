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
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Run Streamlit app
echo.
echo ✅ Starting application...
echo 🌐 Open your browser at: http://localhost:8501
echo.

streamlit run main.py
