import os
import requests
### MUST START SERVERS FIRST USING START ALL SERVER SCRIPT
import time
import soundfile as sf
import sounddevice as sd
import yaml

# Resolve relative to this file, not the process cwd -- cwd varies depending
# on how the app is launched (e.g. run_web.sh does `cd backend` first).
_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'configs', 'character_config.yaml'
)
with open(_CONFIG_PATH, 'r') as f:
    char_config = yaml.safe_load(f)

SOVITS_URL = os.environ.get("SOVITS_URL", "http://127.0.0.1:9880/tts")


def play_audio(path):
    data, samplerate = sf.read(path)
    sd.play(data, samplerate)
    sd.wait()  # Wait until playback is finished

def sovits_gen(in_text, output_wav_pth = "output.wav"):
    url = SOVITS_URL

    payload = {
        "text": in_text,
        "text_lang": char_config['sovits_ping_config']['text_lang'],
        "ref_audio_path": char_config['sovits_ping_config']['ref_audio_path'],  # Make sure this path is valid
        "prompt_text": char_config['sovits_ping_config']['prompt_text'],
        "prompt_lang": char_config['sovits_ping_config']['prompt_lang']
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # throws if not 200

        print(response)

        # Save the response audio if it's binary
        with open(output_wav_pth, "wb") as f:
            f.write(response.content)
        # print("Audio saved as output.wav")

        return output_wav_pth

    except Exception as e:
        print("Error in sovits_gen:", e)
        return None



if __name__ == "__main__":

    start_time = time.time()
    output_wav_pth1 = "output.wav"
    path_to_aud = sovits_gen("if you hear this, that means it is set up correctly", output_wav_pth1)
    
    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    print(path_to_aud)


