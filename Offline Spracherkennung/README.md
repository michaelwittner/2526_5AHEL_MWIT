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
