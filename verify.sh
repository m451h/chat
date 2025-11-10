#!/bin/bash
# EHR Chatbot - Project Verification Script

echo "🔍 Verifying EHR Medical Chatbot Project..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0

# Check function
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        ((FAIL++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $1/ - MISSING"
        ((FAIL++))
    fi
}

echo "📁 Checking Directory Structure..."
check_dir "config"
check_dir "core"
check_dir "db"
check_dir "ui"
check_dir "mock_data"
echo ""

echo "📄 Checking Core Files..."
check_file "main.py"
check_file "requirements.txt"
check_file ".env.example"
check_file ".gitignore"
echo ""

echo "⚙️ Checking Config Files..."
check_file "config/__init__.py"
check_file "config/settings.py"
echo ""

echo "🧠 Checking Core Logic..."
check_file "core/__init__.py"
check_file "core/chatbot.py"
check_file "core/prompts.py"
echo ""

echo "💾 Checking Database Layer..."
check_file "db/__init__.py"
check_file "db/models.py"
check_file "db/operations.py"
echo ""

echo "🎨 Checking UI Components..."
check_file "ui/__init__.py"
check_file "ui/chat_interface.py"
check_file "ui/sidebar.py"
echo ""

echo "📊 Checking Mock Data..."
check_file "mock_data/__init__.py"
check_file "mock_data/backend.py"
check_file "mock_data/diabetes_type2.json"
check_file "mock_data/hypertension.json"
check_file "mock_data/asthma.json"
echo ""

echo "📚 Checking Documentation..."
check_file "README.md"
check_file "QUICKSTART.md"
check_file "DEVELOPMENT.md"
check_file "DEPLOYMENT.md"
check_file "PROJECT_SUMMARY.md"
echo ""

echo "🔧 Checking Run Scripts..."
check_file "run.sh"
check_file "run.bat"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Project is ready.${NC}"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Create .env file: cp .env.example .env"
    echo "  2. Add your OpenAI API key to .env"
    echo "  3. Install dependencies: pip install -r requirements.txt"
    echo "  4. Run application: streamlit run main.py"
    echo ""
    echo "📖 Documentation:"
    echo "  • QUICKSTART.md - 3-minute setup guide"
    echo "  • README.md - Complete overview"
    echo "  • DEVELOPMENT.md - Architecture details"
    echo "  • DEPLOYMENT.md - Production deployment"
    exit 0
else
    echo -e "${RED}❌ Some files are missing!${NC}"
    echo "Please check the project structure."
    exit 1
fi
