from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import get_current_user
from app.models.qa_history import QAHistory

router = APIRouter()

@router.get("/history")
def history(db: Session = Depends(get_db), user=Depends(get_current_user)):

    if user["role"] == "admin":
        histories = db.query(QAHistory).order_by(QAHistory.id.desc()).all()
    else:
        histories = db.query(QAHistory).filter(QAHistory.user_id == user["user_id"]).order_by(QAHistory.id.desc()).all()

    return {"history": [{"id": h.id, "document_id": h.document_id, "question": h.question, "answer": h.answer, "user_id": h.user_id} for h in histories]}