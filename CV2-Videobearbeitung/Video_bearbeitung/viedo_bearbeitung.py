#!/usr/bin/env python3
"""
video_bearbeitung.py

Einfacher Video-Konverter/-Resizer mit OpenCV (cv2) und tkinter GUI.
Dieses Skript liest ein Eingabevideo ein, optional werden Bildgröße und Ziel-fps
angepasst und das Ergebnis in eine Ausgabedatei geschrieben.

WICHTIG:
- OpenCV schreibt keine Audiospuren — das Ausgabefile enthält KEIN Audio.
- Die verfügbaren Codecs/Container hängen vom OpenCV-Build und den auf dem System
  verfügbaren Backends (ggf. libav/ffmpeg) ab. mp4v/XVID sind häufig verwendete
  FourCCs, funktionieren aber nicht in allen Umgebungen.
- Feinsteuerung der Qualität (CRF, Presets, Bitrate) ist mit OpenCV nicht möglich.
  Für genaue Kontrolle und Audio-Muxing ist ffmpeg die bessere Wahl.

Benutzung:
    python3 video_bearbeitung.py

Das Programm öffnet ein GUI-Fenster zur Eingabe der Parameter.

Abhängigkeiten:
    pip install opencv-python
    (tkinter ist in der Standardinstallation enthalten)

Autorenhinweis:
    Dieses Skript ist bewusst einfach gehalten und für schnelle, einfachen
    frame-basierten Konvertierungen/Resizings ohne Audio gedacht.
"""

import cv2
import sys
import os
import threading
from tkinter import Tk, Label, Entry, Button, Frame, filedialog, messagebox, StringVar
from tkinter import ttk


