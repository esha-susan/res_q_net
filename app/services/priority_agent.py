import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

class PriorityAgent:
    def __init__(self):
        # Ensure GEMINI_API_KEY is in your .env file
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        # We use 'gemini-1.5-flash' - it's the fastest version available
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_text(self, transcript: str):
        prompt = f"""
        You are an Advanced Emergency Triage AI. 
        Transcript: "{transcript}"

        Task:
        1. Identify all distinct incidents.
        2. Rank by priority (Life-threat > Public Safety).
        3. Allocate resources: 
           - Use EXPLICIT counts if mentioned (e.g., "send 2 ambulances").
           - Otherwise, ESTIMATE based on scale.
        
        Respond ONLY in valid JSON format:
        {{
            "overall_severity": "Critical/Moderate/Low",
            "incidents": [
                {{
                    "incident_name": "Name",
                    "priority_rank": 1,
                    "resources": [{{"type": "Ambulance", "qty": 1}}],
                    "reasoning": "Short justification"
                }}
            ],
            "final_reasoning": "Summary of triage"
        }}
        """

        try:
            # Setting the response_mime_type forces Gemini to return valid JSON
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            return json.loads(response.text)

        except Exception as e:
            print(f"Gemini Error: {e}")
            return {
                "overall_severity": "Moderate",
                "incidents": [{
                    "incident_name": "Emergency",
                    "priority_rank": 1,
                    "resources": [{"type": "Ambulance", "qty": 1}],
                    "reasoning": "Fallback due to AI error."
                }],
                "final_reasoning": "System error occurred."
            }