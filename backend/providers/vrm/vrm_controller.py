import logging
import json

logger = logging.getLogger(__name__)

class VRMController:
    """
    Manages the 3D VRM model's state, including expressions (BlendShapes)
    and basic procedural animations (breathing, blinking).
    """
    def __init__(self):
        # Default neutral state
        self.state = {
            "expression": "neutral",
            "mouth_open": 0.0,
            "look_at": [0, 0, 0],
            "is_speaking": False
        }

    def get_expression_from_text(self, text):
        """
        Heuristic to determine expression from Riko's response.
        In an 'Elite' version, we'd use a classifier or the LLM's self-report.
        """
        text = text.lower()
        if any(word in text for word in ["happy", "yay", "fun", "senpai!", "love"]):
            return "joy"
        if any(word in text for word in ["sad", "sorry", "bad", "no..."]):
            return "sorrow"
        if any(word in text for word in ["angry", "stop", "hmph", "baka"]):
            return "angry"
        if any(word in text for word in ["surprise", "what?", "wow", "oh!"]):
            return "surprised"
        return "neutral"

    def get_vrm_state(self):
        return self.state

    def update_vrm_state(self, riko_response):
        self.state["expression"] = self.get_expression_from_text(riko_response)
        # We can also handle procedural data here
        return self.state
