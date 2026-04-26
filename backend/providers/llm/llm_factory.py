import logging
import os
import sys

# Ensure local imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def create_llm(backend, model_path, api_key=None, system_prompt=None, openvino_device="CPU") -> LLMProvider:
        logger.info(f"Creating LLM with backend: {backend}")

        if backend == "openai":
            from .llm_openai import OpenAILLM
            return OpenAILLM(api_key, model_path)

        elif backend == "gemini":
            from .llm_gemini import GeminiLLM
            return GeminiLLM(api_key, model_path)

        elif backend == "ollama":
            from .llm_ollama import OllamaLLM
            return OllamaLLM(model_path)

        elif backend in ["cpu_legacy", "llama_cpp", "mps", "rocm", "cpu_modern"]:
            from .llm_local_gguf import LlamaCppLLM
            return LlamaCppLLM(model_path, backend=backend)

        elif backend == "openvino":
            from .llm_local_openvino import OpenVINOLLM
            return OpenVINOLLM(model_path, device=openvino_device)
