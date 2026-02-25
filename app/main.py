import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.services.speech_agent import SpeechAgent
from app.services.priority_agent import PriorityAgent
from app.services.resource_agent import ResourceAgent
from app.services.notification_agent import NotificationAgent
from app.database import engine, get_db
from app import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

speech_agent = SpeechAgent()
priority_agent = PriorityAgent() 
resource_agent = ResourceAgent()
notification_agent = NotificationAgent()

models.Base.metadata.create_all(bind=engine)

@app.post("/upload-audio")
async def process_emergency_call(file: UploadFile = File(...), db: Session = Depends(get_db)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as b: 
        shutil.copyfileobj(file.file, b)

    try:
        transcript = await speech_agent.transcribe_audio(temp_path)
        ai_result = priority_agent.analyze_text(transcript)
        
        severity = ai_result.get("overall_severity", "Moderate")
        reasoning = ai_result.get("final_reasoning", "Emergency detected.")

        new_alert = models.Alert(message=transcript, severity=severity, status="Pending")
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        for incident in ai_result.get("incidents", []):
            for res in incident.get("resources", []):
                resource_agent.allocate(db, new_alert.id, res.get("type"), res.get("qty", 0), status="Pending")

        # THE CALL TRIGGER
        if severity == "Critical":
            print(f"📞 Dispatching Call to Doctor for Alert ID: {new_alert.id}")
            notification_agent.make_emergency_call(
                to_number=os.getenv("DOCTOR_PHONE_NUMBER"),
                doctor_name="Esha",
                incident_summary=reasoning, 
                alert_id=new_alert.id
            )

        return {
            "status": "Success",
            "alert_id": new_alert.id,
            "transcript": transcript,
            "ai_analysis": ai_result
        }
    finally:
        if os.path.exists(temp_path): 
            os.remove(temp_path)

@app.post("/twilio-callback")
async def twilio_callback(alert_id: int, SpeechResult: str = Form(...), db: Session = Depends(get_db)):
    answer = SpeechResult.lower()
    twiml = "<Response>"
    
    if any(word in answer for word in ["yes", "confirm", "dispatch", "yep"]):
        db.query(models.Alert).filter(models.Alert.id == alert_id).update({"status": "Confirmed"})
        # Logic for resource deduction...
        db.commit()
        twiml += "<Say>Confirmed. Dispatching resources now.</Say>"
    else:
        db.query(models.Alert).filter(models.Alert.id == alert_id).update({"status": "Cancelled"})
        db.commit()
        twiml += "<Say>Call ended. No resources dispatched.</Say>"
    
    return Response(content=twiml + "</Response>", media_type="application/xml")