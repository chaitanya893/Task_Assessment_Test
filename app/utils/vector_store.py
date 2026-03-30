from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

# in-memory store
index = faiss.IndexFlatL2(384)
doc_store = []  # [(doc_id, text)]

def add_document(doc_id, text):
    global index, doc_store

    chunks = split_text(text)

    embeddings = model.encode(chunks)

    index.add(np.array(embeddings).astype("float32"))

    for chunk in chunks:
        doc_store.append((doc_id, chunk))


def search(document_id, query, top_k=3):
    global index, doc_store

    query_vec = model.encode([query]).astype("float32")

    D, I = index.search(query_vec, top_k)

    results = []
    for i in I[0]:
        if i < len(doc_store):
            doc_id, text = doc_store[i]
            if doc_id == document_id:
                results.append(text)

    return "\n".join(results)


def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]