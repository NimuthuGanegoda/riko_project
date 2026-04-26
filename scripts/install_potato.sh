#!/bin/bash

echo " ============================================"
echo "    AI Waifu Potato System Installation"
echo " ============================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Installing pip..."
    python3 -m ensurepip --upgrade
fi

echo "📦 Installing minimal dependencies for potato systems..."
pip install -r potato_requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "⚠️  Some packages failed to install, continuing anyway..."
fi

# Create necessary directories if they don't exist
mkdir -p audio
mkdir -p models

echo ""
echo "📝 Creating default configuration..."
if [ ! -f "potato_config.yaml" ]; then
    cat > potato_config.yaml << EOF
OPENAI_API_KEY: sk-YOURAPIKEY
history_file: chat_history_potato.json
model: "gpt-3.5-turbo"

# Potato-optimized settings
local_llm_path: "models/tiny-llm"
local_asr_path: "tiny.en"
backend_preference: "cpu_legacy"

presets:
  default:
    system_prompt: |
      You are Riko, a helpful and cheerful AI companion.
      You speak in a friendly, light-hearted manner.
      Keep your responses concise and avoid overly complex language.
      Be supportive and encouraging to your senpai.

sovits_ping_config:
  text_lang: en
  prompt_lang: en
  ref_audio_path: ./character_files/main_sample.wav
  prompt_text: This is a sample voice for you to just get started with because it sounds kind of cute.
EOF
    echo "✅ Created potato_config.yaml"
fi

echo ""
echo "🎮 Setup Complete!"
echo ""
echo "To start your AI Waifu on potato hardware:"
echo "  ./run_potato_waifu.sh"
echo ""
echo "Or directly run text mode:"
echo "  python potato_text_mode.py"
echo ""