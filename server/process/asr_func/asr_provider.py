from abc import ABC, abstractmethod

class ASRProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes audio file to text.
        """
        pass
