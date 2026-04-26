import os
import sounddevice as sd
import soundfile as sf

def record_audio(output_file="recording.wav", samplerate=44100):
    """
    Simple push-to-talk recorder: record -> save -> return path
    """
    # Remove existing file
    if os.path.exists(output_file):
        os.remove(output_file)
    
    print("Press ENTER to start recording...")
    input()
    
    print("🔴 Recording... Press ENTER to stop")
    
    # Record audio directly
    recording = sd.rec(int(60 * samplerate), samplerate=samplerate, channels=1, dtype='float64')
    input()  # Wait for stop
    sd.stop()
    
    print("⏹️  Saving audio...")
    
    # Write the file
    sf.write(output_file, recording, samplerate)
    return output_file
