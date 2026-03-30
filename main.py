from fastapi import FastAPI
from app.routes import auth, upload, ask, voice, history

app = FastAPI()

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(ask.router)
app.include_router(voice.router)
app.include_router(history.router)

@app.get("/")
def home():
    return {"message": "AI Document QA Running"}