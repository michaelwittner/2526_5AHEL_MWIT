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
     
  
  
