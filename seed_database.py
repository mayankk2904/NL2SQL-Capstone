import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules
try:
    from app.database import SessionLocal, engine
    from app import models, schemas
    from app.crud import create_student
    print("Successfully imported modules")
except ImportError as e:
    print(f"Import error: {e}")
    print("\nChecking project structure...")
    
    # List files to debug
    current_dir = Path(__file__).parent
    print(f"Current directory: {current_dir}")
    if (current_dir / "app").exists():
        print("App folder exists")
        print("Files in app folder:")
        for file in (current_dir / "app").iterdir():
            print(f"  - {file.name}")
    sys.exit(1)


def seed_database():
    # Create tables first
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Sample data
        students_data = [
            {"name": "Krish", "class_name": "Data Science", "section": "A", "marks": 90},
            {"name": "Sudhanshu", "class_name": "Data Science", "section": "B", "marks": 100},
            {"name": "Darius", "class_name": "Data Science", "section": "A", "marks": 86},
            {"name": "Vikash", "class_name": "DEVOPS", "section": "A", "marks": 50},
            {"name": "Dipesh", "class_name": "DEVOPS", "section": "A", "marks": 35},
            {"name": "Amit", "class_name": "Machine Learning", "section": "C", "marks": 95},
            {"name": "Priya", "class_name": "Machine Learning", "section": "B", "marks": 88},
            {"name": "Raj", "class_name": "Web Development", "section": "A", "marks": 75},
            {"name": "Sneha", "class_name": "Web Development", "section": "C", "marks": 92},
            {"name": "Rohan", "class_name": "Data Science", "section": "B", "marks": 78},
            {"name": "Neha Sharma", "class_name": "Data Science", "section": "C", "marks": 85},
            {"name": "Ravi Kumar", "class_name": "Machine Learning", "section": "A", "marks": 88},
            {"name": "Sonia Patel", "class_name": "DEVOPS", "section": "B", "marks": 72},
            {"name": "Arun Singh", "class_name": "Web Development", "section": "A", "marks": 65},
            {"name": "Priyanka Gupta", "class_name": "Data Science", "section": "A", "marks": 95},
            {"name": "Vikram Yadav", "class_name": "Machine Learning", "section": "B", "marks": 78},
            {"name": "Anjali Mishra", "class_name": "DEVOPS", "section": "C", "marks": 82},
            {"name": "Rahul Verma", "class_name": "Web Development", "section": "B", "marks": 91},
            {"name": "Pooja Reddy", "class_name": "Data Science", "section": "B", "marks": 87},
            {"name": "Sanjay Joshi", "class_name": "Machine Learning", "section": "C", "marks": 79},
            {"name": "Meera Nair", "class_name": "DEVOPS", "section": "A", "marks": 68},
            {"name": "Kunal Bose", "class_name": "Web Development", "section": "C", "marks": 84},
            {"name": "Ananya Das", "class_name": "Data Science", "section": "A", "marks": 93},
            {"name": "Rohit Malhotra", "class_name": "Machine Learning", "section": "B", "marks": 81},
            {"name": "Swati Choudhury", "class_name": "DEVOPS", "section": "B", "marks": 77},
        ]
        
        print(f"Seeding {len(students_data)} students...")
        
        # Clear existing data first
        db.query(models.Student).delete()
        db.commit()
        
        # Add students to database
        for i, student_data in enumerate(students_data, 1):
            student = schemas.StudentCreate(**student_data)
            db_student = create_student(db, student)
            if i % 5 == 0 or i == len(students_data):
                print(f"   {i}. Added {db_student.name} - {db_student.class_name} ({db_student.section})")
        
        db.commit()
        print("\nDatabase seeded successfully!")
        print(f"Total students: {len(students_data)}")
        print(f"Class distribution:")
        
        # Show distribution
        from sqlalchemy import func
        distribution = db.query(
            models.Student.class_name,
            func.count(models.Student.id).label('count'),
            func.avg(models.Student.marks).label('avg_marks')
        ).group_by(models.Student.class_name).all()
        
        for class_name, count, avg_marks in distribution:
            print(f"   - {class_name}: {count} students, Avg marks: {avg_marks:.1f}")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database seeding...")
    seed_database()