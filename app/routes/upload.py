from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import admin_required
from app.utils.rag import process_pdf
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
import shutil, os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(admin_required)):

    path = f"{UPLOAD_DIR}/{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Insert Document into PostgreSQL
    doc = Document(filename=file.filename, filepath=path)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Extract text, store in ChromaDB, get raw chunks
    chunks = process_pdf(path, doc.id)

    # Store chunks in PostgreSQL
    for chunk_text in chunks:
        db.add(DocumentChunk(document_id=doc.id, chunk_text=chunk_text))
    db.commit()

    return {"message": f"Uploaded {file.filename} and processed {len(chunks)} chunks successfully.", "document_id": doc.id}

@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return {"documents": [{"id": d.id, "filename": d.filename, "uploaded_at": d.uploaded_at} for d in docs]}