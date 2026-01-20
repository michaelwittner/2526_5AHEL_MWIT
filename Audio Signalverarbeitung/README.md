# Audio Verarbeitung mit numpy

## Folgende Bibliotheken werden für die Audio Verarbeitung benötigt:

  sounddevice -> Zugriff auf Surface Mikro
  
  numpy -> Audio Verarbeitung
  
  matplotlib -> zur Darstellung von Audio Aufzeichnungen
  
## Links:

[Python Lib](https://wiki.python.org/moin/Audio) Zuletzt besucht am: 13.01.2026

[Processing Audio with python](https://medium.com/@mateus.d.assis.silva/processing-audio-with-python-b6ec37ac2f40) Zuletzt besucht am: 13.01.2026

[ChatGPT](https://chatgpt.com/) Zuletzt besucht am: 20.01.2026

## Wie wird Audio verarbeitet?

Es wird automatisch ein Eingabegerät (Mikrofon / Line-In) gesucht

Danach wird eine funktionierende Samplerate gewählt

DEVICE = pick_input_device()

FS = pick_samplerate(DEVICE)

Fensterfunktion gegen Leakage

window = np.hanning(N)

x = buffer * window

Danach wird die eigentliche FFT gemacht (Zeit -> Frequenz) und das Ergebnis in db umgerechnet.

Damit man ein ruhigeres Bild bekommt, wird folgender Code verwendet:

smoothed = (1 - ALPHA) * smoothed + ALPHA * band_db

Abschließend mit matplot ausgegeben








