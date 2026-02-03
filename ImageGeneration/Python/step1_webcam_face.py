import cv2

def main():
    # Versuche zuerst DirectShow (stabil auf Windows)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Falls Kamera 0 nicht geht, probiere Kamera 1
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError("Kamera konnte nicht geöffnet werden. "
                           "Schließe Teams/Zoom/Browser-Kamera-Tabs und versuche es erneut.")

    # Optional: feste Auflösung (hilft manchmal)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Konnte kein Frame lesen. Kamera blockiert oder Treiberproblem.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow("Webcam Face Detect (ESC oder q)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):  # ESC oder q
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
