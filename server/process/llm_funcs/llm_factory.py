import logging
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class LLMFactory:
    @staticmethod
    def create_llm(backend, model_path, api_key=None, system_prompt=None, openvino_device="CPU") -> LLMProvider:
        logger.info(f"Creating LLM with backend: {backend}")

        if backend == "openai":
            from .llm_openai import OpenAILLM
            return OpenAILLM(api_key, model_path) # System prompt usually handled in history or separate

        elif backend == "gemini":
            from .llm_gemini import GeminiLLM
            return GeminiLLM(api_key, model_path)

        elif backend == "ollama":
            from .llm_ollama import OllamaLLM
            return OllamaLLM(model_path)

        elif backend == "cpu_legacy" or backend == "llama_cpp":
            from .llm_local_gguf import LlamaCppLLM
            return LlamaCppLLM(model_path)

        elif backend == "openvino":
            from .llm_local_openvino import OpenVINOLLM
            return OpenVINOLLM(model_path, device=openvino_device)

        else:
            # Default fallback or error
            logger.warning(f"Unknown backend {backend}, falling back to OpenAI check or error.")
            # For now raise error
            raise ValueError(f"Unknown backend: {backend}")
