package com.example.tablet_assistent;

import android.annotation.SuppressLint;
import android.media.AudioFormat;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.util.Log;

public class MicInput {

    private static final String TAG = "MicInput";
    private static final int SAMPLE_RATE = 16000; // ideal für Vosk später
    private static final int CHANNEL = AudioFormat.CHANNEL_IN_MONO;
    private static final int ENCODING = AudioFormat.ENCODING_PCM_16BIT;

    private AudioRecord audioRecord;
    private Thread thread;
    private volatile boolean running = false;

    @SuppressLint("MissingPermission")
    public void start() {
        if (running) return;

        int minBuf = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL, ENCODING);
        if (minBuf <= 0) {
            Log.e(TAG, "getMinBufferSize Fehler: " + minBuf);
            return;
        }

        audioRecord = new AudioRecord(
                MediaRecorder.AudioSource.VOICE_RECOGNITION,
                SAMPLE_RATE,
                CHANNEL,
                ENCODING,
                minBuf * 2
        );

        if (audioRecord.getState() != AudioRecord.STATE_INITIALIZED) {
            Log.e(TAG, "AudioRecord nicht initialisiert.");
            return;
        }

        audioRecord.startRecording();
        running = true;

        thread = new Thread(() -> {
            short[] buffer = new short[minBuf / 2];
            Log.i(TAG, "Audio capture gestartet.");

            while (running) {
                int read = audioRecord.read(buffer, 0, buffer.length);
                if (read > 0) {
                    // Mini-Test: RMS Lautstärke ins Logcat
                    double sum = 0;
                    for (int i = 0; i < read; i++) {
                        double v = buffer[i];
                        sum += v * v;
                    }
                    double rms = Math.sqrt(sum / read);
                    Log.d(TAG, "rms=" + (int) rms);
                }
            }

            Log.i(TAG, "Audio capture gestoppt.");
        }, "MicInputThread");

        thread.start();
    }

    public void stop() {
        running = false;

        if (audioRecord != null) {
            try { audioRecord.stop(); } catch (Exception ignored) {}
            try { audioRecord.release(); } catch (Exception ignored) {}
            audioRecord = null;
        }

        if (thread != null) {
            try { thread.join(300); } catch (InterruptedException ignored) {}
            thread = null;
        }
    }
}
