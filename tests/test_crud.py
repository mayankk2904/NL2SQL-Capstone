import pytest
from app import crud, schemas
from sqlalchemy.exc import IntegrityError

def test_create_student(db_session):
    """Test creating a student"""
    student_data = schemas.StudentCreate(
        name="John Doe",
        class_name="Data Science",
        section="A",
        marks=85
    )
    
    student = crud.create_student(db_session, student_data)
    
    assert student.id is not None
    assert student.name == "John Doe"
    assert student.class_name == "Data Science"
    assert student.section == "A"
    assert student.marks == 85

def test_get_students_empty(db_session):
    """Test getting students from empty database"""
    students = crud.get_students(db_session)
    assert students == []
    assert len(students) == 0

def test_get_students_with_data(db_session):
    """Test getting students with data"""
    # Create test students
    student1 = schemas.StudentCreate(
        name="Alice", class_name="DevOps", section="B", marks=90
    )
    student2 = schemas.StudentCreate(
        name="Bob", class_name="Data Science", section="A", marks=88
    )
    
    crud.create_student(db_session, student1)
    crud.create_student(db_session, student2)
    
    # Test get all students
    students = crud.get_students(db_session)
    assert len(students) == 2
    assert students[0].name in ["Alice", "Bob"]
    assert students[1].name in ["Alice", "Bob"]
    
    students = crud.get_students(db_session, skip=1, limit=1)
    assert len(students) == 1

def test_execute_sql_query_select(db_session):
    """Test executing a valid SELECT query"""
    # First create a student
    student_data = schemas.StudentCreate(
        name="Test Student",
        class_name="Test Class",
        section="T",
        marks=100
    )
    crud.create_student(db_session, student_data)
    
    # Test SELECT query
    result = crud.execute_sql_query(db_session, "SELECT * FROM students")
    assert isinstance(result, list)
    assert len(result) == 1
    
    # Test SELECT with WHERE
    result = crud.execute_sql_query(
        db_session, 
        "SELECT name, marks FROM students WHERE class_name = 'Test Class'"
    )
    assert len(result) == 1
    assert result[0][0] == "Test Student"
    assert result[0][1] == 100

def test_execute_sql_query_count(db_session):
    """Test executing COUNT query"""
    # Create multiple students
    for i in range(3):
        student = schemas.StudentCreate(
            name=f"Student {i}",
            class_name=f"Class {i % 2}",
            section="A",
            marks=70 + i
        )
        crud.create_student(db_session, student)
    
    result = crud.execute_sql_query(db_session, "SELECT COUNT(*) FROM students")
    assert result == [(3,)]

def test_execute_sql_query_invalid():
    """Test executing invalid SQL queries"""
    import pytest
    from sqlalchemy.orm import Session
    
    # Mock session
    class MockSession:
        def execute(self, query):
            raise Exception("Test error")
    
    session = MockSession()
    
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        crud.execute_sql_query(session, "DELETE FROM students")
    
    with pytest.raises(ValueError, match="Query contains forbidden keyword"):
        crud.execute_sql_query(session, "SELECT * FROM students; DROP TABLE students")
    
    with pytest.raises(Exception, match="Error executing query"):
        crud.execute_sql_query(session, "SELECT * FROM non_existent_table")

def test_execute_sql_query_security(db_session):
    """Test SQL injection protection"""
    # Test with semicolon
    query = "SELECT * FROM students;"
    result = crud.execute_sql_query(db_session, query)
    
    query = "SELECT * FROM students /* ; DROP TABLE students */"
    result = crud.execute_sql_query(db_session, query)
    assert isinstance(result, list)