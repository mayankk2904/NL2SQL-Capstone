import pytest
from fastapi import status
from unittest.mock import Mock, patch, MagicMock
import json

def test_startup_event_mocked(client, monkeypatch):
    """Test startup_event function"""
    mock_test_connection = Mock(return_value=True)
    monkeypatch.setattr('app.main.ollama_service.test_connection', mock_test_connection)
    
    mock_test_connection.assert_not_called()
    
    with patch('builtins.print') as mock_print:
        from app.main import startup_event
        startup_event()
        mock_print.assert_any_call("Checking Ollama connection...")
        mock_test_connection.assert_called_once()

def test_read_root_endpoint(client):
    """Test root endpoint documentation"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert "message" in data
    assert "description" in data
    assert "endpoints" in data
    assert "/students/" in data["endpoints"]
    assert "/query/" in data["endpoints"]

def test_get_ollama_status_success(client, monkeypatch):
    """Test Ollama status endpoint success"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.2:3b"},
            {"name": "mistral"}
        ]
    }
    
    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr('app.main.requests.get', mock_get)
    
    response = client.get("/ollama-status")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "connected"
    assert "llama3.2:3b" in data["models"]
    assert "mistral" in data["models"]
    assert data["current_model"] == "llama3.2:3b"
    mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

def test_get_ollama_status_error(client, monkeypatch):
    """Test Ollama status endpoint error"""
    mock_get = Mock(side_effect=Exception("Connection failed"))
    monkeypatch.setattr('app.main.requests.get', mock_get)
    
    response = client.get("/ollama-status")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "error"
    assert "Connection failed" in data["message"]

def test_get_all_students_with_params(client, db_session):
    """Test get students with skip and limit parameters"""
    # Creating 5 test students
    for i in range(5):
        client.post("/students/create", json={
            "name": f"Student {i}",
            "class_name": f"Class {i % 2}",
            "section": "A",
            "marks": 70 + i
        })
    
    response = client.get("/students/?skip=2&limit=2")
    assert response.status_code == status.HTTP_200_OK
    students = response.json()
    assert len(students) == 2
    
    # Test with default parameters
    response = client.get("/students/")
    assert response.status_code == status.HTTP_200_OK
    students = response.json()
    assert len(students) == 5

def test_create_student_endpoint(client):
    """Test student creation endpoint"""
    student_data = {
        "name": "Endpoint Test",
        "class_name": "Endpoint Class",
        "section": "E",
        "marks": 88
    }
    
    response = client.post("/students/create", json=student_data)
    assert response.status_code == status.HTTP_200_OK
    
    created = response.json()
    assert created["name"] == student_data["name"]
    assert created["class_name"] == student_data["class_name"]
    assert created["section"] == student_data["section"]
    assert created["marks"] == student_data["marks"]
    assert "id" in created

def test_test_sql_endpoint_comprehensive(client, db_session):
    """Comprehensive test for SQL testing endpoint"""
    client.post("/students/create", json={
        "name": "SQL Test",
        "class_name": "SQL Class",
        "section": "S",
        "marks": 95
    })
    
    test_queries = [
        ("SELECT * FROM students", 1),
        ("SELECT name, marks FROM students", 1),
        ("SELECT COUNT(*) FROM students", 1),
        ("SELECT AVG(marks) FROM students", 1),
    ]
    
    for sql_query, expected_rows in test_queries:
        response = client.post("/test-sql/", params={"query": sql_query})
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["query"] == sql_query
        assert data["row_count"] == expected_rows
        assert "result" in data

def test_test_sql_endpoint_injection_attempt(client):
    """Test SQL injection attempts are blocked"""
    malicious_queries = [
        "DELETE FROM students",
        "DROP TABLE students",
        "INSERT INTO students VALUES (1, 'test', 'test', 'A', 100)",
        "UPDATE students SET marks = 100",
        "SELECT * FROM students; DELETE FROM students",
    ]
    
    for query in malicious_queries:
        response = client.post("/test-sql/", params={"query": query})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_student_count_endpoint(client, db_session):
    """Test student count endpoint"""
    db_session.query(db_session.get_bind().__class__).delete()
    db_session.commit()
    
    response = client.get("/count")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 0
    
    for i in range(3):
        client.post("/students/create", json={
            "name": f"Count Test {i}",
            "class_name": "Count Class",
            "section": "C",
            "marks": 75
        })
    
    response = client.get("/count")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 3

