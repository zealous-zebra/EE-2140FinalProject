# File: shazamify/audio/recorder.py
# Purpose: Handles threaded, non-blocking audio recording.

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import time
from PyQt6.QtCore import QObject, pyqtSignal

class Recorder(QObject):
    """A worker object that records audio in a separate thread."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(tuple)

    def __init__(self, seconds, fs=16000, out_wav="data/audio_recordings/clip.wav"):
        super().__init__()
        self.seconds = seconds
        self.fs = fs
        self.out_wav = out_wav

    def run(self):
        """The main work function that will be run in the new thread."""
        try:
            samples = int(self.seconds * self.fs)
            audio = sd.rec(samples, samplerate=self.fs, channels=1, dtype="float32")

            for i in range(int(self.seconds)):
                time.sleep(1)
                self.progress.emit(i + 1)

            sd.wait()
            x = audio.flatten()
            Path(self.out_wav).parent.mkdir(parents=True, exist_ok=True)
            write(self.out_wav, self.fs, (x * 32767).astype(np.int16))
            self.finished.emit((self.fs, x))

        except Exception as e:
            print(f"Error during recording: {e}")
            self.finished.emit((0, np.array([])))