import logging
import ollama
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class OllamaLLM(LLMProvider):
    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def generate(self, messages: list) -> str:
        try:
            # Ollama messages format matches OpenAI closely
            clean_messages = []
            for m in messages:
                content = m.get("content", "")
                if isinstance(content, list):
                    text_parts = [item.get("text", "") for item in content if item.get("type") in ["input_text", "output_text", "text"]]
                    clean_content = " ".join(text_parts)
                else:
                    clean_content = content
                
                role = m["role"]
                # Convert "assistant" to "assistant" (ollama supports this)
                clean_messages.append({
                    "role": role,
                    "content": clean_content
                })

            response = ollama.chat(model=self.model_name, messages=clean_messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error communicating with local Ollama: {e}"
