import psycopg2

def get_db():
    return psycopg2.connect(
        host="localhost",
        database="ai_document_qa",
        user="postgres",
        password="root123"
    )