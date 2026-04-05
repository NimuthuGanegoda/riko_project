# 🌸 Project Riko: The Autonomous AI Companion

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Brain](https://img.shields.io/badge/LLM-OpenAI%20%7C%20Gemini%20%7C%20Ollama-blueviolet)](https://github.com/NimuthuGanegoda/riko_project)

Project Riko is an elite, autonomous anime-focused AI companion. She doesn't just respond; she listens, remembers, and observes your world. By combining advanced LLM support with expressive voice synthesis and real-time screen awareness, Riko bridges the gap between software and personality.

---

## ✨ Elite Features

| Feature | Description |
| :--- | :--- |
| 🧠 **Persistent Memory** | Uses **ChromaDB** (RAG) to remember every detail of your past conversations forever. |
| 👂 **Cortana Mode** | **Continuous Listening** with VAD. Just say her name (**"Riko"**) to wake her up. |
| 👁️ **Screen Awareness** | Automatically monitors your clipboard to provide context-aware assistance. |
| 💬 **Multi-Brain** | Toggle between **OpenAI GPT**, **Google Gemini**, and **Ollama (Local)**. |
| 🔊 **Expressive TTS** | Powered by **GPT-SoVITS** for high-quality, character-accurate voice synthesis. |
| 🎧 **Pro STT** | Powered by **Faster-Whisper** for lightning-fast speech-to-text transcription. |

---

## 🚀 The Autonomous Flow

1.  **Continuous Listen**: Riko sits in the background, monitoring audio for activity.
2.  **Wake Word Detection**: When you say her name, she triggers her recording loop.
3.  **Context Injection**: She automatically retrieves past memories and reads your current clipboard.
4.  **Inference**: Your chosen LLM (Remote or Local) generates a snarky or sweet response.
5.  **Voice Synthesis**: Her response is synthesized into high-quality audio in real-time.
6.  **Interaction Complete**: She goes back to sleep, waiting for you to call her again.

---

## 🛠️ Setup & Installation

### 1. Install Core Dependencies
We recommend using `uv` for lightning-fast package management:
```bash
pip install uv 
uv pip install -r requirements.txt
pip install chromadb pyperclip sounddevice soundfile numpy google-generativeai ollama
```

### 2. System Requirements
*   **Audio**: `ffmpeg` (global) and `libportaudio2` (Linux: `sudo apt install libportaudio2`).
*   **GPU (Optional)**: CUDA/cuDNN for Faster-Whisper and Local LLM acceleration.
*   **TTS Server**: Ensure your [GPT-SoVITS API](https://github.com/RVC-Boss/GPT-SoVITS) is running.

---

## ⚙️ Configuration

Customize Riko's personality and brain in `character_config.yaml`.

```yaml
# --- LLM Settings ---
llm_provider: "gemini"    # Options: openai, gemini, ollama, auto
model: "gemini-1.5-flash" # The model name (e.g., "llama3" for Ollama)

# --- API Keys ---
OPENAI_API_KEY: "sk-..."
GEMINI_API_KEY: "..."

# --- Personality ---
presets:
  default:
    system_prompt: |
      You are Riko, a snarky yet affectionate anime girl. 
      You are helpful but often tease your "senpai".
```

---

## 🧪 Usage

1.  **Start your GPT-SoVITS API Server.**
2.  **Run the companion:**
    ```bash
    python server/main_chat.py
    ```
3.  **Run the Web Interface (Optional):**
    ```bash
    ./run_web.sh
    ```
    Access the UI at `http://localhost:3000`.
4.  **Say "Riko"** followed by your message. She will listen and respond!

---

## 📌 Roadmap
- [x] Continuous Listening (VAD)
- [x] Long-Term Memory (RAG)
- [x] Multi-LLM Provider Support
- [ ] Live2D / VRM Visual Frontend
- [ ] Real-time Emotion/Tone Control
- [ ] Desktop Overlay Interface

---

## 🧑‍🎤 Credits & Acknowledgments
*   **TTS**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
*   **ASR**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
*   **Memory**: [ChromaDB](https://github.com/chroma-core/chroma)
*   **Brains**: [OpenAI](https://openai.com), [Google Gemini](https://aistudio.google.com), [Ollama](https://ollama.com)

---

## 📜 License
MIT © Just Rayen.
Feel free to clone, modify, and build your own waifu companion. Stay elite!
