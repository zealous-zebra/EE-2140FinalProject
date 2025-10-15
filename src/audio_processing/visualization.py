#filename: src/audio_processing/visualization.py
#author: Nate Lee
#description: plotting time and frequency domain

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def magnitude_spectrum(x, fs):
    N = len(x)
    win = np.hanning(N)
    X = np.fft.rfft(x * win)
    f = np.fft.rfftfreq(N, 1/fs)
    mag_db = 20*np.log10(np.maximum(np.abs(X), 1e-12))
    return f, mag_db

def save_plots(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    t = np.arange(len(x))/fs

    plt.figure(); plt.title("Time Domain"); plt.plot(t, x); plt.xlabel("s"); plt.ylabel("amp"); plt.grid(True)
    time_png = f"{out_dir}/{stem}_time.png"; plt.savefig(time_png, dpi=120, bbox_inches="tight"); plt.close()

    f, mag_db = magnitude_spectrum(x, fs)
    plt.figure(); plt.title("Magnitude Spectrum"); plt.plot(f, mag_db); plt.xlabel("Hz"); plt.ylabel("dB"); plt.grid(True)
    freq_png = f"{out_dir}/{stem}_spectrum.png"; plt.savefig(freq_png, dpi=120, bbox_inches="tight"); plt.close()

    return {"time_png": time_png, "spectrum_png": freq_png}
