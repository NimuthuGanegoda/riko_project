FROM python:3.10-slim

# ffmpeg: required for audio/voice (per README).
# libsndfile1: required by `soundfile`.
# libportaudio2: `sounddevice` is imported at module level by the TTS/ASR
#   providers -- the import must succeed even though no physical audio
#   device exists in a container, or the process won't even start.
# build-essential, cmake, git: several deps (pyopenjtalk, ctranslate2,
#   llama-cpp-python) compile native extensions at install time.
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 libportaudio2 build-essential cmake git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements/ requirements/

# CPU-only torch by default -- portable to any server, no GPU required. If
# your deploy target has an NVIDIA GPU + nvidia-container-toolkit, swap this
# for the CUDA wheel install install_reqs.sh uses instead.
RUN pip install --no-cache-dir uv \
    && uv pip install --system torch torchaudio \
    && uv pip install --system -r requirements/extra-req.txt --no-deps \
    && uv pip install --system -r requirements/requirements.txt \
    # Imported somewhere under backend/ but absent from every requirements
    # file above -- see docs/DEPLOYMENT.md. Locally this is masked because
    # RikoCore's init is wrapped in try/except (missing import just leaves
    # `riko = None` and every endpoint 500s); in a container it must be
    # explicit or the app silently never actually starts working.
    && uv pip install --system chromadb ollama google-generativeai pyperclip \
       google-auth google-auth-oauthlib

COPY backend/ backend/
COPY main.py .

# Not copying configs/ or character_files/ into the image -- mount them as
# read-only volumes at runtime (see docker-compose.yml) so real API keys
# never end up baked into an image layer.

ENV RIKO_HOST=0.0.0.0
WORKDIR /app/backend
EXPOSE 8000
CMD ["python3", "api.py"]
