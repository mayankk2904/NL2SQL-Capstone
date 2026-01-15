import requests
import sys
import time

def test_ollama_setup():
    print("Testing Ollama Setup")
    print("=" * 50)
    
    # Test 1: Check if Ollama is running
    print("1. Checking Ollama service...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"   Ollama is running!")
            print(f"   Available models: {[m['name'] for m in models]}")
        else:
            print(f"   Ollama returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   Cannot connect to Ollama. Is it running?")
        print("   Run: ollama serve")
        return False
    
    # Test 2: Test SQL generation
    print("\n2. Testing SQL generation...")
    try:
        test_prompt = "Convert to SQL: How many students are there? Table: students"
        payload = {
            "model": "llama3.2:3b",
            "prompt": test_prompt,
            "stream": False,
            "options": {"temperature": 0.1}
        }
        
        start = time.time()
        response = requests.post("http://localhost:11434/api/generate", 
                                json=payload, timeout=30)
        response_time = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            sql = result["response"].strip()
            print(f"   SQL generated in {response_time:.2f}s")
            print(f"   Response: {sql}")
        else:
            print(f"   Failed with status: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"   Error: {e}")
        return False
    
    # Test 3: Pull model if not available
    print("\n3. Checking if model is available...")
    try:
        models_response = requests.get("http://localhost:11434/api/tags")
        models = [m["name"] for m in models_response.json().get("models", [])]
        
        if "llama3.2:3b" not in models:
            print("   llama3.2:3b not found. Available models:")
            for model in models:
                print(f"     - {model}")
            print("\n   To pull the model, run: ollama pull llama3.2:3b")
        else:
            print("   llama3.2:3b model is available!")
    
    except Exception as e:
        print(f"   Error checking models: {e}")
    
    print("\n" + "=" * 50)
    print("Setup Summary:")
    print("Ollama service: Running" if response.status_code == 200 else "Ollama service: Not running")
    print("Next steps:")
    print("   1. Ensure ollama serve is running")
    print("   2. Run: python debug_sql.py")
    print("   3. Run: uvicorn app.main:app --reload")
    
    return True

if __name__ == "__main__":
    success = test_ollama_setup()
    sys.exit(0 if success else 1)