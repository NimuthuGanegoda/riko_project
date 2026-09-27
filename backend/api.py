import json
import logging
import os
import time

# Fix path to allow importing from backend
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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
    # AIRI's dev server may choose a different local port. Production origins
    # still need to be explicitly listed in RIKO_ALLOWED_ORIGINS.
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional shared-secret auth. Unset by default (keeps zero-config local use
# working) but strongly recommended once this is reachable beyond localhost.
API_KEY = os.environ.get("RIKO_API_KEY")


@app.middleware("http")
async def require_api_key(request, call_next):
    if API_KEY and request.url.path not in ("/docs", "/openapi.json", "/health"):
        # Native Riko clients use X-API-Key; OpenAI-compatible clients such as
        # AIRI use Authorization: Bearer. Accept either without duplicating keys.
        bearer = request.headers.get("authorization", "")
        bearer_key = bearer[7:] if bearer.lower().startswith("bearer ") else None
        if request.headers.get("x-api-key") != API_KEY and bearer_key != API_KEY:
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


class OpenAIChatRequest(BaseModel):
    """Subset of the OpenAI chat schema used by AIRI and similar clients."""

    model: str = "riko"
    messages: list[dict]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


def unavailable_response():
    return JSONResponse(
        status_code=503,
        content={"detail": "RikoCore is not initialized. Check the server logs and model configuration."},
    )


@app.get("/health")
async def health():
    return JSONResponse(
        status_code=200 if riko is not None else 503,
        content={"status": "ok" if riko is not None else "unavailable"},
    )


@app.get("/v1/models")
async def openai_models():
    """Expose Riko as an OpenAI-compatible provider for the AIRI frontend."""
    if riko is None:
        return unavailable_response()
    model = str(riko.real_llm_path or "riko")
    return {"object": "list", "data": [{"id": model, "object": "model", "owned_by": "riko"}]}


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: OpenAIChatRequest):
    if riko is None:
        return unavailable_response()

    messages = [m for m in request.messages if m.get("role") in {"system", "user", "assistant"}]
    user_indices = [i for i, m in enumerate(messages) if m.get("role") == "user"]
    if not user_indices:
        return JSONResponse(status_code=400, content={"error": {"message": "A user message is required"}})

    last_user = user_indices[-1]
    content = messages[last_user].get("content", "")
    # AIRI normally sends text, but tolerate OpenAI's structured text parts.
    if isinstance(content, list):
        content = "\n".join(
            str(part.get("text", "")) for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    history = messages[:last_user]
    try:
        text, _ = riko.chat(str(content), history=history)
    except Exception as exc:
        logger.exception("OpenAI-compatible chat failed")
        return JSONResponse(status_code=500, content={"error": {"message": str(exc)}})

    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())
    model = request.model or str(riko.real_llm_path or "riko")

    if request.stream:
        def events():
            chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{"index": 0, "delta": {"role": "assistant", "content": text}, "finish_reason": None}],
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            chunk["choices"] = [{"index": 0, "delta": {}, "finish_reason": "stop"}]
            yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@app.get("/settings")
async def get_settings():
    if riko is None:
        return unavailable_response()
    return {
        "provider": riko.llm_provider,
        "model": riko.real_llm_path,
        "available_providers": ["gemini", "openai", "ollama", "openvino", "cpu_legacy", "llama_cpp"]
    }

@app.post("/settings")
async def update_settings(settings: ModelSettings):
    if riko is None:
        return unavailable_response()
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
    if riko is None:
        return unavailable_response()
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
    if riko is None:
        return unavailable_response()
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
