# Live Audio FFT Visualizer (PC) – Segment-Equalizer (grün/gelb/rot) + Peak-Hold
# pip install numpy sounddevice matplotlib

import numpy as np                      
import sounddevice as sd                
import matplotlib.pyplot as plt         
from matplotlib.animation import FuncAnimation  
import matplotlib.patches as patches    

# -----------------------------
# Auto-Setup: Device + Samplerate
# -----------------------------
def pick_input_device(): # Zweck: Bestimmt automatisch ein geeignetes Audio-Eingabegerät.
    
    default_in = sd.default.device[0]   
    if default_in is not None and default_in >= 0:
        return default_in              

    devices = sd.query_devices()       # Liste aller Audio-Geräte
    candidates = [i for i, d in enumerate(devices)
                  if d.get("max_input_channels", 0) > 0]  # nur Geräte, die überhaupt Input können
    if not candidates:
        raise RuntimeError("Kein Audio-Input-Gerät gefunden.")

    keywords = ["microphone", "mikrofon", "array", "input", "internal", "built-in"]
    
    def score(i):
        # Name enthält Keyword -> höherer Score, mehr Kanäle -> ebenfalls höherer Score.
        name = devices[i]["name"].lower()
        s = 0
        for k in keywords:
            if k in name:
                s += 5
        s += devices[i].get("max_input_channels", 0)
        return s

    return max(candidates, key=score)  # bestes Input-Gerät wählen


def pick_samplerate(device_index): # Findet eine Samplerate, die das Input-Gerät sicher unterstützt.
    
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
N = 2048                               # FFT-Länge / Samples
BARS = 48                              # Anzahl Frequenzbänder (Spalten)
FMIN = 50                              # untere Frequenzgrenze 
FMAX = 16000                           # obere Frequenzgrenze 

DB_FLOOR = -85                         # "Minimum" dB (alles darunter wird als leise angesehen)
DB_TOP = 0                             # "Maximum" dB für Darstellung 

ALPHA = 0.25                           # Glättungsfaktor für ruhigere Anzeige
PEAK_DECAY = 1.2                       # dB pro Update, wie schnell Peak-Hold sinkt

SEGMENTS = 12                          # Anzahl LED-Blöcke pro Band 
GAP = 0.15                             # Abstand zwischen Segmenten (optischer Spalt)

freqs = np.fft.rfftfreq(N, d=1 / FS)

window = np.hanning(N).astype(np.float32)

edges_hz = np.logspace(np.log10(FMIN), np.log10(min(FMAX, FS / 2)), BARS + 1)
# Frequenz-Grenzen der Bänder (logarithmisch verteilt)

edges_idx = np.searchsorted(freqs, edges_hz)
# zu jeder Grenzfrequenz der passende FFT-Index

edges_idx = np.clip(edges_idx, 0, len(freqs) - 1)
# stellt sicher, dass Indizes nicht außerhalb des Arrays liegen

band_centers_hz = np.sqrt(edges_hz[:-1] * edges_hz[1:]) # Band-Mittenfrequenzen 


def fmt_hz(v):
    if v >= 1000:
        return f"{int(round(v / 1000))}k"
    return str(int(round(v)))


tick_hz = np.array([50, 100, 200, 500, 1000, 2000, 5000, 10000, 16000], dtype=float)
# "schöne" Frequenzen, die als Beschriftungen gezeigt werden sollen

tick_pos = [int(np.argmin(np.abs(band_centers_hz - t))) for t in tick_hz]

tick_lbl = [fmt_hz(t) for t in tick_hz]
# Labels als Strings ("50", "100", "1k", ...)

buffer = np.zeros(N, dtype=np.float32)
# enthält das Zeitfenster, das gerade per FFT analysiert wird

smoothed = np.full(BARS, DB_FLOOR, dtype=np.float32)

peaks = np.full(BARS, DB_FLOOR, dtype=np.float32)

DB_RANGE = DB_TOP - DB_FLOOR

DB_PER_SEG = DB_RANGE / SEGMENTS

# -----------------------------
# Plot Setup (Segment-Equalizer)
# -----------------------------
plt.rcParams.update({
    # Zweck: Lesbarkeit (Schriftgrößen)
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
})

fig, ax = plt.subplots(figsize=(11, 5.5), dpi=110)
# fig: Figure-Objekt (Fenster)
# ax: Achsen-Objekt (Plotbereich)

ax.set_xlim(-0.5, BARS - 0.5)          
ax.set_ylim(0, SEGMENTS)               

ax.set_xlabel("Frequenz (Hz, logarithmische Bänder)")  
ax.set_ylabel("Level (Segment)")

