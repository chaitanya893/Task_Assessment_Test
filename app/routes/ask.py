from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import get_current_user
from app.utils.rag import get_stream_answer, get_answer
from app.models.document import Document
from app.models.qa_history import QAHistory

router = APIRouter()

@router.post("/ask")
async def ask(document_id: int, question: str, db: Session = Depends(get_db), user=Depends(get_current_user)):

    doc = db.query(Document).filter(Document.id == document_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    def stream_and_log():
        full_answer = ""
        try:
            for chunk in get_stream_answer(document_id, question):
                full_answer += chunk
                yield chunk
        finally:
            if full_answer:
                history = QAHistory(
                    user_id=user["user_id"],
                    document_id=document_id,
                    question=question,
                    answer=full_answer
                )
                db.add(history)
                db.commit()

    return StreamingResponse(stream_and_log(), media_type="text/event-stream")