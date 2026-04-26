# AI Waifu for Potato Systems Guide

This guide explains how to optimize the AI Waifu application for low-end hardware systems with limited resources.

## What makes this "Potato-Optimized"

1. **CPU-only operation**: No GPU requirements
2. **Lightweight model selection**: Uses quantized models that run efficiently on CPUs
3. **Minimal memory footprint**: Optimized for systems with limited RAM
4. **Reduced feature set**: Focuses on essential functionality

## Configuration for Potato Systems

The system automatically detects hardware capabilities and selects the optimal backend, even on ultra-low-power devices:

- **Intel NPU (Core Ultra):** Automatically prioritizes the Neural Processing Unit via OpenVINO. This drains almost zero battery compared to CPU/GPU.
- **Apple Silicon (M1/M2/M3):** Native Metal (MPS) support. To ensure `llama-cpp-python` installs with Metal support, run:
  ```bash
  CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
  ```
- **AMD GPUs (ROCm):** Automatically routes to hardware acceleration if PyTorch ROCm is detected.
- **Legacy CPUs:** Falls back to legacy CPU mode with lightweight models.
- **No GPU acceleration:** All processing runs on CPU to minimize complexity.

## Recommended Settings for Low-End Hardware

### Character Configuration (`potato_config.yaml`)
```yaml
OPENAI_API_KEY: sk-YOURAPIKEY  # Use OpenAI API to offload heavy computation
history_file: chat_history.json
model: "gpt-3.5-turbo"  # Lighter model than gpt-4.1-mini

# Low-end hardware settings
local_llm_path: "models/tiny-llm"  # Placeholder for tiny model
local_asr_path: "tiny.en"  # Lightweight ASR model
backend_preference: "cpu_legacy"  # Force CPU-only operation

presets:
  default:
    system_prompt: |
      You are Riko, a helpful assistant.
      You speak in a friendly and cheerful manner.
      Keep responses concise and to the point.

sovits_ping_config:
  text_lang: en
  prompt_lang: en
  ref_audio_path: ./character_files/main_sample.wav
  prompt_text: This is a sample voice for you to just get started with.
```

## Alternative Text-Only Mode

For extremely limited systems, consider using the text-only mode:

```bash
python potato_text_mode.py
```

This skips audio processing entirely and provides a text-based interaction.

## Installation Notes

- Use the `potato_requirements.txt` for minimal dependencies
- Models are heavily quantized (Q4, Q8) for CPU efficiency
- Audio processing uses minimal resources