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

Benutzung (Beispiel):
    python3 video_bearbeitung.py input.mov output.mp4 --fps 25 --width 1280 --height 720

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

def main():
    """
    CLI-Entrypoint. Parst Argumente und ruft convert_cv2 auf.
    """

    p = argparse.ArgumentParser(description="Einfacher Video-Konverter mit OpenCV (ohne Audio).")
    # Positionale Argumente: input und output
    p.add_argument("input", help="Eingabedatei (z. B. input.mov)")
    p.add_argument("output", help="Ausgabedatei inkl. Endung (z. B. output.mp4)")
    # Optionale Parameter: fps, width, height
    p.add_argument("--fps", type=float, help="Ziel-fps (z. B. 25.0). Wenn weggelassen, bleibt die Original-fps erhalten.")
    p.add_argument("--width", type=int, help="Ziel-Breite in Pixel (z. B. 1280). Wenn weggelassen, bleibt die Original-Breite erhalten.")
    p.add_argument("--height", type=int, help="Ziel-Höhe in Pixel (z. B. 720). Wenn weggelassen, bleibt die Original-Höhe erhalten.")
    args = p.parse_args()

    # Aufruf der Konvertierungsfunktion mit den geparsten Argumenten
    ok = convert_cv2(args.input, args.output, args.fps, args.width, args.height)
    if not ok:
        # Fehlercode ≠ 0 signalisiert dem Aufrufer, dass etwas schief lief
        sys.exit(1)

    # Erfolgsmeldung und Hinweis, dass kein Audio enthalten ist
    print("Konvertierung fertig (ohne Audio):", args.output)
    print("Hinweis: Audio wurde NICHT übernommen. Für Audio/Muxing nutze ffmpeg oder ähnliche Tools.")

if __name__ == "__main__":
    main()