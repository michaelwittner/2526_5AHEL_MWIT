# 2526_5AHEL_MWIT

Individual Projects for MWIT

---

# Projektübersicht

Ziel des Projekts ist es, ein Webcam-Bild mit einem PNG-Template so zu kombinieren,
dass das Gesicht einer Person durch ein transparentes Loch im Bild sichtbar ist
(„Face in Hole“-Effekt).

Das PNG-Template liegt dabei im Vordergrund, das Webcam-Bild im Hintergrund.

---

# Aufbau des Projekts

Das Projekt besteht aus mehreren Python-Dateien, die schrittweise entwickelt wurden.

---

## step1_webcam_face.py

### Zweck

* Testen der Webcam
* Überprüfung der Gesichtserkennung

### Funktion

* Öffnet die Webcam
* Erkennt Gesichter mit Haar Cascades
* Zeichnet ein Rechteck um erkannte Gesichter

Diese Datei dient ausschließlich als Test- und Einstiegscode.

---

## step2_face_in_hole.py

### Zweck

Erstes „Face in Hole“-Prinzip ohne Transparenz.

### Funktion

* Ein normales Bild (ohne Alpha) wird geladen
* Das erkannte Gesicht wird direkt in das Bild eingefügt
* Eine kreisförmige Maske simuliert das Loch

Diese Variante überschreibt Bildpixel und nutzt noch keinen Alpha-Kanal.

---

## step2_face_in_hole_alpha.py

### Zweck

Endversion mit echtem PNG-Template und Transparenz.

### Funktion

* PNG mit Alpha-Kanal wird geladen
* Webcam-Bild liegt im Hintergrund
* Template liegt im Vordergrund
* Das Gesicht ist nur im transparenten Bereich sichtbar

Diese Datei bildet den Kern des Projekts.

---

# Erweiterte Version (Auto-Loch, mehrere Templates, Live-Steuerung)

Die aktuelle Version wurde technisch deutlich erweitert.

---

## Automatische Loch-Erkennung

Das Template wird als PNG mit Alpha-Kanal geladen.

Transparente Bereiche werden erkannt durch:

Alpha = 0 → transparent
Alpha = 255 → sichtbar

Die transparenten Bereiche werden analysiert, indem alle Pixel mit Alpha = 0
als Maske extrahiert werden.

Bei mehreren getrennten Löchern werden diese mit
`cv2.connectedComponents()` als separate Bereiche erkannt.

Für jeden Bereich wird eine eigene Bounding Box berechnet.
Diese Bounding Box definiert Position und Größe des Gesichtslochs.

---

## Unterstützung von bis zu zwei Gesichtern

* Es werden maximal zwei Gesichter erkannt.
* Die Gesichter werden nach X-Position (links → rechts) sortiert.
* Das linke Gesicht wird dem linken Loch zugeordnet.
* Das rechte Gesicht wird dem rechten Loch zugeordnet.

Damit können Templates mit zwei transparenten Bereichen verwendet werden.

---

## Oval statt Kreis

Statt einer festen Kreis-Maske wird:

* Entweder eine Ellipse angepasst
* Oder die Bounding Box des Lochs verwendet

Dadurch passt sich das Gesicht besser an unregelmäßige Lochformen an.

---

## Mirror dauerhaft aktiv

Das Webcam-Bild wird mit:

`cv2.flip(frame, 1)`

horizontal gespiegelt.
Dadurch wirkt die Darstellung wie eine Selfie-Kamera.

---

# Was bedeutet der Alpha-Kanal?

Ein PNG-Bild kann neben den Farbinformationen (BGR) einen Alpha-Kanal besitzen.

Der Alpha-Kanal bestimmt die Transparenz eines Pixels:

* Alpha = 255 → vollständig sichtbar
* Alpha = 0 → vollständig transparent

Im Projekt bedeutet das:

* Der Körper, Rahmen und Hintergrund des Templates sind sichtbar
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

* `d` → Debug-Modus (Bounding Box anzeigen)
* `p` → aktuelle Parameter ausgeben
* `s` → Screenshot speichern
* `ESC / q` → Programm beenden

---

# Template-Wechsel während der Laufzeit

Mehrere Templates werden in `TEMPLATE_PATHS` definiert.

Wechsel während der Laufzeit:

* `n` → nächstes Template
* `b` → vorheriges Template
* `1–4` → direktes Auswählen

---

# Anforderungen an Templates

* Format: PNG
* Muss einen Alpha-Kanal besitzen
* Gesichtslöcher müssen vollständig transparent sein (Alpha = 0)
* Getrennte Löcher dürfen nicht verbunden sein

Beispiel:
`template_v2.png`

---


