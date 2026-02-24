# 2526_5AHEL_MWIT
Individual Projects for MWIT 

[Einführung](https://pytutorial.com/python-opencv-cv2videocapture-guide/?utm_source=copilot.com)


1.Test ob das video funktioniert:


````
import cv2
# Create a VideoCapture object
cap = cv2.VideoCapture('vid.mov')

while cap.isOpened():
ret, frame = cap.read()
if not ret:
break
cv2.imshow('Frame', frame)
if cv2.waitKey(25) & 0xFF == ord('q'):
break

cap.release()
cv2.destroyAllWindows()
````
2. Video Schneiden

````
import cv2

# --- Einstellungen ---
input_path = 'vid.mov'          # Eingabevideo
output_path = 'cut.mov'         # Ausgabedatei

start_sec = 5                   # Startzeitpunkt in Sekunden
end_sec = 12                    # Endzeitpunkt in Sekunden

# VideoCapture erstellen
cap = cv2.VideoCapture(input_path)

if not cap.isOpened():
    print("Fehler: Video konnte nicht geöffnet werden.")
    exit()

# Videodaten auslesen
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Frame-Bereiche berechnen
start_frame = int(start_sec * fps)
end_frame = int(end_sec * fps)

# VideoWriter vorbereiten
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # funktioniert auch für .mov
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Zum Startframe springen
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

# --- Video durchgehen ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    # Nur Frames im gewünschten Bereich speichern
    if current_frame <= end_frame:
        out.write(frame)

    # Optional: Vorschau anzeigen
    cv2.imshow('Frame', frame)

    # Mit 'q' abbrechen
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

    # Wenn wir über das Endframe hinaus sind → stoppen
    if current_frame > end_frame:
        break

# Aufräumen
cap.release()
out.release()
cv2.destroyAllWindows()

print("Geschnittenes Video gespeichert als:", output_path)

````

3. Video schneiden mit richtiger skalierung und fenstergröße

````
import cv2
import pyautogui

def cut_video(input_path, output_path, start_sec, end_sec):
    # Bildschirmauflösung holen
    screen_width, screen_height = pyautogui.size()

    # VideoCapture erstellen
    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print("Fehler: Video konnte nicht geöffnet werden.")
        return

    # Videodaten auslesen
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Frame-Bereiche berechnen
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)

    # VideoWriter vorbereiten
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Zum Startframe springen
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # --- Video durchgehen ---
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # Nur Frames im gewünschten Bereich speichern
        if current_frame <= end_frame:
            out.write(frame)

        # --- Frame für Vorschau skalieren ---
        scale = min(screen_width / width, screen_height / height)
        new_w = int(width * scale)
        new_h = int(height * scale)

        resized_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Vorschau anzeigen
        cv2.imshow('Frame', resized_frame)

        # Wenn Fenster per X geschlossen wurde → sofort abbrechen
        if cv2.getWindowProperty('Frame', cv2.WND_PROP_VISIBLE) < 1:
            break

        # Mit 'q' abbrechen
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

        # Wenn wir über das Endframe hinaus sind → stoppen
        if current_frame > end_frame:
            break

    # Aufräumen
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("Geschnittenes Video gespeichert als:", output_path)


# --- Aufruf der Funktion ---
cut_video(
    input_path='vid.mov',
    output_path='cut.mov',
    start_sec=5,
    end_sec=12
)



````
<h2></h2>

#!/usr/bin/env python3
"""
video_bearbeitung.py

Einfacher Video-Konverter/-Resizer mit OpenCV (cv2).
Dieses Skript liest ein Eingabevideo ein, optional werden Bildgröße und Ziel-fps
angepasst und das Ergebnis in eine Ausgabedatei geschrieben.

WICHTIG:
- OpenCV schreibt keine Audiospuren — das Ausgabefile enthält KEIN Audio.
- Die verfügbaren Codecs/Container hängen vom OpenCV-Build und den auf dem System
  verfügbaren Backends (ggf. libav/ffmpeg) ab. mp4v/XVID sind häufig verwendete
  FourCCs, funktionieren aber nicht in allen Umgebungen.
- Feinsteuerung der Qualität (CRF, Presets, Bitrate) ist mit OpenCV nicht möglich.
  Für genaue Kontrolle und Audio-Muxing ist ffmpeg die bessere Wahl.

Benutzung (Kommandozeile):
    python3 video_bearbeitung.py input.mov output.mp4 --fps 25 --width 1280 --height 720

Benutzung (Interaktiv in PyCharm oder direkt):
    Wenn das Skript ohne Kommandozeilen-Argumente aufgerufen wird, werden Sie
    zur Eingabe der Parameter aufgefordert.

Abhängigkeiten:
    pip install opencv-python

Autorenhinweis:
    Dieses Skript ist bewusst einfach gehalten und für schnelle, einfachen
    frame-basierten Konvertierungen/Resizings ohne Audio gedacht.
"""

import cv2
import argparse
import sys
import os


