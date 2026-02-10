# Methoden-/Aufrufliste (STT + TTS + Sleep) – aktueller Projektstand

## A) App-Start → Service starten

### 1) `MainActivity.onCreate()`
- UI wird initialisiert.
- Prüft/fordert Berechtigungen an (Mikrofon, ggf. Notifications).
- Startet den Always-on-Teil über den Foreground-Service.

### 2) `MainActivity.checkAndRequestAudioPermission()`
- Prüft `RECORD_AUDIO`.
- Falls nicht vorhanden: Systemdialog für Berechtigung.

### 3) `MainActivity.onRequestPermissionsResult(...)`
- Reagiert auf User-Entscheidung.
- Bei Erfolg: Service-Start / STT-Initialisierung wird ausgelöst.
- Bei Ablehnung: STT bleibt deaktiviert, UI zeigt Status.

### 4) `MainActivity.startAstraService()`
- Erstellt `Intent` auf `AstraForegroundService`.
- Startet Service je nach Android-Version als `startForegroundService(...)` (wichtig ab Android O).

---

## B) Foreground-Service → Stabiler Dauerbetrieb

### 5) `AstraForegroundService.onCreate()`
- Wird beim Service-Start aufgerufen.
- Initialisiert interne Manager/Handler.
- Baut Notification-Channel (falls nötig).
- Bereitet STT/TTS-Subsysteme vor.

### 6) `AstraForegroundService.createNotificationChannel()`
- Legt einen NotificationChannel an (Android O+).
- Zweck: Foreground-Service darf sonst keine Notification anzeigen.

### 7) `AstraForegroundService.buildNotification()`
- Erstellt die laufende Status-Notification (z. B. “Listening…”).
- Setzt Icon, Priorität, Kanal, Text.

### 8) `AstraForegroundService.startInForeground()`
- Ruft `startForeground(notificationId, notification)` auf.
- Zweck: System beendet den Service nicht wegen Hintergrundlimits.

### 9) `AstraForegroundService.onStartCommand(intent, flags, startId)`
- Reagiert auf erneute Starts/Intents.
- Startet (falls noch nicht aktiv):
  - Vosk Modell laden/entpacken
  - SpeechService starten
  - Wake-/Sleep-Status setzen
- Rückgabewert typischerweise `START_STICKY`, damit Service bei Kill neu startet.

---

## C) Vosk Setup → Modell bereitstellen → Recognizer starten

### 10) `AstraForegroundService.initVosk()`
- Setzt Vosk-Logging/Config (z. B. `LibVosk.setLogLevel(...)`).
- Startet das Modell-Setup: Modell aus Assets in App-Speicher.

### 11) `StorageService.unpack(context, modelAssetPath, targetDirName, callback)`
- Entpackt Modell-Ordner aus `assets/` in internen Speicher.
- Ruft danach Callback auf:
  - `onComplete(Model model)`
  - `onError(Exception e)`

### 12) `AstraForegroundService.onModelReady(Model model)` *(Callback aus unpack)*
- Speichert `model` in einer Member-Variable.
- Erstellt `Recognizer` (z. B. mit Sample-Rate 16000).
- Erstellt `SpeechService` (Audioaufnahme + Streaming in Recognizer).
- Startet Listening.

### 13) `AstraForegroundService.createRecognizer(model, sampleRate)`
- `recognizer = new Recognizer(model, sampleRate)`
- Optional: Konfiguration (Wortliste/Grammar, wenn verwendet).
- Zweck: Engine-Instanz, die Audio zu Text decodiert.

### 14) `AstraForegroundService.createSpeechService(recognizer, sampleRate)`
- `speechService = new SpeechService(recognizer, sampleRate)`
- Zweck: Bindet Mikrofon-Audio an den Recognizer.

### 15) `AstraForegroundService.startListening()`
- `speechService.startListening(this)`
- `this` ist `RecognitionListener` → liefert Callbacks (Partial/Final/Error).
- Setzt internen Status: LISTENING = true.

