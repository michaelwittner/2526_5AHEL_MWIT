# Dokumentation – Offline Spracherkennung & Sprachausgabe (STT/TTS) auf Android

**Ziel:** Sprache **offline** in Text umwandeln (STT), daraus **Befehle** ableiten (Keywords) und optional **Antworten sprechen** (TTS) – mit **Wake-Word** und **Schlafmodus**.

---

## Inhaltsverzeichnis

1. Grundlagen: STT und TTS  
2. Wie Spracherkennung technisch funktioniert (Pipeline & Modelle)  
3. Werkzeuge/Tools für Spracherkennung (online & offline)  
4. Online-Spracherkennung (z. B. Cloud): Nutzen und Risiken  
5. Offline-Spracherkennung: Nutzen, Herausforderungen, Architektur  
6. Vosk im Detail (Motivation, Modelle, Einbindung)  
7. Alternativen zu Vosk (Vergleich)  
8. TTS im Projekt (Optionen, Einbindung)  
9. Konkretes Projekt: Vorstellung, Funktionen, Wake-Word-Ablauf (codebasiert)  
10. Zusammenfassung & Ausblick

---

## 1) Grundlagen: STT & TTS

### 1.1 STT (Speech-to-Text)
STT bedeutet: Ein System nimmt Audiodaten auf und erzeugt daraus **Text**.  
Der Text kann anschließend für **Befehlserkennung** (Keywords) oder für weitere Verarbeitung genutzt werden.

### 1.2 TTS (Text-to-Speech)
TTS bedeutet: Das System nimmt Text (z. B. Bestätigungen, Antworten, Statusmeldungen) und erzeugt daraus **gesprochenes Audio**.

---

## 2) Wie Spracherkennung technisch funktioniert

Das Audiosignal liegt als Zeitreihe (Amplitude über Zeit) vor. Spracherkennung versucht daraus **eine Folge von Wörtern** zu rekonstruieren – trotz unterschiedlicher Stimmen, Betonungen, Sprechtempo, Dialekten und Störgeräuschen.

Man unterscheidet grob zwei Ansätze:
- **Klassische Pipeline** (mit klaren Modulen wie Feature-Extraktion, akustisches Modell, Sprachmodell, Decoder)
- **End-to-End** (ein Modell bildet vieles gemeinsam ab; oft leistungsstark, aber häufig rechenintensiver)

---

## 2.1 Die klassische STT-Pipeline (Schritt für Schritt)

### Schritt A: Audioaufnahme & Vorverarbeitung
- Audio wird in einer definierten Abtastrate aufgenommen (typisch 16 kHz, mono).
- Optional: Pegel-Normalisierung, einfache Filter, Rauschreduktion.
- Das Signal wird in kurze Zeitfenster („Frames“) zerlegt (typisch 20–30 ms), oft mit Überlappung.

**Warum Frames?**  
Sprache ändert sich sehr schnell; kurze Fenster geben eine stabile Grundlage, um Merkmale zu berechnen und Wahrscheinlichkeiten abzuleiten.

---

### Schritt B: Feature-Extraktion
Statt rohe Audiosamples direkt zu verarbeiten, berechnet man „Features“, z. B.:
- Log-Mel-Filterbanks
- MFCC-ähnliche Merkmale

**Warum Features?**  
Features reduzieren irrelevante Details und heben sprachrelevante Muster hervor (Resonanzen, Formanten, Spektrum). Das verbessert Robustheit und erleichtert dem Modell das Lernen.

---

### Schritt C: Akustisches Modell (Audio → Laut-/Einheiten-Wahrscheinlichkeiten)  ✅ *mehr Detail*

Das akustische Modell ist der Teil, der **aus den Features** ableitet, welche **sprachlichen Einheiten** gerade wahrscheinlich sind.

#### 1) Was kommt in das akustische Modell hinein?
- Die berechneten Features pro Frame (z. B. ein Vektor pro 10–30 ms).
- Optional Kontext: Viele Systeme betrachten nicht nur einen Frame, sondern mehrere Frames rundherum, um Übergänge („coarticulation“) zu erfassen.

#### 2) Was kommt aus dem akustischen Modell heraus?
Das Modell liefert **Wahrscheinlichkeiten** (oder Scores) für mögliche Sprach-Einheiten, je Frame. Je nach Modellfamilie sind das z. B.:
- **Phoneme** (Sprachlaute),
- **Sub-phonemische Zustände** (z. B. HMM-Zustände / „senones“),
- oder direkt **Token** (bei neueren Ansätzen wie CTC/Transducer).

Wichtig: Das akustische Modell liefert *nicht* sofort „fertige Wörter“. Es liefert zuerst eine Art „Was könnte dieser Lautabschnitt sein?“ – als Wahrscheinlichkeitsverteilung über viele Möglichkeiten.

#### 3) Warum ist das notwendig?
Ein einzelnes Stück Audio ist mehrdeutig:
- Unterschiedliche Personen sprechen denselben Laut unterschiedlich aus.
- Umgebungsgeräusche, Hall, Mikrofonqualität beeinflussen das Signal.
- Sprache „verschmiert“ zeitlich: Laute gehen ineinander über.