def test_health_check_comprehensive(client, monkeypatch):
    """Comprehensive health check test"""
    # Mock database connection
    mock_db = Mock()
    mock_db.execute = Mock(return_value=Mock(scalar=Mock(return_value=5)))
    
    # Mock requests for Ollama check
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get = Mock(return_value=mock_response)
    
    monkeypatch.setattr('app.main.requests.get', mock_get)
    
    # We need to mock the database dependency
    def mock_get_db():
        yield mock_db
    
    # Temporarily override the dependency
    from app.main import app, get_db as original_get_db
    app.dependency_overrides[original_get_db] = mock_get_db
    
    try:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["api"] == "running"
        assert data["database"] == "connected"
        assert data["ollama"] == "connected"
        assert data["student_count"] == 5
        
    finally:
        # Clean up
        app.dependency_overrides.clear()

def test_health_check_database_error(client, monkeypatch):
    """Test health check with database error"""
    # Mock database to raise exception
    mock_db = Mock()
    mock_db.execute = Mock(side_effect=Exception("DB connection failed"))
    
    def mock_get_db():
        yield mock_db
    
    from app.main import app, get_db as original_get_db
    app.dependency_overrides[original_get_db] = mock_get_db
    
    try:
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["database"] == "error: DB connection failed"
        assert data["ollama"] == "unknown"  
        
    finally:
        app.dependency_overrides.clear()

def test_health_check_ollama_error(client, monkeypatch):
    """Test health check with Ollama error"""
    mock_get = Mock(side_effect=Exception("Ollama not running"))
    monkeypatch.setattr('app.main.requests.get', mock_get)
    
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["ollama"] == "not_connected"

def test_natural_language_to_sql_success(client, monkeypatch, db_session):
    """Test successful NL to SQL conversion"""
    # Create test data
    client.post("/students/create", json={
        "name": "Query Student",
        "class_name": "DevOps",
        "section": "D",
        "marks": 85
    })
    
    # Mock Ollama service
    mock_service = Mock()
    mock_service.generate_sql = Mock(return_value="SELECT * FROM students WHERE class_name = 'DevOps'")
    mock_service.explain_query = Mock(return_value="This query finds DevOps students.")
    mock_service.model = "llama3.2:3b"
    
    monkeypatch.setattr('app.main.ollama_service', mock_service)
    
    query_data = {"question": "Show me DevOps students"}
    response = client.post("/query/", json=query_data)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["sql_query"] == "SELECT * FROM students WHERE class_name = 'DevOps'"
    assert data["explanation"] == "This query finds DevOps students."
    assert data["model_used"] == "llama3.2:3b"
    assert data["row_count"] >= 0

def test_natural_language_to_sql_custom_model(client, monkeypatch):
    """Test NL to SQL with custom model parameter"""
    mock_service_instance = Mock()
    mock_service_instance.generate_sql = Mock(return_value="SELECT COUNT(*) FROM students")
    mock_service_instance.explain_query = Mock(return_value="Counts all students.")
    mock_service_instance.model = "custom-model"
    
    mock_service_class = Mock(return_value=mock_service_instance)
    monkeypatch.setattr('app.main.OllamaService', mock_service_class)
    
    query_data = {"question": "How many students?"}
    response = client.post("/query/?model=custom-model", json=query_data)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["model_used"] == "custom-model"
    mock_service_class.assert_called_once_with(model="custom-model")

def test_natural_language_to_sql_validation_error(client):
    """Test NL to SQL with validation error"""
    query_data = {"question": ""}
    response = client.post("/query/", json=query_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_natural_language_to_sql_value_error(client, monkeypatch):
    """Test NL to SQL with ValueError (e.g., non-SELECT query)"""
    mock_service = Mock()
    mock_service.generate_sql = Mock(return_value="DELETE FROM students")
    
    mock_execute = Mock(side_effect=ValueError("Only SELECT queries are allowed"))
    
    monkeypatch.setattr('app.main.ollama_service', mock_service)
    monkeypatch.setattr('app.main.crud.execute_sql_query', mock_execute)
    
    query_data = {"question": "Delete all students"}
    response = client.post("/query/", json=query_data)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only SELECT queries are allowed" in response.json()["detail"]

def test_natural_language_to_sql_general_error(client, monkeypatch):
    """Test NL to SQL with general exception"""
    mock_service = Mock()
    mock_service.generate_sql = Mock(side_effect=Exception("Ollama service unavailable"))
    
    monkeypatch.setattr('app.main.ollama_service', mock_service)
    
    query_data = {"question": "Some question"}
    response = client.post("/query/", json=query_data)
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error processing query" in response.json()["detail"]

def test_cors_middleware(client):
    """Test CORS middleware is configured"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in [h.lower() for h in response.headers]

def test_create_tables_on_startup():
    """Test that tables are created on startup"""

    from app.database import Base, engine
    

    assert len(Base.metadata.tables) > 0
    assert "students" in Base.metadata.tables
    

    try:
        Base.metadata.create_all(bind=engine)
        assert True
    except Exception as e:
        pytest.fail(f"Failed to create tables: {e}")