class VideoConverterGUI:
    """
    GUI-Klasse für den Video-Konverter mit tkinter.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Video Bearbeitung - Konverter")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # Styling
        self.root.configure(bg="#f0f0f0")

        # Erstelle das GUI
        self.create_widgets()

    def create_widgets(self):
        """
        Erstellt alle GUI-Elemente.
        """

        # Titel
        title_label = Label(
            self.root,
            text="Video-Konverter",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333"
        )
        title_label.pack(pady=15)

        # Haupt-Frame
        main_frame = Frame(self.root, bg="#f0f0f0")
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # ===== EINGABEDATEI =====
        Label(main_frame, text="Eingabedatei:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0,
                                                                                               sticky="w", pady=8)
        self.input_var = StringVar()
        input_entry = Entry(main_frame, textvariable=self.input_var, width=35, font=("Arial", 9))
        input_entry.grid(row=0, column=1, padx=10)
        browse_input_btn = Button(main_frame, text="Durchsuchen", command=self.browse_input, bg="#4CAF50", fg="white",
                                  font=("Arial", 9))
        browse_input_btn.grid(row=0, column=2, padx=5)

        # ===== AUSGABEDATEI =====
        Label(main_frame, text="Ausgabedatei:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0,
                                                                                               sticky="w", pady=8)
        self.output_var = StringVar()
        output_entry = Entry(main_frame, textvariable=self.output_var, width=35, font=("Arial", 9))
        output_entry.grid(row=1, column=1, padx=10)
        browse_output_btn = Button(main_frame, text="Durchsuchen", command=self.browse_output, bg="#4CAF50", fg="white",
                                   font=("Arial", 9))
        browse_output_btn.grid(row=1, column=2, padx=5)

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=15)

        # ===== FPS =====
        Label(main_frame, text="Ziel-FPS (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=8)
        self.fps_var = StringVar()
        fps_entry = Entry(main_frame, textvariable=self.fps_var, width=15, font=("Arial", 9))
        fps_entry.grid(row=3, column=1, sticky="w", padx=10)
        Label(main_frame, text="(z.B. 25.0)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=3, column=2,
                                                                                               sticky="w")

        # ===== BREITE =====
        Label(main_frame, text="Ziel-Breite (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=4,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         pady=8)
        self.width_var = StringVar()
        width_entry = Entry(main_frame, textvariable=self.width_var, width=15, font=("Arial", 9))
        width_entry.grid(row=4, column=1, sticky="w", padx=10)
        Label(main_frame, text="(z.B. 1280)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=4, column=2,
                                                                                               sticky="w")

        # ===== HÖHE =====
        Label(main_frame, text="Ziel-Höhe (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=5, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=8)
        self.height_var = StringVar()
        height_entry = Entry(main_frame, textvariable=self.height_var, width=15, font=("Arial", 9))
        height_entry.grid(row=5, column=1, sticky="w", padx=10)
        Label(main_frame, text="(z.B. 720)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=5, column=2,
                                                                                              sticky="w")

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=15)

        # ===== BUTTONS =====
        button_frame = Frame(main_frame, bg="#f0f0f0")
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)

        start_btn = Button(
            button_frame,
            text="Konvertierung starten",
            command=self.start_conversion,
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            width=20,
            height=2
        )
        start_btn.pack(pady=5)

        reset_btn = Button(
            button_frame,
            text="Zurücksetzen",
            command=self.reset_form,
            bg="#f44336",
            fg="white",
            font=("Arial", 10)
        )
        reset_btn.pack(pady=5)

        # Status-Label
        self.status_label = Label(
            self.root,
            text="Bereit",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#666"
        )
        self.status_label.pack(pady=10)

    def browse_input(self):
        """Öffnet Datei-Dialog für Eingabedatei."""
        file_path = filedialog.askopenfilename(
            title="Eingabevideo wählen",
            filetypes=[("Video-Dateien", "*.mov *.mp4 *.avi *.mkv"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)

    def browse_output(self):
        """Öffnet Datei-Dialog für Ausgabedatei."""
        file_path = filedialog.asksaveasfilename(
            title="Ausgabedatei speichern als",
            filetypes=[("MP4-Dateien", "*.mp4"), ("AVI-Dateien", "*.avi"), ("Alle Dateien", "*.*")],
            defaultextension=".mp4"
        )
        if file_path:
            self.output_var.set(file_path)

    def reset_form(self):
        """Setzt alle Felder zurück."""
        self.input_var.set("")
        self.output_var.set("")
        self.fps_var.set("")
        self.width_var.set("")
        self.height_var.set("")
        self.status_label.config(text="Bereit", fg="#666")

    def start_conversion(self):
        """Startet die Konvertierung in einem separaten Thread."""

        # Validierung
        input_path = self.input_var.get().strip()
        output_path = self.output_var.get().strip()

        if not input_path or not output_path:
            messagebox.showerror("Fehler", "Eingabe- und Ausgabedatei sind erforderlich!")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Fehler", "Eingabedatei existiert nicht!")
            return

        # Versuche optionale Parameter zu parsen
        try:
            fps = float(self.fps_var.get()) if self.fps_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Fehler", "FPS muss eine Zahl sein (z.B. 25.0)")
            return

        try:
            width = int(self.width_var.get()) if self.width_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Fehler", "Breite muss eine ganze Zahl sein (z.B. 1280)")
            return

        try:
            height = int(self.height_var.get()) if self.height_var.get().strip() else None
        except ValueError:
            messagebox.showerror("Fehler", "Höhe muss eine ganze Zahl sein (z.B. 720)")
            return

        # Starte Konvertierung in separatem Thread (damit GUI nicht einfriert)
        thread = threading.Thread(
            target=self.run_conversion,
            args=(input_path, output_path, fps, width, height)
        )
        thread.daemon = True
        thread.start()

    def run_conversion(self, input_path, output_path, fps, width, height):
        """
        Führt die Konvertierung durch und aktualisiert den Status.
        """
        self.status_label.config(text="Konvertierung läuft...", fg="#FF9800")
        self.root.update()

        ok = convert_cv2(input_path, output_path, fps, width, height, self.update_status)

        if ok:
            self.status_label.config(text="✓ Konvertierung erfolgreich!", fg="#4CAF50")
            messagebox.showinfo("Erfolg", f"Video erfolgreich konvertiert:\n{output_path}")
        else:
            self.status_label.config(text="✗ Fehler bei der Konvertierung", fg="#f44336")
            messagebox.showerror("Fehler", "Die Konvertierung ist fehlgeschlagen.")

    def update_status(self, message):
        """Aktualisiert das Status-Label."""
        self.status_label.config(text=message)
        self.root.update()


def convert_cv2(input_path, output_path, out_fps=None, out_width=None, out_height=None, status_callback=None):
    """
    Konvertiert ein Video mit OpenCV.

    Parameter:
    - input_path: Pfad zur Eingabedatei (z. B. "in.mov")
    - output_path: Pfad zur Ausgabedatei inklusive Endung (z. B. "out.mp4")
    - out_fps: gewünschte Ziel-FPS (float) oder None, um input-FPS zu verwenden
    - out_width: gewünschte Ziel-Breite (int) oder None, um input-Breite zu verwenden
    - out_height: gewünschte Ziel-Höhe (int) oder None, um input-Höhe zu verwenden
    - status_callback: optionale Funktion für Status-Updates

    Rückgabe:
    - True bei Erfolg, False bei Fehlern.
    """

    # Öffne die Eingabedatei
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        if status_callback:
            status_callback("Fehler: Eingabevideo konnte nicht geöffnet werden")
        print("Fehler: Eingabevideo konnte nicht geöffnet werden.")
        return False

    # Lese Input-Metadaten
    in_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Bestimme Zielwerte
    target_fps = float(out_fps) if out_fps else in_fps
    tw = int(out_width) if out_width else width
    th = int(out_height) if out_height else height

    # FourCC-Code wählen
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".mp4":
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    elif ext in (".avi", ".divx"):
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
    else:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Erzeuge VideoWriter
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (tw, th))
    if not out.isOpened():
        if status_callback:
            status_callback("Fehler: Ausgabedatei konnte nicht geöffnet werden")
        print("Fehler: Ausgabedatei konnte nicht geöffnet werden.")
        cap.release()
        return False

    # Lese und schreibe Frames
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Skaliere bei Bedarf
        if (tw, th) != (width, height):
            frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)

        # Schreibe Frame
        out.write(frame)

        frame_count += 1
        if status_callback and frame_count % 30 == 0:  # Update alle 30 Frames
            progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
            status_callback(f"Konvertierung läuft... {progress:.1f}%")

    # Ressourcen freigeben
    cap.release()
    out.release()
    return True


def main():
    """
    Hauptfunktion: Startet die GUI.
    """
    root = Tk()
    gui = VideoConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()