---

## D) RecognitionListener Callbacks → Text entsteht

### 16) `onPartialResult(String hypothesis)`
- Wird sehr häufig aufgerufen (Zwischenerkennung).
- Typisch passiert:
  - JSON wird geparst (z. B. Feld `"partial"`).
  - UI-Preview aktualisiert (Live-Text).
  - **Keine Aktionen** oder nur sehr vorsichtige (um Fehltrigger zu vermeiden).

### 17) `onResult(String hypothesis)`
- Ergebnis, das oft zwischen Partial und Final liegt (je nach Vosk-Flow).
- Typisch:
  - JSON parsen (Feld `"text"`).
  - Text in “letztes Ergebnis” übernehmen.
  - Optional schon an Parser geben (wenn das System so gebaut ist).

### 18) `onFinalResult(String hypothesis)`
- Wichtigster Callback: Äußerung gilt als abgeschlossen.
- Typisch passiert:
  1. JSON parsen → finaler Text (`"text"`).
  2. Text wird normalisiert (trim, lowercase, Sonderzeichen).
  3. Übergabe an Keyword-/Command-Logik.
  4. UI wird final aktualisiert (Fließtext).

### 19) `onError(Exception e)`
- Fehler im Audio-/Recognizer-Flow.
- Typisch:
  - Status auf ERROR setzen.
  - SpeechService stoppen.
  - Notification/UI anpassen.
  - Optional: Retry-Strategie (mit Delay).

### 20) `onTimeout()`
- Vosk meldet Timeout (z. B. längere Stille).
- Typisch:
  - Zurück in Idle/Wake-Word-Warten
  - oder Listening neu starten (je nach gewünschtem Verhalten)

---

## E) Text → Keyword-/Command-Parser → Aktionen

### 21) `AstraForegroundService.handleRecognizedText(String text)`
- Zentraler Einstieg für finalen Text.
- Prüft:
  - aktueller Zustand (SLEEPING? SPEAKING? ACTIVE?)
  - leeren Text ignorieren
- Übergibt an Wake/Command-Logik.

### 22) `KeywordRouter.route(text)`
- Sucht nach Wake-/Command-Keywords.
- Gibt eine Command-Struktur zurück (z. B. `CommandType` + Parameter).

### 23) `WakeWordLogic.isWakeWord(text)`
- Prüft, ob Aktivierungswort enthalten ist.
- Falls ja:
  - Statuswechsel auf ACTIVE
  - optional akustische Bestätigung (TTS/Beep)
  - “Command-Fenster” öffnen (z. B. die nächsten X Sekunden als Befehlsphase)

### 24) `SleepLogic.isSleepCommand(text)`
- Prüft, ob Schlafbefehl erkannt wurde.
- Falls ja: `enterSleepMode()`.

### 25) `ActionExecutor.execute(command)`
- Dispatch je nach CommandType, z. B.:
  - UI-Status ändern
  - interne Flags setzen
  - TTS Antwort sprechen
  - Sleep/Wake auslösen

---

## F) Schlafmodus (Sleep) → Was wird aufgerufen?

### 26) `enterSleepMode()`
- Setzt Zustand: `SLEEPING = true`.
- Stoppt/limitiert Listening:
  - entweder `stopListening()` oder “nur Wake-Word” aktiv lassen.
- UI wird gedimmt/umgeschaltet (Sleep-Screen).
- Optional: TTS sagt kurzen Bestätigungssatz (falls vorgesehen).

### 27) `exitSleepMode()`
- Setzt Zustand: `SLEEPING = false`.
- UI wird wieder aktiv (Normal-Screen).
- Listening wird gestartet oder auf ACTIVE gesetzt.

### 28) `updateUiForSleepState(isSleeping)`
- Wechselt Layout/Overlays:
  - Dimming / schwarzes Overlay
  - Statusanzeige „Schlafmodus“
  - evtl. reduzierte Elemente

