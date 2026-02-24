# Methoden-/Aufrufliste (STT + TTS + Sleep) – **korrigiert nach deinem Code**

## A) App-Start → Service starten (MainActivity)

### 1) `MainActivity.onCreate(Bundle savedInstanceState)`
- Setzt das Layout (`setContentView(...)`).
- Initialisiert `SleepModeController`.
- Holt UI-Referenzen (`clockCenter`, `speechTextCenter`).
- Aktiviert Fullscreen/Kiosk-Optik über `applyImmersive()`.
- Stellt beim Start ggf. den Schlafmodus aus SharedPreferences wieder her:
  - wenn aktiv → `sleepController.enable(...)` + Text/Uhr ausblenden
  - sonst → `showClock()`
- Startet anschließend den Permission-/Start-Flow: `ensurePermissionsAndStartService()`.

### 2) `MainActivity.applyImmersive()`
- Aktiviert „Immersive Mode“:
  - `WindowCompat.setDecorFitsSystemWindows(..., false)`
  - Status-/Navigationsleisten verstecken (und per Wisch kurz einblendbar machen).

### 3) `MainActivity.ensurePermissionsAndStartService()`
- Prüft `RECORD_AUDIO`:
  - wenn fehlt → `requestPermissions(...)` mit `REQ_RECORD_AUDIO`
- Prüft auf Android 13+ zusätzlich `POST_NOTIFICATIONS`:
  - wenn fehlt → `requestPermissions(...)` mit `REQ_POST_NOTIFICATIONS`
- Wenn alles vorhanden → `startAstraService()`.

### 4) `MainActivity.onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults)`
- Wenn Permission abgelehnt:
  - zeigt `showSpeechText("Permission verweigert.")`
  - ruft `scheduleBackToClock()`
- Wenn ok:
  - ruft wieder `ensurePermissionsAndStartService()` (damit ggf. die nächste Permission geprüft wird und am Ende der Service startet).

### 5) `MainActivity.startAstraService()`
- Startet den Foreground-Service via:
  - `ContextCompat.startForegroundService(this, new Intent(this, AstraForegroundService.class));`

---

## B) UI-Rücksprung / Anzeige-Logik (MainActivity)

### 6) `MainActivity.showSpeechText(String text)`
- Blendet die Uhr aus und zeigt stattdessen den erkannten Text/Status im Center-TextView.

### 7) `MainActivity.showClock()`
- Entfernt geplante Rücksprünge (`removeCallbacks`).
- Wenn Schlafmodus aktiv:
  - Uhr und Text werden ausgeblendet (Overlay bleibt dunkel).
- Sonst:
  - TextView leeren/ausblenden, Uhr wieder einblenden.

### 8) `MainActivity.scheduleBackToClock()`
- Plant nach `UI_RETURN_MS` automatisch zurück zur Uhr.
- Ausnahme: Im Schlafmodus wird **nicht** automatisch zurückgeschaltet.

---

## C) Broadcasts vom Service → UI reagieren lassen (MainActivity)

### 9) `MainActivity.onStart()`
- Registriert den Receiver `astraReceiver` für:
  - `ACTION_WAKE`, `ACTION_PARTIAL`, `ACTION_COMMAND`, `ACTION_TIMEOUT`,
  - `ACTION_SLEEP_ON`, `ACTION_SLEEP_OFF`
- Ab Android 13 mit `registerReceiver(..., Context.RECEIVER_NOT_EXPORTED)`,
  sonst via `ContextCompat.registerReceiver(...)`.

### 10) `MainActivity.onStop()`
- Entfernt UI-Timer (`removeCallbacks`).
- Unregister Receiver (try/catch).

