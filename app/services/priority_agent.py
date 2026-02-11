class PriorityAgent:
    def __init__(self):
        # Critical keywords based on the Problem Statement [cite: 2, 26]
        self.critical_keywords = ["fire", "flood", "explosion", "trapped", "dying", "unconscious"]
        # Moderate keywords for standard emergencies
        self.moderate_keywords = ["accident", "injury", "theft", "leak", "broken"]

    def analyze_text(self, text: str):
        text = text.lower()
        
        # Default starting values [cite: 27]
        severity = "Low"
        priority = "P3"

        if any(word in text for word in self.critical_keywords):
            severity = "Critical"
            priority = "P1"
        elif any(word in text for word in self.moderate_keywords):
            severity = "Moderate"
            priority = "P2"
            
        return {"severity": severity, "priority": priority}