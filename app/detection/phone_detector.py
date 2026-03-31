import cv2
from ultralytics import YOLO

# =========================
# 🔥 LOAD MODEL (ONCE)
# =========================
model = YOLO("yolov8n.pt")   # you can switch to yolov8s.pt for better accuracy

PHONE_CLASS_ID = 67

# =========================
# ⚙️ CONFIG
# =========================
CONF_THRESHOLD = 0.5   # increase to reduce false positives
MIN_BOX_AREA = 2000    # filter very small detections


# =========================
# 📱 DETECT PHONE
# =========================
def detect_phone(frame):
    """
    Returns:
    - phone_detected (bool)
    - phone_boxes (list)
    """

    results = model(frame, conf=CONF_THRESHOLD, verbose=False)

    phone_boxes = []

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])

            if cls == PHONE_CLASS_ID:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                # 🔥 Filter small/noisy boxes
                area = (x2 - x1) * (y2 - y1)
                if area < MIN_BOX_AREA:
                    continue

                phone_boxes.append((x1, y1, x2, y2, conf))

    phone_detected = len(phone_boxes) > 0

    return phone_detected, phone_boxes


# =========================
# 🎯 DRAW BOXES (SEPARATE)
# =========================
def draw_phone_boxes(frame, phone_boxes):
    for (x1, y1, x2, y2, conf) in phone_boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.putText(
            frame,
            f"Phone {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )

    return frame