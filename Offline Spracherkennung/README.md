# 2526_5AHEL_MWIT

## 13.01.2026 ##
Christoph, hier ist eine kurze Doku/Übersicht zu dem, was du herausgefunden hast und vorhast:

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

