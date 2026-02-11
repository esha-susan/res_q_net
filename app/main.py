from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

# Internal imports based on your new structure
from app.services.speech_agent import SpeechAgent
from app.services.priority_agent import PriorityAgent

app = FastAPI(title="ResQNet Backend")

# Initialize Agents [cite: 21]
speech_agent = SpeechAgent()
priority_agent = PriorityAgent()

# Directory for temporary audio storage [cite: 49]
UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "ResQNet Backend is Live"}

@app.post("/upload-audio")
async def upload_voice_message(file: UploadFile = File(...)):
    # 1. Validate file type
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload audio.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 2. Save the uploaded file locally [cite: 175]
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Agent 1: Speech-to-Text
        transcript = await speech_agent.transcribe_audio(file_path)
        
        # 4. Agent 2: Priority & Severity Analysis
        analysis = priority_agent.analyze_text(transcript)
        
        # 5. Return the combined actionable data [cite: 6]
        return {
            "status": "success",
            "filename": file.filename,
            "transcript": transcript,
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup: Remove file after processing [cite: 78]
        if os.path.exists(file_path):
            os.remove(file_path)