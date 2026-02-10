# WAV bearbeiten mit NumPy: Cut + Lauter/Leiser + Plot + (optional) Abspielen + Speichern
#
# Voraussetzungen:
#   pip install numpy scipy matplotlib sounddevice
#
# WICHTIG: Nenne diese Datei NICHT "soundfile.py" (sonst gibt’s Namenskonflikte).
# Lege "audio.wav" in denselben Ordner wie dieses Script – oder setze unten den Pfad.

import warnings
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.io.wavfile import WavFileWarning

# -----------------------------
# Einstellungen
# -----------------------------
INPUT_WAV = "audio.wav"

# Cut (Sekunden). None = von Anfang / bis Ende
CUT_START_S = 2.0
CUT_END_S   = 5.0

# Lauter/Leiser (in dB): +6 dB ~ doppelt so laut, -6 dB ~ halb so laut
GAIN_DB = +6.0

# Optional: weiche Ein-/Ausblendung (Sekunden)
FADE_IN_S  = 0.02
FADE_OUT_S = 0.02

# Output
PLAY_RESULT = True
SAVE_RESULT = True
OUTPUT_WAV = "output_cut_gain.wav"

# Plots
SHOW_PLOTS = True
FFT_N = 4096  # für Spektrum-Plot (muss <= Signal-Länge sein)

# -----------------------------
# Hilfsfunktionen
# -----------------------------
def to_float(x: np.ndarray) -> np.ndarray:
    """Konvertiert Audio-Array auf float32 im Bereich ungefähr [-1, 1]."""
    if np.issubdtype(x.dtype, np.floating):
        return x.astype(np.float32)

    if x.dtype == np.int16:
        return (x.astype(np.float32) / 32768.0)
    if x.dtype == np.int32:
        return (x.astype(np.float32) / 2147483648.0)
    if x.dtype == np.uint8:
        # 8-bit PCM ist oft 0..255 mit 128 als "Null"
        return ((x.astype(np.float32) - 128.0) / 128.0)

    # Fallback: einfach floaten und normalisieren
    xf = x.astype(np.float32)
    m = np.max(np.abs(xf)) + 1e-12
    return xf / m

def float_to_int16(x: np.ndarray) -> np.ndarray:
    """Float [-1..1] -> int16."""
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767.0).astype(np.int16)

def cut_audio(x: np.ndarray, fs: int, start_s, end_s):
    """Schneidet x zwischen start_s und end_s (in Sekunden)."""
    n = x.shape[0]
    start_i = 0 if start_s is None else max(0, int(round(start_s * fs)))
    end_i = n if end_s is None else min(n, int(round(end_s * fs)))
    if end_i <= start_i:
        raise ValueError("CUT_END_S muss größer als CUT_START_S sein (oder None).")
    return x[start_i:end_i]

def apply_gain_db(x: np.ndarray, gain_db: float) -> np.ndarray:
    """Gain in dB anwenden."""
    factor = 10 ** (gain_db / 20.0)
    return x * factor

def apply_fade(x: np.ndarray, fs: int, fade_in_s: float, fade_out_s: float) -> np.ndarray:
    """Fügt Fade-in und Fade-out hinzu (in Sekunden)."""
    y = x.copy()
    n = y.shape[0]

    fi = int(round(fade_in_s * fs))
    fo = int(round(fade_out_s * fs))

    if fi > 1:
        w = np.linspace(0.0, 1.0, fi, dtype=np.float32)
        if y.ndim == 1:
            y[:fi] *= w
        else:
            y[:fi, :] *= w[:, None]

    if fo > 1:
        w = np.linspace(1.0, 0.0, fo, dtype=np.float32)
        if y.ndim == 1:
            y[-fo:] *= w
        else:
            y[-fo:, :] *= w[:, None]

    return y

def plot_time(ax, x: np.ndarray, fs: int, title: str):
    """Zeitbereich-Plot (Amplitude über Zeit)."""
    if x.ndim == 2:
        # für Plot: mono anzeigen (Mittelwert)
        xm = x.mean(axis=1)
    else:
        xm = x
    t = np.arange(len(xm)) / fs
    ax.plot(t, xm)
    ax.set_title(title)
    ax.set_xlabel("Zeit (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)

def plot_spectrum(ax, x: np.ndarray, fs: int, title: str, nfft: int):
    """Frequenzbereich-Plot (FFT, Betrag in dB)."""
    if x.ndim == 2:
        x = x.mean(axis=1)
    x = x[:nfft]
    nfft = len(x)
    if nfft < 16:
        ax.set_title(title + " (zu kurz für FFT)")
        return

    w = np.hanning(nfft).astype(np.float32)
    X = np.fft.rfft(x * w)
    mag = np.abs(X) + 1e-12
    db = 20 * np.log10(mag)
    f = np.fft.rfftfreq(nfft, d=1/fs)

    ax.plot(f, db)
    ax.set_title(title)
    ax.set_xlabel("Frequenz (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, fs/2)

# -----------------------------
# Laden
# -----------------------------
warnings.filterwarnings("ignore", category=WavFileWarning)  # optional: Warnung unterdrücken
fs, x_raw = wavfile.read(INPUT_WAV)

print("Loaded:", INPUT_WAV)
print("Samplerate:", fs, "Hz")
print("Shape:", x_raw.shape, "dtype:", x_raw.dtype)

x = to_float(x_raw)

# -----------------------------
# Bearbeitung: Cut + Gain + Fade + Clipping
# -----------------------------
y = cut_audio(x, fs, CUT_START_S, CUT_END_S)
y = apply_gain_db(y, GAIN_DB)
y = apply_fade(y, fs, FADE_IN_S, FADE_OUT_S)
y = np.clip(y, -1.0, 1.0)

print(f"Cut: {CUT_START_S}s .. {CUT_END_S}s  |  Gain: {GAIN_DB:+.1f} dB")
print("Result length:", len(y)/fs, "s")

# -----------------------------
# Speichern
# -----------------------------
if SAVE_RESULT:
    y_int16 = float_to_int16(y)
    wavfile.write(OUTPUT_WAV, fs, y_int16)
    print("Saved:", OUTPUT_WAV)

# -----------------------------
# Abspielen (optional)
# -----------------------------
if PLAY_RESULT:
    try:
        import sounddevice as sd
        sd.play(y, fs)
        sd.wait()
    except Exception as e:
        print("Playback nicht möglich (sounddevice fehlt oder Gerät-Problem).", e)

# -----------------------------
# Plots (optional)
# -----------------------------
if SHOW_PLOTS:
    nfft = min(FFT_N, y.shape[0], x.shape[0])
    fig, axs = plt.subplots(2, 2, figsize=(12, 6), dpi=110)
    plot_time(axs[0, 0], x, fs, "Original: Zeit/Amplitude")
    plot_time(axs[1, 0], y, fs, "Bearbeitet: Zeit/Amplitude")

    plot_spectrum(axs[0, 1], x, fs, "Original: Spektrum (FFT)", nfft=nfft)
    plot_spectrum(axs[1, 1], y, fs, "Bearbeitet: Spektrum (FFT)", nfft=nfft)

    plt.tight_layout()
    plt.show()
