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
            print("CRITICAL ERROR: Twilio credentials missing in .env file!")

    def make_emergency_call(self, to_number, doctor_name, incident_summary):
        try:
            # Clean the text to ensure no special characters break the XML
            clean_summary = str(incident_summary).replace('"', '').replace("'", "")
            
            # TwiML script with a 2-second pause for the Trial Account 'Press a key' prompt
            twiml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Pause length="2"/>
                <Say voice="Polly.Amy" language="en-GB">
                    Attention Doctor {doctor_name}. This is an automated Res-Q-Net emergency alert.
                    Incident details: {clean_summary}.
                    Please respond immediately.
                </Say>
            </Response>"""

            call = self.client.calls.create(
                twiml=twiml_content,
                to=to_number,
                from_=self.from_number
            )
            print(f"Twilio Call Triggered! SID: {call.sid}")
            return True
        except Exception as e:
            print(f"Twilio API Error: {e}")
            return False