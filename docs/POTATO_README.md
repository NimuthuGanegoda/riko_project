# AI Waifu for Potato Systems

A lightweight, optimized version of the AI Waifu application designed to run smoothly on low-end hardware (potato systems).

## 🥔 What Makes This "Potato-Optimized"

- **Minimal resource usage**: Designed for systems with limited CPU, RAM, and no dedicated GPU
- **CPU-only operation**: No GPU acceleration required
- **Lightweight models**: Uses smaller, quantized models for efficient processing
- **Text-first approach**: Optional text-only mode to reduce computational overhead
- **Simplified dependencies**: Reduced package requirements

## 🚀 Quick Start

### Option 1: Run the Launcher Script (Recommended)
```bash
./run_potato_waifu.sh
```

### Option 2: Manual Setup
1. Install minimal dependencies:
```bash
pip install -r potato_requirements.txt
```

2. Configure your API key in `potato_config.yaml`:
```bash
# Edit the config file and replace 'sk-YOURAPIKEY' with your actual OpenAI API key
nano potato_config.yaml
```

3. Run the text-only mode (lightest option):
```bash
python potato_text_mode.py
```

## ⚙️ Configuration Options

### Potato-Optimized Settings
- `backend_preference: "cpu_legacy"` - Forces CPU-only operation
- `model: "gpt-3.5-turbo"` - Uses a lighter model for faster responses
- `local_asr_path: "tiny.en"` - Uses smallest Whisper model for speech recognition

### Resource-Saving Tips
- Use text-only mode instead of full audio processing
- Choose lighter LLM models (like gpt-3.5-turbo instead of gpt-4)
- Use quantized models (Q4, Q8) when running locally
- Close other applications while running the AI Waifu

## 📋 System Requirements (Potato Level)

### Minimum Requirements:
- CPU: Dual-core processor (Intel/AMD)
- RAM: 2GB+ free memory
- Storage: 500MB free space
- OS: Windows, macOS, or Linux
- Internet: Required for OpenAI API (recommended for potato systems)

### Recommended for Better Experience:
- CPU: Quad-core processor
- RAM: 4GB+ free memory
- SSD storage (for faster loading)

## 🛠️ Modes of Operation

### 1. Text-Only Mode (Lowest Resource Usage)
```bash
python potato_text_mode.py
```
- No audio processing
- Fastest response times
- Minimal memory usage
- Best for very low-end systems

### 2. Full Mode with Audio (More Resources Required)
```bash
python server/main_chat.py
```
- Includes voice synthesis and speech recognition
- Higher quality experience
- Requires more CPU and memory

## 🛡️ Privacy Considerations

- When using OpenAI API (recommended for potato systems), conversations are processed remotely
- Local conversation history is stored in `chat_history_potato.json`
- Audio files are temporary and cleaned up after each interaction

## 🐛 Troubleshooting

### Common Issues:
- **"Out of memory" errors**: Use text-only mode instead of full audio mode
- **Slow responses**: Switch to lighter models (gpt-3.5-turbo)
- **Missing dependencies**: Run `pip install -r potato_requirements.txt`
- **No audio on some systems**: Use text-only mode

### Performance Optimization:
1. Close unnecessary applications
2. Use text-only mode for fastest performance
3. Ensure sufficient free RAM (at least 1GB)
4. Use OpenAI API instead of local models for potato systems

## 📞 Support

For issues specific to potato systems, please check:
- POTATO_GUIDE.md for detailed optimization information
- Run `./run_potato_waifu.sh` for automated setup assistance
- Use text-only mode if experiencing performance issues

---

Enjoy your AI Waifu experience even on the humblest of systems! 🥔💕