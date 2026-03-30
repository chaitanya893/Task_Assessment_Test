# AI Document Q&A System

## Project Description
This project is an AI-powered system where users can upload PDF documents and ask questions based on their content. The system generates accurate answers using AI.

## Tech Stack
- FastAPI
- PostgreSQL
- ChromaDB
- Ollama (Llama 3)
- pdfplumber
- sentence-transformers

## Features
- User Authentication (JWT)
- Role-Based Access Control (Admin/User)
- PDF Upload (Admin only)
- Ask Questions from Documents
- Streaming Responses
- Voice Input Support
- Chat History

## Setup Instructions

1. Clone the repository
git clone https://github.com/chaitanya893/Task_Assessment_Test

2. Go to project folder
cd Task_Assessment_Test

3. Create virtual environment
python -m venv venv
venv\Scripts\activate

4. Install dependencies
pip install -r requirements.txt

5. Run the server
uvicorn main:app --reload

## API Testing
Open:
http://127.0.0.1:8000/docs

## Author
Chaitanya
