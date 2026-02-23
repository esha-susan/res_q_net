import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

# Agent and Database imports
from app.services.speech_agent import SpeechAgent
from app.services.priority_agent import PriorityAgent
from app.services.resource_agent import ResourceAgent
from app.services.notification_agent import NotificationAgent # ADDED
from app.database import engine, get_db
from app import models

app = FastAPI(title="ResQNet - High-Speed AI Dispatch & Voice Alert")

# Initialize Agents
speech_agent = SpeechAgent()
priority_agent = PriorityAgent() 
resource_agent = ResourceAgent()
notification_agent = NotificationAgent() # ADDED

# Create tables in MySQL on startup
models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def health_check():
    return {"status": "online", "engine": "Gemini-1.5-Flash"}

@app.post("/upload-audio")
async def process_emergency_call(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # 1. Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Agent 1: Speech-to-Text (STT)
        transcript = await speech_agent.transcribe_audio(file_path)
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed.")

        # 3. Agent 2: AI Priority & Triage (Gemini)
        ai_result = priority_agent.analyze_text(transcript)
        severity = ai_result.get("overall_severity", "Moderate")
        
        # ---------------------------------------------------------
        # 4. TRIGGER VOICE CALL (The "Calling Thingy")
        # ---------------------------------------------------------
        call_status = "Not Triggered (Non-Critical)"
        if severity == "Critical":
            doctor_phone = os.getenv("DOCTOR_PHONE_NUMBER")
            # This triggers the Twilio call
            success = notification_agent.make_emergency_call(
                to_number=doctor_phone,
                doctor_name="Esha",
                incident_summary=ai_result.get("final_reasoning")
            )
            call_status = "Call Success" if success else "Call Failed"
        # ---------------------------------------------------------

        # 5. Save the main Alert record to DB
        new_alert = models.Alert(
            message=transcript,
            severity=severity,
            priority="Multi-Incident"
        )
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)
        
        # 6. Agent 3: Sequential Dispatching
        dispatch_summary = []
        for incident in ai_result.get("incidents", []):
            incident_actions = {
                "incident": incident.get("incident_name"),
                "rank": incident.get("priority_rank"),
                "dispatch_results": []
            }
            for res in incident.get("resources", []):
                status = resource_agent.allocate(db, new_alert.id, res.get("type"), res.get("qty", 0))
                incident_actions["dispatch_results"].append(status)
            dispatch_summary.append(incident_actions)
        
        return {
            "status": "success",
            "alert_id": new_alert.id,
            "transcript": transcript,
            "call_status": call_status, # Let's you see if the call worked
            "triage_logic": {
                "overall_severity": severity,
                "triage_summary": ai_result.get("final_reasoning")
            },
            "prioritized_dispatch": dispatch_summary
        }
        
    except Exception as e:
        db.rollback()
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=f"System Error: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/inventory")
def view_inventory(db: Session = Depends(get_db)):
    return db.query(models.Resource).all()

@app.get("/dispatch-history")
def view_assignments(db: Session = Depends(get_db)):
    return db.query(models.ResourceAssignment).all()