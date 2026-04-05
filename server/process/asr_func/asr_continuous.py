import os
import queue
import sounddevice as sd
import soundfile as sf
import numpy as np

def listen_continuously(output_file="recording.wav", samplerate=16000, threshold=0.015, silence_duration=1.5):
    """
    Listens continuously and starts recording when audio volume exceeds threshold.
    Stops recording after silence_duration seconds of silence and saves to output_file.
    """
    print("\n👂 Riko is listening in the background... (Say 'Riko' to wake her up)")
    
    q = queue.Queue()

    def callback(indata, frames, time, status):
        # This is called for each audio block
        if status:
            pass # ignore status for now to avoid console spam
        q.put(indata.copy())

    recording = []
    is_recording = False
    silence_frames = 0
    # Approximate number of blocks for silence duration
    blocksize = 1024
    silence_limit = int((samplerate / blocksize) * silence_duration)

    # Start audio stream
    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=blocksize):
        while True:
            data = q.get()
            # Calculate Root Mean Square (RMS) for energy/volume
            rms = np.sqrt(np.mean(data**2))
            
            if not is_recording:
                if rms > threshold:
                    is_recording = True
                    recording.append(data)
                    print("🎙️ Voice detected, recording...", end="\r")
            else:
                recording.append(data)
                if rms < threshold:
                    silence_frames += 1
                else:
                    silence_frames = 0
                
                if silence_frames > silence_limit:
                    break

    print("⏹️  Finished hearing command. Processing...      ")
    
    if os.path.exists(output_file):
        os.remove(output_file)
        
    if not recording:
        return None

    audio_data = np.concatenate(recording, axis=0)
    sf.write(output_file, audio_data, samplerate)
    return output_file
