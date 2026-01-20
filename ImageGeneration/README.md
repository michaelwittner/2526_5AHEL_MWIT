# 2526_5AHEL_MWIT
Individual Projects for MWIT 

# Programmdokumentation – Face in Hole

## Projektübersicht
Ziel des Projekts ist es, ein Webcam-Bild mit einem PNG-Template so zu kombinieren,  
dass das Gesicht einer Person durch ein transparentes Loch im Bild sichtbar ist  
(„Face in Hole“-Effekt).

Das PNG-Template liegt dabei im Vordergrund, das Webcam-Bild im Hintergrund.

---

## Aufbau des Projekts
Das Projekt besteht aus mehreren Python-Dateien, die schrittweise entwickelt wurden.

### step1_webcam_face.py
**Zweck:**
- Testen der Webcam
- Überprüfung der Gesichtserkennung

**Funktion:**
- Öffnet die Webcam
- Erkennt Gesichter mit Haar Cascades
- Zeichnet ein Rechteck um erkannte Gesichter

Diese Datei dient ausschließlich als Test- und Einstiegscode.

---

### step2_face_in_hole.py
**Zweck:**
- Erstes „Face in Hole“-Prinzip ohne Transparenz

**Funktion:**
- Ein normales Bild (ohne Alpha) wird geladen
- Das erkannte Gesicht wird direkt in das Bild eingefügt
- Eine kreisförmige Maske simuliert das Loch

Diese Variante überschreibt Bildpixel und nutzt noch keinen Alpha-Kanal.

---

### step2_face_in_hole_alpha.py
**Zweck:**
- Endversion mit echtem PNG-Template und Transparenz

**Funktion:**
- PNG mit Alpha-Kanal wird geladen
- Webcam-Bild liegt im Hintergrund
- Template liegt im Vordergrund
- Das Gesicht ist nur im transparenten Bereich sichtbar

Diese Datei bildet den Kern des Projekts.

---

## Was bedeutet der Alpha-Kanal?
Ein PNG-Bild kann neben den Farbinformationen (BGR) einen **Alpha-Kanal** besitzen.

Der Alpha-Kanal bestimmt die Transparenz eines Pixels:

- Alpha = 255 → vollständig sichtbar
- Alpha = 0 → vollständig transparent

Im Projekt bedeutet das:
- Der Körper, Rahmen und Hintergrund des Templates sind sichtbar
- Das Loch im Gesicht ist transparent
- Durch das Loch sieht man das Webcam-Bild

---

## Alpha-Compositing
Die Überlagerung von Template und Webcam erfolgt mit folgender Formel:

```python
out = alpha * template + (1 - alpha) * webcam
