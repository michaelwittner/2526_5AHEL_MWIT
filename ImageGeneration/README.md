# 2526_5AHEL_MWIT

# Projektübersicht

Ziel des Projekts ist es, ein Webcam-Bild mit einem PNG-Template so zu kombinieren,
dass das Gesicht einer Person durch ein transparentes Loch im Bild sichtbar ist
(„Face in Hole“-Effekt).

Das PNG-Template liegt dabei im Vordergrund, das Webcam-Bild im Hintergrund.

Das Projekt wurde schrittweise erweitert und technisch verbessert.

_Voraussetzungen_: Python, OpenCV, Numpy
_Entwicklungsumgebung_: PyCharm

# Voraussetzungen
_Installation_
`pip install opencv-python numpy` 

---


# Aufbau des Projekts

Das Projekt besteht aus mehreren Python-Dateien, die nacheinander entwickelt wurden.

---

## Erstes Testprojekt
<img width="412" height="55" alt="grafik" src="https://github.com/user-attachments/assets/b36aaaf5-4bfe-4967-b83a-824e3d31e261" />


## Zweites Testfile: step1_webcam_face.py

### Zweck

Grundlegender Test der Webcam und der Gesichtserkennung.

### Funktion

* Öffnet die Webcam
* Erkennt Gesichter mit Haar Cascades
* Zeichnet eine Bounding Box um erkannte Gesichter

Diese Datei diente als technische Basis für alle weiteren Schritte.

---

## step2_face_in_hole.py

### Zweck

Erstes funktionierendes „Face in Hole“-Prinzip ohne Transparenz.

### Funktion

* Ein normales Bild wird geladen
* Das erkannte Gesicht wird skaliert
* Eine kreisförmige Maske simuliert das Gesichtsloch

Diese Variante überschreibt Pixel direkt und nutzt noch keinen Alpha-Kanal.

---

## step2_face_in_hole_alpha.py

### Zweck

Einführung von PNG-Template mit Transparenz.

### Funktion

* PNG wird geladen
* Webcam-Bild liegt im Hintergrund
* Template liegt im Vordergrund
* Das Gesicht ist nur im transparenten Bereich sichtbar

---

## step2_face_in_hole_auto_ellipse.py

