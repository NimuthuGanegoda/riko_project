# 🪟 Windows Setup Guide

This guide will help you get Project Riko running perfectly on Windows.

## 📋 Prerequisites

1.  **Python 3.10+**: Download from [python.org](https://www.python.org/). **IMPORTANT**: Check the box that says "Add Python to PATH" during installation.
2.  **FFmpeg**: Required for audio/voice features.
    - Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
    - Extract it and add the `bin` folder to your System environment variables (PATH).
3.  **Git**: Download from [git-scm.com](https://git-scm.com/).

## 🚀 Installation

1.  Open a terminal (Command Prompt or PowerShell) in the project folder.
2.  Run the installer:
    ```cmd
    install_reqs.bat
    ```
3.  Follow the browser prompts to sign in with your Google account (for Google Pro features).

## 🧪 Usage

- **Web Mode (Recommended)**: Run `run_web.bat`. Then open your browser to `http://localhost:3000`.
- **Terminal Mode**: Run `python main.py --chat`.

## 🛠️ Troubleshooting

### 1. "python is not recognized..."
This means Python isn't in your PATH. Re-install Python and check the "Add to PATH" box, or add it manually in System Environment Variables.

### 2. Audio/Mic not working
Ensure your default microphone is set correctly in Windows Sound Settings. Riko uses the default system recording device.

### 3. Screen Vision Errors
If `pyautogui` fails, ensure your display scaling is set to 100% for best results, or run the terminal as Administrator.

---
🌸 Enjoy your elite companion on Windows!
