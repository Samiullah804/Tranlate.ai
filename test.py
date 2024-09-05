import sounddevice as sd
import numpy as np
import wave
import keyboard
import librosa
import scipy.io.wavfile as wav

sample_rate = 44100  
channels = 2  
output_filename = 'recorded_audio.wav'

# Function to record audio
def record_audio():
    print("Press 'Space' to start and stop recording.")
    recording = False
    audio_frames = []

    def callback(indata, frames, time, status):
        if recording:
            audio_frames.append(indata.copy())

    stream = sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback, dtype='int16')

    with stream:
        while True:
            if keyboard.is_pressed('space'):
                if not recording:
                    print("Recording started...")
                    recording = True
                    audio_frames.clear()
                else:
                    print("Recording stopped.")
                    recording = False
                    break
            sd.sleep(100)  

    # Save the recorded audio
    audio_data = np.concatenate(audio_frames)
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())

    print(f"Audio saved as {output_filename}.")
    return output_filename


# Main logic
if __name__ == "__main__":
    recorded_file = record_audio()
