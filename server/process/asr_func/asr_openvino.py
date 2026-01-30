from .asr_provider import ASRProvider
import logging
import numpy as np

logger = logging.getLogger(__name__)

class OpenVINOASR(ASRProvider):
    def __init__(self, model_name="base.en", device="GPU"):
        try:
            from optimum.intel import OVModelForSpeechSeq2Seq
            from transformers import AutoProcessor

            logger.info(f"Loading OpenVINO Whisper: {model_name}")
            self.processor = AutoProcessor.from_pretrained(model_name)

            # Load full model on GPU first
            self.model = OVModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                device=device,
                ov_config={"PERFORMANCE_HINT": "LATENCY", "CACHE_DIR": "./model_cache"}
            )

            # Optimization for Intel HD 4000: Encoder GPU, Decoder CPU
            if device == "GPU":
                try:
                    logger.info("Applying Intel HD 4000 optimization: Moving Decoder to CPU")
                    # Recompile decoder on CPU
                    self.model.decoder.request = self.model.decoder._compile_model(
                        self.model.decoder.model,
                        device="CPU",
                        ov_config={"PERFORMANCE_HINT": "LATENCY"}
                    )
                    self.model.decoder.device = "CPU"
                    logger.info("Decoder moved to CPU successfully.")
                except Exception as e:
                    logger.warning(f"Failed to move decoder to CPU: {e}")

        except ImportError:
            logger.error("optimum-intel not installed.")
            raise
        except Exception as e:
            logger.error(f"Failed to init OpenVINO ASR: {e}")
            raise

    def transcribe(self, audio_path: str) -> str:
        try:
            import librosa
            # Always use librosa for safe resampling to 16000
            audio, sr = librosa.load(audio_path, sr=16000)

            # Pad to 30s (Whisper standard) to avoid dynamic shapes in Encoder
            # padding="max_length" pads to max_length (3000 frames)
            inputs = self.processor(
                audio,
                return_tensors="pt",
                sampling_rate=16000,
                padding="max_length"
            )

            generated_ids = self.model.generate(**inputs, max_new_tokens=448)

            transcription = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            return transcription.strip()
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
