# NL2SQL Chatbot 

A full-stack **Natural Language to SQL** chatbot that allows users to ask questions in plain English and receive answers by dynamically generating and executing SQL queries on a relational database.

Built using **FastAPI**, **SQLAlchemy**, **Ollama (LLM)**, and **React + TypeScript**.

---

## 🚀 Features

- Convert natural language queries into SQL
- Uses local LLMs via **Ollama**
- FastAPI backend with clean modular architecture
- SQLAlchemy ORM for PostgreSQL database interaction
- React + TypeScript chatbot UI
- Supports extensible database schemas
- Clean API separation between backend and frontend

---

## 🏗️ Tech Stack

### Backend
- **FastAPI**
- **SQLAlchemy**
- **Python 3.10+**
- **Ollama (LLM inference)**
- **PostgreSQL**

### Frontend
- **React**
- **TypeScript**
- **CSS**
- **Axios**

---

## ⚙️ Prerequisites

- Python 3.10+
- Node.js 18+
- Ollama installed and running
- Git

---

## 🔧 Backend Setup
1️⃣ Create a virtual environment
python -m venv venv
source venv\Scripts\activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run Ollama
Make sure Ollama is running and a model is pulled:
ollama pull llama3
ollama serve

4️⃣ Start the FastAPI server
uvicorn app.main:app --reload
The backend will run at:
http://127.0.0.1:8000

---

## 💻 Frontend Setup

cd frontend/sql-chatbot
npm install
npm start
The frontend will run at:
http://localhost:3000

---

## 🧠 How NL → SQL Works
- The user enters a natural language query in the chatbot UI
- The Query is sent to the FastAPI backend
- The Ollama-powered LLM converts natural language into SQL
- SQLAlchemy safely executes the generated SQL query
- Query results are returned to the frontend
- The chatbot displays a structured and readable response

---

## 📌 Notes
- Ollama must be running locally for the LLM inference to work
- The LLM service layer is modular and can be swapped (e.g., Gemini, OpenAI)
