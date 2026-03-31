import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance

# 🔥 Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)

# 👁️ Eye landmark indices (MediaPipe)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# 👃 Nose landmark
NOSE_INDEX = 1


# 👁️ Eye Aspect Ratio (EAR)
def eye_aspect_ratio(landmarks, eye_indices, w, h):
    points = []

    for i in eye_indices:
        x = int(landmarks[i].x * w)
        y = int(landmarks[i].y * h)
        points.append((x, y))

    # vertical distances
    A = distance.euclidean(points[1], points[5])
    B = distance.euclidean(points[2], points[4])

    # horizontal distance
    C = distance.euclidean(points[0], points[3])

    if C == 0:
        return 0

    ear = (A + B) / (2.0 * C)
    return ear


# 🧠 Main function
def get_eye_status(frame):
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        return "no_face"

    for face_landmarks in results.multi_face_landmarks:
        landmarks = face_landmarks.landmark

        # 👁️ Calculate EAR
        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE, w, h)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE, w, h)

        ear = (left_ear + right_ear) / 2.0

        # 😴 DROWSINESS CHECK
        if ear < 0.20:
            return "drowsy"

        # 👁️ EYE DIRECTION (using nose position)
        nose_x = landmarks[NOSE_INDEX].x

        if nose_x < 0.4:
            return "looking_left"
        elif nose_x > 0.6:
            return "looking_right"
        else:
            return "focused"

    return "unknown"