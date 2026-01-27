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

Siehe unter anderem Programm im Anhang!

Das Audiosignal wird vom Mikrofon als zeitdiskretes Signal mit einer festen Samplerate aufgenommen und in einem Puffer gespeichert (Funktion pick_samplerate). Dieser Datenblock wird mit einer Fensterfunktion (Hann-Fenster) multipliziert, für Reduktion der Störeffekte bei der Fourieranalyse. Anschließend wird mittels FFT das Zeitsignal in den Frequenzbereich umgerechnet. Die Beträge der FFT werden in Dezibel (dB) umgerechnet und zu logarithmischen Frequenzbändern zusammengefasst. Diese Pegel werden zeitlich geglättet und als Balkendiagramm mit Peak-Hold-Anzeige dargestellt.

Darstellung erfolgt mittels Matplot-Lib.









