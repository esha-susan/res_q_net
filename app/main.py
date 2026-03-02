import os
import shutil
from fastapi import FastAPI, UploadFile, File, Depends, Form, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.services.speech_agent import SpeechAgent
from app.services.priority_agent import PriorityAgent
from app.services.resource_agent import ResourceAgent
from app.services.notification_agent import NotificationAgent
from app.database import engine, get_db
from  app import models

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

        # Create the Alert
        new_alert = models.Alert(message=transcript, severity=severity, status="Pending")
        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        # Allocate resources as PENDING initially
        for incident in ai_result.get("incidents", []):
            # Check for both "resources" and "resources_needed" keys based on your AI output
            res_list = incident.get("resources") or incident.get("resources_needed") or []
            for res in res_list:
                resource_agent.allocate(
                    db, 
                    new_alert.id, 
                    res.get("type"), 
                    res.get("qty") or res.get("quantity") or 0, 
                    status="Pending"
                )

        if severity == "Critical":
            notification_agent.make_emergency_call(
                to_number=os.getenv("DOCTOR_PHONE_NUMBER"),
                doctor_name="Esha",
                incident_summary=reasoning, 
                alert_id=new_alert.id
            )

        return {"status": "Success", "alert_id": new_alert.id, "ai_analysis": ai_result}
    finally:
        if os.path.exists(temp_path): 
            os.remove(temp_path)

@app.post("/twilio-callback")
async def twilio_callback(
    alert_id: int = Query(...), 
    SpeechResult: str = Form(None), 
    db: Session = Depends(get_db)
):
    answer = SpeechResult.lower() if SpeechResult else ""
    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response>'
    
    if any(word in answer for word in ["yes", "confirm", "dispatch", "yep"]):
        # 1. Update the Alert table
        db.query(models.Alert).filter(models.Alert.id == alert_id).update({"status": "Confirmed"})
        
        # 2. Update the ResourceAssignment table (THE MISSING STEP)
        db.query(models.ResourceAssignment).filter(
            models.ResourceAssignment.alert_id == alert_id
        ).update({"status": "Confirmed"})
        
        db.commit()
        twiml += "<Say>Resources confirmed and dispatched. Thank you.</Say>"
    else:
        db.query(models.Alert).filter(models.Alert.id == alert_id).update({"status": "Cancelled"})
        db.commit()
        twiml += "<Say>Request cancelled.</Say>"
    
    return Response(content=twiml + "</Response>", media_type="application/xml")