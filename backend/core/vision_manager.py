import os
import base64
import logging
from PIL import Image
from io import BytesIO

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

logger = logging.getLogger(__name__)

class VisionManager:
    def __init__(self):
        self.enabled = PYAUTOGUI_AVAILABLE
        if not self.enabled:
            logger.warning("pyautogui not installed. Screen vision disabled.")

    def capture_screen(self):
        if not self.enabled:
            return None
            
        try:
            screenshot = pyautogui.screenshot()
            # Resize for faster processing and lower token cost
            screenshot.thumbnail((1280, 720))
            
            buffered = BytesIO()
            screenshot.save(buffered, format="JPEG", quality=70)
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            return img_str
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            return None

    def get_vision_prompt(self):
        """
        In a real chat, we'd send the image to a multimodal LLM.
        For Riko, we'll add a 'System Observation' of the screen.
        """
        # This is a placeholder for the multimodal flow.
        # We can implement a specific 'Describe Screen' function using Gemini Pro Vision.
        return "[System: Vision mode enabled. Riko can see your screen.]"
