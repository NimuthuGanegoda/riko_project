# Pinned to bookworm (not the floating `slim` tag) specifically: `slim`
# currently resolves to trixie's GCC 14, which has a libstdc++ regression
# that breaks llama-cpp-python's vendored cpp-httplib build
# ("_M_move_assign was not declared in this scope" in unordered_set.h) --
# verified by actually hitting this while building this image. bookworm's
# GCC 12 doesn't have the bug.
FROM python:3.10-slim-bookworm

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

RUN pip install --no-cache-dir uv

# CPU-only torch by default -- portable to any server, no GPU required. The
# CPU index URL matters: plain `pip install torch` pulls PyPI's default
# build, which bundles full CUDA/nvidia-* wheels (400MB+ each, GBs total)
# even when there's no GPU to use them -- verified while building this
# image. If your deploy target has an NVIDIA GPU + nvidia-container-toolkit,
# swap this for the CUDA wheel install install_reqs.sh uses instead.
RUN uv pip install --system torch torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install --system -r requirements/extra-req.txt --no-deps
RUN uv pip install --system -r requirements/requirements.txt

# requirements/requirements.txt alone assumes a "modern" CPU (AVX2).
# backend/core/hardware.py auto-detects the CPU at runtime and falls back to
# the "cpu_legacy" ASR/LLM path when it doesn't find AVX2 -- which happens
# on some virtualized/cloud CPUs. Verified by actually running this image:
# without requirements_legacy.txt, RikoCore's startup silently fails ("No
# module named 'pywhispercpp'", caught by a try/except that just leaves
# `riko = None`, so every endpoint 500s with no obvious cause). Install both
# so it works regardless of what CPU the container ends up on.
RUN uv pip install --system -r requirements/requirements_legacy.txt

# Imported somewhere under backend/ but absent from every requirements file
# above -- see docs/DEPLOYMENT.md. Locally this is masked because RikoCore's
# init is wrapped in try/except (missing import just leaves `riko = None`
# and every endpoint 500s); in a container it must be explicit or the app
# silently never actually starts working.
RUN uv pip install --system chromadb ollama google-generativeai pyperclip \
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
