from .llm_provider import LLMProvider
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class OpenAILLM(LLMProvider):
    def __init__(self, api_key, model_name="gpt-4.1-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def generate(self, messages: list) -> str:
        try:
            # Filter messages to ensure they match OpenAI format if needed
            # (removing 'type' wrapping if it exists in the dicts from llm_scr.py)
            # llm_scr.py uses specific structure: content: [{"type": "input_text", "text": ...}]
            # OpenAI expects content to be string or list of blocks.

            clean_messages = []
            for m in messages:
                content = m.get("content", "")
                if isinstance(content, list):
                    # extract text from list if it matches the structure
                    text_parts = [item.get("text", "") for item in content if item.get("type") in ["input_text", "output_text", "text"]]
                    clean_content = " ".join(text_parts)
                else:
                    clean_content = content

                clean_messages.append({
                    "role": m["role"],
                    "content": clean_content
                })

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=clean_messages,
                temperature=1,
                top_p=1,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return "Sorry, I encountered an error communicating with the AI service."
