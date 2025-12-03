# File: shazamify/audio/analyzer.py
# Purpose: Contains functions for audio analysis and feature extraction.

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


import librosa
import librosa.display

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


def generate_time_domain(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    t = np.arange(len(x)) / fs
    plt.figure()
    plt.title("Time Domain")
    plt.plot(t, x)
    plt.xlabel("Seconds (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    path = f"{out_dir}/{stem}_time.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path

def generate_magnitude_spectrum(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    f, mag_db = magnitude_spectrum(x, fs)
    plt.figure()
    plt.title("Magnitude Spectrum")
    plt.plot(f, mag_db)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.grid(True)
    path = f"{out_dir}/{stem}_spectrum.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path

def generate_chromagram(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.figure()
    y_harmonic, y_percussive = librosa.effects.hpss(x)
    chroma = librosa.feature.chroma_cqt(y=y_harmonic, sr=fs)
    librosa.display.specshow(chroma, sr=fs, x_axis='time', y_axis='chroma', vmin=0, vmax=1)
    plt.title('Chromagram')
    plt.colorbar()
    path = f"{out_dir}/{stem}_chroma.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path

def generate_spectrogram(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.figure()
    X_stft = librosa.stft(x)
    Xdb = librosa.amplitude_to_db(np.abs(X_stft), ref=np.max)
    librosa.display.specshow(Xdb, sr=fs, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    path = f"{out_dir}/{stem}_spectrogram.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path

def generate_mel_spectrogram(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.figure()
    # Compute Mel Spectrogram
    S = librosa.feature.melspectrogram(y=x, sr=fs, n_mels=128, fmax=8000)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=fs, fmax=8000)
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel-frequency Spectrogram')
    path = f"{out_dir}/{stem}_mel.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path

def generate_tempogram(x, fs, out_dir="data/plots", stem="clip"):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    plt.figure()
    # Compute Fourier Tempogram
    oenv = librosa.onset.onset_strength(y=x, sr=fs)
    tempogram = librosa.feature.fourier_tempogram(onset_envelope=oenv, sr=fs)
    librosa.display.specshow(np.abs(tempogram), sr=fs, hop_length=512, x_axis='time', y_axis='fourier_tempo')
    plt.colorbar()
    plt.title('Fourier Tempogram')
    path = f"{out_dir}/{stem}_tempogram.png"
    plt.savefig(path, dpi=100, bbox_inches="tight")
    plt.close()
    return path