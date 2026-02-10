# 13.01.2026
Idee überlegen

Bibliotheken herunterladen

Code von KI generieren lassen

Probelauf des Programmes:

![Audio-Ausgabe](Audio.png)  

# 20.01.2026

Dokumentation über den aktuellen Stand

# 27.01

Erweiterung des aktuellen Programms:

Töne werden in unterschiedlichen Farben angezeigt, je nach Höhe der Töne wird entschieden, ob diese als niedrig, mittel oder hoch gelten und werden somit grün, gelb, rot eingefärbt.

![Audio-Ausgabe](Audio2.png)    

# 03.02

Audio Dokumentation

Darstellung eines Audiosignales in einem Diagramm (Zeit-/Amplitude)

Das Signal wird aus der audio.wave Datei gelesen und dementsprechend verarbeitet.

Der Code zu folgendem Ergebnis befindet sich im Anhang -> soundfile.py
![Soundfile](soundfile.png) 

Danach können noch unterschiedlichste Funktionen angewendet werden z.B. Cut und Lauter/Leiser

Der Code zu folgendem Ergebnis befindet sich im Anhang -> soundfilewithfeatures.py
![Soundfile](soundfile1.png)

Folgende Ausgabe wurde erzeugt mit Cut und Lauter (+6.0 dB):

Samplerate: 44100 Hz

Cut: 2.0s .. 5.0s  |  Gain: +6.0 dB 

Saved: output_cut_gain.wav

Die neue Audio Datei wurde unter folgendem Namen gespeichert -> output_cut_gain.wav

Lauter: ```GAIN_DB = +6dB``` ... bedeutet doppelt so laut

Lauter: ```GAIN_DB = -6dB``` ... bedeutet halb so laut

Das Fenster kann mit die ```CUT``` Variablen eingestellt werden:

z.B. Fensterlänge von 3 Sekunden: 

```CUT_START_S = 2.0```

```CUT_END_S   = 5.0```

Oder im Falle von der Originallänge wird einfach ```none``` verwendet.

# 10.02

Abschließend wurde noch die Filteroption hinzugefügt:

Der Code zu folgendem Ergebnis befindet sich im Anhang -> soundfilewithfilter.py

![Soundfile](Filter.png)

Hier wurde ein ```CUT``` von 2-5s durchgeführt, die Lautstärke wurde im Originalzustand gelassen, mit einer ```high``` Filterung.

Die Filteroptionen können wie bereits oben erwähnt durch einfache Parameter geändert werden:

```FILTER_MODE = "none"``` ... Keine Filter

```FILTER_MODE = "high"``` ... nur Höhen

```FILTER_MODE = "low"``` ... nur Tiefen (Bass)

```FILTER_MODE = "mid"``` ... nur Mitten
