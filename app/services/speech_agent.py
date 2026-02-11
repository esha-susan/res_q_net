import whisper
import os

class SpeechAgent:
    def __init__(self):
        # Loads the base model (approx 140MB) [cite: 59]
        self.model = whisper.load_model("base")

    async def transcribe_audio(self, file_path: str) -> str:
        """Converts speech file to text using Whisper."""
        if not os.path.exists(file_path):
            return "Error: Audio file not found."
        
        # Perform transcription
        result = self.model.transcribe(file_path)
        return result.get("text", "").strip()