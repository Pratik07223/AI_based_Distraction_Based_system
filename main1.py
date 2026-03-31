import cv2
import time
from collections import deque

# 🧠 Detection
from app.detection.predict_attention import predict_attention
from app.vision.eye_tracker import get_eye_status

# 🚨 Alerts
from app.alerts.notifier import play_sound_alert
from app.alerts.voice_alert import speak_alert
from app.alerts.telegram_alert import send_telegram_alert, send_telegram_photo
from app.utils.screenshot import save_screenshot

# 📱 YOLO (optional)
try:
    from app.detection.phone_detector import detect_phone
    YOLO_AVAILABLE = True
except:
    print("⚠️ YOLO not working, fallback mode enabled")
    YOLO_AVAILABLE = False


cap = cv2.VideoCapture(0)

# 🧠 Buffers
history = deque(maxlen=10)
focus_history = deque(maxlen=30)
phone_history = deque(maxlen=30)

# ⏱️ FPS
prev_time = 0

# 🚨 Alert cooldown
last_alert_time = 0
ALERT_COOLDOWN = 10

# 🧠 Smart alert timers
distraction_start_time = None

WARNING_TIME = 10
ALERT_TIME = 30
CRITICAL_TIME = 40

frame_count = 0
phone_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # 🔍 Attention
    result = predict_attention(frame)

    # 👁️ Eye tracking
    eye_status = get_eye_status(frame)

    # 📱 YOLO phone detection (optional)
    frame_count += 1
    if YOLO_AVAILABLE and frame_count % 5 == 0:
        try:
            phone_detected = detect_phone(frame)
        except:
            phone_detected = False

    if phone_detected:
        result = "phone"

    # 🧠 Combine logic
    if eye_status == "drowsy":
        result = "drowsy"
    # elif eye_status in ["looking_left", "looking_right"]:
    #     result = "distracted"

    # 🧠 Smoothing
    history.append(result)
    final_result = max(set(history), key=history.count)

    # 📊 Focus score
    focus_history.append(1 if final_result == "focused" else 0)
    focus_score = int((sum(focus_history) / len(focus_history)) * 100)

    # 📱 Phone usage score
    phone_history.append(1 if final_result == "phone" else 0)
    phone_score = int((sum(phone_history) / len(phone_history)) * 100)

    # ⏱️ FPS
    now = time.time()
    fps = int(1 / (now - prev_time)) if prev_time != 0 else 0
    prev_time = now

    # 🖥️ DISPLAY
    cv2.putText(frame, f"Status: {final_result}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Focus Score: {focus_score}%", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.putText(frame, f"Phone Usage: {phone_score}%", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, f"FPS: {fps}", (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.putText(frame, f"Eye: {eye_status}", (10, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    # 🚨 SMART AI ALERT SYSTEM
    current_time = time.time()

    if final_result in ["distracted", "phone", "drowsy"]:

        if distraction_start_time is None:
            distraction_start_time = current_time

        elapsed = current_time - distraction_start_time

        cv2.putText(frame, f"Distraction: {int(elapsed)}s", (10, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        print(f"⚠️ {final_result} for {int(elapsed)} sec")

        # 🟡 WARNING
        if WARNING_TIME < elapsed < ALERT_TIME:
            speak_alert("distracted")

        # 🟠 ALERT
        elif ALERT_TIME < elapsed < CRITICAL_TIME:
            if current_time - last_alert_time > ALERT_COOLDOWN:
                play_sound_alert()
                speak_alert(final_result)
                last_alert_time = current_time

        # 🔴 CRITICAL
        elif elapsed > CRITICAL_TIME:
            if current_time - last_alert_time > ALERT_COOLDOWN:

                play_sound_alert()
                speak_alert(final_result)

                send_telegram_alert(f"🚨 CRITICAL: {final_result.upper()} detected!")

                image_path = save_screenshot(frame)

                if image_path:
                    send_telegram_photo(image_path)

                last_alert_time = current_time

    else:
        distraction_start_time = None

    # 🖼️ Show
    cv2.imshow("Focus Guard AI", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()