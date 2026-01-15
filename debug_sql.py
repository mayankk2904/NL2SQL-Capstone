# debug_sql.py - Updated for Ollama
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

load_dotenv()

# Test Ollama SQL generation
try:
    from app.ollama_service import ollama_service
    print("Ollama service imported")
    print(f"Using model: {ollama_service.model}")
    
    # Test questions
    test_questions = [
        "How many students are there?",
        "Show all students in Data Science class",
        "What is the average marks?",
        "List students sorted by marks",
        "Find students with marks above 80",
        "Count students in each class",
        "Show top 5 students by marks",
        "What is the highest marks in Data Science?",
        "List all students with their class and marks",
        "Find average marks for each section"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        try:
            sql = ollama_service.generate_sql(question)
            print(f"Generated SQL: {sql}")
        except Exception as e:
            print(f"Error: {e}")
            
except ImportError as e:
    print(f"Import error: {e}")
    print("\nChecking files...")
    
    # List app directory
    app_dir = Path(__file__).parent / "app"
    if app_dir.exists():
        print(f"App directory: {app_dir}")
        for file in app_dir.iterdir():
            print(f"  - {file.name}")