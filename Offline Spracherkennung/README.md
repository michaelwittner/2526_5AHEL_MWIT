# 2526_5AHEL_MWIT

## 13.01.2026 ##

## Projektziel

Du willst eine **offline** laufende Spracherkennungs-Anwendung auf einem **Android-Tablet**, die:

* dauerhaft (kontrolliert) zuhören kann,
* Sprache in **Fließtext** umwandelt,
* über ein **Wake-Word** aktiviert wird,
* anschließend per **Keyword** bestimmte Aktionen auslöst,
* eine **schöne Oberfläche** (UI) bietet.

## Geplanter Technik-Stack

* **Entwicklungsumgebung:** Android Studio
* **Programmiersprache:** Java (weil du sie am besten kannst)
* **Speech-to-Text (offline):** **Vosk**
* **Logik:** Wake-Word → danach STT → Textanzeige → Keyword-Parser → Aktion

## Hardware / Ressourcen (aktuelles Ziel-Tablet)

* **Android 13**
* **RAM:** **16 GB**

https://amzn.eu/d/37imvau


## Warum diese Wahl

* **Offline-Fokus:** keine Cloud-Abhängigkeit, bessere Kontrolle/Privatsphäre.
* **16 GB RAM:** genug Reserven für längere Sessions, Logs, UI und ggf. später größere Modelle/Features.
* **Android 13:** ausreichend für Foreground-Service-Ansatz, weniger „ganz neu“-Sonderfälle als bei sehr aktuellen Versionen.

## Nächste Schritte (Plan)

1. Android Studio Projekt anlegen + App-Grundgerüst (UI + Service-Struktur)
2. Audio-Aufnahme + Vosk offline Transkription integrieren
3. Wake-Word-Mechanik ergänzen (always-on leichtgewichtig)
4. Keyword-System definieren (Regeln → Aktionen)
5. UI „polish“: Live-Text, Statusanzeigen, Logs/History, Start/Stop

Verwendet: https://chatgpt.com/


---
---


## 20.01.2026 ##


## Ziel (neu festgelegt)

Ein **Android-Tablet** soll **offline** Sprache erkennen (Dauerbetrieb), den erkannten Text als **Fließtext** anzeigen und bei **Triggern/Keywords** definierte **Aktionen/Routinen** auslösen.

## Link

