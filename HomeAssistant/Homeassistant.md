# Home Automation mit Home Assistant
Julian Dietachmair  
5AHEL – 2025/26

---

# Einführung in Home Automation

Unter Home Automation versteht man die automatische Steuerung und Überwachung von Geräten und Systemen in einem Gebäude.  
Ziel ist es, den Alltag komfortabler, sicherer und energieeffizienter zu gestalten.

Typische Anwendungen der Gebäudeautomation sind zum Beispiel:

- automatische Beleuchtung
- Heizungssteuerung
- Rollladen- und Raffstoresteuerung
- Temperaturüberwachung
- Sicherheitsüberwachung (z.B. Kameras oder Sensoren)
- Energieverbrauchsüberwachung
- generelle Automatisierungen und Erleichterungen im Alltag

Durch Sensoren, Aktoren und eine zentrale Steuerung können viele Abläufe automatisiert werden.

---

# Bekannte und professionelle Smart-Home Lösungen

## Loxone

<img width="400" height="300" src="https://github.com/user-attachments/assets/224d55f0-9f2c-4c55-9cf9-c1fc62677dc0" />

Loxone ist ein Smart-Home-System eines österreichischen Herstellers.  
Die Steuerung erfolgt über einen zentralen Miniserver, der mit verschiedenen Erweiterungsmodulen verbunden wird.

Das System ist stark integriert und richtet sich vor allem an Einfamilienhäuser und professionelle Installationen.

---

## KNX

<img width="400" height="300" src="https://github.com/user-attachments/assets/62ef7430-02cf-41d6-a8c6-b4d18e0329c3" />

KNX ist ein internationaler Standard für Gebäudeautomation.  
Im Gegensatz zu Loxone handelt es sich hierbei nicht um einen einzelnen Hersteller, sondern um einen offenen Standard, der von vielen Herstellern unterstützt wird (z.B. Gira, Jung, ABB oder MDT).

Die Kommunikation erfolgt meist über einen eigenen KNX-Bus, der alle Geräte miteinander verbindet.

---

# Vergleich der Systeme

| Kategorie | KNX | Loxone | Home Assistant |
|-----------|-----|--------|---------------|
| Systemtyp | Offener Industriestandard | Proprietäres System eines Herstellers | Open-Source Plattform |
| Hersteller | Viele Hersteller (z.B. Gira, ABB, MDT) | Nur Loxone Hardware | Herstellerunabhängig |
| Installation | meist Bus-Verkabelung | Loxone Tree / Bus | meist Funk oder Netzwerk |
| Flexibilität | hoch | mittel | sehr hoch |
| Erweiterbarkeit | große Auswahl an Geräten | hauptsächlich Loxone Produkte | tausende Integrationen |
| Programmierung | ETS Software notwendig | Loxone Config Software | GUI oder Konfigurationsdateien |
| Kosten | sehr hoch | hoch | niedrig |
| Internetabhängigkeit | keine | keine | optional |

---

# Vorteile und Nachteile

| System | Vorteile | Nachteile |
|------|-----------|-----------|
| KNX | sehr zuverlässiger Industriestandard<br>große Auswahl an Herstellern<br>lange Lebensdauer (oft über 20 Jahre)<br>funktioniert komplett lokal | sehr hohe Kosten<br>Programmierung mit ETS notwendig<br>Installation meist durch Elektriker |
| Loxone | gut integriertes Gesamtsystem<br>einfache Visualisierung<br>viele Funktionen bereits integriert | proprietäres System<br>Hardware relativ teuer<br>Herstellerabhängigkeit |
| Home Assistant | Open-Source und kostenlos<br>sehr große Community<br>Unterstützung von tausenden Geräten und Herstellern<br>sehr flexibel und erweiterbar<br>lokaler Betrieb möglich | Einrichtung kann komplex sein<br>technisches Wissen oft notwendig<br>Updates können Integrationen beeinflussen<br>Wartung muss selbst durchgeführt werden |

---

