# 2526_5AHEL_MWIT
Individual Projects for MWIT 
                                                      HomeAssistant GUI
                                                                                                                                 Julian Dietachmair


- 13.01.2026

- Smartphone-Dashboard:
  PopUps um PopUp Eltern erweitert
  Anpassungen der Entitäten
  Batteriestandanzeige des Temperaturfühlers hinzugefügt und versucht diese passend zu formatieren um die Temperatur & Luftfeuchtigkeitsanzeige noch     leserlich zu lassen und nicht abzuschneiden (im rechten 1/3 der Spalte platzieren)

- Automatisierung für automatische Navigation vom Smartphone auf das Mobile Dashboard, da die Build In Lösung nicht zuverlässig funktioniert und         sich des öfteren zurücksetzt. Lösung mit bereits installierten BrowserMod AddOn von HACS. Bei diesem registriert sich jedes Gerät womit sich           unterscheiden lässt welches Gerät gerade Zugreift bzw das Dashboard anschauen will. So ist es mir möglich auf meinem Laptop automatisch auf der
  Standard Oberfläche zu landen und auf meinem Smartphone auf die fürs Handy optimierte Version zu gelangen.

  YAML der Automatisierung:
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
  

  -20.01.2026

  BrowserMod automatisierung wurde die letzte Woche getestet und funktionierte zwar einigermaßen zuverlässig jedoch gab es den Fehler, dass sich ein   anderer Browser (also ein Gerät zB mein Tablet) ebenfalls zyklisch auf das Smartphone Dashboard navigiert wurde, obwohl ein Zielgerät definiert
  wurde. Nach etwas recherge bin ich auf die GUI Variante davon gestoßen welche robuster sein soll, da diese keine Automatisierung darstellt sondern   von Browser Mod selbst verarbeitet wird. Damit klappts zum Aktuellen Zeitpunkt sehr gut und zuverlässig.

  HA OS auf Raspberry PI 3 Model B+ installieren

  Zuerst Raspberry PI Imager installieren:
  https://www.raspberrypi.com/software/

  Mithilfe von dieser Doku SD Karte flashen:
  https://www.home-assistant.io/installation/raspberrypi/#install-home-assistant-operating-system
  -> Modell auswählen: Raspberry PI 3
  -> Betriebssystem auswählen: Other specific- purpose OS -> Homeautomation -> Homeassistant OS
  -> SD Karte auswählen
  -> Schreiben

  Erster Start von HA:
  -> PI anschließen und SD Karte einfügen
  -> HA startet nun von selbst und öffnet nach vollständigen Start die HA CLI
  -> HA zeigt die IP Adresse und Port des Servers an
  -> IP: 192.168.98.154:8123

    User anlegen:
    Name: HTLSteyr
    Benutzername: htlsteyr
    Passwort: terra123

  Nun landet man auf der Startseite

  Erste Configs:
  Einstellungen -> Add-ons:
  
  Mosquitto broker -> Zum verwenden und verwalten von MQTT Geräten

  File editor -> Ermöglicht einfaches und unkompliziertes Arbeiten mit HA Files vorallem für YAML Configurationen wichtig

  

  
  
  

     
  
  
