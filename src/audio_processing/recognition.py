#filename: src/audio_processing/recognition.py
#author: Nate Lee
#description: audioprocessing


import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path

def record(seconds=3.0, fs=16000, out_wav="data/audio_recordings/clip.wav"):
    samples = int(seconds * fs)
    audio = sd.rec(samples, samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    x = audio.flatten()
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    write(out_wav, fs, (x * 32767).astype(np.int16))
    return fs, x
