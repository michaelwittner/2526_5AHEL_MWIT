# 2526_5AHEL_MWIT
Individual Projects for MWIT 
13.01.2026

Zunächst wurden Informationen über den Raspberry Pi Pico W gesammelt.
Anschließend wurde die MicroPython-Version v1.27.0 (2025-12-09) als .uf2-Datei auf den Pico W aufgespielt.

Der Raspberry Pi Pico W wurde danach erfolgreich vom Gerätemanager erkannt.
Downloadquelle für MicroPython:
https://micropython.org/download/RPI_PICO_W/

Als nächster Schritt wurde nach einem geeigneten Tool gesucht, um einfach Daten und Programme auf den Pico zu übertragen. Hierfür wurde Thonny ausgewählt.
Thonny erkannte den Raspberry Pi Pico W korrekt und stellte eine Verbindung her.
https://thonny.org/

20.01.2026

Für die geplante Datengewinnung wurden ein Beschleunigungs- und Neigungssensor recherchiert. Die Wahl fiel auf den MPU6050.
Produktlink:
https://www.conrad.at/de/p/joy-it-mpu6050-beschleunigungssensor-1-st-passend-fuer-entwicklungskits-bbc-micro-bit-arduino-raspberry-pi-rock-p-2136256.html

Da beim vorherigen Versuch eine falsche Software auf den Pico aufgespielt worden war, musste dies korrigiert werden. Dazu wurde erneut die passende MicroPython-Version installiert:
https://micropython.org/download/RPI_PICO_W/

Nachdem die Verbindung über Thonny hergestellt war, wurde mithilfe von ChatGPT ein Python-Projekt erstellt, das den Raspberry Pi Pico W mit einem WLAN verbindet. Zusätzlich wurde eine einfache HTML-Datei für den Webserver generiert.

Da die Verbindung mit dem Schul-WLAN problematisch war, wurde ein Hotspot über das Handy eingerichtet. Die Verbindung funktionierte einwandfrei, und der Webserver lief erfolgreich.

Weitere Arbeiten

Nach dem Eintreffen des neu bestellten Microcontrollers und des MPU6050-Sensors wurde der Raspberry Pi Pico W erneut mit MicroPython aufgesetzt.

Anschließend wurde eine zweite Datei (zur Sensorauslesung über I²C) erstellt.
Der gesamte Aufbau wurde auf einem Steckbrett (Breadboard) realisiert.

Die Sensordaten können nun erfolgreich ausgelesen werden, darunter:
Beschleunigung
Links / Rechts (X): −0.00 g
Vor / Zurück (Y): −0.02 g
Oben / Unten (Z): 1.03 g
Neigung
Links / Rechts (Roll): −0.1 °
Temperatur
26.7 °C

### ToDo's
* Grafische Anzeige der Beschleunigungsdaten (Fadenkreuz)
* Setup-Seite für Einstellung von
  * Uhrzeit
  * Abtastrate / geplante Fahrtdauer 
  * ...

* Wieviele Daten werden pro Abtastung aufgenommen (Byte)
  Frühe Werte benötigen weniger Speicherplatz ca. 40 Byte
  Negative Werte benötigen eine extra Byte wegen dem Minus
  Spätere Werte benötigen ca. 45 Byte
  Also ca 42 Byte pro Sample
  Das Entspricht:
  20 × 42 ≈ 840 Bytes/s
  ~50 KB / Minute
  ~3.0 MB / Stunde
  Mit 1.2 MB Flash übrig ca. 20 bis 25 min Zeit

* Wieviel Speicherplatz steht zur Verfügung - abzüglich der Firmware!
  2 MB Flash Speicher.
  MicroPython-Firmware (inkl. WLAN-Stack): ca. 600–700 KB
  Verbleibender Flash für Dateien: ca. 1.2–1.3 MB
  
* Wie könnte die Daten komprimiert gespeichert werden - z.B. Delta
  Indem man Binär Logged

