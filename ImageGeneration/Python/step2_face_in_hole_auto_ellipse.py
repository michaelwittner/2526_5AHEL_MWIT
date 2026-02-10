import cv2
import numpy as np

# ============================================================
# TEMPLATE_LISTE
# Hier werden alle verwendeten PNG-Templates eingetragen.
# Jedes Template MUSS:
#  - ein PNG sein
#  - einen Alpha-Kanal besitzen
#  - ein transparentes Loch enthalten (Alpha = 0)
# ============================================================
TEMPLATE_PATHS = [
    "template.png",
    "template2.png",
    "template3.png",
]

# ============================================================
# BASELINE-EINSTELLUNGEN (bewusst fix gehalten)
# ============================================================

# Webcam-Bild wird immer gespiegelt (Selfie-Effekt)
MIRROR = True

# Skalierungsfaktoren für den Gesichtsausschnitt
# kleinere Werte -> mehr Gesicht, weniger Umfeld
FACE_SCALE_X = 1.35
FACE_SCALE_Y = 1.65

# Debug-Overlays (Ellipse, Bounding Box, Text)
DEBUG = True


# ============================================================
# FUNKTION: Loch-Erkennung über den Alpha-Kanal
# ============================================================
def find_hole_ellipse_from_alpha(template_bgra):
    # Alpha-Kanal aus dem BGRA-Bild extrahieren
    alpha = template_bgra[:, :, 3]

    # Transparente Bereiche (Alpha < 30) als Maske definieren
    hole_mask = (alpha < 30).astype(np.uint8) * 255

    # Morphologische Filter, um Störungen zu entfernen
    kernel = np.ones((7, 7), np.uint8)
    hole_mask = cv2.morphologyEx(hole_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    hole_mask = cv2.morphologyEx(hole_mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Konturen der transparenten Bereiche finden
    contours, _ = cv2.findContours(
        hole_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Falls kein Loch gefunden wird -> Abbruch
    if not contours:
        raise RuntimeError(
            "Kein transparentes Loch gefunden. "
            "Template muss ein echtes Alpha-Loch haben."
        )

    # Größte transparente Fläche als Loch verwenden
    cnt = max(contours, key=cv2.contourArea)

    # Bounding-Box des Lochs (für Debug)
    x, y, w, h = cv2.boundingRect(cnt)
    hole_bbox = (x, y, x + w, y + h)

    # Wenn genug Punkte vorhanden sind, Ellipse fitten
    if len(cnt) >= 5:
        (cx, cy), (MA, ma), angle = cv2.fitEllipse(cnt)
        center = (int(cx), int(cy))
        axes = (int(MA / 2), int(ma / 2))  # Halbachsen
        angle = float(angle)
    else:
        # Fallback: Ellipse aus Bounding Box
        center = (x + w // 2, y + h // 2)
        axes = (w // 2, h // 2)
        angle = 0.0

    return center, axes, angle, hole_bbox


# ============================================================
# FUNKTION: Gesichtsausschnitt vergrößern (weniger Zoom)
# ============================================================
def expand_rect(x, y, w, h, scale_x, scale_y, img_w, img_h):
    # Mittelpunkt des Gesicht-Rechtecks
    cx = x + w / 2.0
    cy = y + h / 2.0

    # Neue Größe mit Skalierungsfaktoren
    new_w = w * scale_x
    new_h = h * scale_y

    # Neue Koordinaten berechnen
    x0 = int(round(cx - new_w / 2.0))
    y0 = int(round(cy - new_h / 2.0))
    x1 = int(round(cx + new_w / 2.0))
    y1 = int(round(cy + new_h / 2.0))

    # Begrenzung auf Bildgröße
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(img_w, x1)
    y1 = min(img_h, y1)

    return x0, y0, x1, y1


# ============================================================
# FUNKTION: Gesicht in elliptisches Loch einsetzen
# ============================================================
def paste_face_into_ellipse(template_bgra, face_bgr, hole_center, hole_axes, hole_angle):
    out = template_bgra.copy()

    cx, cy = hole_center
    a, b = hole_axes

    # Ziel-ROI (Bounding Box der Ellipse)
    x0, y0 = cx - a, cy - b
    x1, y1 = cx + a, cy + b

    H, W = out.shape[:2]
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
        return out

    # ROI aus dem Template
    roi = out[y0:y1, x0:x1]  # BGRA

    # Gesicht auf Lochgröße skalieren
    target_w = x1 - x0
    target_h = y1 - y0
    face_resized = cv2.resize(
        face_bgr,
        (target_w, target_h),
        interpolation=cv2.INTER_LINEAR
    )

    # Ellipsenmaske erzeugen
    mask = np.zeros((target_h, target_w), dtype=np.uint8)
    cv2.ellipse(
        mask,
        center=(a, b),
        axes=(a, b),
        angle=hole_angle,
        startAngle=0,
        endAngle=360,
        color=255,
        thickness=-1
    )

    # BGR- und Alpha-Kanäle trennen
    roi_bgr = roi[:, :, :3].astype(np.float32)
    roi_a = roi[:, :, 3].copy()

    # Maske normieren (0..1)
    m = (mask.astype(np.float32) / 255.0)[..., None]

    # Alpha-Compositing (Blending)
    blended = face_resized.astype(np.float32) * m + roi_bgr * (1.0 - m)
    blended = blended.astype(np.uint8)

    # Alpha im Loch sichtbar machen
    roi_a[mask > 0] = 255

    # Ergebnis zurückschreiben
    out[y0:y1, x0:x1, :3] = blended
    out[y0:y1, x0:x1, 3] = roi_a

    return out


# ============================================================
# FUNKTION: Templates laden und vorbereiten
# ============================================================
def load_templates(paths):
    templates = []

    for p in paths:
        t = cv2.imread(p, cv2.IMREAD_UNCHANGED)

        if t is None:
            print(f"[WARN] Template nicht gefunden: {p}")
            continue

        if t.ndim != 3 or t.shape[2] != 4:
            print(f"[WARN] Template hat keinen Alpha-Kanal: {p}")
            continue

        center, axes, angle, bbox = find_hole_ellipse_from_alpha(t)

        templates.append({
            "path": p,
            "img": t,
            "center": center,
            "axes": axes,
            "angle": angle,
            "bbox": bbox
        })

        print(f"[OK] {p} geladen")

    if not templates:
        raise RuntimeError("Kein gültiges Template geladen.")

    return templates


# ============================================================
# MAIN-PROGRAMM
# ============================================================
def main():
    global FACE_SCALE_X, FACE_SCALE_Y, DEBUG

    # Templates laden
    templates = load_templates(TEMPLATE_PATHS)
    idx = 0

    # Webcam öffnen (DirectShow für Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Kamera konnte nicht geöffnet werden.")

    # Gesichtserkennung (Haar Cascade)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    win = (
        "Face in Hole | 1-4 select | n/b switch | [ ] zoom | ;/' y-zoom | "
        "d debug | p print | s shot | ESC/q"
    )
    cv2.namedWindow(win, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    set_window_size_for_template(win, templates[idx]["img"])

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Spiegelung
        if MIRROR:
            frame = cv2.flip(frame, 1)

        # Gesichtserkennung
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        t = templates[idx]
        result = t["img"].copy()

        if len(faces) > 0:
            # größtes Gesicht verwenden
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

            Hf, Wf = frame.shape[:2]
            x0, y0, x1, y1 = expand_rect(
                x, y, w, h,
                FACE_SCALE_X, FACE_SCALE_Y,
                Wf, Hf
            )

            face_roi = frame[y0:y1, x0:x1]
            result = paste_face_into_ellipse(
                result,
                face_roi,
                t["center"],
                t["axes"],
                t["angle"]
            )

        # Anzeige (ohne Alpha)
        display = result[:, :, :3].copy()

        if DEBUG:
            cv2.ellipse(display, t["center"], t["axes"], t["angle"], 0, 360, (255, 0, 0), 2)
            x0, y0, x1, y1 = t["bbox"]
            cv2.rectangle(display, (x0, y0), (x1, y1), (0, 255, 255), 1)

        cv2.imshow(win, display)

        key = cv2.waitKey(1) & 0xFF

        if key in (27, ord('q')):
            break
        elif key == ord('n'):
            idx = (idx + 1) % len(templates)
        elif key == ord('b'):
            idx = (idx - 1) % len(templates)
        elif key in (ord('1'), ord('2'), ord('3'), ord('4')):
            k = int(chr(key)) - 1
            if 0 <= k < len(templates):
                idx = k
        elif key == ord('['):
            FACE_SCALE_X = max(1.05, FACE_SCALE_X - 0.05)
            FACE_SCALE_Y = max(1.05, FACE_SCALE_Y - 0.05)
        elif key == ord(']'):
            FACE_SCALE_X += 0.05
            FACE_SCALE_Y += 0.05
        elif key == ord(';'):
            FACE_SCALE_Y = max(1.05, FACE_SCALE_Y - 0.05)
        elif key == ord("'"):
            FACE_SCALE_Y += 0.05
        elif key == ord('d'):
            DEBUG = not DEBUG
        elif key == ord('p'):
            print(FACE_SCALE_X, FACE_SCALE_Y)
        elif key == ord('s'):
            cv2.imwrite("result_screenshot.png", display)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    def set_window_size_for_template(win_name, template_bgra):
        h, w = template_bgra.shape[:2]
        cv2.resizeWindow(win_name, w, h)


    main()
