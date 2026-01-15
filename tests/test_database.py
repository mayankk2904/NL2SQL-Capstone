import pytest
from sqlalchemy.exc import SQLAlchemyError
from unittest.mock import Mock, patch
from app.database import get_db, SessionLocal, engine, Base

def test_engine_creation():
    """Test database engine creation"""
    assert engine is not None
    assert str(engine.url) == "sqlite:///:memory:"

def test_session_local():
    """Test SessionLocal configuration"""
    assert SessionLocal is not None
    assert SessionLocal.kw['autocommit'] is False
    assert SessionLocal.kw['autoflush'] is False

def test_base_declarative():
    """Test SQLAlchemy Base declarative"""
    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'metadata')

def test_get_db_generator():
    """Test get_db dependency generator"""
    # Mocking a session
    mock_session = Mock()
    
    # Create a context manager mock
    class MockSessionLocal:
        def __init__(self):
            self.session = mock_session
        
        def __call__(self):
            return self
        
        def __enter__(self):
            return self.session
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    # Test with mocked SessionLocal
    original_SessionLocal = SessionLocal
    try:
        import app.database
        app.database.SessionLocal = MockSessionLocal()
        
        db_gen = get_db()
        db = next(db_gen)
        
        assert db == mock_session
        
        try:
            next(db_gen)
        except StopIteration:
            pass
            
    finally:
        app.database.SessionLocal = original_SessionLocal

def test_get_db_exception_handling():
    """Test get_db handles exceptions properly"""
    mock_session = Mock()
    mock_session.close = Mock()
    
    class MockSessionLocal:
        def __init__(self):
            pass
        
        def __call__(self):
            return self
        
        def __enter__(self):
            raise SQLAlchemyError("Test error")
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            return False
    
    original_SessionLocal = SessionLocal
    try:
        import app.database
        app.database.SessionLocal = MockSessionLocal()
        
        with pytest.raises(SQLAlchemyError):
            db_gen = get_db()
            next(db_gen)
            
    finally:
        app.database.SessionLocal = original_SessionLocal