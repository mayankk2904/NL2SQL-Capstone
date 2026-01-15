import pytest
from unittest.mock import Mock, patch
from app.ollama_service import OllamaService

def test_ollama_service_init():
    """Test OllamaService initialization"""
    service = OllamaService()
    assert service.model == "llama3.2:3b"
    assert service.base_url == "http://localhost:11434"
    assert service.sql_prompt is not None
    assert "CRITICAL INSTRUCTIONS" in service.sql_prompt

def test_ollama_service_custom_model():
    """Test OllamaService with custom model"""
    service = OllamaService(model="custom-model")
    assert service.model == "custom-model"

@patch('app.ollama_service.requests.post')
def test_generate_sql_success(mock_post):
    """Test successful SQL generation"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "SELECT COUNT(*) FROM students"
    }
    mock_post.return_value = mock_response
    
    service = OllamaService()
    sql = service.generate_sql("How many students are there?")
    
    assert sql == "SELECT COUNT(*) FROM students"
    mock_post.assert_called_once()

@patch('app.ollama_service.requests.post')
def test_generate_sql_cleaning(mock_post):
    """Test SQL cleaning in generate_sql"""
    # Test with markdown in response
    test_cases = [
        ("```sql\nSELECT * FROM students\n```", "SELECT * FROM students"),
        ("SQL: SELECT COUNT(*) FROM students", "SELECT COUNT(*) FROM students"),
        ("SELECT * FROM students;", "SELECT * FROM students"),
        ("SELECT *\nFROM\nstudents", "SELECT * FROM students"),
    ]
    
    for response_text, expected in test_cases:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": response_text}
        mock_post.return_value = mock_response
        
        service = OllamaService()
        
        with patch.object(service, '_clean_sql', side_effect=service._clean_sql):
            sql = service.generate_sql("test question")
            cleaned = service._clean_sql(response_text)
            assert cleaned == expected

def test_clean_sql_method():
    """Test the _clean_sql method directly"""
    service = OllamaService()
    
    test_cases = [
        ("SELECT * FROM students", "SELECT * FROM students"),
        ("```sql\nSELECT * FROM students\n```", "SELECT * FROM students"),
        ("SQL: SELECT COUNT(*) FROM students", "SELECT COUNT(*) FROM students"),
        ("SELECT * FROM students;", "SELECT * FROM students"),
        ("SELECT *\nFROM\nstudents\nWHERE id = 1", "SELECT * FROM students WHERE id = 1"),
        ("Some text\nSQL: SELECT * FROM students\nMore text", "SELECT * FROM students"),
    ]
    
    for input_sql, expected in test_cases:
        result = service._clean_sql(input_sql)
        assert result == expected, f"Failed for input: {input_sql}"

@patch('app.ollama_service.requests.post')
def test_explain_query(mock_post):
    """Test query explanation generation"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "This query counts all students in the database."
    }
    mock_post.return_value = mock_response
    
    service = OllamaService()
    explanation = service.explain_query("SELECT COUNT(*) FROM students", [(5,)])
    
    assert "counts" in explanation.lower() or "students" in explanation.lower()
    mock_post.assert_called_once()

@patch('app.ollama_service.requests.get')
def test_test_connection_success(mock_get):
    """Test successful connection test"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": "llama3.2:3b"}]
    }
    mock_get.return_value = mock_response
    
    service = OllamaService()
    result = service.test_connection()
    
    assert result is True
    mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

@patch('app.ollama_service.requests.get')
def test_test_connection_failure(mock_get):
    """Test failed connection test"""
    mock_get.side_effect = Exception("Connection failed")
    
    service = OllamaService()
    result = service.test_connection()
    
    assert result is False

@patch('app.ollama_service.requests.post')
def test_generate_sql_api_error(mock_post):
    """Test SQL generation with API error"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    mock_post.return_value = mock_response
    
    service = OllamaService()
    
    with pytest.raises(Exception, match="Ollama API error"):
        service.generate_sql("test question")