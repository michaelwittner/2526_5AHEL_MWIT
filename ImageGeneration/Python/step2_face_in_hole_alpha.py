import cv2
import numpy as np

TEMPLATE_PATH = "template.png"

# Startwerte (egal, du kalibrierst per Klick)
HOLE_CENTER = [520, 560]   # als Liste, damit wir live ändern können
HOLE_RADIUS = 110


def paste_face_bgra(template_bgra, face_bgr, center, radius):
    out = template_bgra.copy()
    cx, cy = int(center[0]), int(center[1])
    r = int(radius)

    x0, y0 = cx - r, cy - r
    x1, y1 = cx + r, cy + r

    H, W = out.shape[:2]
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
        return out

    hole_w, hole_h = x1 - x0, y1 - y0
    face_resized = cv2.resize(face_bgr, (hole_w, hole_h), interpolation=cv2.INTER_LINEAR)

    # Kreis-Maske
    mask = np.zeros((hole_h, hole_w), dtype=np.uint8)
    cv2.circle(mask, (r, r), r, 255, -1)

    roi = out[y0:y1, x0:x1]           # BGRA
    roi_bgr = roi[:, :, :3].copy()
    roi_a = roi[:, :, 3].copy()

    m = (mask.astype(np.float32) / 255.0)[..., None]
    blended_bgr = face_resized.astype(np.float32) * m + roi_bgr.astype(np.float32) * (1.0 - m)
    blended_bgr = blended_bgr.astype(np.uint8)

    new_a = roi_a.copy()
    new_a[mask > 0] = 255

    out[y0:y1, x0:x1, :3] = blended_bgr
    out[y0:y1, x0:x1, 3] = new_a
    return out


def main():
    global HOLE_CENTER, HOLE_RADIUS

    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
    if template is None:
        raise RuntimeError(f"Template nicht gefunden: {TEMPLATE_PATH}")
    if template.ndim != 3 or template.shape[2] != 4:
        raise RuntimeError("template.png hat kein Alpha. Bitte als PNG mit Transparenz exportieren.")

    # Kamera (Windows stabil)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Kamera konnte nicht geöffnet werden.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    win = "Calibrate Face in Hole (Klick=set center | +/- radius | Arrows move | S=print | ESC/q)"
    cv2.namedWindow(win)

    # Maus: Linksklick setzt das Zentrum
    def on_mouse(event, x, y, flags, param):
        nonlocal template
        if event == cv2.EVENT_LBUTTONDOWN:
            HOLE_CENTER[0] = x
            HOLE_CENTER[1] = y

    cv2.setMouseCallback(win, on_mouse)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        result = template.copy()

        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_roi = frame[y:y+h, x:x+w]
            result = paste_face_bgra(result, face_roi, HOLE_CENTER, HOLE_RADIUS)

        # Anzeige: BGR-Kopie + Debug-Kreis/Infos
        display = result[:, :, :3].copy()
        cv2.circle(display, (int(HOLE_CENTER[0]), int(HOLE_CENTER[1])), int(HOLE_RADIUS), (255, 0, 0), 2)
        cv2.circle(display, (int(HOLE_CENTER[0]), int(HOLE_CENTER[1])), 2, (255, 0, 0), -1)

        info = f"center=({HOLE_CENTER[0]},{HOLE_CENTER[1]})  radius={HOLE_RADIUS}"
        cv2.putText(display, info, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(win, display)

        key = cv2.waitKey(1) & 0xFF

        # Exit
        if key in (27, ord('q')):  # ESC oder q
            break

        # Radius
        elif key in (ord('+'), ord('=')):  # + (oft = ohne shift)
            HOLE_RADIUS += 2
        elif key in (ord('-'), ord('_')):
            HOLE_RADIUS = max(10, HOLE_RADIUS - 2)

        # Werte ausgeben (zum Copy/Paste)
        elif key in (ord('s'), ord('S')):
            print(f"HOLE_CENTER = ({HOLE_CENTER[0]}, {HOLE_CENTER[1]})")
            print(f"HOLE_RADIUS = {HOLE_RADIUS}")

        # Pfeiltasten: OpenCV liefert oft 81/82/83/84 oder 0/224 + code je nach System.
        # Wir fangen die häufigsten ab:
        elif key in (81, 2424832):   # left
            HOLE_CENTER[0] -= 1
        elif key in (83, 2555904):   # right
            HOLE_CENTER[0] += 1
        elif key in (82, 2490368):   # up
            HOLE_CENTER[1] -= 1
        elif key in (84, 2621440):   # down
            HOLE_CENTER[1] += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
