import logging
from .asr_provider import ASRProvider

logger = logging.getLogger(__name__)

class ASRFactory:
    @staticmethod
    def create_asr(backend, model_path="base.en") -> ASRProvider:
        logger.info(f"Creating ASR with backend: {backend}")

        if backend == "cuda":
            from .asr_faster_whisper import FasterWhisperASR
            return FasterWhisperASR(model_path, device="cuda")

        elif backend == "openvino":
            from .asr_openvino import OpenVINOASR
            return OpenVINOASR(model_path)

        elif backend == "cpu_legacy" or backend == "whisper_cpp":
            from .asr_whisper_cpp import WhisperCppASR
            return WhisperCppASR(model_path)

        else:
            # Default fallback to CPU faster-whisper
            from .asr_faster_whisper import FasterWhisperASR
            return FasterWhisperASR(model_path, device="cpu")