* WebServer auf PiPico Erklärung
Dein Raspberry Pi Pico W läuft als einfacher HTTP-Webserver, der Sensordaten des MPU6050 bereitstellt und Steuerbefehle entgegennimmt. Beim Aufruf der Webseite lädt der Browser zunächst eine statische HTML-Datei vom Pico, die nur für Darstellung und Benutzeroberfläche zuständig ist. Anschließend fragt ein JavaScript-Timer alle 200 ms über die URL **/data** aktuelle Messwerte ab. Der Pico antwortet darauf mit einem JSON-Objekt, das die momentanen Beschleunigungen, die berechnete Schräglage, die Temperatur sowie die jeweils gespeicherten Maximalwerte enthält. Diese Daten werden im Browser ohne Neuladen der Seite direkt in die Tabelle eingetragen, sodass eine Live-Anzeige entsteht. Zusätzlich senden die Reset-Buttons einfache HTTP-Anfragen an **/reset** mit einem Parameter, der angibt, welcher Maximalwert zurückgesetzt werden soll. Der Pico verarbeitet diese Anfrage, setzt den entsprechenden Wert intern zurück und bestätigt dies mit einer kurzen HTTP-Antwort. Insgesamt übernimmt der Pico die Sensorik, Berechnung, Speicherung und Datenbereitstellung, während der Browser ausschließlich für Anzeige und Bedienung zuständig ist.

* Sensormodul
Der **MPU6050** ist ein kombiniertes **6-Achsen-Inertialsensormodul**, das aus einem **3-Achsen-Beschleunigungssensor** und einem **3-Achsen-Gyroskop** besteht. Der Beschleunigungssensor misst entlang der X-, Y- und Z-Achse sowohl Bewegungsbeschleunigungen als auch die Erdbeschleunigung, wodurch sich Neigung und Lage im Raum bestimmen lassen. Das Gyroskop misst die **Drehgeschwindigkeit** um diese Achsen und eignet sich zur Erfassung schneller Bewegungen und Rotationen. Intern wandelt der MPU6050 die analogen Sensordaten mit **16-Bit-AD-Wandlern** in digitale Werte um und stellt sie über den **I²C-Bus** dem Mikrocontroller zur Verfügung. Zusätzlich besitzt der Chip einen integrierten **Temperatursensor** zur Driftkorrektur. In deinem Programm nutzt du den Beschleunigungssensor, um aus der Richtung der Erdbeschleunigung die Schräglage zu berechnen, während das Gyroskop derzeit nicht ausgewertet wird.

Zu Beginn hat sich der PICO mit einen W-Lan (Hotspot) verbunden. Der PICO kann aber auch sein eigenes W-Lan erstellen. Mit namen Telemetry und passwort speedlane kann man sich mit dem PICO verbinden und hat immer eine Vordefinierte IP Adresse. 

Aktuell wird http Polling verwendet. Hier muss bei jeder Datenübertragung eine neue Verbindung zum PICO aufgebaut werden um die Sensordaten usw zu erhalten. Für eine Zeitnahe Anwändung benötigt man aber eine hohe refresh rate. Bei http Polling hängt die refresh rate auch sehr stark von der Distanz vom PICO zum Endgerät ab. Innerhalb von einen Halben Meter ändert sich die refresh rate von sehr instabile 10 Hz ca zu ein paar wenige Hz. Das Endgerät fragt ab ob er Daten bekommt und der PICO sendet.
Lösung: Websocket. Die Verbindung zum PICO wird einmal aufgebaut und der PIOC sendet Daten ohne Abfrage. Somit kann die refresh rate auf lockerere 20 Hz erhöht worden und könnte noch mehr sein. 
Aktuelle Werte auf der Website:
Beschleunigung x und y Achse und die Schräglage nach links und rechts. Dabei noch alle Best of all Time werte welche auch zurück gesetzt werden können. 
Ein Problem tritt auf wenn man den Sensor um 90° Dreht. Schräglage ist im Motorad normal somit musste das Problem behoben werden. Wenn sich der Pico um 90° dreht wird die X-Achse zur neuen Z-Achse. Also misst die X-Achse die Erdbeschleunigung. Das verfälscht das Ergebnis. Die Erdbeschleunigung beeinflusst die X-Achse bei Neigung mit einer Sinus Kurve. Mit Gemini Pro konnte aber eine Formel entwickelt werden die das ungefähr ausgleicht. 

Um mehr Performance aus dem PICO zu holen werden alle zwei Cores verwendet. Der eine fokusiert sich auf dem Webserver und der andere kümmert sich um den Sensor, logging und SD Karte. Mit Thread konnte dies gelöst werden.

Der PICO hat nur einen 2 MB flash Speicher. Wenn man aber Sensor Daten mit 20 Hz Speichern möchte benötigt man mehr Speicherplatz. 