## Home Assistant
Home Assistant ist eine Open-Source-Plattform für Smart-Home-Automatisierung.  
Es ermöglicht die Integration von tausenden Smart-Home-Geräten verschiedener Hersteller.

### Timeline
| Jahr | Meilenstein |
|-----|-------------|
| 2013 | Home Assistant wird von Paulus Schoutsen als Open-Source-Projekt gestartet. Ziel ist eine lokale und herstellerunabhängige Smart-Home Plattform. |
| 2016 | Home Assistant gewinnt stark an Popularität und erreicht mehrere tausend Sterne auf GitHub. |
| 2017 | Einführung des Add-on Systems, wodurch zusätzliche Dienste (z.B. Datenbanken, MQTT oder Node-RED) direkt integriert werden können. |
| 2017 | Gründung der Firma Nabu Casa, die Entwickler beschäftigt und die langfristige Entwicklung von Home Assistant unterstützt. |
| 2018 | Veröffentlichung von Home Assistant OS, wodurch die Installation deutlich vereinfacht wird. |
| 2019 | Einführung von Home Assistant Cloud durch Nabu Casa (z.B. Integration von Alexa oder Google Assistant). |
| 2020 | Beim GitHub Octoverse gehört Home Assistant zu den 10 größten Open-Source Projekten auf GitHub nach Anzahl der aktiven Mitwirkenden (>63.000). |
| 2021 | Verbesserte Benutzeroberfläche und vereinfachte Geräteintegration über die grafische Oberfläche. |
| 2023 | Einführung von „Assist“, einem lokalen Sprachassistenten für Home Assistant. |
| 2024 | Home Assistant wird in die Open Home Foundation überführt, um die langfristige Unabhängigkeit des Projekts sicherzustellen. |

---

## Installationsvarianten

### Home Assistant OS
- komplettes Betriebssystem mit minimaler Linux-Umgebung
- einfacher Einstieg
- beinhaltet Supervisor und Add-ons

### Home Assistant Core
- reine Software, läuft in einer Python-Umgebung
- volle Kontrolle über das Betriebssystem
- keine Add-ons oder Supervisor, separat zu installieren

### Hardware
- Raspberry Pi ab Modell 3  
- Mini-PC / Intel NUC  
- Server  
- virtuelle Maschinen (z.B. auf Proxmox)  
- ältere Laptops funktionieren auch

### Minimale Anforderungen (ungefähr)
- CPU: 1–2 Kerne  
- RAM: 2 GB  
- Speicher: 16–32 GB

### Fertige Home Assistant Server
- Home Assistant Yellow → vollwertiger Server, Onboard Zigbee, optional Z-Wave, für größere Installationen  
- Home Assistant Green → kompakt, günstig, ideal für kleine Installationen

  <img width="500" height="350" alt="image" src="https://github.com/user-attachments/assets/2d9a0f17-629c-4f8d-ba02-4e0a79552c51" />

