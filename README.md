# Project Riko

Project Riko is an elite anime-focused AI companion project by Just Rayen. She doesn't just listen; she remembers everything about you and stays aware of your world. It combines OpenAI’s GPT, GPT-SoVITS voice synthesis, and Faster-Whisper ASR into a fully autonomous conversational pipeline.

**tested with python 3.10+ Windows >10 and Linux Ubuntu**

## ✨ Elite Features

- 💬 **LLM-based dialogue** using OpenAI API (configurable system prompts)
- 🧠 **Long-Term Memory (RAG)**: Uses a persistent vector database (`ChromaDB`) to remember past conversations and context forever.
- 👂 **Cortana-style Listening**: Continuous Voice Activity Detection (VAD). Just say her name (**"Riko"**) to wake her up!
- 👁️ **Screen Awareness**: Automatically monitors your clipboard to stay aware of what you are working on.
- 🔊 **Expressive Voice Generation** via GPT-SoVITS API.
- 🎧 **High-Accuracy Speech Recognition** using Faster-Whisper.
- 📁 Clean YAML-based config for personality configuration.


## ⚙️ Configuration

All prompts and parameters are stored in `character_config.yaml`.

```yaml
OPENAI_API_KEY: sk-YOURAPIKEY
history_file: chat_history.json
model: "gpt-4.1-mini"
presets:
  default:
    system_prompt: |
      You are a helpful assistant named Riko.
      You speak like a snarky anime girl.
      Always refer to the user as "senpai".

sovits_ping_config:
  text_lang: en
  prompt_lang : en
  ref_audio_path : ./character_files/main_sample.wav
  prompt_text : This is a sample voice for you to just get started with because it sounds kind of cute.
  
```

## 🛠️ Setup

### Install Dependencies

```bash
pip install uv 
uv pip install -r requirements.txt
pip install chromadb pyperclip sounddevice soundfile numpy
```

**System Requirements:**

* `ffmpeg` installed (for audio processing)
* `portaudio` (for sounddevice on Linux: `sudo apt install libportaudio2`)
* CUDA & cuDNN (Optional, for Faster-Whisper GPU acceleration)


## 🧪 Usage

### 1. Launch the GPT-SoVITS API 

### 2. Run the main script:

```bash
python server/main_chat.py
```

### The Autonomous Flow:

1. **Continuous Listen**: Riko waits in the background using VAD.
2. **Wake Word**: Speak her name (**"Riko"**) to trigger her attention.
3. **Transcription**: Transcribes your voice with Faster-Whisper.
4. **Context Retrieval**: Automatically pulls relevant past memories from her vector database and reads your current clipboard.
5. **Brain**: Passes all context to GPT for a highly personalized response.
6. **Voice Synthesis**: Synthesizes her voice using GPT-SoVITS.
7. **Playback**: Plays her response back to you.


## 📌 TODO / Future Improvements

* [ ] GUI or web interface
* [x] Live microphone input support (Continuous Listening)
* [ ] Emotion or tone control in speech synthesis
* [ ] VRM model frontend


## 🧑‍🎤 Credits

* Voice synthesis powered by [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)
* ASR via [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper)
* Vector Database by [ChromaDB](https://github.com/chroma-core/chroma)
* Language model via [OpenAI GPT](https://platform.openai.com)


## 📜 License

MIT — feel free to clone, modify, and build your own waifu voice companion.
