import logging
import os
import sys

# Ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from .asr_provider import ASRProvider

logger = logging.getLogger(__name__)

class ASRFactory:
    @staticmethod
    def create_asr(backend, model_path="base.en", openvino_device="CPU") -> ASRProvider:
        logger.info(f"Creating ASR with backend: {backend}")

        if backend in ["cuda", "rocm"]:
            from .asr_faster_whisper import FasterWhisperASR
            return FasterWhisperASR(model_path, device="cuda")

        elif backend == "mps":
            from .asr_faster_whisper import FasterWhisperASR
            # Faster-Whisper doesn't natively support MPS yet, so we fallback to CPU
            return FasterWhisperASR(model_path, device="cpu")

        elif backend == "openvino":
            from .asr_openvino import OpenVINOASR
            return OpenVINOASR(model_path, device=openvino_device)

        elif backend == "cpu_legacy" or backend == "whisper_cpp":
            from .asr_whisper_cpp import WhisperCppASR
            return WhisperCppASR(model_path)

        else:
            # Default fallback to CPU faster-whisper
            from .asr_faster_whisper import FasterWhisperASR
            return FasterWhisperASR(model_path, device="cpu")
