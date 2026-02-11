import whisper
import os

class SpeechAgent:
    def __init__(self):
        self.model = whisper.load_model("base")

    # Ensure this name is exactly 'transcribe_audio'
    async def transcribe_audio(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return "File not found."
        
        # Whisper transcription
        result = self.model.transcribe(file_path)
        return result.get("text", "").strip()