- mehrere PNG-Templates mit Alpha-Kanal geladen + automatisch analysiert.  
- Ellipse/Bounding Box bestimmt, um das Gesicht passend einzusetzen.
- wechsel zwischen mehreren Templates:
    - n/b switch
    - [] zoom
    - ;/' y-zoom
    - d debug
    - p print (`FACE_SCALE_X`; `FACE_SCALE_Y`.   
    - s shot (speichert Screenshot)


# Erweiterte Version – Finale Implementierung

---

## 1. Bibliotheken 

<img width="209" height="76" alt="grafik" src="https://github.com/user-attachments/assets/9ebefde8-5abf-4c94-b1ff-f7b83f0d1760" />

- **cv2**: Kamera, Gesichtserkennung, Bildverarbeitung
- **numpy**: Masken und Rechenoperationen
- **time**: Zeitstempel für Screenshots / Hilfsfunktionen

## 2. Template-Liste und Grundeinstellungen

<img width="562" height="375" alt="grafik" src="https://github.com/user-attachments/assets/b6c18486-2cea-460c-92b5-86232b3a98cb" />

- `TEMPLATES` enthält PNG-Dateien
- `OVERFILL` macht Gesicht leicht größer als das Loch
- `CAMERA_SCALE` vergrößert Kamerabereich
- `zoom_left` und `zoom_right` speichern  Zoom für linkes und rechtes Gesicht

## 3. Gesichtsstabilisierung vorbereiten
Problem:
Die Gesichtserkennung schwankt leicht zwischen einzelnen Frames.

Lösung:
glätten

<img width="286" height="102" alt="grafik" src="https://github.com/user-attachments/assets/11003ff4-6407-4a26-8840-10d40e38590e" />

## 4. Freeze-Edit-Modus
`s` drücken: Bild wird eingefroren --> danach noch fein justierbar

<img width="218" height="60" alt="grafik" src="https://github.com/user-attachments/assets/7c872c1f-e486-43e2-89f5-04ad366ffe95" />

## 5.Alpha-Compositing und Alpha-Kanal


# Was bedeutet der Alpha-Kanal?

Ein PNG-Bild kann neben den Farbinformationen (BGR) einen Alpha-Kanal besitzen.

Der Alpha-Kanal bestimmt die Transparenz eines Pixels:

* Alpha = 255 → vollständig sichtbar
* Alpha = 0 → vollständig transparent

Die Überlagerung von Template und Webcam erfolgt mit folgender Formel:

```
out = alpha * template + (1 - alpha) * webcam
```
<img width="505" height="117" alt="grafik" src="https://github.com/user-attachments/assets/69bdb50c-5586-4d51-846f-06baca7b6778" />


Dabei gilt:

* Template wird nur dort angezeigt, wo Alpha > 0
* Webcam wird nur dort angezeigt, wo Alpha = 0


## 6. Template laden
Das Template wird als PNG mit Alpha-Kanal geladen.
Zusätzlich werden die transparenten Bereiche analysiert.

<img width="633" height="245" alt="grafik" src="https://github.com/user-attachments/assets/923cab9d-fb41-434c-9ae1-96bc48e3ff7d" />

`IMREAD_UNCHANGED` lädt auch den Alpha-Kanal mit.
Es wird geprüft, ob das Template existiert und Transparenz besitzt.

## 7. Automatische Loch-Erkennung
Das Gesichtsloch wird automatisch über den Alpha-Kanal gefunden.

<img width="521" height="90" alt="grafik" src="https://github.com/user-attachments/assets/061085f4-4449-4ed5-b0f9-f5a2b34e6d11" />

## 8. Mehrere Löcher erkennen
Falls ein Template mehrere Gesichtsöffnungen hat, werden diese getrennt erkannt.

<img width="586" height="70" alt="grafik" src="https://github.com/user-attachments/assets/df2d3dfd-60f8-40fe-aac0-139e957cc86c" />

`connectedComponents` trennt zusammenhängende Lochbereiche.
So können z. B. zwei Gesichter in einem Template verwendet werden.

## 9. Bounding Box der Löcher berechnen
Für jedes Loch wird ein rechteckiger Bereich berechnet.

<img width="416" height="169" alt="grafik" src="https://github.com/user-attachments/assets/962e7247-f632-4955-bbd0-4be54522b2e0" />

Die Bounding Box umschließt das Loch vollständig.
Sie definiert Position und Größe des Gesichtsbereichs.

## 10. Gesichtsstabilisierung
Die Gesichtsposition wird geglättet, um Zittern zu reduziere

<img width="542" height="421" alt="grafik" src="https://github.com/user-attachments/assets/fc38d2f5-0e9c-42f3-bb65-b648edb34d7c" />

Alte und neue Werte werden gemischt.
Kleine Schwankungen werden reduziert.
Das Ergebnis wirkt ruhiger.

## 11.Initialisierung im Hauptprogramm
Im Hauptprogramm werden Template, Kamera und Gesichtserkennung vorbereitet.

<img width="722" height="142" alt="grafik" src="https://github.com/user-attachments/assets/c2bb0318-a8b0-48d8-aebd-1c0a02ddbd77" />

`template_bgr` enthält die Farbinformation.
`alpha` wird auf den Bereich 0 bis 1 normiert.
`CAP_DSHOW` wird unter Windows verwendet.

## 12.Gesichtserkennung
Die Haar Cascade erkennt Gesichter im Graustufenbild.

<img width="538" height="211" alt="grafik" src="https://github.com/user-attachments/assets/72c8559e-bfc2-4b01-98d2-140805e3a3b3" />

Das Bild wird in Graustufen umgewandelt.
`detectMultiScale` erkennt Gesichter verschiedener Größe.
Rückgabe pro Gesicht: `(x, y, w, h)`

## 13.Sortierung der Gesichter
Damit linkes Gesicht ins linke Loch kommt, werden die Gesichter nach X-Position sortiert

<img width="478" height="40" alt="grafik" src="https://github.com/user-attachments/assets/59954e2c-43d2-457c-bee5-f7e040bc4df6" />

`f[0]` ist die X-Position.
Es werden maximal zwei Gesichter verwendet.
Links → links, rechts → rechts.

## 14. Kamera-Spielraum vergrößern
Vor der Verarbeitung wird das Kamerabild vergrößert, damit mehr Bewegungsfreiheit entsteht.

<img width="789" height="110" alt="grafik" src="https://github.com/user-attachments/assets/75b91c0e-4bbc-466b-a38c-34933da7f3d1" />

Das Bild wird zuerst größer gemacht.
Danach wird mittig ausgeschnitten.
Dadurch entsteht mehr Spielraum.

## 15. Gesicht ins Loch einsetzen
Das Gesicht wird auf die Lochgröße skaliert und an der richtigen Stelle eingesetzt.

<img width="567" height="121" alt="grafik" src="https://github.com/user-attachments/assets/fc50ac0d-df1a-4c5f-824b-54adb39b1d36" />
<img width="604" height="46" alt="grafik" src="https://github.com/user-attachments/assets/636428e9-216e-4282-ae40-dfbd84808c1a" />

Das Gesicht wird proportional skaliert.
`OVERFILL` sorgt dafür, dass das Loch gut ausgefüllt wird.
`zoom` erlaubt manuelle Nachjustierung.

## 16. Template-Wechsel

<img width="831" height="212" alt="grafik" src="https://github.com/user-attachments/assets/79a26d1f-1caf-47a2-bb76-3ede1d08d027" />

n = nächstes Template
b = vorheriges Template

## 17.Steuerung
| Taste     | Funktion             |
| --------- | -------------------- |
| `+ / -`   | Zoom linkes Gesicht  |
| `p / m`   | Zoom rechtes Gesicht |
| `s`       | Freeze/Edit-Modus    |
| `d`       | Debug-Modus          |
| `n / b`   | Template wechseln    |
| `ESC / q` | Beenden              |

## 18. Quellen


- OpenCV Dokumentation – CascadeClassifier / detectMultiScale  
  https://docs.opencv.org/4.x/d1/de5/classcv_1_1CascadeClassifier.html  
  zuletzt besucht: 23.03.2026 

- OpenCV Dokumentation – Connected Components / Shape Analysis  
  https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html  
  zuletzt besucht: 23.03.2026 

- OpenCV Dokumentation – VideoCapture  
  https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html  
  zuletzt besucht: 23.03.2026 

- OpenCV Dokumentation – Geometric Image Transformations  
  https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html  
  zuletzt besucht: 23.03.2026 

- NumPy Dokumentation – Grundlagen / Arrays  
  https://numpy.org/doc/stable/user/absolute_beginners.html  
  zuletzt besucht: 23.03.2026 :

- PyCharm Dokumentation – Installation Guide  
  https://www.jetbrains.com/help/pycharm/installation-guide.html  
  zuletzt besucht: 23.03.2026 

## KI-Unterstützung

- ChatGPT wurde zur Unterstützung bei:
  - Code-Strukturierung
  - Debugging
  - Erklärung technischer Konzepte