Das akustische Modell ist dafür da, diese Variabilität abzufangen und trotzdem brauchbare Scores zu liefern.

#### 4) Wie arbeitet ein akustisches Modell konzeptionell?

##### (a) Klassische Variante (HMM + neuronales Netz)
Historisch wurde häufig verwendet:
- Ein **HMM** (Hidden Markov Model) modelliert, dass Sprache eine zeitliche Abfolge von Zuständen ist.
- Ein **neuronales Netz** (früher GMM/ später DNN) liefert pro Frame die Wahrscheinlichkeit für Zustände.

So entsteht eine zeitlich konsistente Bewertung:  
„Wenn Zustand X gerade aktiv war, ist Zustand Y als nächster plausibel.“

##### (b) Neuere Varianten (CTC / Transducer / Attention)
Viele moderne Systeme nutzen:
- **CTC** (Connectionist Temporal Classification): Modelliert eine Zuordnung zwischen Frame-Folge und Token-Folge mit speziellen Mechanismen für Wiederholungen/Leerzeichen.
- **Transducer (RNN-T)**: Kombiniert akustische Information und eine interne Vorhersagekomponente; gut für Streaming.
- **Attention/Transformer**: Sehr leistungsfähig, oft aber rechenintensiver.

Praktisch bleibt die Grundidee gleich:  
Aus Audiofeatures werden **Token-Scores** erzeugt, die später in Text übersetzt werden.

#### 5) Training: Wie lernt ein akustisches Modell das überhaupt?
Damit ein Modell Sprache erkennt, braucht es:
- Viele Stunden gelabeltes Sprachmaterial (Audio + Transkript).
- Ein Trainingsverfahren, das Audioabschnitte mit Textabschnitten in Beziehung setzt:
  - bei HMM-basierten Systemen häufig über Alignments,
  - bei CTC/Transducer über passende Zielfunktionen, die auch ohne harte Frame-Zuordnung funktionieren.

Das Modell lernt dabei:
- typische Muster für Laute,
- wie Laute je nach Kontext variieren,
- und wie sich Störfaktoren statistisch auswirken.

#### 6) Ergebnis aus Schritt C (was liegt „nachher“ vor?)
Nach dem akustischen Modell liegt eine Sequenz aus Frames vor, und zu jedem Frame:
- eine Verteilung/Score-Liste über mögliche Einheiten.

**Das ist der zentrale Input für den Decoder (Schritt E):**  
Der Decoder „baut“ daraus zusammen mit Lexikon + Sprachmodell die beste Wortfolge.

---

### Schritt D: Sprachmodell (Wortfolgen plausibel machen)
Das Sprachmodell bewertet, welche Wortfolgen in einer Sprache wahrscheinlich sind (Grammatik, Häufigkeit, typische Sequenzen).

**Warum?**  
Viele Laute sind akustisch ähnlich. Das Sprachmodell hilft, Mehrdeutigkeiten zu lösen und die plausiblere Wortfolge zu bevorzugen.

---

### Schritt E: Decoder (Suche nach dem besten Text)
Der Decoder kombiniert:
- Scores aus dem akustischen Modell,
- ein Lexikon (Zuordnung Laute ↔ Wörter),
- das Sprachmodell (Wortfolgen-Wahrscheinlichkeit)

und sucht die insgesamt wahrscheinlichste Wortsequenz.

Ergebnisarten:
- **Partial Results** (Zwischentext während gesprochen wird)
- **Final Results** (Endergebnis nach Sprechpause/Äußerungsende)

---

## 3) Welche Tools stehen zur Verfügung (Spracherkennung)

Man kann Tools grob so einteilen:
- **Online/Cloud-STT** (Audio wird an einen Dienst gesendet, dort verarbeitet)
- **Offline/On-Device-STT** (Modell liegt lokal, Verarbeitung passiert auf dem Gerät)

Zusätzlich wichtig (für Assistenzsysteme):
- **Wake-Word Engines** (sehr leichtgewichtig, immer aktiv)
- **Keyword-Parser / Intent-Router** (Text → Aktion)

---

## 4) Online-Spracherkennung: Probleme/Risiken

### 4.1 Datenschutz & Datenfluss
Bei Cloud-STT wird Audio häufig an externe Server übertragen. Das erzeugt:
- Datenschutz- und Compliance-Themen,
- Abhängigkeit von Anbieter-Richtlinien,
- Risiko, dass sensible Inhalte übertragen werden.

### 4.2 Abhängigkeit von Internet
- Ohne Internet: keine Erkennung oder stark eingeschränkt.
- Bei schlechter Verbindung: Verzögerungen, Abbrüche.

### 4.3 Kosten
- Typisch: Abrechnung pro Minute/Request.
- Always-On-Systeme können schnell teuer werden.

### 4.4 Vendor-Lock-In
- API-Änderungen, Preise oder Limits können sich ändern.

---

## 5) Offline-Spracherkennung: Nutzen, Herausforderungen, Architektur

