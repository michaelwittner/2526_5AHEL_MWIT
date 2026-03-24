# Videobearbeitung

## Einführung und Aufgabenstellung

Videosignale können auf unterschiedliche Weise be- und verarbeitet werden. Ziel dieses Projekts ist es, ein vorhandenes Video einzulesen, es digital zu bearbeiten (z.B. Skalierung, FPS-Anpassung, Format-Konvertierung) und das Ergebnis in eine neue Ausgabedatei zu schreiben. Die Steuerung erfolgt über ein grafisches Benutzeroberfläche (GUI), die mit **tkinter** umgesetzt wurde.

Dieses Projekt entstand als Erweiterung zur Audioverarbeitung und zeigt, wie ähnliche Prinzipien – Frame-basiertes Einlesen, Verarbeiten, Ausgeben – auch im Videobereich Anwendung finden.

## Folgende Bibliotheken werden für die Videobearbeitung benötigt:

```opencv-python``` (cv2) → Die zentrale Bibliothek für Computer Vision und Videobearbeitung in Python. Ermöglicht das Einlesen, Skalieren und Schreiben von Video-Frames.

```tkinter``` → GUI-Bibliothek aus der Python-Standardinstallation. Wird für das Benutzeroberfläche (Eingabefelder, Buttons, Dialoge) verwendet.

```threading``` → Ermöglicht das Ausführen der Videokonvertierung in einem separaten Thread, damit die GUI während der Verarbeitung nicht einfriert.

```os``` → Betriebssystemfunktionen wie Dateipfad-Operationen und Existenzprüfungen.

## Links:

