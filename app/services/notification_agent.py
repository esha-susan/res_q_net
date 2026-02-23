from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationAgent:
    def __init__(self):
        # These come from your .env file
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")
        self.client = Client(self.account_sid, self.auth_token)

    def make_emergency_call(self, to_number, doctor_name, incident_summary):
        """Makes a physical phone call and reads a message to the doctor."""
        try:
            # TwiML is the 'script' the AI reads over the phone
            message_content = (
                f"Emergency alert for Doctor {doctor_name}. "
                f"Priority incident reported: {incident_summary}. "
                "Please respond to the emergency coordinates immediately."
            )
            
            call = self.client.calls.create(
                twiml=f'<Response><Say voice="polly.Amy" language="en-GB">{message_content}</Say></Response>',
                to=to_number,
                from_=self.from_number
            )
            print(f"Call initiated! SID: {call.sid}")
            return True
        except Exception as e:
            print(f"Twilio Call Error: {e}")
            return False