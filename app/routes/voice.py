import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import speech_recognition as sr
import shutil

from app.database import get_db
from app.utils.security import get_current_user
from app.utils.rag import get_stream_answer
from app.models.document import Document
from app.models.qa_history import QAHistory

router = APIRouter()
os.makedirs("uploads/audio", exist_ok=True)

@router.post("/ask-voice")
async def ask_voice(
    document_id: int = Form(...), 
    audio_file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    audio_path = f"uploads/audio/{audio_file.filename}"
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(audio_file.file, buffer)

    try:
        from pydub import AudioSegment
        wav_path = f"{audio_path}.wav"
        # transcode to wav for speech_recognition
        audio = AudioSegment.from_file(audio_path)
        audio.export(wav_path, format="wav")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Audio conversion failed: {str(e)}. File might be corrupted or unsupported format.")

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            question = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Audio could not be transcribed clearly. Please upload a clear .wav file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {str(e)}")
    finally:
        # Clean up audio files
        if os.path.exists(audio_path):
            os.remove(audio_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    def stream_and_log():
        # Inform user of the parsed transcription first!
        yield f"🗣️ Heard Question: {question}\n\n"
        
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
