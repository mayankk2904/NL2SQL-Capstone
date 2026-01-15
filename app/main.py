from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from app import schemas, crud, models
from app.database import engine, get_db
# from app.gemini_service import gemini_service
from app.ollama_service import ollama_service

# Creating database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Natural Language to SQL API (Ollama)",
    description="Convert natural language questions to SQL queries using Ollama LLM",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Check Ollama connection on startup"""
    print("Checking Ollama connection...")
    if ollama_service.test_connection():
        print("Ollama connected successfully!")
    else:
        print("Warning: Ollama not connected. /query endpoint may fail.")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Natural Language to SQL API",
        "description": "Using Ollama LLM for SQL generation",
        "endpoints": {
            "/": "This documentation",
            "/students/": "Get all students",
            "/students/create": "Create new student (POST)",
            "/query/": "Convert natural language to SQL and execute (POST)",
            "/test-sql/": "Test SQL query execution (POST)",
            "/health": "Health check with Ollama status",
            "/count": "Get student count directly",
            "/ollama-status": "Check Ollama connection status"
        }
    }

@app.get("/ollama-status")
def get_ollama_status():
    """Check Ollama connection and model info"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "connected",
                "models": [m["name"] for m in models],
                "current_model": ollama_service.model,
                "base_url": ollama_service.base_url
            }
        else:
            return {"status": "error", "message": "Cannot reach Ollama"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/students/", response_model=List[schemas.StudentResponse])
def get_all_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students

@app.post("/students/create", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)

@app.post("/test-sql/")
def test_sql_query(query: str, db: Session = Depends(get_db)):
    """
    Direct SQL query testing endpoint
    """
    try:
        result = crud.execute_sql_query(db, query)
        return {
            "query": query,
            "result": result,
            "row_count": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/count")
def get_student_count(db: Session = Depends(get_db)):
    """
    Direct endpoint to get student count
    """
    try:
        result = db.execute(text("SELECT COUNT(*) FROM students"))
        count = result.scalar()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check
    """
    health_status = {
        "api": "running",
        "database": "unknown",
        "ollama": "unknown",
        "student_count": 0
    }
    
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        
        result = db.execute(text("SELECT COUNT(*) FROM students"))
        health_status["student_count"] = result.scalar()
        
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            health_status["ollama"] = "connected"
        else:
            health_status["ollama"] = "error"
    except:
        health_status["ollama"] = "not_connected"
    
    return health_status

@app.post("/query/", response_model=schemas.SQLResponse)
def natural_language_to_sql(
    query: schemas.NLQuery, 
    db: Session = Depends(get_db),
    model: Optional[str] = Query(None, description="Optional: Specify Ollama model to use")
):

    try:
        print(f"Processing question: {query.question}")
        
        if model:
            # Use specified model
            from app.ollama_service import OllamaService
            temp_service = OllamaService(model=model)
            sql_query = temp_service.generate_sql(query.question)
        else:
            sql_query = ollama_service.generate_sql(query.question)
        
        print(f"Generated SQL: {sql_query}")
        
        result = crud.execute_sql_query(db, sql_query)
        print(f"Query returned {len(result)} rows")
        
        if model:
            explanation = temp_service.explain_query(sql_query, result)
        else:
            explanation = ollama_service.explain_query(sql_query, result)
        
        return {
            "sql_query": sql_query,
            "result": result,
            "explanation": explanation,
            "row_count": len(result),
            "model_used": model or ollama_service.model
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")