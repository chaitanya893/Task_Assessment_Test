import pdfplumber
import chromadb
from chromadb.utils import embedding_functions
import requests
import os

CHROMA_PATH = "chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Use sentence-transformers embedding function
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = chroma_client.get_or_create_collection(
    name="document_chunks",
    embedding_function=sentence_transformer_ef
)

def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def process_pdf(path, document_id: int):
    text = extract_text(path)
    
    # Simple chunking logic (by paragraphs/lines)
    # Split by newlines and group slightly larger chunks to preserve context
    raw_chunks = [c.strip() for c in text.split("\n") if c.strip()]
    
    chunks = []
    current_chunk = ""
    for c in raw_chunks:
        if len(current_chunk) + len(c) < 1000:
            current_chunk += " " + c
        else:
            chunks.append(current_chunk.strip())
            current_chunk = c
    
    if current_chunk:
        chunks.append(current_chunk.strip())

    ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id} for _ in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    return chunks

def call_ollama(context, question):
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
    model = os.getenv("OLLAMA_MODEL", "llama3")
    
    prompt = f"""You are a helpful and highly intelligent AI assistant. Your task is to accurately and comprehensively answer the user's question using ONLY the provided document context.

Instructions:
1. Provide a detailed, easy-to-read answer.
2. Structure your response perfectly formatting it in paragraphs. Do not just list raw bullet points without explanations.
3. If the answer cannot be found in the context, politely reply: "I'm sorry, but I cannot find the answer to that in the provided document." do not guess or hallucinate.

Context:
{context}

Question:
{question}

Answer:"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        raw_ans = response.json().get("response", "No answer returned.")
        
        # Strip markdown newlines and bullets so it shows purely as single-line text in JSON
        clean_ans = raw_ans.replace("\n", " ")
        clean_ans = clean_ans.replace("*", "")
        # Remove any double spaces
        clean_ans = " ".join(clean_ans.split())
        
        return clean_ans
    except Exception as e:
        return f"Error contacting Ollama AI: {str(e)}"

def get_answer(document_id: int, question: str):
    results = collection.query(
        query_texts=[question],
        n_results=4,
        where={"document_id": document_id}
    )
    
    if not results["documents"] or not results["documents"][0]:
        return "No relevant context found in the document to answer the question."
        
    context_chunks = results["documents"][0]
    context = "\n\n".join(context_chunks)
    
    return call_ollama(context, question)

import requests
import json

def stream_ollama(context, question):
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
    model = os.getenv("OLLAMA_MODEL", "llama3")
    
    prompt = f"""You are a helpful and highly intelligent AI assistant. Your task is to accurately and comprehensively answer the user's question using ONLY the provided document context.

Instructions:
1. Provide a detailed, easy-to-read answer.
2. Structure your response perfectly formatting it in paragraphs. Do not just list raw bullet points without explanations.
3. If the answer cannot be found in the context, politely reply: "I'm sorry, but I cannot find the answer to that in the provided document." do not guess or hallucinate.

Context:
{context}

Question:
{question}

Answer:"""

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    try:
        with requests.post(ollama_url, json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    if chunk:
                        yield chunk
    except Exception as e:
        yield f"\n[Error contacting Ollama AI: {str(e)}]"

def get_stream_answer(document_id: int, question: str):
    results = collection.query(
        query_texts=[question],
        n_results=4,
        where={"document_id": document_id}
    )
    
    if not results["documents"] or not results["documents"][0]:
        yield "No relevant context found in the document to answer the question."
        return
        
    context_chunks = results["documents"][0]
    context = "\n\n".join(context_chunks)
    
    yield from stream_ollama(context, question)