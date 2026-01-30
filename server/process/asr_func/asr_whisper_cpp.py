from .asr_provider import ASRProvider
import logging

logger = logging.getLogger(__name__)

class WhisperCppASR(ASRProvider):
    def __init__(self, model_name="base.en"):
        try:
            from pywhispercpp.model import Model
            logger.info(f"Loading Whisper-cpp: {model_name}")
            # Ensure model name is compatible or map it
            self.model = Model(model_name, print_realtime=False, print_progress=False)
        except ImportError:
            logger.error("pywhispercpp not installed.")
            raise
        except Exception as e:
            logger.error(f"Failed to init whisper-cpp: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        # n_threads should be adjustable or auto
        segments = self.model.transcribe(audio_path, n_threads=4)
        # pywhispercpp returns objects with text attribute
        text = " ".join([segment.text for segment in segments])
        return text.strip()
