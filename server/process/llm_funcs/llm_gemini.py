import logging
import google.generativeai as genai
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class GeminiLLM(LLMProvider):
    def __init__(self, api_key, model_name="gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def generate(self, messages: list) -> str:
        try:
            # Convert messages to Gemini format
            # Gemini expects a list of parts, but for simplicity we can use their chat interface
            
            # Extract history (all except last message)
            # OpenAI format: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]
            # Gemini chat history: [{"role": "user", "parts": ["..."]}, {"role": "model", "parts": ["..."]}]
            
            gemini_history = []
            system_instruction = ""
            
            for m in messages[:-1]:
                role = m["role"]
                content = m.get("content", "")
                
                # Handle list-based content (from my previous edits)
                if isinstance(content, list):
                    text_parts = [item.get("text", "") for item in content if item.get("type") in ["input_text", "output_text", "text"]]
                    clean_content = " ".join(text_parts)
                else:
                    clean_content = content
                
                if role == "system":
                    system_instruction += clean_content + "\n"
                elif role == "user":
                    gemini_history.append({"role": "user", "parts": [clean_content]})
                elif role == "assistant":
                    gemini_history.append({"role": "model", "parts": [clean_content]})

            # Last message
            last_msg = messages[-1]
            last_content = last_msg.get("content", "")
            if isinstance(last_content, list):
                text_parts = [item.get("text", "") for item in last_content if item.get("type") in ["input_text", "output_text", "text"]]
                last_clean_content = " ".join(text_parts)
            else:
                last_clean_content = last_content

            # If we have a system instruction, we should ideally use it when initializing the model
            # but for simplicity in this turn, we can prepend it to the first user message or handle it if model allows.
            if system_instruction:
                # Re-initialize with system instruction if present
                self.model = genai.GenerativeModel(self.model_name, system_instruction=system_instruction)

            chat = self.model.start_chat(history=gemini_history)
            response = chat.send_message(last_clean_content)
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return "Sorry, I encountered an error communicating with Gemini."
