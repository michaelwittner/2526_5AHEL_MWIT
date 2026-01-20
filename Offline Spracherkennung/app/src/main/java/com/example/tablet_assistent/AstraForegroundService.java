package com.example.tablet_assistent;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;

import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;

import org.json.JSONObject;
import org.vosk.LibVosk;
import org.vosk.LogLevel;
import org.vosk.Model;
import org.vosk.Recognizer;
import org.vosk.android.RecognitionListener;
import org.vosk.android.SpeechService;
import org.vosk.android.StorageService;

import java.io.IOException;

public class AstraForegroundService extends Service implements RecognitionListener {

    // Broadcasts (UI hört nur darauf, wenn sie offen ist)
    public static final String ACTION_WAKE = "com.example.tablet_assistent.ACTION_WAKE";
    public static final String ACTION_COMMAND = "com.example.tablet_assistent.ACTION_COMMAND";
    public static final String ACTION_TIMEOUT = "com.example.tablet_assistent.ACTION_TIMEOUT";

    public static final String EXTRA_TEXT = "text";
    public static final String EXTRA_TRIGGER = "trigger";

    private static final String CHANNEL_ID = "astra_listen";
    private static final int NOTIF_ID = 1001;

    private static final String WAKE_WORD = "astra";

    // Gate-Logik
    private enum State { IDLE, ARMED }
    private State state = State.IDLE;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private Runnable disarmRunnable;

    private static final long ARMED_MS = 7000;     // nach "Astra" hast du 7s für den Command
    private static final long WAKE_COOLDOWN_MS = 1500;

    private long lastWakeMs = 0;

    // Vosk
    private Model model;
    private SpeechService speechService;

    @Override
    public void onCreate() {
        super.onCreate();

        // Weniger internes Logging
        LibVosk.setLogLevel(LogLevel.INFO);

        createNotificationChannel();
        startForeground(NOTIF_ID, buildNotification("Initialisiere Astra…"));

        initModelFromAssets();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Damit Android versucht den Service wieder zu starten, falls er beendet wird
        return START_STICKY;
    }

    private void initModelFromAssets() {
        // assets/vosk-model-small-de-0.15  -> wird nach app-interner Storage entpackt
        StorageService.unpack(
                this,
                "vosk-model-small-de-0.15",
                "vosk-model-de",
                model -> {
                    this.model = model;
                    startListening();
                    updateNotification("Astra hört zu (offline)…");
                },
                exception -> updateNotification("Model-Fehler: " + exception.getMessage())
        );
    }

    private void startListening() {
        try {
            Recognizer recognizer = new Recognizer(model, 16000.0f);
            speechService = new SpeechService(recognizer, 16000.0f);
            speechService.startListening(this);
        } catch (IOException e) {
            updateNotification("Start-Fehler: " + e.getMessage());
        }
    }

    private void stopListening() {
        if (speechService != null) {
            speechService.stop();
            speechService.shutdown();
            speechService = null;
        }
    }

    // ===== RecognitionListener =====

    @Override
    public void onPartialResult(String hypothesis) {
        // WICHTIG: Ignorieren -> kein Spam (partial kommt extrem oft)
    }

    @Override
    public void onResult(String hypothesis) {
        // optional: nicht nötig
    }

    @Override
    public void onFinalResult(String hypothesis) {
        String text = extractText(hypothesis);
        if (text.isEmpty()) return;

        String norm = normalize(text);

        long now = System.currentTimeMillis();

        if (state == State.IDLE) {
            // Nur auf Wake-Word reagieren
            if (norm.contains(WAKE_WORD) && (now - lastWakeMs) > WAKE_COOLDOWN_MS) {
                lastWakeMs = now;
                arm();
                broadcastWake();
            }
            return;
        }

        // state == ARMED: Nächster finaler Satz ist der Command
        String command = removeWakeWord(norm).trim();
        if (command.isEmpty()) {
            // Falls jemand nur "Astra" sagt: armed bleibt bis Timeout
            return;
        }

        disarm();
        broadcastCommand(command);

        // Beispiel-Keywords (kannst du erweitern)
        if (command.contains("aufwachen")) {
            // TODO: später Routine (z.B. Uhrzeit/Datum ansagen)
        } else if (command.contains("gute nacht")) {
            // TODO: später Bildschirm abdunkeln (in-App)
        }
    }

    @Override
    public void onError(Exception e) {
        updateNotification("ASR-Fehler: " + e.getMessage());
        // defensiv neu starten
        restartListening();
    }

    @Override
    public void onTimeout() {
        // defensiv neu starten
        restartListening();
    }

    private void restartListening() {
        stopListening();
        if (model != null) startListening();
    }

    // ===== Gate / State =====

    private void arm() {
        state = State.ARMED;
        updateNotification("Astra bereit… (sprich deinen Befehl)");
        if (disarmRunnable != null) handler.removeCallbacks(disarmRunnable);
        disarmRunnable = () -> {
            disarm();
            broadcastTimeout();
        };
        handler.postDelayed(disarmRunnable, ARMED_MS);
    }

    private void disarm() {
        state = State.IDLE;
        updateNotification("Astra hört zu (offline)…");
        if (disarmRunnable != null) handler.removeCallbacks(disarmRunnable);
        disarmRunnable = null;
    }

    // ===== Broadcast helpers =====

    private void broadcastWake() {
        Intent i = new Intent(ACTION_WAKE);
        i.setPackage(getPackageName());
        sendBroadcast(i);
    }

    private void broadcastCommand(String command) {
        Intent i = new Intent(ACTION_COMMAND);
        i.setPackage(getPackageName());
        i.putExtra(EXTRA_TEXT, command);
        sendBroadcast(i);
    }

    private void broadcastTimeout() {
        Intent i = new Intent(ACTION_TIMEOUT);
        i.setPackage(getPackageName());
        sendBroadcast(i);
    }

    // ===== JSON extract / normalize =====

    private String extractText(String hypothesis) {
        try {
            JSONObject json = new JSONObject(hypothesis);
            return json.optString("text", "").trim();
        } catch (Exception ignored) {
            return "";
        }
    }

    private String normalize(String s) {
        return s.toLowerCase()
                .replace("ä", "ae")
                .replace("ö", "oe")
                .replace("ü", "ue")
                .replace("ß", "ss")
                .trim();
    }

    private String removeWakeWord(String s) {
        // entfernt nur das erste Vorkommen von "astra"
        int idx = s.indexOf(WAKE_WORD);
        if (idx < 0) return s;
        String before = s.substring(0, idx).trim();
        String after = s.substring(idx + WAKE_WORD.length()).trim();
        return (before + " " + after).trim();
    }

    // ===== Notification =====

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel ch = new NotificationChannel(
                    CHANNEL_ID,
                    "Astra Offline Spracherkennung",
                    NotificationManager.IMPORTANCE_LOW
            );
            ch.setDescription("Läuft im Hintergrund, damit Keywords erkannt werden.");
            NotificationManager nm = getSystemService(NotificationManager.class);
            if (nm != null) nm.createNotificationChannel(ch);
        }
    }

    private Notification buildNotification(String text) {
        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle("Tablet_Assistent")
                .setContentText(text)
                .setOngoing(true)
                .build();
    }

    private void updateNotification(String text) {
        NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (nm != null) nm.notify(NOTIF_ID, buildNotification(text));
    }

    @Override
    public void onDestroy() {
        disarm();
        stopListening();
        if (model != null) {
            model.close();
            model = null;
        }
        super.onDestroy();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
