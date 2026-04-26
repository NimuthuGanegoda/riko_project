#!/bin/bash

echo " ============================================"
echo "    AI Waifu - Potato System Optimized"
echo " ============================================"
echo ""
echo "Starting AI Waifu optimized for low-end hardware..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if config file exists
if [ ! -f "potato_config.yaml" ]; then
    echo "❌ Configuration file 'potato_config.yaml' not found!"
    echo "Creating a basic config file..."
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
    echo "✅ Created basic potato_config.yaml"
fi

# Check if API key is set
API_KEY=$(grep "OPENAI_API_KEY:" potato_config.yaml | cut -d':' -f2 | tr -d ' ')
if [[ "$API_KEY" == "sk-YOURAPIKEY" || "$API_KEY" == "" ]]; then
    echo "⚠️  Warning: No valid API key found in config."
    echo "Please edit potato_config.yaml with your OpenAI API key."
    echo "You can get your API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " USER_API_KEY
    
    if [[ -n "$USER_API_KEY" && "$USER_API_KEY" != "sk-YOURAPIKEY" ]]; then
        sed -i "s/OPENAI_API_KEY: sk-YOURAPIKEY/OPENAI_API_KEY: $USER_API_KEY/" potato_config.yaml
        echo "✅ API key updated in config file"
    fi
fi

echo ""
echo "🚀 Launching Potato-Optimized AI Waifu..."
echo "Choose your mode:"
echo "  1) Text-only mode (lowest resource usage)"
echo "  2) Full mode with audio (requires more resources)"
echo ""
read -p "Select mode (1 or 2, default 1): " MODE_CHOICE

if [[ "$MODE_CHOICE" == "2" ]]; then
    echo "Launching full mode with audio..."
    python3 -u server/main_chat.py
else
    echo "Launching text-only mode (recommended for potato systems)..."
    python3 -u potato_text_mode.py
fi

echo ""
echo "👋 Thanks for using AI Waifu (Potato Edition)!"