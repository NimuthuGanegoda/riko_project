from .llm_provider import LLMProvider
import logging

logger = logging.getLogger(__name__)

class OpenVINOLLM(LLMProvider):
    def __init__(self, model_path, device="GPU"):
        try:
            from optimum.intel import OVModelForCausalLM
            from transformers import AutoTokenizer

            logger.info(f"Loading OpenVINO model from {model_path} on {device}")

            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Ensure left padding for generation
            self.tokenizer.padding_side = "left"

            # Configuration for Ivy Bridge / Legacy
            ov_config = {
                "PERFORMANCE_HINT": "LATENCY",
                "CACHE_DIR": "./model_cache"
            }

            self.model = OVModelForCausalLM.from_pretrained(
                model_path,
                device=device,
                ov_config=ov_config
            )

        except ImportError:
            logger.error("optimum-intel or openvino not installed.")
            raise
        except Exception as e:
            logger.error(f"Failed to load OpenVINO model: {e}")
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
            clean_messages.append({"role": m["role"], "content": clean_content})

        # Use chat template if available
        if hasattr(self.tokenizer, "apply_chat_template"):
            try:
                prompt = self.tokenizer.apply_chat_template(clean_messages, tokenize=False, add_generation_prompt=True)
            except Exception:
                # Fallback manual template
                prompt = ""
                for m in clean_messages:
                    prompt += f"<|{m['role']}|>\n{m['content']}</s>\n"
                prompt += "<|assistant|>\n"
        else:
            prompt = ""
            for m in clean_messages:
                prompt += f"{m['role']}: {m['content']}\n"
            prompt += "assistant: "

        # Disable dynamic shapes by padding to fixed length (Prompt 2 instruction)
        # We choose a safe max_length. 1024 or 512.
        # For legacy hardware, 512 might be safer for memory.
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding="max_length",
            max_length=512,
            truncation=True
        )

        # Generate
        gen_out = self.model.generate(
            **inputs,
            max_new_tokens=128, # Keep generation short for stability
            pad_token_id=self.tokenizer.pad_token_id,
            do_sample=True,
            temperature=0.7
        )

        # Decode
        prompt_len = inputs.input_ids.shape[1]
        out_ids = gen_out[0][prompt_len:]
        text = self.tokenizer.decode(out_ids, skip_special_tokens=True)
        return text
