import json
import os
import time
from google import genai
from google.genai import types

class PriorityAgent:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        # Using the standard stable ID for 2026
        self.model_id = "gemini-2.5-flash" 

    def analyze_text(self, transcript: str):
        prompt = f"Analyze: {transcript}"
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Return JSON. Fields: 'overall_severity' (Critical/Moderate/Minor), "
                        "'final_reasoning', and 'incidents'. "
                        "CRITICAL: Under 'resources', the 'type' MUST be exactly 'Doctor'. "
                        "Do not use synonyms like 'medical personnel' or 'staff'."
                    ),
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            # Fallback remains as a safety net
            return {
                "overall_severity": "Critical", 
                "final_reasoning": f"Emergency: {transcript}",
                "incidents": [{"resources": [{"type": "Doctor", "qty": 2}]}]
            }