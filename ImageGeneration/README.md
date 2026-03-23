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

`TEMPLATES` enthält PNG-Dateien
`OVERFILL` macht Gesicht leicht größer als das Loch
`CAMERA_SCALE` vergrößert Kamerabereich
`zoom_left` und `zoom_right` speichern  Zoom für linkes und rechtes Gesicht

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



Das Template wird als PNG mit einem sogenannten *Alpha-Kanal* geladen.
  * Alpha gehört zu RGB dazu, wenn ein Bild Transparenz speichern kann
  * RGB beschreibt die Farbe eines Pixels, Alpha beschreibt wie sichtbar es ist (RGBA)

Der Alpha-Kanal enthält die Transparenz jedes Pixels:

* Alpha = 0 → Pixel ist vollständig transparent
* Alpha = 255 → Pixel ist sichtbar

Zuerste wird nur dieser Alpha-Kanal ausgelesen:

`alpha = template[:, :, 3]
hole_mask = (alpha == 0).astype(np.uint8) * 255`
Wo alpha == 0 → True → wird zu 1 → 255 ⇒ weiß(transparent)
sonst → False → wird zu 0 ⇒ schwarz(sichtbares Template)

  * --> Alle transparenten Pixel (Alpha=0) werden als Maske markiert.
  * --> Diese Maske zeigt die Position der Öffnung für das Fesicht.

Wenn mehrere getrennte transparenten Bereiche vorhanden sind, werden diese
mit OpenCV automatisch erkannt:
`num_labels, labels = cv2.connectedComponents(hole_mask)`
Damit weden mehrere Löcher voneinander getrennt.

OpenCV(Open Source Computer Vision Library):
  Bibliothek für Bild- und Videobearbeitung
  - Webcam lesen
  - Gesichter erkennen (Haar Cascades)
  - Masken bearbeiten
  - Bildbereiche ausschneiden/skalieren
  - Bilder zusammensetzen 

Für jedes Loch wird anschließend eine sogenannte *Bounding Box* berechnet:
`y0, y1 = ys.min(), ys.max()
x0, x1 = xs.min(), xs.max()`

= der rechteckige Bereich, der ein Loch vollständig umschließt.

Diese Bounding Box definiert:
* Wo das Gesicht eingesetzt wird
* Wie groß das Gesicht werden muss
  
Dadurch funktionieren verschiedene Templates Automatisch, ohne dass die Koordinaten
für das Gesicht jedes mal manuell angepasst werden muss. 

---

## Unterstützung von bis zu zwei Gesichtern

Die Gesichtserkennung erfolgt mit einer _Haar Cascade_:

→ vortrainiertes Klassifikationsmodell zur Objekterkennung
  * sucht im Bild nach typischen Kontrastmustern z.B.:
      *  Augenbereich dunkler als Stirn
      *  Nase heller als Augen
      *  Symmetrische Strukturen
   

`faces = face_cascade.detectMultiScale(gray, 1.05, 4)`

Diese Funktion liefert für jedes erkannte Gesicht:
`(x, y, w, h)` → Position und Größe des Gesichts

Die Gesichter werden anschließend nach ihrer horizontalen Position sortiert:
`faces = sorted(faces, key=lambda f: f[0])[:2]`
Das heißt:
  - Linkes Gesicht → linkes Loch
  - Rechtes Gesicht → rechtes Loch
    
Falls nur ein Gesicht erkannt wird, wird nur das erste Loch verwendet.



## Gesichtsstabilisierung

Problem:
Die Gesichtserkennung schwankt leicht zwischen einzelnen Frames.

Lösung:
Exponentielle Glättung der Position.

Die aktuelle Position wird mit der vorherigen Position kombiniert.
Dadurch werden kleine Sprünge reduziert.

Ergebnis:

* Ruhigere Darstellung
* Weniger Zittern
* Natürlichere Bewegung

---

## Erweiterter Kamera-Spielraum

Die Kameraaufnahme wird vor der Verarbeitung vergrößert.

Dadurch entsteht mehr Bewegungsfreiheit innerhalb des Templates.

Vorteile:

* Gesicht wird nicht sofort abgeschnitten
* Bewegungen wirken natürlicher
* Bessere Zentrierung möglich

---

## Freeze-Edit-Modus

Mit der Taste `s` kann der aktuelle Frame eingefroren werden.

Im Freeze-Modus:

* Zoom kann weiter angepasst werden
* Das Bild bleibt stabil
* Feine Nachjustierung ist möglich

Erneutes Drücken von `s` kehrt in den Live-Modus zurück.

---

# Was bedeutet der Alpha-Kanal?

Ein PNG-Bild kann neben den Farbinformationen (BGR) einen Alpha-Kanal besitzen.

Der Alpha-Kanal bestimmt die Transparenz eines Pixels:

* Alpha = 255 → vollständig sichtbar
* Alpha = 0 → vollständig transparent

Im Projekt bedeutet das:

* Der Körper und Hintergrund des Templates sind sichtbar
* Das Loch im Gesicht ist transparent
* Durch das Loch sieht man das Webcam-Bild

---

# Alpha-Compositing

Die Überlagerung von Template und Webcam erfolgt mit folgender Formel:

```
out = alpha * template + (1 - alpha) * webcam
```

Dabei gilt:

* Template wird nur dort angezeigt, wo Alpha > 0
* Webcam wird nur dort angezeigt, wo Alpha = 0

Dies ist der zentrale technische Mechanismus des Projekts.

---

# Live-Steuerung

Während der Laufzeit können verschiedene Parameter angepasst werden.

## Zoom-Steuerung

Bei einem Gesicht:

* `+ / -` → Zoom

Bei zwei Gesichtern:

* `+ / -` → Zoom linkes Gesicht
* `p / m` → Zoom rechtes Gesicht

---

## Weitere Steuerung

* `s` → Freeze / Edit-Modus
* `d` → Debug-Modus (Bounding Box anzeigen)
* `n` → nächstes Template
* `b` → vorheriges Template
* `ESC / q` → Programm beenden

---

# Template-Anforderungen

* Format: PNG
* Muss einen Alpha-Kanal besitzen
* Gesichtslöcher müssen vollständig transparent sein (Alpha = 0)
* Getrennte Löcher dürfen nicht verbunden sein

---

# Technische Besonderheiten der finalen Version

* Automatische Loch-Erkennung über Alpha-Maske
* Unterstützung von ein oder zwei Gesichtern
* Dynamische Template-Wechsel während der Laufzeit
* Stabilisierung der Gesichtserkennung
* Erweiterter Kamera-Spielraum
* Benutzerfreundliche Live-Steuerung

---

# Aktueller Stand

Das Projekt ist funktionsfähig, stabil und präsentationsbereit.

Es erfüllt die Anforderungen:

* Gesicht hinter PNG
* Transparente Loch-Erkennung
* Mehrere Templates
* Zwei-Gesichter-Unterstützung
* Stabilisierung
* Benutzerinteraktion während der Laufzeit

