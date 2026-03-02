import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationAgent:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.client = Client(self.account_sid, self.auth_token) if self.account_sid else None

    def make_emergency_call(self, to_number, doctor_name, incident_summary, alert_id):
        if not self.client: return False
        try:
            # IMPORTANT: Verify this ngrok URL is still active
            base_url = "https://deann-equicontinuous-unpractically.ngrok-free.dev"
            callback_url = f"{base_url}/twilio-callback?alert_id={alert_id}"
            
            twiml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Gather input="speech" action="{callback_url}" method="POST" speechTimeout="auto">
                    <Say>Attention Doctor {doctor_name}. Emergency: {incident_summary}. Say Yes to confirm dispatch.</Say>
                </Gather>
                <Say>No response received. Goodbye.</Say>
            </Response>"""

            self.client.calls.create(twiml=twiml_content, to=to_number, from_=self.from_number)
            return True
        except Exception as e:
            print(f"Twilio Error: {e}")
            return False