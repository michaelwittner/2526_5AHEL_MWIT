# 2526_5AHEL_MWIT

**Individual Projects for MWIT**
**Projekt:** Home Assistant GUI
**Autor:** Julian Dietachmair

---

## Projektübersicht

Dieses Repository dokumentiert die Entwicklung und Konfiguration einer **Home‑Assistant‑Benutzeroberfläche**, mit besonderem Fokus auf ein **smartphone‑optimiertes Dashboard** sowie eine **zuverlässige Navigation mittels BrowserMod**.

---

## Änderungsprotokoll

### 📅 13.01.2026

#### Smartphone‑Dashboard

* Pop-ups um **Eltern‑Pop-ups** erweitert
* Anpassungen an den verwendeten **Entitäten**
* **Batteriestandsanzeige** des Temperaturfühlers hinzugefügt
* Layout‑Optimierung:

  * Batterieanzeige im **rechten Drittel der Spalte** platziert
  * Ziel: Temperatur- und Luftfeuchtigkeitsanzeige **leserlich halten** und **Abschneiden vermeiden**

#### Automatisierung: Smartphone → Mobile Dashboard

Da die integrierte Home‑Assistant‑Lösung für die automatische Navigation unzuverlässig war (teilweise Zurücksetzen), wurde eine **eigene Lösung mit BrowserMod (HACS)** umgesetzt.

**Funktionsweise:**

* Jedes Gerät registriert sich bei BrowserMod
* Geräte lassen sich eindeutig unterscheiden (Smartphone, Laptop, Tablet)
* Ergebnis:

  * **Laptop:** Standard‑Dashboard
  * **Smartphone:** Mobile‑optimiertes Dashboard

**YAML – Automatisierung:**

```yaml
alias: Smartphone → Smartphone Dashboard erzwingen
mode: single

trigger:
  - platform: state
    entity_id: binary_sensor.browser_mod_nothing_phone_2
    to: "on"

condition:
  - condition: template
    value_template: >
      {{ state_attr('binary_sensor.browser_mod_nothing_phone_2', 'browser') == 'mobile' }}

action:
  - delay: "00:00:02"
  - service: browser_mod.navigate
    data:
      deviceID:
        - browser_mod_nothing_phone_2
      path: /dashboard-smartphone
```

---

### 📅 20.01.2026

#### BrowserMod – Optimierung

Die oben genannte Automatisierung wurde über eine Woche getestet. Dabei trat folgendes Problem auf:

* Andere Geräte (z. B. Tablet) wurden **zyklisch ebenfalls** auf das Smartphone‑Dashboard weitergeleitet
* Dies geschah trotz definiertem Zielgerät

**Lösung:**

* Umstieg auf die **GUI‑basierte BrowserMod‑Konfiguration**
* Vorteil:

  * Keine klassische HA‑Automatisierung
  * Verarbeitung direkt durch BrowserMod
  * Deutlich **robuster und zuverlässiger**

Aktueller Stand: **funktioniert stabil und korrekt**.

---

## Installation: Home Assistant OS

### Hardware

* **Raspberry Pi 3 Model B+**

### Vorbereitung

1. **Raspberry Pi Imager installieren:**
   [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)

2. **SD‑Karte flashen** (gemäß offizieller HA‑Dokumentation):
   [https://www.home-assistant.io/installation/raspberrypi/#install-home-assistant-operating-system](https://www.home-assistant.io/installation/raspberrypi/#install-home-assistant-operating-system)

   **Auswahl im Imager:**

   * Modell: *Raspberry Pi 3*
   * Betriebssystem:
     *Other specific‑purpose OS → Home Automation → Home Assistant OS*
   * SD‑Karte auswählen
   * Schreiben starten

---

### Erster Start

* Raspberry Pi anschließen
* SD‑Karte einsetzen
* Home Assistant startet automatisch
* Nach dem vollständigen Start wird die **HA‑CLI** angezeigt

**Zugriffsdaten:**

* IP‑Adresse: `192.168.98.154`
* Port: `8123`

---

### Benutzer anlegen

* **Name:** HTLSteyr
* **Benutzername:** htlsteyr
* **Passwort:** terra123

➡️ Danach Weiterleitung auf die Home‑Assistant‑Startseite

---

## Erste Konfigurationen

**Pfad:** `Einstellungen → Add-ons`

### Installierte Add-ons

* **Mosquitto Broker**
  Zum Verwalten und Verwenden von MQTT‑Geräten

* **File Editor**
  Ermöglicht einfaches Arbeiten mit Home‑Assistant‑Dateien
  Besonders wichtig für **YAML‑Konfigurationen**

---

### 📅 27.01.2026

* Nicht anwesend aufgrund von **Krankheit**

---

## 📅 03.02.2026

### Home Assistant Core Update
- **Version:** 2026.1.2 → 2026.1.3  
- **Art:** Minor Update  
- **Versionshinweise:**  
  https://www.home-assistant.io/blog/2026/01/07/release-20261/

---

### Installation von HACS (Home Assistant Community Store)

Zur Erweiterung von Home Assistant um Community-Integrationen und Custom Cards wurde **HACS** installiert.

**Vorgehensweise:**
1. Aufruf der offiziellen HACS-Dokumentation  
   https://hacs.xyz/docs/use/download/download/#to-download-hacs
2. Ausführen des **Get-HACS Installationsskripts**
3. Warten, bis HACS vollständig heruntergeladen wurde
4. Hinzufügen von **HACS** über  
   *Einstellungen → Geräte & Dienste → Integration hinzufügen*
5. Durchführung der **GitHub-Authentifizierung**
6. **Neustart von Home Assistant**

Nach dem Neustart steht HACS vollständig zur Verfügung.

---

### Raspberry Pi 3 – Systemüberwachung

#### Systemdaten erfassen
Zur Überwachung der Systemressourcen des Raspberry Pi 3 wurde die Integration **System Monitor** verwendet.

**Schritte:**
- Installation der Integration **System Monitor** über *Geräte & Dienste*
- Aktivierung der gewünschten Entitäten (z. B. CPU-Temperatur, CPU-Auslastung, RAM)
- Testweise Darstellung der Sensordaten in einem neu erstellten Dashboard (*Dashboard-Start*)

---

#### Visualisierung der Systemdaten

Zur übersichtlichen Darstellung der Systemressourcen wurde eine Custom Card eingesetzt.

- Installation der **RPi Monitor Card** über **HACS**
- Einbindung der Card in ein Dashboard mittels YAML-Konfiguration
- Darstellung folgender Systemwerte:
  - CPU-Temperatur
  - CPU-Auslastung
  - Arbeitsspeicher-Auslastung
  - Swap-Nutzung
  - Systemlast (Load Average)
  - Laufzeit (Uptime)
oard-Start) dargestellt
Installieren von RPi Monitor Card über HACS

---



