from pydantic import BaseModel
from typing import Optional, List

# Student schemas
class StudentBase(BaseModel):
    name: str
    class_name: str
    section: str
    marks: int

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    
    class Config:
        from_attributes = True

# Query schemas
class NLQuery(BaseModel):
    question: str

class SQLResponse(BaseModel):
    sql_query: str
    result: List[tuple]
    explanation: Optional[str] = None