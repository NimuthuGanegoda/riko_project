# 🌸 Project Riko: The Autonomous AI Companion

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Multi-Brain](https://img.shields.io/badge/LLM-Gemini_Pro%20%7C%20ChatGPT%20%7C%20Ollama-blueviolet)](https://github.com/NimuthuGanegoda/riko_project)
[![Google Pro](https://img.shields.io/badge/Google-Gemini_Pro_💎-4285F4?logo=google-gemini&logoColor=white)](https://aistudio.google.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20iOS%20%7C%20Android-green)](https://github.com/NimuthuGanegoda/riko_project)

Project Riko is an elite, autonomous anime-focused AI companion. She doesn't just respond; she listens, remembers, and observes your world. By combining advanced LLM support with expressive voice synthesis and real-time screen awareness, Riko bridges the gap between software and personality.

---

## 📂 Project Structure

Project Riko is built with a clean, modular architecture for maximum performance and portability:
- **`backend/`**: Core engine, hardware-accelerated providers (ASR, LLM, TTS), and API server.
- **`client/`**: Modern React-based Web UI with PWA support for mobile devices.
- **`configs/`**: Character personalities and system-wide configuration files.
- **`docs/`**: Detailed guides for optimization and platform-specific tweaks.
- **`requirements/`**: Optimized dependency lists for various hardware (CUDA, ROCm, NPU, Potato).
- **`scripts/`**: Utility scripts for model conversion and potato-system optimization.

---

## ✨ Elite Features

| Feature | Description |
| :--- | :--- |
| 🧠 **Persistent Memory** | Uses **ChromaDB** (RAG) to remember every detail of your past conversations forever. |
| 🎓 **Autonomous Learning** | **Mem0-style Fact Manager** that learns and remembers your personal details forever. |
| 👂 **Cortana Mode** | **Continuous Listening** with VAD. Just say her name (**"Riko"**) to wake her up. |
| 🤖 **Active Assistant** | She can execute actions for you! Ask her to open websites, check the time, or launch apps. |
| 💎 **Keyless Google Pro** | **Google Pro Subscription** integration via browser login (ADC). No manual API keys needed! |
| 🔄 **Dynamic Brain Swapping** | Switch between **Gemini**, **ChatGPT**, and **Ollama** on the fly through the Web UI. |
| ⚡ **Hardware Accelerated** | Optimized for **Intel NPU**, **Apple Silicon (Metal)**, **NVIDIA (CUDA)**, and **AMD (ROCm)**. |
| 👁️ **Full Screen Vision** | Powered by **PyAutoGUI**. Riko can capture and "see" your workspace to help you. |
| 🔊 **Expressive TTS** | Powered by **GPT-SoVITS** for high-quality, character-accurate voice synthesis. |
| 📱 **Mobile Ready** | Full **PWA Support**. Install Riko on your iPhone or Android home screen! |
| 🎬 **3D VRM Support** | (Alpha) Support for interactive **3D Anime Models** with lip-sync. |

---

## 🛠️ Setup & Installation

### 1. Automatic Install (Recommended)
This script installs all dependencies and triggers the Google Auth browser login automatically.

**Linux/Ubuntu:**
```bash
chmod +x install_reqs.sh
./install_reqs.sh
```

**Windows:**
```cmd
install_reqs.bat
```

### 2. Manual Dependencies
If you prefer manual control, use the optimized requirement files:
```bash
pip install uv 
uv pip install -r requirements/requirements.txt
uv pip install -r requirements/extra-req.txt
```

---

## ⚙️ Configuration

Customize Riko's personality in `configs/character_config.yaml`.

- **Google Pro (ADC):** Just sign in via the browser during installation.
- **ChatGPT:** Add your API key to the `OPENAI_API_KEY` field in the config.
- **Local Models:** Riko automatically detects your hardware and loads the best quantized GGUF/OpenVINO models.

---

## 🧪 Usage

### Terminal Mode (Voice + Text)
```bash
python3 main.py --chat
```

### Web & Mobile Mode (Recommended)
1. Start the backend:
   ```bash
   ./run_web.sh  # Linux
   run_web.bat   # Windows
   ```
2. Access the UI at `http://localhost:3000`.
3. **Mobile Setup:** On your iPhone or Android, open the URL and select **"Add to Home Screen"** to install Riko as an app!

---

## 🚀 Hardware Optimization

Riko is "Super Lite" and adapts to your system:
- **Intel Core Ultra:** Uses the **NPU** for zero-latency, low-power inference.
- **Mac M1/M2/M3:** Uses **Metal (MPS)** for native Apple Silicon speed.
- **AMD/NVIDIA:** Uses **ROCm/CUDA** for high-performance GPU acceleration.
- **Potato PC:** Falls back to legacy CPU mode with highly quantized models.

---

## 🧑‍🎤 Credits & Acknowledgments
*   **TTS**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
*   **ASR**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
*   **Memory**: [ChromaDB](https://github.com/chroma-core/chroma)
*   **Brains**: [OpenAI](https://openai.com), [Google Gemini](https://aistudio.google.com), [Ollama](https://ollama.com)

---

## 📜 License
MIT © Just Rayen. Enhanced & Re-Engineered by Nimuthu.
