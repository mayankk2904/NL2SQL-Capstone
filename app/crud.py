# app/crud.py - UPDATED
from sqlalchemy.orm import Session
from sqlalchemy import text  # IMPORT THIS
from app import models, schemas
from typing import List, Optional
import re

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(
        name=student.name,
        class_name=student.class_name,
        section=student.section,
        marks=student.marks
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()

def execute_sql_query(db: Session, sql_query: str):
    """
    Execute raw SQL query safely with SQLAlchemy text() wrapper
    """
    try:
        # Clean the SQL query
        sql_query = sql_query.strip()
        
        # Basic security check
        query_upper = sql_query.upper()
        
        # Only allow SELECT queries for safety
        if not query_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed for security reasons")
        
        # Check for dangerous keywords
        forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT']
        for keyword in forbidden_keywords:
            if keyword in query_upper:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")
        
        # Remove trailing semicolon if present
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        
        # Execute with text() wrapper
        result = db.execute(text(sql_query))
        rows = result.fetchall()
        
        # Convert to list of tuples
        return [tuple(row) for row in rows]
        
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")