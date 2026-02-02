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

Neuer Stand: Oval/Auto-Loch + Live-Steuerung + Template-Wechsel

Seit dem letzten Stand wurde die „Face in Hole“-Endversion erweitert:

Oval statt Kreis: Das Einfügen erfolgt nicht mehr mit einer Kreis-Maske, sondern als Ellipse/Oval, passend zum Loch im Template.

Automatische Loch-Erkennung: Die Position und Größe des Lochs wird pro Template automatisch über den Alpha-Kanal erkannt (transparenter Bereich) und als Ellipse angenähert (fitEllipse / Bounding-Box als Fallback).

Mirror dauerhaft aktiv: Das Webcam-Bild wird standardmäßig gespiegelt (cv2.flip(frame, 1)), damit es wie eine Selfie-Kamera wirkt.

Live-Zoom / Feinjustierung: Die Größe des sichtbaren Gesichts wird über skalierte ROI-Werte angepasst (mehr Gesicht / weniger Umfeld) ohne hartes Reinzoomen.
Steuerung:

[ / ] → Zoom (FACE_SCALE_X/Y)

; / ' → vertikaler Zoom (FACE_SCALE_Y)

d → Debug ein/aus

p → aktuelle Werte ausgeben (zum Fixieren)

s → Screenshot speichern

ESC / q → beenden

Template-Wechsel per Tastendruck: Mehrere Templates werden in TEMPLATE_PATHS hinterlegt und können während der Laufzeit gewechselt werden:

n / b → nächstes/vorheriges Template

1–4 → direktes Auswählen

Hinweis zu Templates:
Alle Templates müssen als PNG mit Transparenz (Alpha) vorliegen (Loch = transparent).
Mein aktuelles Template heißt template_v2(.png) und muss in TEMPLATE_PATHS entsprechend eingetragen werden.
