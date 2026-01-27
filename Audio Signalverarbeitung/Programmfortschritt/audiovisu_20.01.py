# Live Audio FFT Visualizer (PC) – schönere/lesbarere Grafik + Peak-Hold
# pip install numpy sounddevice matplotlib

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# -----------------------------
# Auto-Setup: Device + Samplerate
# -----------------------------
def pick_input_device():
    default_in = sd.default.device[0]  # (input, output)
    if default_in is not None and default_in >= 0:
        return default_in

    devices = sd.query_devices()
    candidates = [i for i, d in enumerate(devices) if d.get("max_input_channels", 0) > 0]
    if not candidates:
        raise RuntimeError("Kein Audio-Input-Gerät gefunden.")

    keywords = ["microphone", "mikrofon", "array", "input", "internal", "built-in"]
    def score(i):
        name = devices[i]["name"].lower()
        s = 0
        for k in keywords:
            if k in name:
                s += 5
        s += devices[i].get("max_input_channels", 0)
        return s

    return max(candidates, key=score)

def pick_samplerate(device_index):
    for fs in (48000, 44100, 32000, 16000, 8000):
        try:
            sd.check_input_settings(device=device_index, samplerate=fs, channels=1)
            return fs
        except Exception:
            pass
    raise RuntimeError("Konnte keine passende Samplerate fürs Input-Device finden.")

DEVICE = pick_input_device()
FS = pick_samplerate(DEVICE)

# -----------------------------
# FFT / Visual Settings
# -----------------------------
N = 2048
BARS = 48
FMIN = 50
FMAX = 16000

DB_FLOOR = -85
DB_TOP = 0

ALPHA = 0.25          # Glättung der Balken
PEAK_DECAY = 1.2      # dB pro Update: wie schnell Peak-Hold runterfällt

freqs = np.fft.rfftfreq(N, d=1/FS)
window = np.hanning(N).astype(np.float32)

edges_hz = np.logspace(np.log10(FMIN), np.log10(min(FMAX, FS/2)), BARS + 1)
edges_idx = np.searchsorted(freqs, edges_hz)
edges_idx = np.clip(edges_idx, 0, len(freqs) - 1)

# Band-Mitten (für Achsenbeschriftung)
band_centers_hz = np.sqrt(edges_hz[:-1] * edges_hz[1:])  # geometrisches Mittel

def fmt_hz(v):
    if v >= 1000:
        return f"{int(round(v/1000))}k"
    return str(int(round(v)))

# "schöne" Tick-Frequenzen
tick_hz = np.array([50, 100, 200, 500, 1000, 2000, 5000, 10000, 16000], dtype=float)
tick_pos = [int(np.argmin(np.abs(band_centers_hz - t))) for t in tick_hz]
tick_lbl = [fmt_hz(t) for t in tick_hz]

# Audio-Puffer & Glättung
buffer = np.zeros(N, dtype=np.float32)
smoothed = np.full(BARS, DB_FLOOR, dtype=np.float32)
peaks = np.full(BARS, DB_FLOOR, dtype=np.float32)

# -----------------------------
# Plot Setup (lesbarer)
# -----------------------------
plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
})

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=110)
ax.set_ylim(DB_FLOOR, DB_TOP)
ax.set_ylabel("Level (dB)")
ax.set_xlabel("Frequenz (Hz, logarithmische Bänder)")
ax.set_xticks(tick_pos)
ax.set_xticklabels(tick_lbl)
ax.set_yticks(np.arange(DB_FLOOR, DB_TOP + 1, 10))

# dezentes Gitternetz
ax.grid(True, axis="y", linewidth=0.8, alpha=0.35)
ax.grid(True, axis="x", linewidth=0.5, alpha=0.15)

# Balken
bars = ax.bar(np.arange(BARS), np.full(BARS, DB_FLOOR), width=0.85)

# Peak-Hold als Marker (Standardfarbe, kein extra Farbwunsch nötig)
peak_line, = ax.plot(np.arange(BARS), peaks, marker="_", linestyle="None", markersize=10)

# Titel mit Device-Name
dev_name = sd.query_devices(DEVICE)["name"]
ax.set_title(f"Live Audio Spectrum (FFT)  |  {dev_name}  |  FS={FS} Hz  |  N={N}")

fig.tight_layout()

print("Using input device:", DEVICE, "-", dev_name)
print("Samplerate:", FS)

# -----------------------------
# Audio Callback
# -----------------------------
def audio_callback(indata, frames, time, status):
    global buffer
    x = indata[:, 0].astype(np.float32)
    if len(x) >= N:
        buffer[:] = x[-N:]
    else:
        buffer = np.roll(buffer, -len(x))
        buffer[-len(x):] = x

# -----------------------------
# Animation Update
# -----------------------------
def update(_):
    global smoothed, peaks

    x = buffer * window
    X = np.fft.rfft(x)
    mag = np.abs(X) + 1e-12
    db = 20 * np.log10(mag)

    band_db = np.full(BARS, DB_FLOOR, dtype=np.float32)
    for i in range(BARS):
        a, b = edges_idx[i], edges_idx[i + 1]
        if b > a:
            band_db[i] = np.max(db[a:b])

    # Glättung
    smoothed = (1 - ALPHA) * smoothed + ALPHA * band_db

    # Peak hold (fällt langsam runter)
    peaks = np.maximum(peaks - PEAK_DECAY, smoothed)

    # Update Balken
    for bar, h in zip(bars, smoothed):
        bar.set_height(float(np.clip(h, DB_FLOOR, DB_TOP)))

    # Update Peak Marker
    peak_line.set_ydata(np.clip(peaks, DB_FLOOR, DB_TOP))

    return (*bars, peak_line)

# -----------------------------
# Stream Start
# -----------------------------
try:
    stream = sd.InputStream(
        device=DEVICE,
        samplerate=FS,
        channels=1,
        blocksize=N // 2,
        callback=audio_callback
    )
    with stream:
        ani = FuncAnimation(fig, update, interval=30, blit=False)
        plt.show()
except Exception as e:
    print("\nFehler beim Starten des Audio-Streams:")
    print(e)
    print("\nTipp: Geräte anzeigen mit:\n  python -c \"import sounddevice as sd; print(sd.query_devices())\"")
