import pytest
from pydantic import ValidationError
from app import schemas

def test_student_create_valid():
    """Test valid StudentCreate schema"""
    student = schemas.StudentCreate(
        name="John Doe",
        class_name="Data Science",
        section="A",
        marks=85
    )
    
    assert student.name == "John Doe"
    assert student.class_name == "Data Science"
    assert student.section == "A"
    assert student.marks == 85

def test_student_create_invalid():
    """Test invalid StudentCreate schema"""
    # Test missing required field
    with pytest.raises(ValidationError):
        schemas.StudentCreate(
            name="John Doe",
            class_name="Data Science",
            # Missing section and marks
        )
    
    # Test invalid marks (negative)
    with pytest.raises(ValidationError):
        schemas.StudentCreate(
            name="John Doe",
            class_name="Data Science",
            section="A",
            marks=-10
        )
    
    # Test invalid marks (not integer)
    with pytest.raises(ValidationError):
        schemas.StudentCreate(
            name="John Doe",
            class_name="Data Science",
            section="A",
            marks="not_a_number" 
        )

def test_student_response():
    """Test StudentResponse schema"""
    student = schemas.StudentResponse(
        id=1,
        name="Jane Doe",
        class_name="Cloud Computing",
        section="B",
        marks=92
    )
    
    assert student.id == 1
    assert student.name == "Jane Doe"
    assert student.class_name == "Cloud Computing"
    assert student.section == "B"
    assert student.marks == 92
    
    assert student.Config.from_attributes is True

def test_nlquery_schema():
    """Test NLQuery schema"""
    query = schemas.NLQuery(question="How many students are there?")
    assert query.question == "How many students are there?"
    
    with pytest.raises(ValidationError):
        schemas.NLQuery(question="")

def test_sqlresponse_schema():
    """Test SQLResponse schema"""
    response = schemas.SQLResponse(
        sql_query="SELECT * FROM students",
        result=[(1, "John", "DS", "A", 85), (2, "Jane", "CC", "B", 92)],
        explanation="This query retrieves all students."
    )
    
    assert response.sql_query == "SELECT * FROM students"
    assert len(response.result) == 2
    assert response.explanation == "This query retrieves all students."
    
    response = schemas.SQLResponse(
        sql_query="SELECT COUNT(*) FROM students",
        result=[(5,)]
    )
    assert response.sql_query == "SELECT COUNT(*) FROM students"
    assert response.result == [(5,)]
    assert response.explanation is None