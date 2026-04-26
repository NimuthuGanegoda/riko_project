# 🌸 Project Riko: The Autonomous AI Companion

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Brain](https://img.shields.io/badge/LLM-Gemini_Pro%20%7C%20ChatGPT%20%7C%20Ollama-blueviolet)](https://github.com/NimuthuGanegoda/riko_project)
[![Google Pro](https://img.shields.io/badge/Google-Gemini_Pro_💎-4285F4?logo=google-gemini&logoColor=white)](https://aistudio.google.com)

Project Riko is an elite, autonomous anime-focused AI companion. She doesn't just respond; she listens, remembers, and observes your world. By combining advanced LLM support with expressive voice synthesis and real-time screen awareness, Riko bridges the gap between software and personality.

---

## 📂 Project Structure
...
- `scripts/`: Maintenance and potato-system optimization tools.

---

## 📱 Multi-Platform Support

Project Riko is designed to follow you everywhere:

- **Windows:** Native `.bat` scripts for easy installation and execution.
- **Linux (Ubuntu/Debian):** Full shell script support with hardware-accelerated backends.
- **Mobile (iOS/Android):** Optimized **Progressive Web App (PWA)** interface. 
  - Access Riko on your phone by navigating to the Web UI and selecting **"Add to Home Screen"**.
  - Enjoy voice chat and AI assistance directly from your mobile device while the PC handles the heavy lifting!

---

## ✨ Elite Features

| Feature | Description |
| :--- | :--- |
| 🧠 **Persistent Memory** | Uses **ChromaDB** (RAG) to remember every detail of your past conversations forever. |
| 👂 **Cortana Mode** | **Continuous Listening** with VAD. Just say her name (**"Riko"**) to wake her up. |
| 💎 **Keyless Google Pro** | **Google Pro Subscription** integration via browser login (ADC). No manual API keys! |
| 🔄 **Dynamic Brain Swapping** | Switch between **Gemini**, **ChatGPT**, and **Ollama** on the fly through the Web UI. |
| 👁️ **Screen Awareness** | Automatically monitors your clipboard to provide context-aware assistance. |
| 🔊 **Expressive TTS** | Powered by **GPT-SoVITS** for high-quality, character-accurate voice synthesis. |
| 🎧 **Pro STT** | Powered by **Faster-Whisper** for lightning-fast speech-to-text transcription. |

---

## 🛠️ Setup & Installation

### 1. Automatic Install (Recommended)
Simply run the installation script. It will install all dependencies and **trigger the Google Auth browser login** for you!
```bash
chmod +x install_reqs.sh
./install_reqs.sh
```

### 2. Manual Dependencies
If you prefer manual control:
```bash
pip install uv 
uv pip install -r requirements/requirements.txt
uv pip install -r requirements/extra-req.txt
```

---

## ⚙️ Configuration

Customize Riko's personality in `configs/character_config.yaml`.

```yaml
# --- Default Brain ---
llm_provider: "gemini" 
model: "gemini-1.5-pro"  # Use that Pro power! 💎

# --- API Keys ---
OPENAI_API_KEY: "sk-..." # Your ChatGPT Key
```

---

## 🧪 Usage

1.  **Start your GPT-SoVITS API Server.**
2.  **Run the companion (Terminal Mode):**
    ```bash
    python3 main.py --chat
    ```
3.  **Run the companion (Web Mode):**
    ```bash
    ./run_web.sh
    ```
    Access the UI at `http://localhost:3000` to chat and switch models on the fly!

---

## 🧑‍🎤 Credits & Acknowledgments
*   **TTS**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
*   **ASR**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
*   **Memory**: [ChromaDB](https://github.com/chroma-core/chroma)
*   **Brains**: [OpenAI](https://openai.com), [Google Gemini](https://aistudio.google.com), [Ollama](https://ollama.com)

---

## 📜 License
MIT © Just Rayen. Updated & Enhanced by Nimuthu.
