from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    class Config:
        env_file = ".env"

settings = Settings()