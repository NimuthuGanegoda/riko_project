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

## 🛠️ Complete Installation Guide

### 📋 Prerequisites

Before you start, ensure you have the following installed:
1.  **Python 3.10+**: Download from [python.org](https://www.python.org/).
2.  **FFmpeg**: Required for audio/voice features.
    - **Linux**: `sudo apt install ffmpeg`
    - **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add `bin` to your PATH.
3.  **Git**: Download from [git-scm.com](https://git-scm.com/).
4.  **Google Cloud CLI** (Optional but Recommended): For browser-based Google Pro login.

### 🚀 Automatic Installation (Fastest)

Clone the repository and run the installer for your platform:

**Linux / Ubuntu:**
```bash
git clone https://github.com/NimuthuGanegoda/riko_project.git
cd riko_project
chmod +x install_reqs.sh
./install_reqs.sh
```

**Windows:**
```cmd
git clone https://github.com/NimuthuGanegoda/riko_project.git
cd riko_project
install_reqs.bat
```

The installer will automatically:
- Install the `uv` package manager for lightning-fast dependencies.
- Install all core and extra requirements (Vision, 3D, etc.).
- **Open your browser** to sign in with Google for your Pro subscription.
- Download necessary NLP models (NLTK).

### 📱 Mobile Installation (iOS/Android)

Riko is a Progressive Web App (PWA). To take her with you:
1.  Run the backend on your PC (see Usage below).
2.  Open your mobile browser and navigate to your PC's IP address on port 3000 (e.g., `http://192.168.1.10:3000`).
3.  Select **"Add to Home Screen"** (iOS: Share button -> Add to Home Screen | Android: Menu -> Install App).
4.  Riko will now appear as an app on your home screen with full mic access!

---

## ⚙️ Configuration

Customize Riko's personality and brains in `configs/character_config.yaml`.

- **Google Pro (ADC):** Just sign in via the browser during installation. Riko will automatically use your subscription!
- **ChatGPT:** Add your API key to the `OPENAI_API_KEY` field.
- **Local Models:** Riko automatically detects your hardware (NPU, Metal, CUDA) and loads the best models.

---

## 🧪 Usage

### 💬 Terminal Mode
For a quick voice/text chat in your console:
```bash
python3 main.py --chat
```

### 🌐 Web & Mobile Mode (Full Experience)
1. Start the backend API:
   ```bash
   ./run_web.sh  # Linux
   run_web.bat   # Windows
   ```
2. The UI will be available at `http://localhost:3000`. You can now chat, see her expressions, and switch models on the fly!

---

## 🚀 Hardware Optimization

Riko is designed to be "Super Lite" and adapts to your system:
- **Intel Core Ultra:** Automatically uses the **NPU** for ultra-low power inference.
- **Apple Silicon (M1/M2/M3):** Uses **Metal (MPS)** for native Mac speed.
- **AMD/NVIDIA GPUs:** Uses **ROCm/CUDA** for high-performance acceleration.
- **Potato PC:** Falls back to legacy CPU mode with highly quantized models to ensure smooth operation on older hardware.

---

## 🧑‍🎤 Credits & Acknowledgments
*   **TTS**: [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
*   **ASR**: [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
*   **Memory**: [ChromaDB](https://github.com/chroma-core/chroma)
*   **Brains**: [OpenAI](https://openai.com), [Google Gemini](https://aistudio.google.com), [Ollama](https://ollama.com)
*   **Visual Logic**: Inspired by and integrated from [AIRI (moeru-ai/airi)](https://github.com/moeru-ai/airi).
*   **Interruption Flow**: Logic refined based on [Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber).
*   **Learning Engine**: Autonomous fact management inspired by [Mem0](https://github.com/mem0ai/mem0).

---

## 📜 License
MIT © Just Rayen. Enhanced & Re-Engineered by Nimuthu.
