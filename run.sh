#!/bin/bash

# EHR Chatbot Run Script

echo "🩺 Starting EHR Medical Chatbot..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "📝 Please edit .env file and add your OPENAI_API_KEY"
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run Streamlit app
echo ""
echo "✅ Starting application..."
echo "🌐 Open your browser at: http://localhost:8501"
echo ""

streamlit run main.py
