from app.models import Student

def test_student_model():
    """Test Student model creation"""
    student = Student(
        name="Test Student",
        class_name="Test Class",
        section="T",
        marks=85
    )
    
    assert student.name == "Test Student"
    assert student.class_name == "Test Class"
    assert student.section == "T"
    assert student.marks == 85
    assert student.id is None  # Not set until persisted
    
    # Test __repr__ method
    repr_str = repr(student)
    assert "Student" in repr_str
    assert "Test Student" in repr_str
    assert "Test Class" in repr_str
    assert "85" in repr_str

def test_student_table_name():
    """Test that table name is correctly set"""
    assert Student.__tablename__ == "students"

def test_student_columns():
    """Test that all columns are defined"""
    columns = Student.__table__.columns
    column_names = {col.name for col in columns}
    
    expected_columns = {"id", "name", "class_name", "section", "marks"}
    assert column_names == expected_columns
    
    # Test column types
    id_col = Student.__table__.c.id
    assert str(id_col.type) == "INTEGER"
    assert id_col.primary_key
    
    name_col = Student.__table__.c.name
    assert str(name_col.type) == "VARCHAR(100)"
    assert not name_col.nullable
    
    marks_col = Student.__table__.c.marks
    assert str(marks_col.type) == "INTEGER"
    assert not marks_col.nullable