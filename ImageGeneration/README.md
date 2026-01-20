# 2526_5AHEL_MWIT
Individual Projects for MWIT 

# Programmdokumentation – Face in Hole

## Projektziel
Ziel dieses Projekts ist es, ein Webcam-Bild so mit einem PNG-Template zu kombinieren,  
dass das Gesicht einer Person durch ein transparentes „Loch“ im Bild sichtbar wird  .

Dabei soll das Template im Vordergrund liegen, während das Kamerabild im Hintergrund sichtbar ist.

---

## Verwendete Technologien
- **Python 3**
- **OpenCV (cv2)** für:
  - Zugriff auf die Webcam
  - Gesichtserkennung
  - Bildverarbeitung
- **PNG mit Alpha-Kanal** zur Darstellung des Vordergrund-Templates
- **GitHub** zur Versionsverwaltung

---

## Programmübersicht
Das Programm besteht aus folgenden Hauptschritten:

1. Laden des PNG-Templates mit Transparenz
2. Initialisierung der Webcam
3. Gesichtserkennung im Kamerabild
4. Verarbeitung und Transformation des Kamerabildes
5. Alpha-Compositing (Überlagerung von Template und Webcam)
6. Anzeige des Ergebnisses

---

## Laden des Templates
Das Template wird als PNG mit Alpha-Kanal geladen:

```python
template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)