### 11) `astraReceiver.onReceive(Context context, Intent intent)`  *(BroadcastReceiver in MainActivity)*
- Reagiert auf Events vom Service:
  - `ACTION_SLEEP_ON`:
    - `sleepController.enable(...)`
    - Uhr/Text ausblenden
    - Timer stoppen
  - `ACTION_SLEEP_OFF`:
    - `sleepController.disable(...)`
    - `showClock()`
  - Wenn Schlafmodus aktiv → **keine** Texte anzeigen (bleibt schwarz)
  - `ACTION_WAKE`:
    - zeigt `"Astra …"` und ruft `scheduleBackToClock()`
  - `ACTION_PARTIAL`:
    - liest `EXTRA_TEXT` und zeigt Partial-Text + `scheduleBackToClock()`
  - `ACTION_COMMAND`:
    - liest `EXTRA_TEXT` und zeigt finalen Command-Text + `scheduleBackToClock()`
  - `ACTION_TIMEOUT`:
    - zurück zur Uhr (`showClock()`)

### 12) `MainActivity.onWindowFocusChanged(boolean hasFocus)`
- Wenn Fokus wieder da ist: Systembars erneut verstecken (Immersive stabil halten).

---

## D) Foreground-Service Lifecycle (AstraForegroundService)

### 13) `AstraForegroundService.onCreate()`
- Setzt Vosk LogLevel: `LibVosk.setLogLevel(LogLevel.INFO)`
- Notification-Setup:
  - `createNotificationChannel()`
  - `startInForeground("Astra: Service gestartet")`
- Prüft `RECORD_AUDIO`:
  - wenn fehlt → Notification updaten + `stopSelf()`
- Initialisiert TTS:
  - `tts = new TtsManager(this, callbacks)`
  - `tts.init()`
  - Callback-Logik:
    - `onStartSpeaking()` → `stopListening()` + `pauseArmedTimer()`
    - `onDoneSpeaking()` / `onErrorSpeaking()` → `startListening()` + ggf. `restartArmedTimer()`
- Startet Modell-Laden:
  - `updateNotification("Astra: Modell wird geladen…")`
  - `initModelFromAssets()`

### 14) `AstraForegroundService.onStartCommand(Intent intent, int flags, int startId)`
- Gibt `START_STICKY` zurück (Service soll nach Kill wiederkommen).

---

## E) Vosk Setup → Modell bereitstellen → Listening starten (AstraForegroundService)

### 15) `AstraForegroundService.initModelFromAssets()`
- Entpackt Modell aus `assets/`:
  - `StorageService.unpack(this, "vosk-model-small-de-0.15", "vosk-model-de", successCallback, errorCallback)`
- Success-Callback `(Model m) -> { ... }`:
  - `model = m`
  - Notification: „Modell OK…“
  - `startListening()`
  - Notification: „hört zu…“
- Error-Callback `(Exception e) -> { ... }`:
  - Log + Notification „Modell-Fehler“

### 16) `AstraForegroundService.startListening()`
- Schutz: wenn `model == null` → return
- Stoppt vorher sauber: `stopListening()`
- Erstellt Recognizer direkt hier:
  - `Recognizer recognizer = new Recognizer(model, 16000.0f)`
  - `configureEndpointerIfPossible(recognizer)` (falls Methode vorhanden)
- Erstellt SpeechService direkt hier:
  - `speechService = new SpeechService(recognizer, 16000.0f)`
  - `speechService.startListening(this)` (RecognitionListener callbacks kommen in diese Klasse)

### 17) `AstraForegroundService.stopListening()`
- Stoppt + shutdown von `speechService` und setzt `speechService = null`.

### 18) `AstraForegroundService.configureEndpointerIfPossible(Recognizer r)`
- Versucht per Reflection `setEndpointerDelays(...)` zu setzen
  (damit Speech-Ende / Pausen besser erkannt werden).

### 19) `AstraForegroundService.restartListeningSoon()`
- Nach kurzer Verzögerung:
  - `stopListening()`
  - `startListening()`
- Wird bei Fehlern genutzt.

---

## F) RecognitionListener Callbacks → Text entsteht (AstraForegroundService)

