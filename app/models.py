from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    class_name = Column(String(50), nullable=False)  # Using class_name instead of class
    section = Column(String(10), nullable=False)
    marks = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<Student(name='{self.name}', class='{self.class_name}', marks={self.marks})>"