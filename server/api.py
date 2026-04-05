import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional

from riko_core import RikoCore
from process.tts_func.sovits_ping import sovits_gen

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RikoCore
# We lazy-load it or initialize on startup
riko = None

@app.on_event("startup")
async def startup_event():
    global riko
    try:
        riko = RikoCore(config_path='character_config.yaml')
        logger.info("RikoCore initialized successfully for Web API.")
    except Exception as e:
        logger.error(f"Failed to initialize RikoCore: {e}")

class ChatRequest(BaseModel):
    text: str
    history: Optional[List[dict]] = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response_text, updated_history = riko.chat(request.text, history=request.history)
        
        # Generate Audio
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
            "audio_url": audio_url
        }
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/voice")
async def voice_endpoint(file: UploadFile = File(...), history: str = Form(None)):
    try:
        # Save temporary recording
        temp_audio = Path("audio") / f"temp_upload_{uuid.uuid4().hex}.wav"
        temp_audio.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_audio, "wb") as buffer:
            buffer.write(await file.read())

        # Transcribe
        user_text = riko.asr.transcribe(str(temp_audio))
        temp_audio.unlink() # Cleanup
        
        if not user_text:
            return JSONResponse(status_code=400, content={"detail": "Could not hear anything."})

        # Chat
        import json
        history_list = json.loads(history) if history else None
        response_text, updated_history = riko.chat(user_text, history=history_list)

        # Generate Audio
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
            "audio_url": audio_url
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
