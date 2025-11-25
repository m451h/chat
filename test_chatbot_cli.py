"""
Test script for chatbot_cli.py
Run this to verify the CLI interface works correctly
"""
import json
import subprocess
import sys
from pathlib import Path

def test_health():
    """Test health check command"""
    print("Testing health check...")
    input_data = {"command": "health"}
    
    result = run_cli(input_data)
    if result and result.get("success"):
        print("✅ Health check passed")
        return True
    else:
        print("❌ Health check failed")
        return False

def test_generate_educational():
    """Test generate educational content"""
    print("\nTesting generate educational content...")
    input_data = {
        "command": "generate_educational",
        "treatment_plan_name": "دیابت نوع 2",
        "condition_data": {
            "age": 45,
            "gender": "male"
        },
        "session_id": 0
    }
    
    result = run_cli(input_data)
    if result and result.get("success"):
        message = result.get("message", "")
        print(f"✅ Generated message (first 100 chars): {message[:100]}...")
        return True
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print(f"❌ Failed: {error}")
        return False

def test_chat():
    """Test chat command"""
    print("\nTesting chat...")
    input_data = {
        "command": "chat",
        "question": "سلام",
        "session_id": 123,
        "conversation_history": None,
        "condition_data": None
    }
    
    result = run_cli(input_data)
    if result and result.get("success"):
        answer = result.get("answer", "")
        print(f"✅ Chat response (first 100 chars): {answer[:100]}...")
        return True
    else:
        error = result.get("error", "Unknown error") if result else "No response"
        print(f"❌ Failed: {error}")
        return False

def run_cli(input_data):
    """Run chatbot_cli.py with input data"""
    script_path = Path(__file__).parent / "core" / "chatbot_cli.py"
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        json_input = json.dumps(input_data, ensure_ascii=False)
        stdout, stderr = process.communicate(input=json_input, timeout=120)
        
        if process.returncode != 0:
            print(f"Error output: {stderr}")
            return None
        
        return json.loads(stdout)
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Testing chatbot_cli.py")
    print("=" * 50)
    
    # Check if OPENAI_API_KEY is set
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set. Some tests may fail.")
        print()
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Generate Educational", test_generate_educational()))
    results.append(("Chat", test_chat()))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

