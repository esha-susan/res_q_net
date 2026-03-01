import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.services.speech_agent import SpeechAgent
from app.services.priority_agent import PriorityAgent
from app.services.resource_agent import ResourceAgent
from app.services.notification_agent import NotificationAgent
from app.services.location_agent import LocationAgent

from app.database import engine, get_db
from app import models

app = FastAPI(title="ResQNet - AI Dispatch & Voice Alert")

# 🔥 CORS FIX
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
location_agent = LocationAgent()

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def health_check():
    return {"status": "online"}


@app.post("/upload-audio")
async def process_emergency_call(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Please upload a valid audio file.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcript = await speech_agent.transcribe_audio(file_path)

        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed.")

        ai_result = priority_agent.analyze_text(transcript)
        severity = ai_result.get("overall_severity", "Moderate")

        location_data = location_agent.get_coordinates(transcript)

        lat = None
        lng = None
        zone_name = "Unassigned"

        if location_data:
            lat = location_data["latitude"]
            lng = location_data["longitude"]
            zone_name = location_data["address"]

        new_alert = models.Alert(
            message=transcript,
            severity=severity,
            priority="Multi-Incident",
            zone=zone_name,
            latitude=lat,
            longitude=lng
        )

        db.add(new_alert)
        db.commit()
        db.refresh(new_alert)

        return {
            "status": "success",
            "alert_id": new_alert.id,
            "transcript": transcript,
            "latitude": lat,
            "longitude": lng,
            "zone": zone_name
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.get("/alerts-map")
def get_alert_locations(db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).all()

    return [
        {
            "id": alert.id,
            "message": alert.message,
            "severity": alert.severity,
            "latitude": alert.latitude,
            "longitude": alert.longitude
        }
        for alert in alerts
        if alert.latitude and alert.longitude
    ]