ax.set_xticks(tick_pos)                
ax.set_xticklabels(tick_lbl)           
ax.set_yticks(range(0, SEGMENTS + 1))  

ax.grid(True, axis="y", linewidth=0.8, alpha=0.35)     
ax.grid(True, axis="x", linewidth=0.5, alpha=0.15)     # Hilfslinien

dev_name = sd.query_devices(DEVICE)["name"]

ax.set_title(f"Live Audio Spectrum (FFT)  |  {dev_name}  |  FS={FS} Hz  |  N={N}")

fig.tight_layout()                      

print("Using input device:", DEVICE, "-", dev_name)  
print("Samplerate:", FS)


def seg_color(seg_index: int): # bestimmt die Farbe eines Segments je nach Höhe
    # Zweck: klassische Anzeige: unten grün, Mitte gelb, oben rot
    
    if seg_index >= int(SEGMENTS * 0.75):
        return (1.0, 0.15, 0.15)        # rot
    elif seg_index >= int(SEGMENTS * 0.55):
        return (1.0, 0.95, 0.25)        # gelb
    else:
        return (0.25, 1.0, 0.25)        # grün


rects = []
# 2D-Liste mit Rechtecken: rects[band][segment]

for b in range(BARS):                   
    col = []
    for s in range(SEGMENTS):           
        r = patches.Rectangle(
            (b - 0.4, s + GAP / 2),     
            0.8,                        
            1 - GAP,                   
            linewidth=0,                
            facecolor=seg_color(s),     
            alpha=0.12                  
        )
        ax.add_patch(r)                 
        col.append(r)                   
    rects.append(col)                  

peak_markers, = ax.plot(
    np.arange(BARS), np.zeros(BARS),
    marker="_", linestyle="None", markersize=12
)

# -----------------------------
# Audio Callback
# -----------------------------
def audio_callback(indata, frames, time, status): # wird von sounddevice automatisch aufgerufen, wenn neue Audiodaten eintreffen.
    

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

    x = buffer * window                 # Fensterung gegen Spektralleckage
    X = np.fft.rfft(x)                  # FFT nur für positive Frequenzen
    mag = np.abs(X) + 1e-12             # Betrag (Amplitude), +eps gegen log(0)
    db = 20 * np.log10(mag)             # Umrechnung in dB

    band_db = np.full(BARS, DB_FLOOR, dtype=np.float32)

    for i in range(BARS):
        a, b = edges_idx[i], edges_idx[i + 1]  
        if b > a:
            band_db[i] = np.max(db[a:b])       

    smoothed = (1 - ALPHA) * smoothed + ALPHA * band_db
    # zeitliche Glättung, weniger Flackern

    peaks = np.maximum(peaks - PEAK_DECAY, smoothed)

    clamped = np.clip(smoothed, DB_FLOOR, DB_TOP)

    levels = ((clamped - DB_FLOOR) / DB_PER_SEG).astype(int)

    levels = np.clip(levels, 0, SEGMENTS)

    for b in range(BARS):
        on = int(levels[b])             
        for s in range(SEGMENTS):
            rects[b][s].set_alpha(0.95 if s < on else 0.12)
            # Segment an/aus schalten über Helligkeit (alpha)

    peak_clamped = np.clip(peaks, DB_FLOOR, DB_TOP)

    peak_level = (peak_clamped - DB_FLOOR) / DB_PER_SEG

    peak_markers.set_ydata(np.clip(peak_level, 0, SEGMENTS))
    # Markerposition je Band setzen

    return (peak_markers,)              # Rückgabe: geändertes Objekt 


# -----------------------------
# Stream Start
# -----------------------------
try:
    stream = sd.InputStream(
        device=DEVICE,                  # ausgewähltes Mikrofon/Line-In
        samplerate=FS,                  # Samplerate
        channels=1,                     # Mono
        blocksize=N // 2,               # Callback bekommt halb so große Blöcke (schnelleres Update)
        callback=audio_callback         # Funktion, die die Audiodaten entgegennimmt
    )

    with stream:                        # Stream läuft nur innerhalb dieses Blocks
        ani = FuncAnimation(
            fig, update,
            interval=30,                # ca. alle 30 ms neue Anzeige
            blit=False                  # einfacher/robuster (Patch-Updates)
        )
        plt.show()                      # Fenster anzeigen und Eventloop starten

except Exception as e:
    # Zweck: Fehlerausgabe
    print("\nFehler beim Starten des Audio-Streams:")
    print(e)
    print("\nTipp: Geräte anzeigen mit:\n  python -c \"import sounddevice as sd; print(sd.query_devices())\"")
