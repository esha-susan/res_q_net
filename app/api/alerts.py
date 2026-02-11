from fastapi import APIRouter, UploadFile, File
from app.services.speech_agent import SpeechAgent

router = APIRouter()
speech_agent = SpeechAgent()

@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    # Save file temporarily and transcribe
    with open(f"temp_{file.filename}", "wb") as f:
        f.write(await file.read())
    
    transcript = await speech_agent.transcribe(f"temp_{file.filename}")
    return {"transcript": transcript}