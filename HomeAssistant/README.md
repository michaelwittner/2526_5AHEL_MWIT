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

