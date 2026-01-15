import os
import tempfile
from pathlib import Path
from unittest.mock import patch

def test_settings_defaults():
    """Test that Settings has default values"""
    from app.config import Settings
    
    with patch.dict(os.environ, {}, clear=True):
        settings = Settings()
        assert settings.OLLAMA_MODEL == "llama3.2:3b"
        assert settings.OLLAMA_BASE_URL == "http://localhost:11434"

def test_settings_from_env():
    """Test that Settings reads from environment variables"""
    test_env = {
        "DATABASE_URL": "postgresql://test:test@localhost/testdb",
        "OLLAMA_MODEL": "test-model",
        "OLLAMA_BASE_URL": "http://test:11434"
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        from app.config import Settings
        settings = Settings()
        assert settings.DATABASE_URL == test_env["DATABASE_URL"]
        assert settings.OLLAMA_MODEL == test_env["OLLAMA_MODEL"]
        assert settings.OLLAMA_BASE_URL == test_env["OLLAMA_BASE_URL"]

def test_env_file_loading():
    """Test loading from .env file"""
    # Creating a temporary .env file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("DATABASE_URL=postgresql://envfile:test@localhost/testdb\n")
        f.write("OLLAMA_MODEL=env-model\n")
        env_file = f.name
    
    try:
        with patch('app.config.load_dotenv') as mock_load_dotenv:
            import importlib
            import app.config
            importlib.reload(app.config)
            
            mock_load_dotenv.assert_called()
    finally:
        # Clean up
        Path(env_file).unlink()