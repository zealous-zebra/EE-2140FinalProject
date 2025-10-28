# File: shazamify/audio/analyzer.py
# Purpose: Contains functions for audio analysis and feature extraction.

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def magnitude_spectrum(x, fs):
    """Calculates the magnitude spectrum of a signal."""
    N = len(x)
    win = np.hanning(N)

    # Calculate the Fast Fourier Transform of the windowed signal
    X = np.fft.rfft(x * win)

    # Calculate the corresponding frequency values for the x-axis of the plot
    # THIS WAS THE LINE THAT WAS FIXED
    f = np.fft.rfftfreq(N, 1 / fs)

    # Convert the magnitude to decibels (dB)
    mag_db = 20 * np.log10(np.maximum(np.abs(X), 1e-12))

    return f, mag_db


def generate_and_save_plots(x, fs, out_dir="data/plots", stem="clip"):
    """
    Generates and saves time domain and frequency domain plots of the audio data.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    t = np.arange(len(x)) / fs

    # Generate Time Domain plot
    plt.figure()
    plt.title("Time Domain")
    plt.plot(t, x)
    plt.xlabel("Seconds (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    time_png = f"{out_dir}/{stem}_time.png"
    plt.savefig(time_png, dpi=120, bbox_inches="tight")
    plt.close()

    # Generate Magnitude Spectrum plot
    f, mag_db = magnitude_spectrum(x, fs)
    plt.figure()
    plt.title("Magnitude Spectrum")
    plt.plot(f, mag_db)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.grid(True)
    freq_png = f"{out_dir}/{stem}_spectrum.png"
    plt.savefig(freq_png, dpi=120, bbox_inches="tight")
    plt.close()

    return {"time_png": time_png, "spectrum_png": freq_png}