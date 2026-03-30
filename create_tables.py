from app.database import engine, Base

from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.qa_history import QAHistory

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Done")