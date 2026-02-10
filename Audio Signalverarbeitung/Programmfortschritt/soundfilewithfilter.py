# Anfängerfreundlich: WAV laden -> (Cut) -> (Filter: Tief/Mitte/Höhen oder EQ) -> Gain -> Plot -> Abspielen -> Speichern
#
# Install:
#   pip install numpy scipy matplotlib sounddevice

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt

# ============================================================
# 1) EINSTELLUNGEN (HIER ÄNDERST DU ALLES)
# ============================================================

INPUT_WAV = "audio.wav"

# --- Cut (Ausschnitt) in Sekunden ---
CUT_START_S = 2.0     # z.B. 2.0 -> ab Sekunde 2 starten
CUT_END_S   = 5.0     # z.B. 5.0 -> bis Sekunde 5 (None = bis Ende)

# --- Filter-Modus wählen ---
# "none" = kein Filter
# "low"  = nur Tiefen (Bass)
# "mid"  = nur Mitten
# "high" = nur Höhen
# "eq3"  = 3-Band-EQ (Tief/Mitte/Höhen getrennt + mischen)
FILTER_MODE = "high"

# Trennfrequenzen (Grenzen) für Tief/Mitte/Höhen:
LOW_CROSS_HZ  = 250.0     # Tiefen: < 250 Hz
HIGH_CROSS_HZ = 4000.0    # Höhen:  > 4000 Hz

# Nur für FILTER_MODE = "eq3": Bereiche anheben/absenken (dB)
EQ_LOW_DB  = 0.0
EQ_MID_DB  = 0.0
EQ_HIGH_DB = 0.0

# Gesamt lauter/leiser (nach dem Filter/EQ), in dB
GAIN_DB = +0.0

# Output
PLAY_RESULT = True
SAVE_RESULT = True
OUTPUT_WAV = "output.wav"

# Plots
SHOW_PLOTS = True
FFT_N = 4096  # wie viele Samples für den FFT-Plot (kleiner = schneller)

# ============================================================
# 2) HILFSFUNKTIONEN
# ============================================================

def db_to_lin(db: float) -> float:
    """dB -> Linear-Faktor"""
    return 10 ** (db / 20.0)

def to_float_audio(x: np.ndarray) -> np.ndarray:
    """Audio nach float32 umwandeln (typisch Bereich -1..+1)."""
    if x.dtype == np.int16:
        return (x.astype(np.float32) / 32768.0)
    if x.dtype == np.int32:
        return (x.astype(np.float32) / 2147483648.0)
    if np.issubdtype(x.dtype, np.floating):
        return x.astype(np.float32)
    # Fallback:
    x = x.astype(np.float32)
    m = np.max(np.abs(x)) + 1e-12
    return x / m

def float_to_int16(x: np.ndarray) -> np.ndarray:
    """float (-1..1) -> int16 zum Speichern als WAV."""
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767.0).astype(np.int16)

def cut_seconds(x: np.ndarray, fs: int, start_s: float, end_s):
    """Schneidet den Bereich start_s..end_s aus."""
    start_i = int(start_s * fs) if start_s is not None else 0
    end_i   = int(end_s * fs) if end_s is not None else x.shape[0]
    start_i = max(0, start_i)
    end_i   = min(x.shape[0], end_i)
    if end_i <= start_i:
        raise ValueError("Cut-Bereich ist ungültig (CUT_END_S muss > CUT_START_S sein).")
    return x[start_i:end_i]

def make_filter_sos(fs: int, mode: str):
    """Erstellt einen Butterworth-Filter als SOS (stabil)."""
    nyq = fs / 2.0

    # kleine Sicherheitsgrenzen, damit nix exakt 0 oder exakt Nyquist ist
    low = np.clip(LOW_CROSS_HZ, 1.0, nyq - 1.0)
    high = np.clip(HIGH_CROSS_HZ, 1.0, nyq - 1.0)

    order = 4  # gut als Anfänger-Standard

    if mode == "low":   # Lowpass
        wn = low / nyq
        return butter(order, wn, btype="lowpass", output="sos")

    if mode == "high":  # Highpass
        wn = high / nyq
        return butter(order, wn, btype="highpass", output="sos")

    if mode == "mid":   # Bandpass
        lo = min(low, high)
        hi = max(low, high)
        wn = [lo / nyq, hi / nyq]
        return butter(order, wn, btype="bandpass", output="sos")

    raise ValueError("Unbekannter Filtermodus.")

