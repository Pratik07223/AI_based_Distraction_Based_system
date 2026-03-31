import cv2
import mediapipe as mp

# 🧪 Debug (remove later if you want)
print("MediaPipe path:", mp.__file__)
print("Has solutions:", hasattr(mp, "solutions"))

# ❗ Safety check (prevents crash)
if not hasattr(mp, "solutions"):
    raise ImportError(
        "❌ mediapipe is not installed correctly OR wrong environment is active.\n"
        "👉 Activate venv310 and reinstall mediapipe."
    )

# ✅ Initialize MediaPipe properly
mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

def crop_face(frame):
    """
    Detects and crops the face from a frame.
    Returns cropped face if detected, otherwise returns original frame.
    """

    if frame is None:
        return frame

    h, w, _ = frame.shape

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face
    results = face_detector.process(rgb_frame)

    if results and results.detections:
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box

        # Convert to pixel values
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        bw = int(bbox.width * w)
        bh = int(bbox.height * h)

        # ✅ Boundary protection
        x = max(0, x)
        y = max(0, y)
        bw = min(w - x, bw)
        bh = min(h - y, bh)

        face = frame[y:y+bh, x:x+bw]

        if face is not None and face.size > 0:
            return face

    # 🔁 fallback
    return frame