### 20) `AstraForegroundService.onPartialResult(String hypothesis)`
- Wenn TTS gerade spricht (`tts.isSpeaking()`) → return
- `extractPartial(hypothesis)` → holt JSON-Feld `"partial"`
- Nur im Zustand `State.ARMED`:
  - Wake-Word wird aus dem Partial entfernt (über `afterWakeWordOriginal(...)`)
  - UI-Updates werden gedrosselt (Throttle):
    - `broadcastPartial(cleaned)`

### 21) `AstraForegroundService.onResult(String hypothesis)`
- Ruft intern: `handleHypothesis(hypothesis, "result")`

### 22) `AstraForegroundService.onFinalResult(String hypothesis)`
- Ruft intern: `handleHypothesis(hypothesis, "final")`

### 23) `AstraForegroundService.handleHypothesis(String hypothesis, String src)`
- Wenn TTS spricht → return
- `extractText(hypothesis)` → holt JSON-Feld `"text"`
- `normalize(text)` → vereinheitlicht (lowercase, ä→ae, Sonderzeichen → Leerzeichen, mehrfach spaces)
- Dedup (gegen doppelte Finals):
  - vergleicht `lastHandledNorm` + Zeitfenster `RESULT_DEDUP_MS`
- Verhalten abhängig vom internen `state`:

**State.IDLE:**
- Wenn Wake-Word nicht enthalten → return
- Cooldown (`WAKE_COOLDOWN_MS`) verhindert direktes Wiedertriggern
- `broadcastWake()` + `armSession()`
- Wenn im selben Satz schon ein Command nach „astra“ kommt:
  - `cmdOrig = afterWakeWordOriginal(text)`
  - `handleCommand(cmdOrig)`
  - Wenn erkannt → `restartArmedTimer()`
- Wenn nur „astra“:
  - `speakPromptOnce()` (Prompt nur 1× pro Session)

**State.ARMED:**
- Nimmt kompletten Text als Command (falls wieder „astra …“ vorkommt → Teil nach „astra“)
- Ignoriert sehr kurze/unsinnige Finals über `isIgnorable(...)` (Timer wird nicht verlängert)
- Führt aus: `handled = handleCommand(cmdOrig)`
- Nur wenn `handled == true` → `restartArmedTimer()`

### 24) `AstraForegroundService.onError(Exception e)`
- Notification updaten + `restartListeningSoon()`

### 25) `AstraForegroundService.onTimeout()`
- `restartListeningSoon()`

---

## G) Command-/Keyword-Handling (alles im Service, keine separaten Router-Klassen)

### 26) `AstraForegroundService.handleCommand(String commandOrig)`
- Normalisiert: `commandNorm = normalize(commandOrig)`
- Sendet Text an UI: `broadcastCommand(commandOrig)`
- Prüft Keywords über `containsWord(...)` und `KeyPhrases.*`:
  - Schlafmodus:
    - `broadcastSleepOn()`
    - `speak("Gute Nacht.")`
    - return `true`
  - Aufwachen:
    - `broadcastSleepOff()`
    - spricht Uhrzeit + Datum
    - return `true`
  - „sag hallo zu …“:
    - `extractHelloTarget(...)` → Name/Teil extrahieren
    - spricht Hallo…
    - return `true`
  - „danke“ → spricht „Gern.“ → true
  - „uhrzeit / wie spät“ → spricht Uhrzeit → true
  - „datum / welcher tag“ → spricht Datum → true
- Unbekannt:
  - return `false` (bewusst ruhig bleiben)

### 27) `AstraForegroundService.speakPromptOnce()`
- Sagt „Ja, wie kann ich helfen?“ **nur einmal pro Session** (`promptSpokenThisSession`).

### 28) `AstraForegroundService.speak(String text)`
- Wrapper:
  - prüft `tts != null` und `tts.isReady()`
  - ruft `tts.speakFlush(text)`

