#!/usr/bin/env python3
# Shebang: Ermöglicht direktes Ausführen auf Linux/macOS

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
# Dokumentation / Docstring des gesamten Moduls

import cv2
# Importiert OpenCV-Bibliothek für Videobearbeitung

import sys
# Importiert Systemfunktionen (wird hier nicht verwendet)

import os
# Importiert Betriebssystem-Funktionen (für Dateipfade, Existenzprüfung)

import threading
# Importiert Threading-Modul für asynchrone Prozesse (damit GUI nicht einfriert)

from tkinter import Tk, Label, Entry, Button, Frame, filedialog, messagebox, StringVar
# Importiert GUI-Komponenten aus tkinter:
# - Tk: Hauptfenster
# - Label: Text-Beschriftungen
# - Entry: Eingabefelder
# - Button: Schaltflächen
# - Frame: Container für andere Elemente
# - filedialog: Datei-Auswahl-Dialoge
# - messagebox: Fehlermeldungen/Bestätigungen
# - StringVar: Variablen für GUI-Eingaben

from tkinter import ttk


# Importiert modernere tkinter-Komponenten (z.B. Separatoren)


class VideoConverterGUI:
    # Definition der Klasse für die GUI des Video-Konverters
    """
    GUI-Klasse für den Video-Konverter mit tkinter.
    """

    # Docstring (Beschreibung) der Klasse

    def __init__(self, root):
        # Konstruktor: wird aufgerufen, wenn Klasse instanziiert wird
        # Parameter: root = tkinter Hauptfenster

        self.root = root
        # Speichert das Fenster als Klassenvariable

        self.root.title("Video Bearbeitung - Konverter")
        # Setzt den Titel des Fensters

        self.root.geometry("500x550")
        # Setzt die Fenstergröße: 500 Pixel breit, 550 Pixel hoch

        self.root.resizable(False, False)
        # Macht das Fenster nicht größenveränderbar (weder horizontal noch vertikal)

        # Styling
        self.root.configure(bg="#f0f0f0")
        # comment: Setzt Hintergrundfarbe des Fensters auf helles Grau

        # Erstelle das GUI
        self.create_widgets()
        # Ruft Funktion auf, die alle GUI-Elemente erzeugt

    def create_widgets(self):
        # Definition der Methode, die alle GUI-Elemente erstellt
        """
        Erstellt alle GUI-Elemente.
        """
        # Docstring der Methode

        # Titel
        title_label = Label(
            # Erzeugt ein Label (Text-Element)
            self.root,
            # im Hauptfenster
            text="Video-Konverter",
            # mit diesem Text
            font=("Arial", 18, "bold"),
            # Arial-Schrift, Größe 18, fett
            bg="#f0f0f0",
            # Hintergrundfarbe helles Grau
            fg="#333"
            # Schriftfarbe dunkelgrau
        )
        title_label.pack(pady=15)
        # Platziert das Label mit 15 Pixel Abstand oben und unten

        # Haupt-Frame
        main_frame = Frame(self.root, bg="#f0f0f0")
        # Erzeugt einen Container-Frame (Behälter für andere Elemente)
        # mit grauem Hintergrund

        main_frame.pack(padx=20, pady=10, fill="both", expand=True)
        # Platziert Frame mit 20px Abstand links/rechts, 10px oben/unten
        # füllt ganzen verfügbaren Platz aus

        # ===== EINGABEDATEI =====
        Label(main_frame, text="Eingabedatei:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=0, column=0,
                                                                                               sticky="w", pady=8)
        # Erzeugt Label "Eingabedatei:" und platziert es im Gitter
        # row=0, column=0 (oben links), sticky="w" (haftet auf der linken Seite)

        self.input_var = StringVar()
        # Erzeugt StringVar-Variable für das Eingabefeld (speichert Benutzereingabe)

        input_entry = Entry(main_frame, textvariable=self.input_var, width=35, font=("Arial", 9))
        # Erzeugt Eingabefeld mit 35 Zeichen Breite
        # Verbunden mit self.input_var (Änderungen werden in Variable gespeichert)

        input_entry.grid(row=0, column=1, padx=10)
        # Platziert Eingabefeld neben Label (Spalte 1)

        browse_input_btn = Button(main_frame, text="Durchsuchen", command=self.browse_input, bg="#4CAF50", fg="white",
                                  font=("Arial", 9))
        # Erzeugt grünen Button mit Text "Durchsuchen"
        # command=self.browse_input: ruft die browse_input()-Methode auf wenn geklickt

        browse_input_btn.grid(row=0, column=2, padx=5)
        # Platziert Button rechts neben Eingabefeld (Spalte 2)

        # ===== AUSGABEDATEI =====
        Label(main_frame, text="Ausgabedatei:", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=1, column=0,
                                                                                               sticky="w", pady=8)
        # Erzeugt Label "Ausgabedatei:" in Zeile 1 (ähnlich wie Eingabedatei)

        self.output_var = StringVar()
        # Erzeugt Variable für Ausgabedatei-Pfad

        output_entry = Entry(main_frame, textvariable=self.output_var, width=35, font=("Arial", 9))
        # Erzeugt Eingabefeld für Ausgabedatei

        output_entry.grid(row=1, column=1, padx=10)
        # Platziert in Zeile 1, Spalte 1

        browse_output_btn = Button(main_frame, text="Durchsuchen", command=self.browse_output, bg="#4CAF50", fg="white",
                                   font=("Arial", 9))
        # Erzeugt Button für Ausgabedatei-Dialog
        # command=self.browse_output: ruft andere Methode auf

        browse_output_btn.grid(row=1, column=2, padx=5)
        # Platziert Button in Zeile 1, Spalte 2

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=15)
        # Erzeugt horizontale Trennlinie in Zeile 2
        # columnspan=3: zieht sich über alle 3 Spalten
        # sticky="ew": dehnt sich von osten nach westen (links-rechts)

        # ===== FPS =====
        Label(main_frame, text="Ziel-FPS (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=3, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=8)
        # Erzeugt Label "Ziel-FPS (optional):" in Zeile 3

        self.fps_var = StringVar()
        # Variable für FPS-Eingabe

        fps_entry = Entry(main_frame, textvariable=self.fps_var, width=15, font=("Arial", 9))
        # Erzeugt Eingabefeld für FPS (schmäler als Dateipfade)

        fps_entry.grid(row=3, column=1, sticky="w", padx=10)
        # Platziert in Zeile 3, Spalte 1

        Label(main_frame, text="(z.B. 25.0)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=3, column=2,
                                                                                               sticky="w")
        # Erzeugt Hilftext "(z.B. 25.0)" in Spalte 2 (Beispiel)

        # ===== BREITE =====
        Label(main_frame, text="Ziel-Breite (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=4,
                                                                                                         column=0,
                                                                                                         sticky="w",
                                                                                                         pady=8)
        # Erzeugt Label in Zeile 4

        self.width_var = StringVar()
        # Variable für Breite

        width_entry = Entry(main_frame, textvariable=self.width_var, width=15, font=("Arial", 9))
        # Eingabefeld für Breite

        width_entry.grid(row=4, column=1, sticky="w", padx=10)
        # Platziert in Zeile 4, Spalte 1

        Label(main_frame, text="(z.B. 1280)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=4, column=2,
                                                                                               sticky="w")
        # Hilftext "(z.B. 1280)" in Spalte 2

        # ===== HÖHE =====
        Label(main_frame, text="Ziel-Höhe (optional):", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=5, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=8)
        # Erzeugt Label in Zeile 5

        self.height_var = StringVar()
        # Variable für Höhe

        height_entry = Entry(main_frame, textvariable=self.height_var, width=15, font=("Arial", 9))
        # Eingabefeld für Höhe

        height_entry.grid(row=5, column=1, sticky="w", padx=10)
        # Platziert in Zeile 5, Spalte 1

        Label(main_frame, text="(z.B. 720)", font=("Arial", 8), bg="#f0f0f0", fg="#666").grid(row=5, column=2,
                                                                                              sticky="w")
        # Hilftext "(z.B. 720)" in Spalte 2

        # Separator
        ttk.Separator(main_frame, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=15)
        # Zweite horizontale Trennlinie in Zeile 6 (vor Buttons)

        # ===== BUTTONS =====
        button_frame = Frame(main_frame, bg="#f0f0f0")
        # Erzeugt neuen Frame speziell für Buttons

        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        # Platziert Button-Frame in Zeile 7, über alle 3 Spalten

        start_btn = Button(
            # Erzeugt Konvertierungs-Button
            button_frame,
            # im button_frame
            text="Konvertierung starten",
            # mit diesem Text
            command=self.start_conversion,
            # ruft start_conversion() auf wenn geklickt
            bg="#2196F3",
            # blauer Hintergrund
            fg="white",
            # weißer Text
            font=("Arial", 11, "bold"),
            # Arial, Größe 11, fett
            width=20,
            # 20 Zeichen breit
            height=2
            # doppelte Höhe
        )
        start_btn.pack(pady=5)
        # Platziert Button mit 5px Abstand oben/unten

        reset_btn = Button(
            # Erzeugt Zurücksetzen-Button
            button_frame,
            # im button_frame
            text="Zurücksetzen",
            # mit diesem Text
            command=self.reset_form,
            # ruft reset_form() auf wenn geklickt
            bg="#f44336",
            # roter Hintergrund
            fg="white",
            # weißer Text
            font=("Arial", 10)
            # Arial, Größe 10
        )
        reset_btn.pack(pady=5)
        # Platziert Button mit 5px Abstand

        # Status-Label
        self.status_label = Label(
            # Erzeugt Status-Label (speichert als Klassenvariable)
            self.root,
            # im Hauptfenster
            text="Bereit",
            # initiale Text
            font=("Arial", 9),
            # kleine Schrift
            bg="#f0f0f0",
            # grauer Hintergrund
            fg="#666"
            # dunkelgrauer Text
        )
        self.status_label.pack(pady=10)
        # Platziert Label unten im Fenster mit 10px Abstand

    def browse_input(self):
        # Methode für Datei-Dialog (Eingabedatei auswählen)
        """Öffnet Datei-Dialog für Eingabedatei."""
        # Docstring

        file_path = filedialog.askopenfilename(
            # Öffnet "Datei öffnen"-Dialog und speichert Pfad
            title="Eingabevideo wählen",
            # Dialog-Titel
            filetypes=[("Video-Dateien", "*.mov *.mp4 *.avi *.mkv"), ("Alle Dateien", "*.*")]
            # Filter für Dateitypen
        )
        if file_path:
            # Wenn Datei ausgewählt wurde (nicht abgebrochen)
            self.input_var.set(file_path)
            # Setzt Pfad in das Eingabefeld

    def browse_output(self):
        # Methode für Datei-Dialog (Ausgabedatei speichern)
        """Öffnet Datei-Dialog für Ausgabedatei."""
        # Docstring

        file_path = filedialog.asksaveasfilename(
            # Öffnet "Speichern unter"-Dialog
            title="Ausgabedatei speichern als",
            # Dialog-Titel
            filetypes=[("MP4-Dateien", "*.mp4"), ("AVI-Dateien", "*.avi"), ("Alle Dateien", "*.*")],
            # Filter für Dateitypen
            defaultextension=".mp4"
            # Standardendung .mp4
        )
        if file_path:
            # Wenn Datei ausgewählt wurde
            self.output_var.set(file_path)
            # Setzt Pfad in das Ausgabefeld

    def reset_form(self):
        # Methode zum Zurücksetzen aller Felder
        """Setzt alle Felder zurück."""
        # Docstring

        self.input_var.set("")
        # Setzt Eingabedatei auf leer

        self.output_var.set("")
        # Setzt Ausgabedatei auf leer

        self.fps_var.set("")
        # Setzt FPS auf leer

        self.width_var.set("")
        # Setzt Breite auf leer

        self.height_var.set("")
        # Setzt Höhe auf leer

        self.status_label.config(text="Bereit", fg="#666")
        # Setzt Status-Label auf "Bereit"

    def start_conversion(self):
        # Methode, die aufgerufen wird wenn "Start"-Button geklickt wird
        """Startet die Konvertierung in einem separaten Thread."""
        # Docstring

        # Validierung
        input_path = self.input_var.get().strip()
        # Holt Eingabedatei-Pfad und entfernt Leerzeichen am Anfang/Ende

        output_path = self.output_var.get().strip()
        # Holt Ausgabedatei-Pfad und entfernt Leerzeichen

        if not input_path or not output_path:
            # Prüft ob beide Felder gefüllt sind
            messagebox.showerror("Fehler", "Eingabe- und Ausgabedatei sind erforderlich!")
            # Zeigt Fehlermeldung
            return
            # Bricht Funktion ab

        if not os.path.exists(input_path):
            # Prüft ob Eingabedatei existiert
            messagebox.showerror("Fehler", "Eingabedatei existiert nicht!")
            # Zeigt Fehlermeldung
            return
            # Bricht Funktion ab

        # Versuche optionale Parameter zu parsen
        try:
            # Versucht folgenden Code auszuführen
            fps = float(self.fps_var.get()) if self.fps_var.get().strip() else None
            # Konvertiert FPS zu Dezimalzahl
            # Wenn leer, dann None (nicht konvertieren)
        except ValueError:
            # Falls Konvertierung fehlschlägt (z.B. "abc" statt Zahl)
            messagebox.showerror("Fehler", "FPS muss eine Zahl sein (z.B. 25.0)")
            # Zeigt Fehlermeldung
            return
            # Bricht Funktion ab

        try:
            # Versucht folgenden Code auszuführen
            width = int(self.width_var.get()) if self.width_var.get().strip() else None
            # Konvertiert Breite zu ganzer Zahl
            # Wenn leer, dann None
        except ValueError:
            # Falls Konvertierung fehlschlägt
            messagebox.showerror("Fehler", "Breite muss eine ganze Zahl sein (z.B. 1280)")
            # Zeigt Fehlermeldung
            return
            # Bricht Funktion ab

        try:
            # Versucht folgenden Code auszuführen
            height = int(self.height_var.get()) if self.height_var.get().strip() else None
            # Konvertiert Höhe zu ganzer Zahl
            # Wenn leer, dann None
        except ValueError:
            # Falls Konvertierung fehlschlägt
            messagebox.showerror("Fehler", "Höhe muss eine ganze Zahl sein (z.B. 720)")
            # Zeigt Fehlermeldung
            return
            # Bricht Funktion ab

        # Starte Konvertierung in separatem Thread (damit GUI nicht einfriert)
        thread = threading.Thread(
            # Erzeugt neuen Thread
            target=self.run_conversion,
            # Welche Funktion soll im Thread laufen
            args=(input_path, output_path, fps, width, height)
            # Argumente für diese Funktion
        )
        thread.daemon = True
        # Thread beendet sich automatisch wenn Hauptprogramm endet

        thread.start()
        # Startet den Thread

    def run_conversion(self, input_path, output_path, fps, width, height):
        # Methode, die die Konvertierung in eigenem Thread ausführt
        """
        Führt die Konvertierung durch und aktualisiert den Status.
        """
        # Docstring

        self.status_label.config(text="Konvertierung läuft...", fg="#FF9800")
        # Ändert Status-Label auf "Konvertierung läuft..." (orange)

        self.root.update()
        # Aktualisiert GUI sofort

        ok = convert_cv2(input_path, output_path, fps, width, height, self.update_status)
        # Ruft Konvertierungsfunktion auf
        # Callback self.update_status wird für Fortschritts-Updates aufgerufen
        # Rückgabe: True bei Erfolg, False bei Fehler

        if ok:
            # Falls Konvertierung erfolgreich war
            self.status_label.config(text="✓ Konvertierung erfolgreich!", fg="#4CAF50")
            # Ändert Status-Label (grün, mit Häkchen)

            messagebox.showinfo("Erfolg", f"Video erfolgreich konvertiert:\n{output_path}")
            # Zeigt Erfolgs-Meldung mit Ausgabepfad
        else:
            # Falls Fehler aufgetreten ist
            self.status_label.config(text="✗ Fehler bei der Konvertierung", fg="#f44336")
            # Ändert Status-Label (rot, mit X)

            messagebox.showerror("Fehler", "Die Konvertierung ist fehlgeschlagen.")
            # Zeigt Fehlermeldung

    def update_status(self, message):
        # Callback-Methode, wird von convert_cv2() aufgerufen
        """Aktualisiert das Status-Label."""
        # Docstring

        self.status_label.config(text=message)
        # Ändert Status-Label mit neuem Text

        self.root.update()
        # Aktualisiert GUI sofort


def convert_cv2(input_path, output_path, out_fps=None, out_width=None, out_height=None, status_callback=None):
    # Funktion (nicht in Klasse): Hauptfunktion für Video-Konvertierung
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
    # Ausführlicher Docstring

    # Öffne die Eingabedatei
    cap = cv2.VideoCapture(input_path)
    # Öffnet Eingabedatei zum Lesen (cap = capture)

    if not cap.isOpened():
        # Prüft ob erfolgreich geöffnet wurde
        if status_callback:
            # Falls Callback-Funktion vorhanden ist
            status_callback("Fehler: Eingabevideo konnte nicht geöffnet werden")
            # Ruft Callback mit Fehlermeldung auf
        print("Fehler: Eingabevideo konnte nicht geöffnet werden.")
        # Gibt Fehlermeldung auf Konsole aus
        return False
        # Gibt False zurück (Fehler)

    # Lese Input-Metadaten
    in_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    # Holt FPS des Eingabevideos (fallback auf 30.0 wenn nicht lesbar)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # Holt Breite der Eingabe-Frames

    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Holt Höhe der Eingabe-Frames

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Holt Gesamtzahl der Frames im Video

    # Bestimme Zielwerte
    target_fps = float(out_fps) if out_fps else in_fps
    # Wenn out_fps angegeben: benutze das
    # Sonst: benutze Original-FPS

    tw = int(out_width) if out_width else width
    # Wenn out_width angegeben: benutze das (tw = target width)
    # Sonst: benutze Original-Breite

    th = int(out_height) if out_height else height
    # Wenn out_height angegeben: benutze das (th = target height)
    # Sonst: benutze Original-Höhe

    # FourCC-Code wählen
    ext = os.path.splitext(output_path)[1].lower()
    # Holt Dateiendung: splitext zerlegt in (name, ext), [1] nimmt ext
    # .lower() macht es kleingeschrieben

    if ext == ".mp4":
        # Falls Dateiendung .mp4 ist
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        # FourCC-Code für MP4 (Codec-ID)
    elif ext in (".avi", ".divx"):
        # Falls Dateiendung .avi oder .divx ist
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        # FourCC-Code für AVI (XVID-Codec)
    else:
        # Ansonsten (für alle anderen Endungen)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        # Default: MP4-Codec

    # Erzeuge VideoWriter
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (tw, th))
    # Erzeugt Schreiber für Ausgabe-Video
    # Parameter: Pfad, Codec, FPS, Zielgröße (Tupel)

    if not out.isOpened():
        # Prüft ob erfolgreich erstellt wurde
        if status_callback:
            # Falls Callback vorhanden
            status_callback("Fehler: Ausgabedatei konnte nicht geöffnet werden")
            # Ruft Callback mit Fehlermeldung auf
        print("Fehler: Ausgabedatei konnte nicht geöffnet werden.")
        # Gibt Fehlermeldung auf Konsole aus
        cap.release()
        # Gibt Ressourcen frei (schließt Eingabedatei)
        return False
        # Gibt False zurück (Fehler)

    # Lese und schreibe Frames
    frame_count = 0
    # Counter für verarbeitete Frames

    while True:
        # Endlosschleife
        ret, frame = cap.read()
        # Liest einen Frame
        # ret = True/False (erfolgreich/nicht erfolgreich)
        # frame = Bild als NumPy-Array

        if not ret:
            # Falls ret False ist (Video zu Ende oder Fehler)
            break
            # Bricht Schleife ab

        # Skaliere bei Bedarf
        if (tw, th) != (width, height):
            # Prüft ob Zielgröße anders als Originalgröße ist
            frame = cv2.resize(frame, (tw, th), interpolation=cv2.INTER_AREA)
            # Skaliert Frame auf Zielgröße
            # INTER_AREA ist hochwertige Skalierung

        # Schreibe Frame
        out.write(frame)
        # Schreibt Frame in Ausgabedatei

        frame_count += 1
        # Inkrementiert Counter

        if status_callback and frame_count % 30 == 0:
            # Falls Callback vorhanden UND frame_count durch 30 teilbar (alle 30 Frames)
            progress = (frame_count / total_frames * 100) if total_frames > 0 else 0
            # Berechnet Fortschritt als Prozentsatz
            # Falls total_frames = 0: setze progress auf 0

            status_callback(f"Konvertierung läuft... {progress:.1f}%")
            # Ruft Callback mit Fortschritt auf
            # {progress:.1f}% = Zahl mit 1 Dezimalstelle

    # Ressourcen freigeben
    cap.release()
    # Schließt Eingabedatei und gibt Speicher frei

    out.release()
    # Schließt Ausgabedatei und gibt Speicher frei

    return True
    # Gibt True zurück (Erfolg)


def main():
    # Hauptfunktion des Programms
    """
    Hauptfunktion: Startet die GUI.
    """
    # Docstring

    root = Tk()
    # Erzeugt das Hauptfenster

    gui = VideoConverterGUI(root)
    # Erzeugt GUI-Klasse mit Fenster (ruft __init__ auf)

    root.mainloop()
    # Startet die Ereignisschleife
    # Wartet auf Benutzereingaben (Clicks, Eingaben, etc.)


if __name__ == "__main__":
    # Prüft ob Skript direkt ausgeführt wird (nicht als Modul importiert)
    main()
    # Ruft Hauptfunktion auf