def convert_cv2(input_path, output_path, out_fps=None, out_width=None, out_height=None):
    """
    Konvertiert ein Video mit OpenCV.

    Parameter:
    - input_path: Pfad zur Eingabedatei (z. B. "in.mov")
    - output_path: Pfad zur Ausgabedatei inklusive Endung (z. B. "out.mp4")
    - out_fps: gewünschte Ziel-FPS (float) oder None, um input-FPS zu verwenden
    - out_width: gewünschte Ziel-Breite (int) oder None, um input-Breite zu verwenden
    - out_height: gewünschte Ziel-Höhe (int) oder None, um input-Höhe zu verwenden

    Rückgabe:
    - True bei Erfolg, False bei Fehlern.
    """

    # Öffne die Eingabedatei
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        # Datei konnte nicht geöffnet werden (falscher Pfad, kein Codec, etc.)
        print("Fehler: Eingabevideo konnte nicht geöffnet werden.")
        return False

    # Lese Input-Metadaten
    # Manche Container liefern 0.0 oder None für FPS; daher Default-Wert
    in_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    # Breite/Höhe in Pixeln (ganzzahlig)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Bestimme Zielwerte: falls None übernehme die Input-Werte
    target_fps = float(out_fps) if out_fps else in_fps
    tw = int(out_width) if out_width else width
    th = int(out_height) if out_height else height

    # FourCC-Code wählen basierend auf Ausgabedateiendung
    # Hinweis: mp4v ist ein verbreiteter Fallback, H.264 (x264) ist nicht zuverlässig
    # über OpenCV schreibbar, abhängig vom Build. Für verlässliches H.264-Output
    # empfiehlt sich ffmpeg.
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".mp4":
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    elif ext in (".avi", ".divx"):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
    else:
        # Fallback: mp4v für unbekannte Endungen
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Erzeuge den VideoWriter: öffnet die Ausgabedatei zum Schreiben
    # Parameter: Pfad, FourCC, fps, (width, height)
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (tw, th))
    if not out.isOpened():
        # Fehler beim Öffnen/Erstellen der Ausgabedatei (Berechtigungen, ungültiger FourCC, ...)
        print("Fehler: Ausgabedatei konnte nicht geöffnet werden.")
        cap.release()
        return False

    # Lese Frames in einer Schleife und schreibe sie in den Writer
    # Wenn die Zielauflösung anders ist, werden Frames mit INTER_AREA skaliert
    # (gute Qualität beim Verkleinern).
    while True:
        ret, frame = cap.read()
        if not ret:
            # Ende des Videos oder Lese-Fehler
            break

        # Falls Zielgröße unterschiedlich zur Quellgröße ist, skaliere
        if (tw, th) != (width, height):
            # cv2.resize erwartet (width, height)
            frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)

        # Schreibe Frame in Ausgabedatei
        out.write(frame)

    # Ressourcen freigeben: Capture und Writer schließen
    cap.release()
    out.release()
    return True


def get_input_interactive():
    """
    Interaktiver Modus: Fragt den Nutzer nach Eingabe- und Ausgabepfad
    sowie optionalen Parametern.

    Rückgabe:
    - Tupel (input_path, output_path, fps, width, height)
    """
    print("\n" + "=" * 60)
    print("VIDEO-BEARBEITUNG - Interaktiver Modus")
    print("=" * 60 + "\n")

    # Eingabedatei
    input_path = input("Eingabedatei (z. B. input.mov): ").strip()
    if not input_path:
        print("Fehler: Eingabedatei ist erforderlich!")
        return None

    # Ausgabedatei
    output_path = input("Ausgabedatei mit Endung (z. B. output.mp4): ").strip()
    if not output_path:
        print("Fehler: Ausgabedatei ist erforderlich!")
        return None

    # Optionale Parameter
    print("\nOptionale Parameter (Eingeben zum Überspringen):")

    fps_input = input("Ziel-FPS (z. B. 25.0) [optional]: ").strip()
    fps = float(fps_input) if fps_input else None

    width_input = input("Ziel-Breite in Pixel (z. B. 1280) [optional]: ").strip()
    width = int(width_input) if width_input else None

    height_input = input("Ziel-Höhe in Pixel (z. B. 720) [optional]: ").strip()
    height = int(height_input) if height_input else None

    return (input_path, output_path, fps, width, height)


def main():
    """
    CLI-Entrypoint. Parst Kommandozeilen-Argumente oder startet
    interaktiven Modus, falls keine Argumente vorhanden sind.
    """

    # Prüfe, ob Kommandozeilen-Argumente vorhanden sind
    if len(sys.argv) > 1:
        # Kommandozeilen-Modus
        p = argparse.ArgumentParser(description="Einfacher Video-Konverter mit OpenCV (ohne Audio).")
        # Positionale Argumente: input und output
        p.add_argument("input", help="Eingabedatei (z. B. input.mov)")
        p.add_argument("output", help="Ausgabedatei inkl. Endung (z. B. output.mp4)")
        # Optionale Parameter: fps, width, height
        p.add_argument("--fps", type=float,
                       help="Ziel-fps (z. B. 25.0). Wenn weggelassen, bleibt die Original-fps erhalten.")
        p.add_argument("--width", type=int,
                       help="Ziel-Breite in Pixel (z. B. 1280). Wenn weggelassen, bleibt die Original-Breite erhalten.")
        p.add_argument("--height", type=int,
                       help="Ziel-Höhe in Pixel (z. B. 720). Wenn weggelassen, bleibt die Original-Höhe erhalten.")
        args = p.parse_args()

        input_path = args.input
        output_path = args.output
        fps = args.fps
        width = args.width
        height = args.height
    else:
        # Interaktiver Modus (PyCharm oder direkt ausgeführt)
        result = get_input_interactive()
        if result is None:
            sys.exit(1)
        input_path, output_path, fps, width, height = result

    # Aufruf der Konvertierungsfunktion mit den geparsten Argumenten
    ok = convert_cv2(input_path, output_path, fps, width, height)
    if not ok:
        # Fehlercode ≠ 0 signalisiert dem Aufrufer, dass etwas schief lief
        sys.exit(1)

    # Erfolgsmeldung und Hinweis, dass kein Audio enthalten ist
    print("\n" + "=" * 60)
    print("Konvertierung fertig (ohne Audio):", output_path)
    print("=" * 60)
    print("Hinweis: Audio wurde NICHT übernommen. Für Audio/Muxing nutze ffmpeg oder ähnliche Tools.")


    if __name__ == "__main__":
    main()

    ----
    