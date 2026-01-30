from .asr_provider import ASRProvider
import logging

logger = logging.getLogger(__name__)

class FasterWhisperASR(ASRProvider):
    def __init__(self, model_size="base.en", device="cpu", compute_type="float32"):
        try:
            from faster_whisper import WhisperModel
            if device == "cuda":
                compute_type = "float16"

            logger.info(f"Loading Faster-Whisper: {model_size} on {device} ({compute_type})")
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except ImportError:
            logger.error("faster-whisper not installed.")
            raise

    def transcribe(self, audio_path: str) -> str:
        segments, _ = self.model.transcribe(audio_path)
        text = " ".join([segment.text for segment in segments])
        return text.strip()
