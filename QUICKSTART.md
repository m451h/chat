# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Prerequisites
- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Step 1: Install

```bash
# Clone or extract the project
cd ehr_chatbot

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

Or manually create `.env`:
```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./ehr_chatbot.db
```

### Step 3: Run

```bash
streamlit run main.py
```

The app will open automatically at `http://localhost:8501`

## 📱 Using the Application

### 1. Select a Demo User
Choose one of the test users:
- **علی احمدی**: Has diabetes + hypertension
- **فاطمه محمدی**: Has hypertension
- **حسین رضایی**: Has asthma

### 2. Select a Condition
Click on any condition button in the right sidebar (e.g., "دیابت نوع دو")

### 3. Read Educational Content
The chatbot will generate comprehensive educational content about the selected condition

### 4. Ask Questions
Type your questions in Persian, such as:
- "آیا باید دارو را قبل از غذا مصرف کنم؟"
- "چه غذاهایی برای من مناسب است؟"
- "علائم هشداردهنده چیست؟"

### 5. Browse History
Click on previous chat sessions in the sidebar to continue old conversations

## 🎯 Example Workflows

### Workflow 1: New Diabetes Patient Education
1. Select "علی احمدی" user
2. Click "دیابت نوع دو" condition
3. Read the comprehensive educational note
4. Ask: "متفورمین چطور باید مصرف شود؟"
5. Get personalized answer based on user's data

### Workflow 2: Continuing Previous Conversation
1. Select user and condition
2. Click on a previous session from history
3. Continue the conversation from where you left off

## 🔧 Customization

### Add Your Own Condition

1. Create a JSON file in `mock_data/`:
```json
{
  "condition_name": "نام بیماری به فارسی",
  "condition_name_en": "condition_english_name",
  "patient_data": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

2. Update `mock_data/backend.py`:
```python
mock_conditions = {
    1234567890123: [
        {
            "name": "نام بیماری",
            "name_en": "condition_english_name",
            "data_file": "condition_english_name.json"
        }
    ]
}
```

3. Restart the application

### Change OpenAI Model Settings

Edit `.env`:
```
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

## 🐛 Troubleshooting

### "OPENAI_API_KEY is required"
**Solution**: Make sure `.env` file exists and contains your API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### "ModuleNotFoundError"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Persian text displays incorrectly
**Solution**: The app includes RTL CSS. Make sure you're using a browser that supports RTL layout (Chrome, Firefox, Safari).

### Slow responses
**Possible causes**:
- Network connection to OpenAI
- Large conversation history (reduce MAX_CONVERSATION_HISTORY in .env)
- API rate limits

**Solution**: Check your internet connection and OpenAI API status

### Database locked error
**Solution**: Close other instances of the application or delete `ehr_chatbot.db` to reset

## 📚 Next Steps

- **Read README.md**: Complete project overview
- **Read DEVELOPMENT.md**: Architecture and advanced customization
- **Read DEPLOYMENT.md**: Production deployment guide

## 🆘 Need Help?

Check the documentation:
- [README.md](README.md) - Project overview
- [DEVELOPMENT.md](DEVELOPMENT.md) - Developer guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

## 🎉 Success!

You're now running a production-ready medical educational chatbot! The system is:
- ✅ Generating personalized educational content
- ✅ Answering questions in Persian
- ✅ Saving conversation history
- ✅ Supporting multiple conditions per user
- ✅ Streaming responses for better UX

**Enjoy building amazing patient education experiences!** 🩺