* **Vosk API (GitHub):** [https://github.com/alphacep/vosk-api](https://github.com/alphacep/vosk-api)

## Hardware / Ressourcen (Zielgerät)

* Zielgerät: **Blackview Mega1**
* Eckdaten (relevant fürs Projekt): **Android 13**, **16 GB RAM**, 256 GB Speicher (Reserve für größere Modelle / längere Sessions)
* Einschätzung: Realtime-Performance hängt eher an **CPU/Latency** als nur an RAM.

## Offline-Routinen (geplant)

* Routinen werden als **Aktionen nach Keyword-Erkennung** umgesetzt (Mechanik steht, konkrete Liste kann wachsen).
* Beispiel-Richtung: „Aufwachen“ / „Gute Nacht“ (Details werden bei der Implementierung finalisiert).
  *(Wenn deine Freundin das Tablet nutzt, kann sie natürlich dieselben Routinen genauso auslösen.)*

## UI / Design

* Ziel-Seitenverhältnis fürs Layout: **16:9**
* UI soll enthalten: **Live-Text**, **Start/Stop**, **Status/Logs** (übersichtlich + „schön“).

Verwendet: https://chatgpt.com/


---
---


## 27.01.2026 ##


### Funktioniert

* **Vosk (Offline Speech-to-Text)** läuft.
* **Keyword-Erkennung** ist implementiert.
* Der Assistent **spricht mit einem** (Sprachausgabe aktiv).
* **Schlafmodus** ist vorhanden.

## Komponenten

* **STT (Speech-to-Text):** Vosk (offline)
* **Intent/Keyword-Logik:** Keyword/Trigger-System (aktiv)
* **TTS (Text-to-Speech):** Sprachausgabe aktiv (Engine je nach Implementierung/System)
* **Zustandslogik:** Normalmodus ↔ Schlafmodus

## Referenzen / Links

* **Vosk API (GitHub):** [https://github.com/alphacep/vosk-api](https://github.com/alphacep/vosk-api)
* **SherpaTTS (F-Droid):** [https://f-droid.org/en/packages/org.woheller69.ttsengine/](https://f-droid.org/en/packages/org.woheller69.ttsengine/) ([f-droid.org][2]



## 1) STT (Speech-to-Text) mit Vosk

### Warum Vosk?

* **Offline-fähig**: Keine Cloud, keine Internet-Abhängigkeit → Datenschutz, Zuverlässigkeit, sofortige Reaktion. ([GitHub][1])
* **Deutsch-Support**: Vosk unterstützt u. a. **Deutsch** und viele weitere Sprachen. ([GitHub][1])
* **Android-tauglich**: Vosk ist für mobile/embedded Nutzung gedacht (auch Android). ([alphacephei.com][2])

### Warum dieses Modell (klein vs. groß)?

praktisch für ein **mobiles Modell** entschieden, weil:

* **Small-Models** sind für Mobile-Anwendungen gedacht (typisch ~50 MB) und brauchen im Betrieb grob **~300 MB RAM** → passt gut für Tablet/Foreground-Service. ([alphacephei.com][3])
* **Big-Models** liefern zwar mehr Genauigkeit, sind aber eher „Server-Klasse“ und können **bis zu ~16 GB RAM** brauchen → unnötig schwer/träge fürs Always-on-Tablet. ([alphacephei.com][3])

**Praxis-Fazit:** Small-Model = schneller Start, weniger Risiko für Out-of-Memory/CPU-Last, ideal für Dauerbetrieb. ([alphacephei.com][3])

### Wie wurde Vosk eingebunden (Konzept & Ablauf)?

1. **Vosk-Bibliothek** ins Android-Projekt integriert (STT-Engine).
2. **Sprachmodell** in die App gebracht (typisch als **Assets**) und beim Start/Setup in App-Speicher **entpackt**, damit Vosk schnell und zuverlässig darauf zugreifen kann. ([alphacephei.com][4])
3. Danach wird ein **Recognizer** mit dem Modell initialisiert und bekommt fortlaufend Audiodaten aus dem Mikrofon. (Vosk verarbeitet daraus Partial/Final-Text.) ([GitHub][1])

### Wichtiger Grund für “Model entpacken” + UUID-Datei

* In der Android-Demo/typischen Einbindung wird das Modell aus **Assets entpackt**; dabei ist wichtig, dass die Modelldateien vollständig sind – inkl. **UUID** (die in manchen Setups über Gradle/Build-Schritte erzeugt/erwartet wird). ([alphacephei.com][4])
  **Warum das wichtig ist:** Ohne vollständige Modelstruktur kann „unpack/init model“ fehlschlagen (klassischer Stolperstein).



## 2) Keyword/Trigger-Logik auf STT-Text

### Warum Keywords (statt “frei interpretieren”)?

* **Robustheit**: Klare Trigger verhindern Fehlaktionen.
* **Offline**: Kein „LLM muss alles verstehen“, sondern: STT → Text → Keyword-Match → Aktion.

### Wie ist es gekoppelt?

* Vosk liefert **Text** (Teil- oder Endergebnis).
* Dein Parser prüft: **Wake-Word/Keyword** vorhanden?
* Dann wird in einen passenden **Zustand** gewechselt und die **Aktion** ausgelöst.



## 3) TTS (Text-to-Speech) mit SherpaTTS

### Warum SherpaTTS?

* **Offline-TTS-Engine** für Android, Open Source, als System-TTS nutzbar. ([GitHub][5])
* Nutzt **Piper**-Voice und basirend auf „Next-gen Kaldi“. ([GitHub][5])
* **Wichtig fürs Projektziel:** Nach einmaligem Voice-Setup funktioniert das Sprechen **komplett offline** → passt zu deinem Offline-Assistenten-Konzept. ([f-droid.org][6])

### Warum welches Voice-Modell?

Die Auswahl eines TTS-Voices macht man praxisnah nach:

* **Verständlichkeit** (klare Aussprache bei Befehlen)
* **Latenz** (schneller Beginn beim Sprechen)
* **Modellgröße** (Speicher/Startup)
* **Sprachqualität** (natürlich vs. „roboterhaft“)

SherpaTTS lädt beim ersten Start typischerweise das gewählte Voice-Modell; danach ist es offline nutzbar. ([f-droid.org][6])

### Wie wurde SherpaTTS eingebunden?

* SherpaTTS wird als **Android TTS Engine** eingerichtet (Systemebene).
* Deine App nutzt danach die **normale Android-TextToSpeech-Schnittstelle** – aber die Ausgabe läuft über SherpaTTS als Engine.

**Warum so?**
Du musst keine „Spezial-TTS-API“ hart einbauen; du nutzt die Android-Standardstelle und kannst die Engine systemweit austauschen (praktisch fürs Testen).



## 4) STT + TTS Zusammenspiel (warum das entscheidend ist)

### Das Kernproblem: Feedback/Loop

Wenn TTS spricht, kann STT den eigenen Lautsprecher wieder aufnehmen → dann „antwortet“ der Assistent auf sich selbst und hängt in einer Schleife.

### Warum ein Zustandsmodell nötig ist

Du brauchst Zustände wie z. B.:

* **LISTENING** (STT aktiv)
* **PROCESSING** (Text auswerten)
* **SPEAKING** (TTS aktiv)
* **SLEEPING** (reduziert/aus)

**Wichtige Regel:** Während **SPEAKING** wird STT **pausiert oder ignoriert**, damit keine Selbst-Transkription passiert.



## 5) Schlafmodus (bezogen auf STT/TTS)

### Warum Schlafmodus?

* **Ruhiger Betrieb** (kein „Dauer-Gerede“)
* **Energie sparen**
* **Klare Nutzerlogik** („jetzt ist Ruhe“)

### Was ändert sich technisch?

Typisch:

* STT wird auf **minimalen Trigger** reduziert.
* TTS wird **unterdrückt** oder stark vereinfacht (z. B. nur bestätigende, kurze Ausgabe – wenn überhaupt).


---

## Quellen (Projekt-relevant)

* Vosk Toolkit / Offline / Sprachen: ([GitHub][1])
* Vosk Modelle (small vs big, RAM-Anforderungen): ([alphacephei.com][3])
* Vosk Android Hinweise (Assets/Unpack/UUID): ([alphacephei.com][4])
* SherpaTTS (Engine, Piper/Coqui, Offline nach Download): ([GitHub][5])



[1]: https://github.com/alphacep/vosk-api?utm_source=chatgpt.com "alphacep/vosk-api: Offline speech recognition ..."
[2]: https://alphacephei.com/vosk/?utm_source=chatgpt.com "VOSK Offline Speech Recognition API"
[3]: https://alphacephei.com/vosk/models?utm_source=chatgpt.com "VOSK Models"
[4]: https://alphacephei.com/vosk/android?utm_source=chatgpt.com "Offline speech recognition on Android with VOSK"
[5]: https://github.com/woheller69/ttsEngine?utm_source=chatgpt.com "woheller69/ttsEngine"
[6]: https://f-droid.org/en/packages/org.woheller69.ttsengine/?utm_source=chatgpt.com "SherpaTTS | F-Droid - Free and Open Source Android App ..."


Verwendet: https://chatgpt.com/


---
---


## 03.02.2026 ##

* Ideensammlung (keine weiteren Vorhaben)
* Projekt-Vorstellung-Planung
* Infomationssammlung bezüglich STT

---
---

## 2026-02-10 

* Präsentationsinhalt weiter ausgearbeitet. 
* Zusätzlich wurde die Worterkennung für den Schlafmodus überarbeitet, um das Umschalten in den Schlafmodus zuverlässiger und stabiler zu machen.

