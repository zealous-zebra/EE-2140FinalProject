# filename: src/audio_processing/recognition.py
# author: Nate Lee
# description: audioprocessing

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pathlib import Path
import time

# --- NEW: Import QObject and pyqtSignal for threading ---
from PyQt6.QtCore import QObject, pyqtSignal


# This is the original function, we can keep it for other potential uses
def record(seconds=3.0, fs=16000, out_wav="data/audio_recordings/clip.wav"):
    samples = int(seconds * fs)
    audio = sd.rec(samples, samplerate=fs, channels=1, dtype="float32")
    sd.wait()
    x = audio.flatten()
    Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
    write(out_wav, fs, (x * 32767).astype(np.int16))
    return fs, x


# --- NEW: Recorder worker class for non-blocking recording ---
class Recorder(QObject):
    """
    A worker object that records audio in a separate thread.
    Inherits from QObject to use the signal/slot mechanism.
    """
    # Define the signals that this worker can emit
    progress = pyqtSignal(int)  # To report which second is being recorded
    finished = pyqtSignal(tuple)  # To send back the (fs, x) data when done

    def __init__(self, seconds, fs=16000, out_wav="data/audio_recordings/clip.wav"):
        super().__init__()
        self.seconds = seconds
        self.fs = fs
        self.out_wav = out_wav

    def run(self):
        """ The main work function that will be run in the new thread. """
        try:
            samples = int(self.seconds * self.fs)

            # Start the recording in the background. This call returns immediately.
            audio = sd.rec(samples, samplerate=self.fs, channels=1, dtype="float32")

            # Instead of sd.wait(), we now wait manually in a loop, emitting progress.
            for i in range(int(self.seconds)):
                time.sleep(1)  # Wait for one second
                self.progress.emit(i + 1)  # Emit the current second

            # Wait for any remaining time to ensure the recording is complete
            sd.wait()

            # Process and save the audio file
            x = audio.flatten()
            Path(self.out_wav).parent.mkdir(parents=True, exist_ok=True)
            write(self.out_wav, self.fs, (x * 32767).astype(np.int16))

            # Emit the finished signal with the recorded data
            self.finished.emit((self.fs, x))

        except Exception as e:
            print(f"Error during recording: {e}")
            # Emit an empty tuple on failure
            self.finished.emit((0, np.array([])))
