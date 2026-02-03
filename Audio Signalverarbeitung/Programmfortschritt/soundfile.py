import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

fs, x = wavfile.read("audio.wav")          # fs = samplerate

# Stereo -> Mono (optional)
if x.ndim == 2:
    x = x.mean(axis=1)

# int16 -> float (-1..1)
if x.dtype == np.int16:
    x = x.astype(np.float32) / 32768.0
else:
    x = x.astype(np.float32)

t = np.arange(len(x)) / fs                # Zeitachse in Sekunden

plt.figure(figsize=(10,4))
plt.plot(t, x)
plt.xlabel("Zeit (s)")
plt.ylabel("Amplitude")
plt.title("Audiosignal im Zeitbereich")
plt.tight_layout()
plt.show()
