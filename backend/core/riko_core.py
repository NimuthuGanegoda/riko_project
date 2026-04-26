import os
import yaml
import uuid
import logging
from pathlib import Path

# Fix path to allow local imports
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from core.hardware import HardwareDetector
from managers.model_manager import ModelManager
from providers.asr.asr_factory import ASRFactory
from providers.llm.llm_factory import LLMFactory
from managers.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class RikoCore:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'configs', 'character_config.yaml')
            
        # Load Config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Hardware Detection
        self.detector = HardwareDetector()
        self.hw_config = self.detector.get_hardware_config()
        
        self.backend = self.config.get('backend_preference', 'auto')
        if self.backend == 'auto':
            self.backend = self.hw_config['backend']

        # Initialize ASR
        self.asr_path = self.config.get('local_asr_path', 'base.en')
        self.asr = ASRFactory.create_asr(self.backend, self.asr_path)

        # Initialize LLM
        self.mm = ModelManager()
        self.llm_path = self.config.get('local_llm_path', 'models/riko-llm')
        
        self.llm_provider = self.config.get('llm_provider', 'auto')
        if self.llm_provider == 'auto':
            if self.backend == 'cuda':
                self.llm_provider = "openai"
            elif self.backend == 'openvino':
                self.llm_provider = "openvino"
            elif self.backend in ['mps', 'rocm', 'cpu_modern']:
                self.llm_provider = "llama_cpp"
            else:
                self.llm_provider = "cpu_legacy"

        if self.llm_provider in ["openvino", "cpu_legacy", "llama_cpp"]:
            self.real_llm_path = self.mm.find_model(self.llm_path, self.llm_provider)
        else:
            self.real_llm_path = self.config['model']

        self.api_key = self.config.get('OPENAI_API_KEY')
        if self.llm_provider == "gemini":
            self.api_key = self.config.get('GEMINI_API_KEY')

        self.llm = LLMFactory.create_llm(
            self.llm_provider, 
            self.real_llm_path, 
            api_key=self.api_key, 
            openvino_device=self.hw_config.get('openvino_device', 'CPU')
        )

        # Memory & History - Fixed paths
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
        self.memory_db = MemoryManager(db_path=db_path)
        
        self.system_prompt_content = self.config['presets']['default']['system_prompt']
        self.system_prompt = [{"role": "system", "content": self.system_prompt_content}]

    def switch_model(self, provider, model_name=None):
        """Switches the active LLM provider and model."""
        logger.info(f"Switching LLM to Provider: {provider}, Model: {model_name}")
        
        self.llm_provider = provider
        if model_name:
            self.real_llm_path = model_name
        else:
            self.real_llm_path = self.config.get('model', 'gpt-3.5-turbo')

        # Get the correct API key for the provider
        api_key = self.config.get('OPENAI_API_KEY')
        if self.llm_provider == "gemini":
            api_key = self.config.get('GEMINI_API_KEY')
        elif self.llm_provider == "ollama":
            api_key = None 

        self.llm = LLMFactory.create_llm(
            self.llm_provider, 
            self.real_llm_path, 
            api_key=api_key, 
            openvino_device=self.hw_config.get('openvino_device', 'CPU')
        )
        return f"Successfully switched to {provider} ({self.real_llm_path})"

    def chat(self, user_text, history=None, use_memory=True, use_clipboard=False):
        if history is None:
            history = list(self.system_prompt)

        final_user_msg = user_text
        if use_memory:
            past_context = self.memory_db.get_context(user_text, n_results=3)
            if past_context:
                final_user_msg = f"Relevant past memories:\n{past_context}\n\nUser's current message: {user_text}"

        if use_clipboard:
            try:
                import pyperclip
                clip_text = pyperclip.paste()
                if clip_text and clip_text.strip():
                    history.append({"role": "system", "content": f"[System: User's clipboard: '{clip_text[:500]}']"})
            except:
                pass

        history.append({"role": "user", "content": final_user_msg})
        response = self.llm.generate(history)
        
        self.memory_db.add_memory(user_text, "user")
        self.memory_db.add_memory(response, "assistant")
        
        history.append({"role": "assistant", "content": response})
        return response, history