### 29) `AstraForegroundService.isIgnorable(String cmdNorm)`
- Filtert „Müll“ wie: sehr kurz, nur „astra“, „ja“, „ok/okay“ usw.

---

## H) Session-/Timer-Steuerung (Wake-Fenster)

### 30) `AstraForegroundService.armSession()`
- Setzt `state = State.ARMED`
- Reset von Session-Flags:
  - `promptSpokenThisSession = false`
  - Partial-UI Cache reset
- Startet/erneuert den ARMED-Timer: `restartArmedTimer()`

### 31) `AstraForegroundService.restartArmedTimer()`
- Wenn TTS spricht → return (Timer nicht während TTS)
- Entfernt alte `disarmRunnable`
- Plant `disarmRunnable` nach `ARMED_MS`:
  - setzt `state = State.IDLE`
  - reset Partial-UI
  - `broadcastTimeout()`

### 32) `AstraForegroundService.pauseArmedTimer()`
- Entfernt geplanten disarm-Timer (wird beim TTS-Start aufgerufen).

---

## I) Broadcast-Methoden (Service → Activity)

### 33) `broadcastWake()`
### 34) `broadcastPartial(String partial)`
### 35) `broadcastCommand(String command)`
### 36) `broadcastTimeout()`
### 37) `broadcastSleepOn()`
### 38) `broadcastSleepOff()`
- Jeweils:
  - `Intent` mit Action
  - `setPackage(getPackageName())` (damit es im App-Kontext bleibt)
  - ggf. `putExtra(EXTRA_TEXT, ...)`
  - `sendBroadcast(...)`

---

## J) TTS-Manager (TtsManager)

### 39) `TtsManager.init()`
- Erstellt `new TextToSpeech(context, this)` (OnInitListener).

### 40) `TtsManager.onInit(int status)`
- Setzt Sprache (`Locale.GERMANY`, fallback `Locale.GERMAN`)
- Setzt Rate/Pitch
- Registriert `UtteranceProgressListener`:
  - `onStart()` → `speaking=true` + Callback `onStartSpeaking()`
  - `onDone()` → `speaking=false` + Callback `onDoneSpeaking()`
  - `onError()` → `speaking=false` + Callback `onErrorSpeaking()`
- Setzt `ready=true`

### 41) `TtsManager.speakFlush(String text)`
- Erzeugt `utteranceId`
- Ruft `tts.speak(text, QUEUE_FLUSH, params, utteranceId)`

### 42) `TtsManager.isReady()` / `TtsManager.isSpeaking()`
- Liefert Statusflags zurück.

### 43) `TtsManager.shutdown()`
- Stoppt TTS, `shutdown()`, setzt Flags zurück.

---

## Service Cleanup

### 44) `AstraForegroundService.onDestroy()`
- Entfernt disarm-Timer
- `stopListening()`
- `tts.shutdown()`
- `model.close()`
- `super.onDestroy()`

### 45) `AstraForegroundService.onBind(Intent intent)`
- Gibt `null` zurück (nicht gebunden).

---

## Kurzüberblick als Aufrufkette (kompakt, korrigiert)

1. `MainActivity.onCreate()`  
2. `ensurePermissionsAndStartService()` → (Permissions) → `startAstraService()`  
3. `AstraForegroundService.onCreate()` → `createNotificationChannel()` → `startInForeground()`  
4. `tts.init()` + `initModelFromAssets()`  
5. `StorageService.unpack(..., m -> { model=m; startListening(); }, e -> {...})`  
6. `startListening()` → `Recognizer` + `SpeechService.startListening(this)`  
7. `onPartialResult()` (nur ARMED) / `onResult()` / `onFinalResult()` → `handleHypothesis()`  
8. `handleCommand()` → `broadcastCommand()` + ggf. `broadcastSleepOn/Off()` + `speak(...)`  
9. UI reagiert über `astraReceiver.onReceive(...)` + `SleepModeController.enable/disable()`
