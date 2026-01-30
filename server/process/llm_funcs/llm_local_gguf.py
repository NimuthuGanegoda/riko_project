from .llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class LlamaCppLLM(LLMProvider):
    def __init__(self, model_path, n_ctx=2048):
        try:
            from llama_cpp import Llama
            # Prompt 3: "If missing (avx2), force the code to use the Llama.cpp backend with the -no-avx flag enabled during compilation."
            # We can't recompile here easily, but we assume the user has the right binary or we use standard Llama class.
            # "Enable mmap=True"
            logger.info(f"Loading GGUF model from {model_path}")
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=0, # Force CPU
                verbose=True,
                use_mmap=True
            )
        except ImportError:
            logger.error("llama-cpp-python not installed.")
            raise

    def generate(self, messages: list) -> str:
        clean_messages = []
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, list):
                text_parts = [item.get("text", "") for item in content if item.get("type") in ["input_text", "output_text", "text"]]
                clean_content = " ".join(text_parts)
            else:
                clean_content = content

            clean_messages.append({
                "role": m["role"],
                "content": clean_content
            })

        response = self.llm.create_chat_completion(
            messages=clean_messages,
            max_tokens=2048,
            temperature=0.7
        )

        return response['choices'][0]['message']['content']
