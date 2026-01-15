import sys
import subprocess
import os

def run_tests():
    """Run pytest with coverage report"""
    print("Running tests with coverage report...")
    print("=" * 60)
    
    # Set test environment variables
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['OLLAMA_MODEL'] = 'test-model'
    os.environ['OLLAMA_BASE_URL'] = 'http://test:11434'
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=app",  # Coverage for app module
        "--cov-report=term-missing:skip-covered",  # Show only missing lines
        "--cov-report=html",  # Generate HTML report
        "--cov-report=xml",  # Generate XML report
        "--cov-fail-under=85",  # Fail if coverage below 85%
        "-v",  # Verbose output
        "--tb=short"  # Shorter traceback
    ]
    
    result = subprocess.run(cmd)
    
    print("\n" + "=" * 60)
    
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print(f"✗ Tests failed with exit code: {result.returncode}")
    
    print("\nCoverage reports generated:")
    print("1. HTML report: htmlcov/index.html")
    print("2. XML report: coverage.xml")
    
    try:
        if sys.platform == "win32":
            os.startfile("htmlcov/index.html")
        elif sys.platform == "darwin":
            subprocess.run(["open", "htmlcov/index.html"])
        else:
            subprocess.run(["xdg-open", "htmlcov/index.html"])
    except:
        pass  
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())