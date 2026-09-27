import logging

from anthropic import Anthropic

from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicLLM(LLMProvider):
    """Claude provider using Anthropic's supported API authentication."""

    def __init__(self, api_key, model_name="claude-sonnet-4-5"):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for the Anthropic provider")
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name

    def generate(self, messages: list, image_b64: str | None = None) -> str:
        system_parts = []
        clean_messages = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict) and item.get("type") in {"input_text", "output_text", "text"}
                )
            if role == "system":
                system_parts.append(str(content))
            elif role in {"user", "assistant"}:
                clean_messages.append({"role": role, "content": str(content)})

        if image_b64 and clean_messages and clean_messages[-1]["role"] == "user":
            text = clean_messages[-1]["content"]
            clean_messages[-1]["content"] = [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
                },
                {"type": "text", "text": text},
            ]

        try:
            response = self.client.messages.create(
                model=self.model_name,
                system="\n".join(system_parts),
                messages=clean_messages,
                max_tokens=2048,
            )
            return "".join(block.text for block in response.content if block.type == "text")
        except Exception:
            logger.exception("Anthropic generation error")
            raise