### 5.1 Vorteile offline
- Unabhängig von Internet
- Daten bleiben lokal
- Konstante Latenz (kein Netzwerk)
- Planbare Kosten

### 5.2 Herausforderungen offline
- Rechenleistung/Temperatur/Verbrauch
- Modellgröße vs. Genauigkeit
- Update-Strategie für Modelle
- Robustheit in lauten Umgebungen

### 5.3 Typische Architektur für Offline-Assistenten
1. Wake-Word (leicht, dauerhaft)  
2. STT (nur bei Bedarf aktiv)  
3. Parser/Keywords (deterministisch)  
4. Action-Ausführung  
5. TTS-Feedback  
6. Zustandsmaschine (gegen Loops, für Schlafmodus)

---

## 6) Offline im Detail – Vosk

### 6.1 Warum Vosk?
Vosk ist geeignet, weil:
- es offline läuft,
- auf mobilen Geräten praktikabel ist,
- Streaming-Erkennung unterstützt (wichtig für geringe Latenz).

### 6.2 Modelle (small vs. big) – Entscheidungskriterium
- **Small**: geringer Speicherbedarf, schneller, stabiler für Dauerbetrieb.
- **Big**: potenziell bessere Genauigkeit, aber deutlich höherer Ressourcenbedarf.


### 6.3 Einbindung (prinzipieller Ablauf)
1. Modell liegt lokal (z. B. entpackt im App-Speicher).  
2. Recognizer wird initialisiert.  
3. Audioframes werden kontinuierlich an die Engine übergeben.  
4. Engine liefert Partial/Final Text.  
5. Text geht an Parser/Router.

---

## 7) Alternativen zu Vosk (Offline)

Man kann offline auch nutzen:
- **Whisper lokal** (hohe Qualität möglich, aber je nach Modell und Gerät rechenintensiv)
- **whisper.cpp** (portabel, häufig leichter integrierbar, Performance stark geräteabhängig)
- **Coqui STT** (offen/trainierbar, aber Integrations- und Modellaufwand höher)

Die Auswahl hängt ab von:
- Echtzeit-Anforderung,
- Modellgröße,
- Integrationsaufwand,
- Zielhardware.

---

## 8) TTS (Text-to-Speech) im Projekt

### 8.1 Prinzip
TTS erzeugt aus Text Audio. In Android gibt es dafür eine Standard-Schnittstelle, über die eine App Text sprechen lassen kann.

### 8.2 Offline-TTS-Optionen (z. B. Engine statt Cloud)
Man kann eine Offline-TTS-Engine nutzen (z. B. SherpaTTS als System-Engine), damit die Ausgabe unabhängig von Internet funktioniert.

---

## 9) Konkretes Projekt: Vorstellung, Funktionen, Wake-Word-Ablauf

### 9.1 Projektvorstellung
Das Projekt ist ein Offline-Sprachassistent auf Android-Tablet, der:
- Wake-Word nutzt,
- Sprache offline transkribiert (STT),
- Keywords erkennt,
- Aktionen ausführt,
- Sprachausgabe macht (TTS),
- einen Schlafmodus besitzt.

### 9.2 Aktuelle Funktionen (Ist-Stand)
- Offline-STT (Vosk) funktioniert.
- Keyword-Erkennung funktioniert.
- Sprachausgabe ist aktiv (der Assistent spricht).
- Schlafmodus ist umgesetzt.

### 9.3 Was passiert nach dem Wake-Word?
**Konzeptuell** sieht die Kette so aus:

1. **Foreground-Service** läuft dauerhaft und verwaltet Audio/Status.  
2. **Wake-Word-Detector** erkennt das Aktivierungswort.  
3. Event/Callback → Zustandswechsel auf „aktiv zuhören“.  
4. **STT-Engine** wird gestartet oder in den aktiven Modus geschaltet.  
5. STT liefert Text (Partial/Final).  
6. **Command-Parser** analysiert den finalen Text auf Keywords.  
7. **Action-Executor** führt die Aktion aus.  
8. Optional: **TTS-Manager** spricht eine Bestätigung/Antwort.  
9. Zustandsmaschine entscheidet: zurück zu Idle (Wake-Word warten) oder in Schlafmodus.

### 9.4 Zustandsmaschine (warum notwendig)
Ohne Zustandsmodell entstehen typische Probleme:
- wiederholte Prompt-Sätze,
- Selbst-Trigger durch TTS (TTS wird von STT wieder erkannt),
- unzuverlässiger Schlafmodus.

Ein solides Zustandsmodell trennt klar:
- Wake-Word-Warten (leicht)
- aktives Zuhören (STT)
- Verarbeiten (Parser)
- Sprechen (TTS)
- Schlafmodus (reduziert/aus)

---

## 10) Zusammenfassung
Das Projekt setzt auf eine robuste Offline-Architektur:
- Wake-Word als Filter,
- Vosk für Offline-STT,
- Keyword-Parser für deterministische Aktionen,
- TTS für Feedback,
- Schlafmodus + Zustandsmaschine für Stabilität und Ruhe.
