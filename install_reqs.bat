@echo off
setlocal enabledelayedexpansion

echo 🌸 Project Riko: Windows Elite Installation 🌸

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    pause
    exit /b
)

:: Install UV for lightning-fast installs
echo 🚀 Installing UV package manager...
pip install uv

:: Install core dependencies from the new modular structure
echo 📦 Installing core dependencies...
uv pip install -r requirements\requirements.txt
uv pip install -r requirements\extra-req.txt
uv pip install google-auth google-auth-oauthlib

:: Trigger Google Auth (ADC)
echo --------------------------------------------------------
echo 🌟 TRIGGERING GOOGLE PRO AUTHENTICATION 🌟
echo Senpai, I'm opening your browser so you can sign in!
echo --------------------------------------------------------
gcloud auth application-default login || (
    echo ⚠️ Note: gcloud CLI not found. 
    echo If you want to use browser-based login, please install Google Cloud SDK.
    echo Otherwise, you can manually enter your API keys in configs\character_config.yaml.
)

:: Download NLTK data
echo 📚 Downloading NLP models...
python -c "import nltk; nltk.download('averaged_perceptron_tagger'); nltk.download('cmudict')"

echo.
echo 🌸 Installation Complete! 🌸
echo 💡 Use 'run_web.bat' to start the Web/Mobile UI.
echo 💡 Use 'python main.py --chat' for Terminal Mode.
pause
