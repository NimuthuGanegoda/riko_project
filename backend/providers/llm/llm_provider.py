from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: list, image_b64: str | None = None) -> str:
        """
        Generates a response based on the conversation history (messages).
        messages: list of dicts with 'role' and 'content'.
        image_b64: optional base64-encoded image (e.g. a screen capture) attached
        to the current turn, for providers that support multimodal input.
        Providers without vision support may ignore this parameter.
        """
