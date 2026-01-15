# app/gemini_service.py - UPDATED for new package
try:
    import google.genai as genai  # New package
    from google.genai import types  # For new API
    USE_NEW_API = True
except ImportError:
    # Fallback to old package if needed
    import google.generativeai as genai
    USE_NEW_API = False

from app.config import settings
from typing import List
import time

class GeminiService:
    def __init__(self):
        if USE_NEW_API:
            # New API configuration
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            self.model_name = "gemini-2.5-flash"
        else:
            # Old API configuration
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Enhanced prompt for better SQL generation
        self.prompt = """
        You are an expert SQL developer. Convert the following natural language question into a PostgreSQL SQL query.
        
        Database Schema:
        Table: students
        Columns:
        - id (integer, primary key)
        - name (varchar(100))
        - class_name (varchar(50))
        - section (varchar(10))
        - marks (integer)
        
        Important Instructions:
        1. Return ONLY the SQL query, no explanations, no markdown formatting
        2. Use PostgreSQL syntax
        3. Never use backticks (```) in the output
        4. Always use table name "students" (lowercase)
        5. Use column names exactly as shown above
        6. For class filter, use column "class_name"
        7. Make the query efficient and safe
        
        Examples:
        Question: "How many students are there?"
        SQL: SELECT COUNT(*) FROM students;
        
        Question: "Show all students in Data Science class"
        SQL: SELECT * FROM students WHERE class_name = 'Data Science';
        
        Question: "Which student has the highest marks?"
        SQL: SELECT * FROM students ORDER BY marks DESC LIMIT 1;
        
        Question: "What is the average marks in DevOps class?"
        SQL: SELECT AVG(marks) FROM students WHERE class_name = 'DevOps';
        
        Question: "List all students sorted by name"
        SQL: SELECT * FROM students ORDER BY name ASC;
        
        Now convert this question:
        """
    
    def generate_sql(self, natural_language_query: str) -> str:
        """Convert natural language to SQL query"""
        try:
            full_prompt = self.prompt + f"\nQuestion: {natural_language_query}\nSQL:"
            
            if USE_NEW_API:
                # New API call
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt
                )
                sql_query = response.text.strip()
            else:
                # Old API call
                response = self.model.generate_content(full_prompt)
                sql_query = response.text.strip()
            
            # Clean up the response
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1]
                
            return sql_query
            
        except Exception as e:
            raise Exception(f"Error generating SQL: {str(e)}")
    
    def explain_query(self, sql_query: str, result: List[tuple]) -> str:
        """Generate explanation for the query result"""
        explanation_prompt = f"""
        Explain the following SQL query and its result in simple terms:
        
        SQL Query: {sql_query}
        
        Query Result: {result}
        
        Provide a brief 1-2 sentence explanation of what this query does and what the result means.
        """
        
        try:
            if USE_NEW_API:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=explanation_prompt
                )
            else:
                response = self.model.generate_content(explanation_prompt)
                
            return response.text
            
        except Exception as e:
            print(f"Warning: Could not generate explanation: {e}")
            return "Explanation not available."

# Create global instance
gemini_service = GeminiService()