# Audio Verarbeitung mit numpy

## Folgende Bibliotheken werden für die Audio Verarbeitung benötigt:

  sounddevice -> Zugriff auf Surface Mikro
  
  numpy -> Audio Verarbeitung
  
  matplotlib -> zur Darstellung von Audio Aufzeichnungen
  
  [scipy](https://scipy.org/) -> falls aus einer Datei gelesen werden soll
  
## Links:

[Python Lib](https://wiki.python.org/moin/Audio) Zuletzt besucht am: 13.01.2026

[Processing Audio with python](https://medium.com/@mateus.d.assis.silva/processing-audio-with-python-b6ec37ac2f40) Zuletzt besucht am: 13.01.2026

[ChatGPT](https://chatgpt.com/) Zuletzt besucht am: 27.01.2026

## Wie wird Audio verarbeitet?

Siehe unter anderem Programmfortschritt -> audiovisu_20.01!

Das Audiosignal wird vom Mikrofon als zeitdiskretes Signal mit einer festen Samplerate aufgenommen und in einem Puffer gespeichert (Funktion pick_samplerate). Dieser Datenblock wird mit einer Fensterfunktion (Hann-Fenster) multipliziert, für Reduktion der Störeffekte bei der Fourieranalyse. Anschließend wird mittels FFT das Zeitsignal in den Frequenzbereich umgerechnet. Die Beträge der FFT werden in Dezibel (dB) umgerechnet und zu logarithmischen Frequenzbändern zusammengefasst. Diese Pegel werden zeitlich geglättet und als Balkendiagramm mit Peak-Hold-Anzeige dargestellt.

Darstellung erfolgt mittels Matplot-Lib.

Das Programm wurde in einem Prinzip erweitert, wo alle Töne in einer gewissen Farbe angezeigt werden, in der Praxis kennt man so etwas öfters von z.B. einem Mischpult.

Für weitere Details siehe Programmfortschritt -> audiovisu_27.01!

### Audioverarbeitung mit numpy
Wie kann ich ein Audiosignal von einer Datei öffnen?

NumPy allein liest keine Audioformate, man nutzt NumPy zum Verarbeiten, aber zum Einlesen braucht man Bibliotheken wie z.B. scipy, soundfile oder wave

#### Worauf ist bei der Bearbeitung von Audiosignalen zu achten?

Beim Bearbeiten von Audiosignalen ist das Abtasttheorem wichtig: Ein Signal wird als viele einzelne Messwerte pro Sekunde gespeichert (Samplerate, z.B. 44,1 kHz oder 48 kHz). Damit man eine bestimmte maximale Frequenz im Signal korrekt darstellen kann, muss man mit mindestens der doppelten Frequenz abtasten (Samplerate ≥ 2 · f_max). Das bedeutet, man kann nur Frequenzen bis zur Hälfte der Samplerate korrekt darstellen (Nyquist-Grenze). Frequenzen darüber führen zu Aliasing, also “falschen” Frequenzen im unteren Bereich. Besonders beim Downsampling muss man deshalb vorher mit einem Tiefpass (Anti-Aliasing-Filter) alles oberhalb der neuen Nyquist-Grenze entfernen. Für FFT-Auswertungen nutzt man oft Fensterfunktionen (z.B. Hann, Rechteck, ...), damit das Spektrum sauberer und stabiler wird.

#### Wie werden die Daten in numpy gespeichert?

Nach dem Einlesen werden die Werte in x und fs gespeichert.

x: ein NumPy-Array mit Samples
fs: Samplingrate in Hz

#### Mono und Stereo Signale werden folgendermaßen gespeichert:

Mono Signal: x.shape == (N,)
→ N Samples hintereinander

Stereo/Mehrkanal: x.shape == (N, C)
→ N Samples, C -> wie viele Kanäle (z.B. 2)

#### Viele WAVs (Soundfiles) kommen als Integer:

int16 ->  Wertebereich -32768 … +32767

int32 -> im Sonderfall

#### Wie ist ein Audiosignal "aufgebaut"?

Ein Audiosignal beschreibt Schall über die Zeit. Ein Mikrofon wandelt die Druckschwankungen der Luft in eine elektrische Spannung um, die sich ständig verändert. Digital wird dieses Signal als Folge von Messwerten (Samples) gespeichert: Die Samplerate gibt an, wie viele Samples pro Sekunde aufgenommen werden, die Bit-Tiefe bestimmt die Genauigkeit der Werte. Ein Audiosignal kann Mono (1 Kanal) oder Stereo (2 Kanäle: links/rechts) sein.

Darstellung eines Audiosignales in einem Diagramm (Zeit-/Amplitude)?
Audio-Bearbeitung:
   Was bedeutet Audio Bearbeitung - welche Funktionen können realisiert werden.
     - Cut
     - Lauter/Leiser

     - Filterung Höhen/Tiefen/Mittel 

Funktioniert das auch "live"







