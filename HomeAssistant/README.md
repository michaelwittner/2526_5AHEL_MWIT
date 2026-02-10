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

### 📅 10.02.2026

## Shelly H&T Gen1 – Temperatur- & Luftfeuchtesensor

### Geräteübersicht

Der **Shelly H&T Gen1** ist ein WLAN-basierter Temperatur- und Luftfeuchtigkeitssensor mit besonders langer Batterielaufzeit.

🔗 Produktseite:  
https://shelly.cloud/products/shelly-humidity-temperature-smart-home-automation-sensor/

#### Funktionsweise (Energiesparmodus)

Der Shelly H&T arbeitet standardmäßig in einem **starken Energiesparmodus**:

- Der WLAN-Controller ist die meiste Zeit **deaktiviert**
- Das Gerät wacht nur auf bei:
  - periodischen Intervallen
  - einer **Änderung der Messwerte**, die den konfigurierten Schwellwert überschreitet
- Nach dem Senden der Sensordaten wird das WLAN **sofort wieder abgeschaltet**

➡️ Dadurch ergibt sich eine sehr lange Batterielaufzeit, jedoch **keine kontinuierliche Live-Verbindung**.

---

### Setup-Modus (manuelle Konfiguration)

Durch **einmaliges Drücken der User-Taste** wechselt der Shelly H&T in den **Setup-Modus**:

- WLAN bleibt für **3 Minuten aktiv**
- Konfiguration über das Webinterface möglich
- Ein weiterer kurzer Tastendruck versetzt das Gerät wieder in den Schlafmodus

---

### Factory Reset

Um den Shelly H&T auf Werkseinstellungen zurückzusetzen:

1. Gerät ggf. aufwecken
2. **User-Taste gedrückt halten**
3. Loslassen, sobald die LED **nicht mehr schnell blinkt**

---

## Home Assistant – MQTT-Konfiguration

### MQTT-Broker (Mosquitto)

Der Shelly H&T wird über den **Mosquitto MQTT-Broker** in Home Assistant eingebunden.

**Angelegte Zugangsdaten:**

- **Benutzername:** `shellyht3CBD1F`
- **Passwort:** `terra123`

---

## Shelly H&T – Gerätekonfiguration

📘 Offizielle Dokumentation:  
https://shelly-api-docs.shelly.cloud/gen1/#mqtt-support

Der Shelly H&T besitzt einen **integrierten Webserver** zur Konfiguration.

### Zugriff auf das Webinterface

1. Gerät in den **Setup-Modus** versetzen  
   (User-Taste einmal drücken)
2. Mit dem vom Shelly bereitgestellten WLAN-Access-Point verbinden
3. Webinterface aufrufen über die feste IP-Adresse: **192.168.33.1**


---

### MQTT-Einstellungen im Shelly

**Pfad:**  
`Internet & Security → Advanced – Developer Settings`

**Konfiguration:**

- **MQTT aktivieren:** `true`
- **MQTT-Server:** IP-Adresse von Home Assistant  
  (nicht statisch, kann sich bei Neustart ändern)
- **Port:** `1883`
- **MQTT-Benutzer:** `shellyht3CBD1F`
- **MQTT-Passwort:** `terra123`

---

### Beobachtetes Verhalten

Nach der Konfiguration versucht sich der Shelly H&T mit dem MQTT-Broker zu verbinden.  
Im Mosquitto-Protokoll erscheint dabei ein neues Gerät, das jedoch lediglich als: `Client unknown`
angezeigt wird.

---

### Fehleranalyse / Vereinfachung

Um mögliche Konfigurationsfehler auszuschließen, wurden die MQTT-Zugangsdaten testweise vereinfacht:

- **MQTT-Benutzer:** `shelly`
- **MQTT-Passwort:** `shelly123`

➡️ Diese Anpassung führte **zu keiner Veränderung des Verhaltens**.  
Das Gerät wird weiterhin nur als unbekannter Client im MQTT-Broker angezeigt.

---

**Aktueller Stand:**  
Die MQTT-Verbindung kommt zustande, jedoch werden **keine Sensordaten erfolgreich verarbeitet**.


