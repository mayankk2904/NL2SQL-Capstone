import requests
import json
from typing import List, Optional
import time
from app.config import settings

class OllamaService:
    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_BASE_URL
        
        self.sql_prompt = """You are an expert SQL developer. Convert the natural language question to PostgreSQL SQL query.

Database Schema:
Table: students
Columns:
- id (integer, primary key)
- name (varchar(100))
- class_name (varchar(50))
- section (varchar(10))
- marks (integer)

CRITICAL INSTRUCTIONS:
1. If the question asks about tables/columns NOT in the schema, return: "ERROR: Table not found in schema"
2. Only generate SQL if the question matches the available schema
3. Return ONLY the SQL query, nothing else
4. No explanations, no markdown formatting
5. Never use backticks (```) in output
6. Always use table name "students" (lowercase)
7. Use exact column names: name, class_name, section, marks
8. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP)
9. Make queries efficient and safe

EXAMPLES:
Question: "How many students are there?"
SQL: SELECT COUNT(*) FROM students

Question: "Show all students in Data Science class"
SQL: SELECT * FROM students WHERE class_name = 'Data Science'

Question: "Which student has the highest marks?"
SQL: SELECT * FROM students ORDER BY marks DESC LIMIT 1

Question: "What is the average marks in DevOps class?"
SQL: SELECT AVG(marks) FROM students WHERE class_name = 'DevOps'

Question: "List students sorted by name"
SQL: SELECT * FROM students ORDER BY name ASC

NOW CONVERT THIS QUESTION:
"""
    
    def generate_sql(self, natural_language_query: str) -> str:
        """Convert natural language to SQL query using Ollama"""
        try:
            full_prompt = f"{self.sql_prompt}\nQuestion: {natural_language_query}\nSQL:"
            
            # Prepare request to Ollama
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1, 
                    "num_predict": 300,  
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            print(f"Calling Ollama with model: {self.model}")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            response_time = time.time() - start_time
            print(f"Ollama response time: {response_time:.2f}s")
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error {response.status_code}: {response.text}")
            
            result = response.json()
            sql_query = result["response"].strip()
            
            # Clean up the response
            sql_query = self._clean_sql(sql_query)
            
            print(f"Generated SQL: {sql_query}")
            return sql_query
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
        except requests.exceptions.Timeout:
            raise Exception("Ollama request timed out. Try a smaller model or check system resources.")
        except Exception as e:
            raise Exception(f"Error generating SQL with Ollama: {str(e)}")
    
    def _clean_sql(self, sql_query: str) -> str:
        """Clean up SQL query from Ollama response"""
        # Remove markdown code blocks
        sql_query = sql_query.replace("```sql", "").replace("```", "")
        
        if "SQL:" in sql_query:
            sql_query = sql_query.split("SQL:")[-1]
        
        sql_query = sql_query.strip()
        
        # Remove trailing semicolon
        if sql_query.endswith(';'):
            sql_query = sql_query[:-1]
        
        sql_query = ' '.join(sql_query.splitlines())
        
        return sql_query
    
    def explain_query(self, sql_query: str, result: List[tuple]) -> str:
        """Generate explanation for the query result"""
        explanation_prompt = f"""Explain this SQL query and its result in simple, clear terms.

SQL Query: {sql_query}

Query Result: {result[:5]}  # Show first 5 rows

Provide a brief 1-2 sentence explanation of:
1. What the SQL query does
2. What the result means

Explanation:"""
        
        try:
            payload = {
                "model": self.model,
                "prompt": explanation_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Slightly higher for more natural explanations
                    "num_predict": 150
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result["response"].strip()
                return explanation
            else:
                return f"Query returned {len(result)} rows. SQL: {sql_query}"
                
        except Exception as e:
            print(f"Could not generate explanation: {e}")
            return f"Query returned {len(result)} rows. SQL: {sql_query}"
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"Ollama is running. Available models: {[m['name'] for m in models]}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Cannot connect to Ollama at {self.base_url}")
            return False
        return False

ollama_service = OllamaService()