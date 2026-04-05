from process.asr_func.asr_continuous import listen_continuously
from process.tts_func.sovits_ping import sovits_gen, play_audio
from pathlib import Path
import os
import json
import yaml
import uuid
import logging
import pyperclip

from hardware import HardwareDetector
from model_manager import ModelManager
from process.asr_func.asr_factory import ASRFactory
from process.llm_funcs.llm_factory import LLMFactory
from memory_manager import MemoryManager

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
    llm = LLMFactory.create_llm(llm_backend, real_llm_path, api_key=config.get('OPENAI_API_KEY'), openvino_device=hw_config.get('openvino_device', 'CPU'))
except Exception as e:
    logger.error(f"Failed to initialize LLM: {e}")
    exit(1)


# History Management
HISTORY_FILE = config['history_file']
SYSTEM_PROMPT = [{"role": "system", "content": config['presets']['default']['system_prompt']}]
memory_db = MemoryManager(db_path="chroma_db")

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
    
    # Retrieve long-term memory context
    past_context = memory_db.get_context(user_spoken_text, n_results=3)
    if past_context:
        context_msg = f"Relevant past memories:\n{past_context}\n\nUser's current message: {user_spoken_text}"
        messages.append({"role": "user", "content": context_msg})
    else:
        messages.append({"role": "user", "content": user_spoken_text})

    print("Riko is thinking...")
    
    # Screen Awareness: Read Clipboard
    try:
        clip_text = pyperclip.paste()
        if clip_text and clip_text.strip():
            # Inject clipboard silently
            messages.append({"role": "system", "content": f"[System: The user's current clipboard contains: '{clip_text[:500]}']"})
    except Exception:
        pass

    try:
        response = llm.generate(messages)
        print(f"Riko: {response}")
    except Exception as e:
        logger.error(f"LLM Generation failed: {e}")
        continue

    messages.append({"role": "assistant", "content": response})
    save_history(messages)
    
    # Save to long-term memory
    memory_db.add_memory(user_spoken_text, "user")
    memory_db.add_memory(response, "assistant")

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
