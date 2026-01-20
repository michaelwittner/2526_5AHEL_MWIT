package com.example.tablet_assistent;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.widget.TextClock;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import androidx.core.view.WindowCompat;

public class MainActivity extends AppCompatActivity {

    private static final int REQ_RECORD_AUDIO = 1001;
    private static final int REQ_POST_NOTIFICATIONS = 1002;

    private TextClock clockCenter;
    private TextView speechTextCenter;

    private final BroadcastReceiver astraReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if (action == null) return;

            if (AstraForegroundService.ACTION_WAKE.equals(action)) {
                // Wake-Word "Astra" erkannt -> jetzt kommt gleich der Command
                showSpeechText("Astra …");
            } else if (AstraForegroundService.ACTION_COMMAND.equals(action)) {
                String cmd = intent.getStringExtra(AstraForegroundService.EXTRA_TEXT);
                if (cmd != null && !cmd.isEmpty()) {
                    showSpeechText(cmd);
                }
            } else if (AstraForegroundService.ACTION_TIMEOUT.equals(action)) {
                // Kein Command innerhalb des Fensters -> zurück zur Uhrzeit
                showClock();
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Views aus deinem Layout
        clockCenter = findViewById(R.id.clockCenter);
        speechTextCenter = findViewById(R.id.speechTextCenter);

        // Startzustand: Uhrzeit sichtbar, Sprachtext aus
        showClock();

        // Fullscreen / Immersive
        applyImmersive();

        // Permissions + Service starten
        ensurePermissionsAndStartService();
    }

    private void applyImmersive() {
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowInsetsController controller = getWindow().getInsetsController();
        if (controller != null) {
            controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
            controller.setSystemBarsBehavior(
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            );
        }
    }

    private void ensurePermissionsAndStartService() {
        // 1) RECORD_AUDIO
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_RECORD_AUDIO);
            return;
        }

        // 2) POST_NOTIFICATIONS (Android 13+), für Foreground-Service Notification sinnvoll
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_POST_NOTIFICATIONS);
                return;
            }
        }

        startAstraService();
    }

    private void startAstraService() {
        Intent i = new Intent(this, AstraForegroundService.class);
        ContextCompat.startForegroundService(this, i);
    }

    private void showSpeechText(String text) {
        if (clockCenter != null) clockCenter.setVisibility(View.GONE);
        if (speechTextCenter != null) {
            speechTextCenter.setText(text);
            speechTextCenter.setVisibility(View.VISIBLE);
        }
    }

    private void showClock() {
        if (speechTextCenter != null) {
            speechTextCenter.setText("");
            speechTextCenter.setVisibility(View.GONE);
        }
        if (clockCenter != null) clockCenter.setVisibility(View.VISIBLE);
    }

    @Override
    protected void onStart() {
        super.onStart();

        IntentFilter f = new IntentFilter();
        f.addAction(AstraForegroundService.ACTION_WAKE);
        f.addAction(AstraForegroundService.ACTION_COMMAND);
        f.addAction(AstraForegroundService.ACTION_TIMEOUT);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(astraReceiver, f, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(astraReceiver, f);
        }
    }

    @Override
    protected void onStop() {
        super.onStop();
        try {
            unregisterReceiver(astraReceiver);
        } catch (Exception ignored) {}
    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (grantResults.length == 0 || grantResults[0] != PackageManager.PERMISSION_GRANTED) {
            // Keine Statuszeilen – wir zeigen nur kurz Text in der Mitte
            showSpeechText("Permission verweigert.");
            return;
        }

        // Nach jeder erteilten Permission nochmal prüfen und dann Service starten
        ensurePermissionsAndStartService();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) {
                controller.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
            }
        }
    }
}
