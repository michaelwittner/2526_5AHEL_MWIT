# 2526_5AHEL_MWIT
Individual Projects for MWIT 
13.1.2026
Informationen über die Pi-Pico-W wurden gesammelt und die MicroPython Version v1.27.0 (2025-12-09) .uf2 wurde raufgespielt.
Pi Pico wird vom Gerätemanager erkannt: https://micropython.org/download/RPI_PICO_W/
Danach wurde eine Tool gesucht um auf den Pi Pico einfach Daten spielen kann. Dabei wurde Thonny ausgewählt. 
Thonny hat den Pi Pico erkannt.
https://thonny.org/

20.1.2026
Ein Beschleunigungssensor und Neigungssensor wurden für die Datengewinnung gesucht.
https://www.conrad.at/de/p/joy-it-mpu6050-beschleunigungssensor-1-st-passend-fuer-entwicklungskits-bbc-micro-bit-arduino-raspberry-pi-rock-p-2136256.html?insert=UP&utm_source=google-shopping-de&utm_source=google&utm_medium=search&utm_medium=cpc&utm_campaign=shopping-online-de&utm_campaign=Shopping_AT_2025&utm_content=shopping-ad_cpc&WT.srch=1&ef_id=CjwKCAiAybfLBhAjEiwAI0mBBr9C7ffb8zKMXnKoxc4loea1cZD2x9dRlVpK-wu9Pr6pGFt5EAWgyRoCacQQAvD_BwE:G:s&utm_id=22317741252&gad_source=1&gad_campaignid=22317741252&gbraid=0AAAAADoNYuy0NyCAPozyMTOhB8LFvJRIi&gclid=CjwKCAiAybfLBhAjEiwAI0mBBr9C7ffb8zKMXnKoxc4loea1cZD2x9dRlVpK-wu9Pr6pGFt5EAWgyRoCacQQAvD_BwE

Da beim letzten Mal eine falsche Software auf den Pico gespielt wurde, musste dies noch ausgebessert werden.
https://micropython.org/download/RPI_PICO_W/
Als nun via "Thonny" die Verbindung zum Pico hergestellt wurde, wurde ein Python Projekt mit Chat GPT geschrieben, damit der Pico sich mit einen W-Lan verbindet. Die einfache HTML Datei wurde auch noch von Chat GPT generiert wurden. Da die Verbindung mit dem Schul-Wlan sich als etwas kompliziert herausstellte, erstellte ich einen Hot Spot mit meinem Handy. Der Pico hat sich perfekt verbunden und der Webserver funktioniert.

Nachdem der neue bestellte Microkontroller und MPU6050 angekommen ist musste der Raspberry neue mit Micropython aufgesetzt werden. Danach wurde eine zweite php Datei erstellt um die Sensordaten auszulesen über I2C. Der Aufbau wurde auf einen Steckboard umgesetzt. Sensordaten können nun ausgelesen werden (Neigung, Beschleunigung und Temperatur).
----------------------------------------
Beschleunigung:
  Links / Rechts (X): -0.00 g
  Vor / Zurück  (Y): -0.02 g
  Oben / Unten  (Z): 1.03 g
Neigung:
  Links / Rechts (Roll): -0.1 °
Temperatur:
  26.7 °C
----------------------------------------

### ToDo's
* Grafische Anzeige der Beschleunigungsdaten (Fadenkreuz)
* Setup-Seite für Einstellung von
  * Uhrzeit
  * Abtastrate / geplante Fahrtdauer 
  * ...

* Wieviele Daten werden pro Abtastung aufgenommen (Byte)
* Wieviel Speicherplatz steht zur Verfügung - abzüglich der Firmware! 
* Wie könnte die Daten komprimiert gespeichert werden - z.B. Delta

* WebServer auf PiPico Erklärung
* Sensormodul