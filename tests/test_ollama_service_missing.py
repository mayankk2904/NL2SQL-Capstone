import pytest
from unittest.mock import Mock, patch, MagicMock
from app.ollama_service import OllamaService
import requests

def test_generate_sql_timeout():
    """Test SQL generation timeout handling"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(Exception, match="Ollama request timed out"):
            service.generate_sql("test question")

def test_generate_sql_connection_error():
    """Test SQL generation connection error"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")
        
        with pytest.raises(Exception, match="Cannot connect to Ollama"):
            service.generate_sql("test question")

def test_generate_sql_api_error_with_text():
    """Test SQL generation with API error that has text"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        with pytest.raises(Exception, match="Ollama API error 500"):
            service.generate_sql("test question")

def test_explain_query_api_error():
    """Test explanation generation with API error"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = service.explain_query("SELECT * FROM students", [(1, "test", "class", "A", 100)])
        
        assert "Query returned" in result
        assert "SELECT * FROM students" in result

def test_explain_query_exception():
    """Test explanation generation with exception"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_post.side_effect = Exception("Some error")
        
        result = service.explain_query("SELECT COUNT(*) FROM students", [(5,)])
        
        assert "Query returned" in result
        assert "rows" in result

def test_explain_query_empty_result():
    """Test explanation with empty result"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "No data found"}
        mock_post.return_value = mock_response
        
        result = service.explain_query("SELECT * FROM students WHERE 1=0", [])
        
        assert result is not None

def test_test_connection_success_with_models():
    """Test connection test with models returned"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3.2:3b", "size": 1000},
                {"name": "mistral", "size": 2000}
            ]
        }
        mock_get.return_value = mock_response
        
        result = service.test_connection()
        
        assert result is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)

def test_test_connection_http_error():
    """Test connection test with HTTP error"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = service.test_connection()
        
        assert result is False

def test_generate_sql_with_options():
    """Test SQL generation includes correct options"""
    service = OllamaService()
    
    with patch('app.ollama_service.requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "SELECT * FROM students"}
        mock_post.return_value = mock_response
        
        service.generate_sql("test question")
        
        call_args = mock_post.call_args
        
        assert call_args is not None
        json_data = call_args[1]['json']
        
        assert "options" in json_data
        assert json_data["options"]["temperature"] == 0.1
        assert json_data["options"]["num_predict"] == 300
        assert json_data["stream"] is False

def test_clean_sql_edge_cases():
    """Test SQL cleaning with edge cases"""
    service = OllamaService()
    
    test_cases = [
        ("", ""),  # Empty string
        ("   ", ""),  # Only spaces
        ("SELECT", "SELECT"),  # Single word
        ("```\nSELECT\n```", "SELECT"),  # Only backticks
        ("SQL:\nSELECT", "SELECT"),  # SQL: at start
        ("Some text SQL: SELECT", "SELECT"),  # SQL: in middle
        ("SELECT *;", "SELECT *"),  # Multiple semicolons
        ("```sql\nSELECT *\nFROM students\nWHERE id=1\n```", "SELECT * FROM students WHERE id=1"),
    ]
    
    for input_sql, expected in test_cases:
        result = service._clean_sql(input_sql)
        assert result == expected, f"Failed for: '{input_sql}'"