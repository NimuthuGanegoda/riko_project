import logging
import os

# Fix path to allow importing from backend
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

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

# Client (Vite dev server / built PWA) only ever talks to this API from
# localhost; no cookies/credentials are used, so we don't need "*" + credentials.
ALLOWED_ORIGINS = os.environ.get(
    "RIKO_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional shared-secret auth. Unset by default (keeps zero-config local use
# working) but strongly recommended once this is reachable beyond localhost.
API_KEY = os.environ.get("RIKO_API_KEY")


@app.middleware("http")
async def require_api_key(request, call_next):
    if API_KEY and request.url.path not in ("/docs", "/openapi.json"):
        if request.headers.get("x-api-key") != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    return await call_next(request)


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
    history: list[dict] | None = None
    use_vision: bool | None = False

class ModelSettings(BaseModel):
    provider: str
    model: str | None = None

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
        response_text, updated_history = riko.chat(request.text, history=request.history, use_vision=request.use_vision)
        
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
async def voice_endpoint(file: UploadFile = File(...), history: str = Form(None), use_vision: bool = Form(False)):
    global is_interrupted
    is_interrupted = False
    if riko.asr is None:
        return JSONResponse(
            status_code=501,
            content={"detail": "Server-side speech recognition is disabled on this deployment. Use browser speech recognition instead."}
        )
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
        response_text, updated_history = riko.chat(user_text, history=history_list, use_vision=use_vision)

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
    audio_dir = Path("audio").resolve()
    # Strip any path components the client tries to smuggle in (../, absolute
    # paths, etc.) so this can only ever resolve inside audio_dir.
    safe_name = Path(filename).name
    path = (audio_dir / safe_name).resolve()
    if path.parent != audio_dir or not path.exists():
        return JSONResponse(status_code=404, content={"detail": "Audio not found"})
    return FileResponse(path)

if __name__ == "__main__":
    import uvicorn
    # Default to loopback only; set RIKO_HOST=0.0.0.0 explicitly to expose on
    # the LAN (e.g. for a phone/overlay client), and set RIKO_API_KEY when you do.
    host = os.environ.get("RIKO_HOST", "127.0.0.1")
    # Hosts like Render assign the port dynamically via $PORT rather than
    # letting you fix it -- fall back to 8000 for local/Docker use.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host=host, port=port)
