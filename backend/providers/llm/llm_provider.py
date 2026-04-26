from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: list) -> str:
        """
        Generates a response based on the conversation history (messages).
        messages: list of dicts with 'role' and 'content'.
        """
        pass
