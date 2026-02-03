import cv2
import numpy as np

TEMPLATE_PATH = "template.png"  # dein Bild mit Loch

# HIER anpassen:
HOLE_CENTER = (320, 240)  # (x, y) im Template
HOLE_RADIUS = 90          # Radius in Pixeln


def paste_face_into_template(template_bgr, face_bgr, center, radius):
    out = template_bgr.copy()

    x0 = center[0] - radius
    y0 = center[1] - radius
    x1 = center[0] + radius
    y1 = center[1] + radius

    h, w = out.shape[:2]
    if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
        return out

    hole_w = x1 - x0
    hole_h = y1 - y0

    face_resized = cv2.resize(face_bgr, (hole_w, hole_h), interpolation=cv2.INTER_LINEAR)

    # Kreis-Maske
    mask = np.zeros((hole_h, hole_w), dtype=np.uint8)
    cv2.circle(mask, (radius, radius), radius, 255, -1)

    roi = out[y0:y1, x0:x1]

    mask_f = (mask.astype(np.float32) / 255.0)[..., None]
    blended = face_resized.astype(np.float32) * mask_f + roi.astype(np.float32) * (1.0 - mask_f)

    out[y0:y1, x0:x1] = blended.astype(np.uint8)
    return out


def main():
    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_COLOR)
    if template is None:
        raise RuntimeError(f"Template nicht gefunden: {TEMPLATE_PATH}")

    # Kamera (DirectShow, wie vorher)
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

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        result = template.copy()

        if len(faces) > 0:
            # größtes Gesicht nehmen
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            face_roi = frame[y:y+h, x:x+w]
            result = paste_face_into_template(result, face_roi, HOLE_CENTER, HOLE_RADIUS)

        # Debug-Kreis, damit du Position/Radius einstellen kannst
        cv2.circle(result, HOLE_CENTER, HOLE_RADIUS, (255, 0, 0), 2)

        cv2.imshow("Face in Hole (ESC oder q)", result)
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