- siehe: [Home Assistant Hardware Vergleich](https://www.seeedstudio.com/blog/2024/07/23/home-assistant-green-vs-yellow-vs-blue/)

---

## Funkstandards & Protokolle

Home Assistant unterstützt die wichtigsten Funkstandards und Kommunikationsprotokolle:

| Protokoll | Beschreibung | Typische Geräte |
|-----------|-------------|----------------|
| MQTT | Netzwerkprotokoll für IoT-Kommunikation | Sensoren, Aktoren, Wetterstationen |
| Zigbee | Funkstandard für Smart-Home Geräte | Lampen, Sensoren, Schalter |
| Z-Wave | Drahtloses Mesh-Netzwerk für Heimautomation | Steckdosen, Relais, Thermostate |
| Thread | IP-basiertes Mesh für moderne Smart-Home Geräte | Sensoren, Tür-/Fenstersensoren |
| Matter | Neuer herstellerübergreifender Standard | Lampen, Thermostate, Sicherheitssysteme |
| WLAN / Wi-Fi | Geräte direkt über Netzwerk verbunden | Lampen, Lautsprecher, Kameras |
| Bluetooth / BLE | Kurzstreckenfunkgeräte | Sensoren, Smart Locks |

> Home Assistant kann somit Geräte aus fast allen Funkstandards und Ökosystemen zusammenführen und zentral steuern.

## Überblick: Wichtige Smart-Home Protokolle

### MQTT

<img width="500" height="250" alt="image" src="https://github.com/user-attachments/assets/85ca25c1-6fd8-4656-a7f8-4c2d89ba4932" />

Funktionsweise:  
MQTT arbeitet nach dem Publish/Subscribe-Modell. Geräte senden (publish) Daten an einen zentralen Broker. Andere Geräte oder Software können diese Daten abonnieren (subscribe) und darauf reagieren.

Terminologie:  
- Broker: zentrale Instanz, die alle Nachrichten empfängt und verteilt  
- Publisher: Gerät/Software, das Daten sendet  
- Subscriber: Gerät/Software, das Daten empfängt  
- Topic: „Adresse“ oder Kategorie für Nachrichten, z.B. `home/livingroom/temperature`

Besonderheiten:  
- Leichtgewichtig, ideal für Sensoren und IoT  
- Daten laufen zentral über den Broker  
- Sehr flexibel, herstellerunabhängig  

---

### Zigbee

<img width="500" height="300" alt="image" src="https://github.com/user-attachments/assets/5098f12c-cebb-4910-9990-2b7de03b1a7f" />

Funktionsweise:  
Zigbee ist ein Mesh-Netzwerk, bei dem Geräte direkt oder über andere Geräte als Router kommunizieren. Geräte leiten Signale weiter, um Reichweite und Stabilität zu erhöhen.

Technische Details:  
- Frequenz: 2,4 GHz (weltweit einheitlich)  
- Topologie: Coordinator → Router → End Devices  
- Datenübertragung: IEEE 802.15.4 auf PHY/MAC-Layer  
- Sicherheit: AES-128 Verschlüsselung auf Netzwerk- und Anwendungsebene  

Terminologie:  
- Coordinator: zentrales Gerät im Zigbee-Netzwerk, meist Gateway oder Hub  
- Router: Geräte, die Signale weiterleiten (z.B. Steckdosen)  
- End Device: batteriebetriebenes Gerät, das nur Daten sendet/empfängt  

Besonderheiten:  
- Energiesparend, ideal für batteriebetriebene Sensoren  
- Geräte arbeiten als Mesh zusammen → hohe Stabilität  
- Standardisiert, viele Hersteller kompatibel  

---

### Matter

<img width="500" height="250" alt="image" src="https://github.com/user-attachments/assets/c7a6c1e3-fb4e-4f3b-8d1b-975d95fea05f" />

Funktionsweise:  
Matter ist ein herstellerübergreifender Smart-Home-Standard, der auf IP-Netzwerken (Wi-Fi oder Thread) läuft. Geräte erkennen sich automatisch und können direkt miteinander kommunizieren.

Technische Details:  
- Jedes Gerät hat eine eindeutige IPv6-Adresse → direkt adressierbar  
- Kommunikationsmodell: Client/Server + Event-Subscription (Geräte senden Events oder Controller fragt ab)  
- Sicherheit: Verschlüsselte Kommunikation, Authentifizierung, Geräteidentität  
- Netzwerk: Mesh über Thread oder WLAN  
- Interoperabilität: Geräte verschiedener Hersteller arbeiten direkt zusammen  

Terminologie:  
- Controller: Gerät oder App, die Matter-Geräte steuert  
- Device: Matter-kompatibles Gerät, z.B. Lampe, Thermostat  
- Fabric: logische Gruppe von Geräten im Netzwerk  

Besonderheiten:  
- Einheitlicher Standard für unterschiedliche Hersteller  
- Plug & Play, herstellerübergreifend  
- Cloud optional, Geräte können lokal gesteuert werden


  #Installieren von Homeassistant auf einem Raspberry PI 3 Modell B+

  ---

# Praktischer Teil: Installation und Konfiguration

Für den praktischen Teil wurde Home Assistant auf einem Raspberry Pi 3 installiert und anschließend ein Sensor über MQTT und eine Steckdose über Zigbee integriert.

---

# Installation von Home Assistant

## Verwendete Hardware

- Raspberry Pi 3 Model B+
- microSD-Karte
- Netzwerkverbindung

---

## Vorbereitung

Installation des Raspberry Pi Imagers:

https://www.raspberrypi.com/software/

Flashen der SD-Karte gemäß offizieller Dokumentation:

https://www.home-assistant.io/installation/raspberrypi/

Auswahl im Imager:

- Modell: Raspberry Pi 3
- Betriebssystem:  
  Other specific-purpose OS → Home Automation → Home Assistant OS
- SD-Karte auswählen
- Schreibvorgang starten

---

## Erster Start

Nach dem Einschalten startet Home Assistant automatisch.

Zugriff über Webbrowser:

http://192.168.98.154:8123
Homeassistant IP Adresse der Instanz + Port -> 8123


Beim ersten Start wird ein Benutzerkonto erstellt.

Name: HTLSteyr  
Benutzername: htlsteyr

Danach öffnet sich das Home-Assistant Dashboard.

---

# Erste Erweiterungen

## Mosquitto MQTT Broker

Über die Add-on Verwaltung wurde der **Mosquitto Broker** installiert.

Pfad:

Einstellungen → Add-ons

Der Broker ermöglicht die Kommunikation zwischen IoT-Geräten über das MQTT-Protokoll.

Typische Anwendungen:

- Sensorwerte übertragen
- Geräte steuern
- Kommunikation zwischen verschiedenen Systemen

---

## File Editor

Der File Editor ermöglicht das Bearbeiten von Konfigurationsdateien direkt im Browser.

Besonders wichtig für:

- YAML-Konfigurationen
- Automationen
- Dashboard-Konfigurationen

---

# Integration eines Sensors über MQTT

## Shelly H&T Gen1 – Temperatur- und Luftfeuchtesensor

Der Shelly H&T Gen1 ist ein WLAN-basierter Temperatur- und Luftfeuchtigkeitssensor.

Produktseite:  
https://shelly.cloud/products/shelly-humidity-temperature-smart-home-automation-sensor/

---

## Funktionsweise

Der Sensor arbeitet in einem Energiesparmodus.

- WLAN ist die meiste Zeit deaktiviert
- Gerät wacht nur bei Messwertänderungen oder periodisch auf
- Daten werden gesendet
- anschließend wird WLAN wieder deaktiviert

Dadurch erreicht das Gerät eine sehr lange Batterielaufzeit.

---

## Konfiguration des Sensors

Der Shelly besitzt einen integrierten Webserver.

Zugriff:

1. Gerät in den Setup-Modus versetzen (User-Taste drücken)
2. Mit dem vom Shelly bereitgestellten WLAN verbinden
3. Webinterface öffnen

http://192.168.33.1


---

## MQTT Konfiguration

Pfad im Webinterface:

Internet & Security → Advanced – Developer Settings

Konfiguration:

- MQTT aktivieren
- MQTT Server: IP-Adresse von Home Assistant
- Port: 1883
- Benutzername und Passwort für MQTT festlegen

Nach der Konfiguration sendet der Sensor seine Daten an den MQTT Broker.

---

# Einbindung in Home Assistant

Der Shelly H&T Gen1 unterstützt kein MQTT Auto Discovery.

Daher müssen die Sensoren manuell in der Datei `configuration.yaml` angelegt werden.

````yaml
mqtt:
  sensor:
    - name: "Shelly H&T Temperatur"
      state_topic: "shellies/shellyht-3CBD1F/sensor/temperature"
      unit_of_measurement: "°C"
      device_class: temperature

    - name: "Shelly H&T Luftfeuchtigkeit"
      state_topic: "shellies/shellyht-3CBD1F/sensor/humidity"
      unit_of_measurement: "%"
      device_class: humidity

    - name: "Shelly H&T Batterie"
      state_topic: "shellies/shellyht-3CBD1F/sensor/battery"
      unit_of_measurement: "%"
      device_class: battery




