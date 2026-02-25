import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

class NotificationAgent:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if all([self.account_sid, self.auth_token, self.from_number]):
            self.client = Client(self.account_sid, self.auth_token)
        else:
            print("CRITICAL ERROR: Twilio credentials missing!")

    def make_emergency_call(self, to_number, doctor_name, incident_summary, alert_id):
        try:
            # REPLACE THIS URL with your ngrok URL
            base_url = "https://deann-equicontinuous-unpractically.ngrok-free.dev"
            callback_url = f"{base_url}/twilio-callback?alert_id={alert_id}"
            
            twiml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Pause length="2"/>
                <Gather input="speech" action="{callback_url}" method="POST" speechTimeout="auto">
                    <Say voice="Polly.Amy" language="en-GB">
                        Attention Doctor {doctor_name}. Emergency detected: {incident_summary}. 
                        Do you confirm the dispatch of requested resources? Please say 'Yes' or 'No'.
                    </Say>
                </Gather>
                <Say voice="Polly.Amy">We did not hear a response. The request will remain pending. Goodbye.</Say>
            </Response>"""

            call = self.client.calls.create(
                twiml=twiml_content,
                to=to_number,
                from_=self.from_number
            )
            print(f"Interactive Call Triggered! SID: {call.sid}")
            return True
        except Exception as e:
            print(f"Twilio API Error: {e}")
            return False