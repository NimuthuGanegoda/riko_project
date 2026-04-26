import os
import uuid
import logging
import yaml
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional

# Fix path to allow importing from backend
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.riko_core import RikoCore
from providers.tts.sovits_ping import sovits_gen
from providers.vrm.vrm_controller import VRMController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Global state for visuals and interruption
vrm = VRMController()
is_interrupted = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

riko = None

@app.on_event("startup")
async def startup_event():
    global riko
    try:
        # Adjusted config path
        CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'configs', 'character_config.yaml')
        riko = RikoCore(config_path=CONFIG_PATH)
        logger.info("RikoCore initialized successfully for Web API.")
    except Exception as e:
        logger.error(f"Failed to initialize RikoCore: {e}")

class ChatRequest(BaseModel):
    text: str
    history: Optional[List[dict]] = None

class ModelSettings(BaseModel):
    provider: str
    model: Optional[str] = None

@app.get("/settings")
async def get_settings():
    return {
        "provider": riko.llm_provider,
        "model": riko.real_llm_path,
        "available_providers": ["gemini", "openai", "ollama", "openvino", "cpu_legacy", "llama_cpp"]
    }

@app.post("/settings")
async def update_settings(settings: ModelSettings):
    try:
        msg = riko.switch_model(settings.provider, settings.model)
        return {"message": msg, "provider": riko.llm_provider, "model": riko.real_llm_path}
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/interrupt")
async def interrupt_endpoint():
    global is_interrupted
    is_interrupted = True
    logger.info("❌ Interruption signal received.")
    return {"status": "ok", "message": "Stopping generation/playback"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global is_interrupted
    is_interrupted = False 
    try:
        response_text, updated_history = riko.chat(request.text, history=request.history)
        
        if is_interrupted:
            return JSONResponse(status_code=204, content={"message": "Interrupted"})

        vrm_state = vrm.update_vrm_state(response_text)
        
        uid = uuid.uuid4().hex
        audio_filename = f"web_output_{uid}.wav"
        audio_path = Path("audio") / audio_filename
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        
        audio_url = None
        try:
            gen_path = sovits_gen(response_text, str(audio_path))
            if gen_path:
                audio_url = f"/audio/{audio_filename}"
        except Exception as e:
            logger.error(f"TTS Failed: {e}")

        return {
            "text": response_text,
            "history": updated_history,
            "audio_url": audio_url,
            "vrm_state": vrm_state
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/voice")
async def voice_endpoint(file: UploadFile = File(...), history: str = Form(None)):
    global is_interrupted
    is_interrupted = False
    try:
        temp_audio = Path("audio") / f"temp_upload_{uuid.uuid4().hex}.wav"
        temp_audio.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_audio, "wb") as buffer:
            buffer.write(await file.read())

        user_text = riko.asr.transcribe(str(temp_audio))
        temp_audio.unlink()
        
        if not user_text:
            return JSONResponse(status_code=400, content={"detail": "Could not hear anything."})

        import json
        history_list = json.loads(history) if history else None
        response_text, updated_history = riko.chat(user_text, history=history_list)

        if is_interrupted:
            return JSONResponse(status_code=204, content={"message": "Interrupted"})

        vrm_state = vrm.update_vrm_state(response_text)

        uid = uuid.uuid4().hex
        audio_filename = f"web_output_{uid}.wav"
        audio_path = Path("audio") / audio_filename
        
        audio_url = None
        try:
            gen_path = sovits_gen(response_text, str(audio_path))
            if gen_path:
                audio_url = f"/audio/{audio_filename}"
        except Exception as e:
            logger.error(f"TTS Failed: {e}")

        return {
            "user_text": user_text,
            "text": response_text,
            "history": updated_history,
            "audio_url": audio_url,
            "vrm_state": vrm_state
        }
    except Exception as e:
        logger.error(f"Voice chat failed: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    path = Path("audio") / filename
    if path.exists():
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"detail": "Audio not found"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
