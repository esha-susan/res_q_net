from fastapi import FastAPI, UploadFile, File, HTTPException
from app.services.speech_agent import SpeechAgent
import shutil
import os

app = FastAPI(title="ResQNet Backend")
speech_agent = SpeechAgent()

# Ensure a temporary directory exists for audio processing
UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-audio")
async def upload_voice_message(file: UploadFile = File(...)):
    # 1. Validate file type (basic check)
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload audio.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # 2. Save the uploaded file locally
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Process with the Speech Agent
        transcript = await speech_agent.transcribe_audio(file_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "transcript": transcript
        }
    finally:
        # Cleanup: Remove the file after processing to save space
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/")
def read_root():
    return {"message": "ResQNet Backend is Live"}