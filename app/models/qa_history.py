from sqlalchemy import Column, Integer, Text, ForeignKey
from app.database import Base


class QAHistory(Base):
    __tablename__ = "qa_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    document_id = Column(Integer)
    question = Column(Text)
    answer = Column(Text)