---

## G) TTS (Sprachausgabe) → Initialisierung, Sprechen, Rückkopplung vermeiden

### 29) `TtsManager.init(context)`
- Erstellt `TextToSpeech(...)`.
- Registriert `OnInitListener`.

### 30) `TextToSpeech.OnInitListener.onInit(status)`
- Prüft, ob Initialisierung OK ist.
- Setzt Sprache (z. B. `Locale.GERMAN` oder Voice).
- Setzt TTS-Parameter (Rate/Pitch, falls genutzt).

### 31) `TtsManager.speak(text, utteranceId)`
- Startet Sprachausgabe.
- Setzt `UtteranceProgressListener` (Start/Done/Error), falls verwendet.
- Sehr wichtig im Projekt:
  - vor dem Speak: STT pausieren/ignorieren, damit TTS nicht wieder erkannt wird.

### 32) `UtteranceProgressListener.onStart(utteranceId)`
- Zustand auf `SPEAKING = true`.
- `pauseListening()` oder “Ignore STT results” Flag setzen.

### 33) `UtteranceProgressListener.onDone(utteranceId)`
- Zustand `SPEAKING = false`.
- `resumeListening()` bzw. Rückkehr in passenden Modus:
  - ACTIVE Listening
  - oder Idle/Wake-Word

### 34) `UtteranceProgressListener.onError(utteranceId)`
- Fehlerbehandlung: Logging + Zustand zurücksetzen + Listening ggf. neu starten.

---

## H) Listening steuern (Start/Stop/Pause)

### 35) `stopListening()`
- `speechService.stop()`
- Setzt Flags: LISTENING = false
- Wird z. B. in Sleep oder bei Fehlern genutzt.

### 36) `pauseListening()`
- Entweder hart stoppen oder “Soft Pause”:
  - Hard: `speechService.stop()`
  - Soft: `ignoreResults = true` (Callbacks werden ignoriert)
- Wird vor allem während TTS benötigt.

### 37) `resumeListening()`
- Startet Listening erneut:
  - `speechService.startListening(this)`
- Setzt Flags zurück:
  - ignoreResults = false
  - LISTENING = true

---

## I) Broadcasts / Wake-Aktionen (falls verwendet)

### 38) `BroadcastReceiver.onReceive(context, intent)`
- Reagiert auf `ACTION_WAKE` oder ähnliche Intents.
- Ruft `exitSleepMode()` oder `startListening()` auf.
- Zweck: externe Trigger (UI-Button, Systemevent, anderer Teil der App).

---

## J) Service-Lifecycle (Aufräumen)

### 39) `AstraForegroundService.onDestroy()`
- Stoppt SpeechService.
- Schließt Recognizer/Model (wenn nötig).
- Stoppt TTS / `tts.shutdown()`.
- Entfernt Handler-Callbacks.

### 40) `AstraForegroundService.onBind(intent)`
- Falls nicht gebunden: gibt `null` zurück (typisch bei reinem Start-Service).
- Wenn gebunden: liefert Binder (falls UI direkt mit Service kommuniziert).

---

## Kurzüberblick als Aufrufkette (kompakt)

1. `MainActivity.onCreate()`  
2. `startAstraService()`  
3. `AstraForegroundService.onCreate()` → `startInForeground()`  
4. `initVosk()` → `StorageService.unpack(...)`  
5. `onModelReady()` → `createRecognizer()` → `createSpeechService()` → `startListening()`  
6. `onPartialResult()` / `onFinalResult()`  
7. `handleRecognizedText()` → `KeywordRouter.route()` → `ActionExecutor.execute()`  
8. Optional `TtsManager.speak()` → `onStart()` pausiert STT → `onDone()` resumed  
9. `enterSleepMode()` / `exitSleepMode()` je nach Command
