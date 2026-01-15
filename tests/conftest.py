import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from typing import Generator
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(scope="session")
def create_tables(engine):
    """Create all tables for testing"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, create_tables):
    """Create a fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# Mock for OllamaService to avoid actual API calls during tests
@pytest.fixture
def mock_ollama_service(monkeypatch):
    """Mock the OllamaService for testing"""
    from app.ollama_service import OllamaService
    
    class MockOllamaService:
        def __init__(self, model=None):
            self.model = model or "llama3.2:3b"
            self.base_url = "http://localhost:11434"
            
        def generate_sql(self, question):
            # Return mock SQL based on question
            question_lower = question.lower()
            if "count" in question_lower or "how many" in question_lower:
                return "SELECT COUNT(*) FROM students"
            elif "average" in question_lower:
                return "SELECT AVG(marks) FROM students"
            elif "highest" in question_lower or "maximum" in question_lower:
                return "SELECT * FROM students ORDER BY marks DESC LIMIT 1"
            elif "devops" in question_lower:
                return "SELECT * FROM students WHERE class_name = 'DevOps'"
            else:
                return "SELECT * FROM students LIMIT 5"
        
        def explain_query(self, sql_query, result):
            return f"Mock explanation for query: {sql_query}"
        
        def test_connection(self):
            return True
    
    monkeypatch.setattr('app.ollama_service.ollama_service', MockOllamaService())
    monkeypatch.setattr('app.main.ollama_service', MockOllamaService())
    
    return MockOllamaService()