def apply_sos_filter(x: np.ndarray, sos) -> np.ndarray:
    """Filter auf Mono oder Stereo anwenden (ohne Phasenverschiebung)."""
    if x.ndim == 1:
        return sosfiltfilt(sos, x).astype(np.float32)

    # Stereo/Mehrkanal: jeden Kanal einzeln filtern
    y = np.empty_like(x, dtype=np.float32)
    for ch in range(x.shape[1]):
        y[:, ch] = sosfiltfilt(sos, x[:, ch])
    return y

def mono_for_plot(x: np.ndarray) -> np.ndarray:
    """Für Plots: Stereo -> Mono."""
    return x.mean(axis=1) if x.ndim == 2 else x

def plot_time(ax, x: np.ndarray, fs: int, title: str):
    xm = mono_for_plot(x)
    t = np.arange(len(xm)) / fs
    ax.plot(t, xm)
    ax.set_title(title)
    ax.set_xlabel("Zeit (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)

def plot_fft(ax, x: np.ndarray, fs: int, title: str, nfft: int):
    xm = mono_for_plot(x)
    nfft = min(nfft, len(xm))
    xm = xm[:nfft]
    if nfft < 64:
        ax.set_title(title + " (zu kurz)")
        return

    w = np.hanning(nfft).astype(np.float32)
    X = np.fft.rfft(xm * w)
    f = np.fft.rfftfreq(nfft, d=1/fs)

    mag = np.abs(X) + 1e-12
    db = 20 * np.log10(mag)

    ax.plot(f, db)
    ax.set_title(title)
    ax.set_xlabel("Frequenz (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(0, fs/2)
    ax.grid(True, alpha=0.3)

# ============================================================
# 3) PROGRAMMSTART
# ============================================================

# WAV laden
fs, x_raw = wavfile.read(INPUT_WAV)
x = to_float_audio(x_raw)

print("Datei:", INPUT_WAV)
print("Samplerate:", fs, "Hz")
print("Shape:", x_raw.shape, "dtype:", x_raw.dtype)

# Cut
x_cut = cut_seconds(x, fs, CUT_START_S, CUT_END_S)

# Filter / EQ
mode = FILTER_MODE.lower()

if mode == "none":
    y = x_cut

elif mode in ("low", "mid", "high"):
    sos = make_filter_sos(fs, mode)
    y = apply_sos_filter(x_cut, sos)

elif mode == "eq3":
    # Tief, Mitte, Hoch getrennt filtern und dann mischen
    sos_low = make_filter_sos(fs, "low")
    sos_mid = make_filter_sos(fs, "mid")
    sos_high = make_filter_sos(fs, "high")

    low_part = apply_sos_filter(x_cut, sos_low)
    mid_part = apply_sos_filter(x_cut, sos_mid)
    high_part = apply_sos_filter(x_cut, sos_high)

    gL = db_to_lin(EQ_LOW_DB)
    gM = db_to_lin(EQ_MID_DB)
    gH = db_to_lin(EQ_HIGH_DB)

    y = gL * low_part + gM * mid_part + gH * high_part

    # Falls zu laut -> normalisieren, damit es nicht clippt
    peak = np.max(np.abs(y)) + 1e-12
    if peak > 1.0:
        y = y / peak

else:
    raise ValueError("FILTER_MODE muss sein: none, low, mid, high, eq3")

# Gesamt-Gain
y = y * db_to_lin(GAIN_DB)

# Clipping-Schutz
y = np.clip(y, -1.0, 1.0)

print(f"Cut: {CUT_START_S}s .. {CUT_END_S}s | Filter: {FILTER_MODE} | Gain: {GAIN_DB:+.1f} dB")

# Speichern
if SAVE_RESULT:
    wavfile.write(OUTPUT_WAV, fs, float_to_int16(y))
    print("Gespeichert:", OUTPUT_WAV)

# Abspielen
if PLAY_RESULT:
    try:
        import sounddevice as sd
        sd.play(y, fs)
        sd.wait()
    except Exception as e:
        print("Abspielen ging nicht:", e)

# Plots
if SHOW_PLOTS:
    nfft = min(FFT_N, len(mono_for_plot(x_cut)), len(mono_for_plot(y)))

    fig, axs = plt.subplots(2, 2, figsize=(12, 6), dpi=110)
    plot_time(axs[0, 0], x_cut, fs, "Original (nach Cut): Zeit/Amplitude")
    plot_time(axs[1, 0], y, fs, "Bearbeitet: Zeit/Amplitude")

    plot_fft(axs[0, 1], x_cut, fs, "Original (nach Cut): FFT", nfft)
    plot_fft(axs[1, 1], y, fs, "Bearbeitet: FFT", nfft)

    plt.tight_layout()
    plt.show()
