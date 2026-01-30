from process.asr_func.asr_push_to_talk import record_audio
from process.tts_func.sovits_ping import sovits_gen, play_audio
from pathlib import Path
import os
import json
import yaml
import uuid
import logging

from hardware import HardwareDetector
from model_manager import ModelManager
from process.asr_func.asr_factory import ASRFactory
from process.llm_funcs.llm_factory import LLMFactory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(' \n ========= Starting Chat... ================ \n')

# Load Config
with open('character_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Hardware Detection
detector = HardwareDetector()
hw_config = detector.get_hardware_config()
logger.info(f"Hardware Config: {hw_config}")

backend = config.get('backend_preference', 'auto')
if backend == 'auto':
    backend = hw_config['backend']
logger.info(f"Selected Backend: {backend}")

# Initialize ASR
asr_path = config.get('local_asr_path', 'base.en')
try:
    # ASR Factory handles backend selection (cuda, openvino, cpu_legacy)
    asr = ASRFactory.create_asr(backend, asr_path)
except Exception as e:
    logger.error(f"Failed to initialize ASR: {e}")
    exit(1)

# Initialize LLM
mm = ModelManager()
llm_path = config.get('local_llm_path', 'models/riko-llm')

# Determine LLM Backend
# Logic:
# - If backend is OpenVINO -> Use OpenVINO LLM
# - If backend is CPU Legacy / Generic CPU (no CUDA) -> Use GGUF
# - If backend is CUDA -> Default to OpenAI (or CUDA Local if implemented, but strictly OpenAI is default for Riko)
llm_backend = backend

if backend == 'cuda':
    llm_backend = "openai"
elif backend not in ['openvino']:
    # Fallback for CPU / Legacy -> GGUF
    llm_backend = "cpu_legacy"

# Resolve model path (find quantized versions if local)
if llm_backend in ["openvino", "cpu_legacy"]:
    real_llm_path = mm.find_model(llm_path, llm_backend)
else:
    real_llm_path = config['model'] # OpenAI model name

logger.info(f"Initializing LLM: {llm_backend} with {real_llm_path}")
try:
    llm = LLMFactory.create_llm(llm_backend, real_llm_path, api_key=config.get('OPENAI_API_KEY'))
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    exit(1)


# History Management
HISTORY_FILE = config['history_file']
SYSTEM_PROMPT = [{"role": "system", "content": config['presets']['default']['system_prompt']}]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return list(SYSTEM_PROMPT)

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

while True:
    conversation_recording = Path("audio") / "conversation.wav"
    conversation_recording.parent.mkdir(parents=True, exist_ok=True)

    # Record
    try:
        record_audio(str(conversation_recording))
    except Exception as e:
        logger.error(f"Recording failed: {e}")
        continue

    # Transcribe
    try:
        user_spoken_text = asr.transcribe(str(conversation_recording))
        print(f"User: {user_spoken_text}")
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        continue

    if not user_spoken_text:
        continue

    # LLM Generation
    messages = load_history()
    messages.append({"role": "user", "content": user_spoken_text})

    print("Riko is thinking...")
    try:
        response = llm.generate(messages)
        print(f"Riko: {response}")
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        continue

    messages.append({"role": "assistant", "content": response})
    save_history(messages)

    # TTS
    uid = uuid.uuid4().hex
    filename = f"output_{uid}.wav"
    output_wav_path = Path("audio") / filename
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        gen_aud_path = sovits_gen(response, output_wav_path)
        play_audio(output_wav_path)
    except Exception as e:
        logger.error(f"TTS failed: {e}")

    # Cleanup
    [fp.unlink() for fp in Path("audio").glob("*.wav") if fp.is_file()]