[OpenCV Dokumentation](https://docs.opencv.org/) Zuletzt besucht am: 22.03.2026

[OpenCV Python Tutorial](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html) Zuletzt besucht am: 22.03.2026

[tkinter Dokumentation](https://docs.python.org/3/library/tkinter.html) Zuletzt besucht am: 22.03.2026

[Python threading](https://docs.python.org/3/library/threading.html) Zuletzt besucht am: 22.03.2026

[ChatGPT](https://claude.ai/) Zuletzt besucht am: 22.03.2026

---

## Was ist OpenCV (cv2)?

OpenCV steht für **Open Source Computer Vision Library** und ist eine der meistgenutzten Bibliotheken für Bild- und Videobearbeitung in Python. Sie wurde ursprünglich von Intel entwickelt und 2000 veröffentlicht. Heute wird sie von der OpenCV-Foundation weiterentwickelt.

In Python wird OpenCV über das Paket `opencv-python` installiert und als `cv2` importiert:

```python
import cv2
```

OpenCV ist in C++ geschrieben, besitzt aber Python-Bindings, was bedeutet: Man schreibt Python-Code, aber die eigentliche Verarbeitung läuft performant im Hintergrund in C++.

---

## Wie ist ein Videosignal „aufgebaut"?

Ein Video ist im Grunde eine Abfolge von Einzelbildern (Frames), die schnell genug hintereinander abgespielt werden, damit das menschliche Auge Bewegung wahrnimmt. Ähnlich wie bei Audio gibt es auch beim Video bestimmte technische Kenngrößen:

**FPS (Frames per Second)** gibt an, wie viele Bilder pro Sekunde im Video enthalten sind. Typische Werte sind 24 FPS (Film), 25 FPS (PAL/Europa), 30 FPS (NTSC/Amerika) und 60 FPS (Sport/Gaming).

**Auflösung** beschreibt die Bildgröße in Pixeln. Verbreitete Auflösungen sind z.B. 1280×720 (HD), 1920×1080 (Full HD) oder 3840×2160 (4K).

**Codec** ist das Kompressionsverfahren, mit dem die Frames gespeichert werden. Bekannte Codecs sind H.264, H.265, XVID oder MP4V.

**Container** ist das Dateiformat, das Video- und Audiodaten (und Metadaten) zusammenhält – z.B. `.mp4`, `.avi`, `.mkv`.

Ein einzelner Frame wird von OpenCV als **NumPy-Array** gespeichert, in der Form `(Höhe, Breite, 3)` – die 3 steht dabei für die drei Farbkanäle **BGR** (Blau, Grün, Rot). Wichtig: OpenCV verwendet standardmäßig BGR und nicht RGB wie viele andere Bibliotheken.

```python
# Beispiel: Einlesen eines Videos und Ausgabe der Frame-Größe
cap = cv2.VideoCapture("video.mp4")
ret, frame = cap.read()
print(frame.shape)  # z.B. (720, 1280, 3)
```

---

## Wichtige Funktionen von cv2 in diesem Projekt

### `cv2.VideoCapture()`

Öffnet eine Videodatei (oder Kamera) zum Lesen. Rückgabe ist ein `VideoCapture`-Objekt.

```python
cap = cv2.VideoCapture("video.mp4")
```

Über `cap.get()` lassen sich Metadaten wie FPS, Breite, Höhe und Frameanzahl abfragen:

```python
fps    = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
```

### `cap.read()`

Liest den nächsten Frame aus der geöffneten Datei. Rückgabe ist ein Tupel `(ret, frame)`:
- `ret`: `True` wenn erfolgreich, `False` am Ende des Videos
- `frame`: das Bild als NumPy-Array

```python
ret, frame = cap.read()
if not ret:
    break  # Kein Frame mehr → Video ist zu Ende
```

### `cv2.VideoWriter_fourcc()`

Definiert den Codec (FourCC-Code) für die Ausgabedatei. FourCC steht für „Four Character Code" – ein 4-Buchstaben-Kode, der den Codec identifiziert.

```python
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # für .mp4
fourcc = cv2.VideoWriter_fourcc(*"XVID")  # für .avi
```

### `cv2.VideoWriter()`

Erstellt eine Ausgabedatei zum Schreiben von Frames. Benötigt Pfad, Codec, FPS und Zielgröße.

```python
out = cv2.VideoWriter("output.mp4", fourcc, 25.0, (1280, 720))
```

### `cv2.resize()`

Skaliert einen Frame auf eine neue Größe. Das `interpolation`-Argument bestimmt die Methode – `cv2.INTER_AREA` eignet sich gut beim Verkleinern.

```python
frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
```

### `cap.release()` / `out.release()`

Schließen die Eingabe- bzw. Ausgabedatei und geben Ressourcen frei. Wichtig, damit keine Speicherlecks entstehen.

```python
cap.release()
out.release()
```

---

## Wie funktioniert die Videokonvertierung im Programm?

Der Ablauf der Konvertierung folgt einem klaren Frame-für-Frame-Prinzip:

1. Die Eingabedatei wird mit `cv2.VideoCapture()` geöffnet und die Metadaten (FPS, Breite, Höhe, Frameanzahl) werden ausgelesen.
2. Zielwerte für FPS und Auflösung werden festgelegt – entweder aus den Benutzereingaben oder, falls leer, aus den Originaldaten übernommen.
3. Der passende FourCC-Code wird anhand der Dateiendung der Ausgabedatei gewählt.
4. Der `VideoWriter` wird mit den Zielparametern erstellt.
5. In einer Schleife wird Frame für Frame gelesen, bei Bedarf mit `cv2.resize()` skaliert und anschließend in die Ausgabedatei geschrieben.
6. Alle 30 Frames wird der Fortschritt in Prozent berechnet und über einen Callback an die GUI übergeben.
7. Am Ende werden beide Dateien geschlossen.

```python
while True:
    ret, frame = cap.read()
    if not ret:
        break
    if (tw, th) != (width, height):
        frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)
    out.write(frame)
```

---

## Threading – warum und wie?

Ohne Threading würde die Konvertierung im Hauptthread der GUI laufen. Das Ergebnis: Das Fenster friert ein und reagiert nicht mehr auf Benutzereingaben. Deshalb wird die Konvertierung in einem separaten **Daemon-Thread** gestartet:

```python
thread = threading.Thread(
    target=self.run_conversion,
    args=(input_path, output_path, fps, width, height)
)
thread.daemon = True  # Thread endet automatisch mit dem Programm
thread.start()
```

Der Callback `update_status()` wird aus dem Thread heraus aufgerufen und aktualisiert das Status-Label in der GUI mit dem aktuellen Fortschritt.

---

## Die GUI mit tkinter

Die Benutzeroberfläche besteht aus folgenden Elementen:

**Eingabefelder:** Für Eingabedatei, Ausgabedatei, Ziel-FPS, Ziel-Breite und Ziel-Höhe. Alle sind optional außer Eingabe- und Ausgabedatei.

**Datei-Dialoge:** Über die „Durchsuchen"-Buttons öffnen sich native Betriebssystem-Dialoge zum Auswählen (`askopenfilename`) bzw. Speichern (`asksaveasfilename`) von Dateien.

**Status-Label:** Zeigt den aktuellen Status der Konvertierung an – „Bereit", „Konvertierung läuft... X%", „✓ Erfolgreich" oder „✗ Fehler".

**Zurücksetzen-Button:** Leert alle Eingabefelder und setzt den Status zurück.

---

## Wichtige Einschränkung: Kein Audio!

OpenCV ist eine Bibliothek für **Bildverarbeitung**, nicht für Audioverarbeitung. Der `VideoWriter` schreibt nur Video-Frames – **keine Audiospur**. Das bedeutet: Das konvertierte Video ist stumm, auch wenn die Originaldatei Ton enthielt.

Für eine vollständige Video-Konvertierung inklusive Audio müsste man z.B. `ffmpeg` als externen Prozess aufrufen oder eine Bibliothek wie `moviepy` verwenden.

---

## Vorteile von OpenCV (cv2)

**Sehr hohe Performance:** Da OpenCV intern in C++ implementiert ist, läuft die Frame-Verarbeitung deutlich schneller als in reinem Python.

**Riesige Funktionssammlung:** OpenCV enthält neben Videobearbeitung auch Bildfilter, Kanten- und Objekterkennung, Gesichtserkennung, optischen Fluss, Kamerakalibrierung und vieles mehr.

**Große Community und gute Dokumentation:** Es gibt tausende Tutorials, StackOverflow-Antworten und offizielle Dokumentation.

**Plattformübergreifend:** OpenCV läuft auf Windows, macOS und Linux ohne Anpassungen.

**Kostenlos und Open Source:** Lizenziert unter der BSD-Lizenz, also frei für kommerzielle und private Nutzung.

**Einfache Installation:**

```bash
pip install opencv-python
```

---

## Nachteile von OpenCV (cv2)

**Kein Audio-Support:** OpenCV kann Audiospuren weder lesen noch schreiben. Für Videos mit Ton braucht man immer eine zusätzliche Lösung.

**Eingeschränkte Codec-Kontrolle:** Feineinstellungen wie Bitrate, Qualitätsstufe (CRF), Encoding-Preset oder Hardware-Beschleunigung sind mit OpenCV kaum oder gar nicht möglich.

**BGR statt RGB:** OpenCV verwendet BGR als Farbkanalreihenfolge. Das kann zu Farbfehlern führen, wenn man Frames an andere Bibliotheken (z.B. matplotlib, PIL) weitergibt, ohne vorher zu konvertieren:

```python
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

**Containerformat-Unterstützung begrenzt:** Nicht alle Kombinationen aus Container und Codec funktionieren auf allen Systemen. Die Verfügbarkeit hängt vom OpenCV-Build und den installierten Backend-Bibliotheken (libav, ffmpeg) ab.

**Kein direktes Streaming:** OpenCV ist nicht optimal für Live-Streaming oder Echtzeit-Broadcasting ausgelegt.

---

## Alternativen zu OpenCV

| Bibliothek | Stärken | Schwächen |
|---|---|---|
| **ffmpeg** (via subprocess) | Volle Codec-Kontrolle, Audio, sehr schnell | Kein Python-native, schwierige API |
| **moviepy** | Audio + Video, einfache API, Python-nativ | Langsamer, braucht ffmpeg im Hintergrund |
| **imageio** | Einfaches Lesen/Schreiben, auch ffmpeg-Backend | Weniger Funktionen als OpenCV |
| **PyAV** | Python-Bindings für libav/ffmpeg, Audio+Video | Komplexere API |
| **GStreamer** | Professionelles Streaming, Pipeline-basiert | Sehr komplexe Einrichtung |

### ffmpeg (Kommandozeile)

`ffmpeg` ist das mächtigste Werkzeug für Videokonvertierung, kann aber auch direkt aus Python über `subprocess` aufgerufen werden:

```python
import subprocess
subprocess.run([
    "ffmpeg", "-i", "input.mp4",
    "-vf", "scale=1280:720",
    "-r", "25",
    "output.mp4"
])
```

Im Gegensatz zu OpenCV behält ffmpeg dabei auch die Audiospur und erlaubt genaue Qualitätssteuerung.

### moviepy

`moviepy` bietet eine einfachere, Python-native API und unterstützt sowohl Video als auch Audio:

```python
from moviepy.editor import VideoFileClip
clip = VideoFileClip("input.mp4").resize((1280, 720))
clip.write_videofile("output.mp4", fps=25)
```

Intern nutzt moviepy ebenfalls ffmpeg, bietet aber eine bequemere Schnittstelle. Für Schnitt, Effekte und Texteinblendungen ist moviepy oft die bessere Wahl gegenüber OpenCV.

### Zusammenfassung der Abwägung

OpenCV ist ideal für **frame-basierte Bildverarbeitung**, Computer Vision und schnelle Skalierungen ohne Audio. Für Projekte, bei denen Audio erhalten bleiben soll, oder bei denen genaue Kontrolle über Codec und Qualität gefragt ist, ist **ffmpeg** oder **moviepy** die bessere Wahl.

---

## Wie werden Videodaten intern gespeichert?

### In einer MP4-Datei

Eine MP4-Datei ist ein Containerformat. Sie enthält mindestens eine Video- und eine Audiospur sowie Timing- und Indexdaten. Video wird typischerweise mit H.264 oder H.265 komprimiert, Audio meist als AAC. Der Container sorgt dafür, dass Bild und Ton beim Abspielen synchron bleiben.

### In einer AVI-Datei

AVI (Audio Video Interleave) ist ein älteres Microsoft-Format. Video und Audio werden abwechselnd in Blöcken gespeichert. AVI ist weniger effizient komprimiert als MP4, dafür breiter unterstützt von älteren Software-Tools.

### Wie speichert OpenCV einen Frame?

OpenCV speichert jeden Frame als NumPy-Array mit der Form `(Höhe, Breite, 3)`. Die drei Kanäle sind in der Reihenfolge **B, G, R** gespeichert (Blau, Grün, Rot). Jeder Kanalwert liegt zwischen 0 und 255 (uint8). Ein Full-HD-Frame (1920×1080) hat damit genau `1920 × 1080 × 3 = 6.220.800 Bytes ≈ 6 MB` unkomprimiert.

Das ist auch der Grund, warum Videocompression so wichtig ist: Ein unkomprimiertes 10-Sekunden-Video bei 30 FPS würde `30 × 10 × 6 MB = 1.800 MB ≈ 1,8 GB` benötigen. Codecs wie H.264 komprimieren das auf einen Bruchteil davon.

---

## Programmfortschritt und Struktur

Das Programm ist nach dem objektorientierten Prinzip mit einer Klasse `VideoConverterGUI` und einer separaten Funktion `convert_cv2()` aufgebaut.

**`VideoConverterGUI`** verwaltet die gesamte GUI: Fenster erstellen, Widgets platzieren, Benutzereingaben validieren und den Konvertierungs-Thread starten.

**`convert_cv2()`** ist die eigentliche Verarbeitungsfunktion. Sie ist bewusst unabhängig von der GUI gehalten (kein tkinter-Code darin), damit sie im Prinzip auch ohne GUI aufgerufen werden könnte.

Diese Trennung von GUI-Logik und Verarbeitungslogik ist ein gutes Software-Design-Prinzip, das Wartbarkeit und Wiederverwendbarkeit verbessert.

### Unterstützte Eingabeformate

`.mov`, `.mp4`, `.avi`, `.mkv` und weitere Formate, je nach installierten Codecs auf dem System.

### Unterstützte Ausgabeformate

```
.mp4  →  FourCC: mp4v
.avi  →  FourCC: XVID
andere → FourCC: mp4v (Default)
```

---

## Benutzung

```bash
pip install opencv-python
python3 video_bearbeitung.py
```

Das Programm öffnet ein GUI-Fenster. Dort können Eingabedatei, Ausgabedatei sowie optional Ziel-FPS, -Breite und -Höhe angegeben werden. Mit „Konvertierung starten" wird die Verarbeitung gestartet, der Fortschritt ist im Status-Label sichtbar.

**Hinweis:** Das Ausgabevideo enthält **keine Audiospur**, da OpenCV keine Audioverarbeitung unterstützt. Für Videos mit Audio ist `ffmpeg` oder `moviepy` empfohlen.
