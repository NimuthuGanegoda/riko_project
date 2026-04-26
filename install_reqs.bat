@echo off
echo 🌸 Project Riko: Windows Installation 🌸

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

:: Install UV for faster installs
pip install uv

:: Install dependencies
echo Installing core dependencies...
uv pip install -r requirements\requirements.txt
uv pip install -r requirements\extra-req.txt
uv pip install google-auth google-auth-oauthlib

:: Trigger Google Auth
echo --------------------------------------------------------
echo 🌟 TRIGGERING GOOGLE PRO AUTHENTICATION 🌟
echo Senpai, I'm opening your browser so you can sign in!
echo --------------------------------------------------------
gcloud auth application-default login

:: Download NLTK data
python -c "import nltk; nltk.download('averaged_perceptron_tagger'); nltk.download('cmudict')"

echo 🌸 Installation Complete! Run run_web.bat to start Riko. 🌸
pause
