import cv2
import time
from collections import deque

from app.detection.predict_attention import predict_attention
from app.vision.eye_tracker import get_eye_status

from app.alerts.notifier import play_sound_alert
from app.alerts.voice_alert import speak_alert
from app.alerts.telegram_alert import send_telegram_alert, send_telegram_photo
from app.utils.screenshot import save_screenshot

# =========================
# YOLO PHONE DETECTION
# =========================
try:
    from app.detection.phone_detector import detect_phone, draw_phone_boxes
    YOLO_AVAILABLE = True
except:
    YOLO_AVAILABLE = False


# =========================
# CONFIG
# =========================
LANG = "en"
COOLDOWN = 6

L1 = 5
L2 = 10
L3 = 20

ENABLE_TELEGRAM = True
ENABLE_SCREENSHOT = True

CONF_THRESHOLD = 0.6   # 🆕 confidence filter


# =========================
# INIT
# =========================
cap = cv2.VideoCapture(0)

history = deque(maxlen=10)
focus_history = deque(maxlen=30)
phone_history = deque(maxlen=30)

frame_count = 0
phone_detected = False
phone_boxes = []

prev_time = 0

phone_start = None
distract_start = None

last_voice_time = 0
last_sound_time = 0
last_critical_time = 0

log_file = open("output_log.txt", "w")


# =========================
# VOICE
# =========================
def say(msg_key):
    mapping = {
        "phone": ("Please stop using phone", "कृपया मोबाइल का उपयोग बंद करें"),
        "distracted": ("Please pay attention", "कृपया ध्यान दें"),
        "focus": ("Please focus", "कृपया फोकस करें"),
        "critical_phone": ("You are using phone too long", "आप बहुत देर से मोबाइल उपयोग कर रहे हैं"),
        "critical_dist": ("You are distracted too long", "आप लंबे समय से ध्यान नहीं दे रहे हैं"),
    }

    en_text, hi_text = mapping.get(msg_key, ("Alert", "अलर्ट"))

    if LANG == "hi":
        speak_alert(hi_text)
    else:
        speak_alert(en_text)


def can_fire(last_time):
    return (time.time() - last_time) > COOLDOWN


# =========================
# MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))

    # =========================
    # MODEL (UPDATED)
    # =========================
    try:
        result, confidence = predict_attention(frame)
    except:
        result = predict_attention(frame)
        confidence = 1.0

    # 🔥 Ignore weak predictions (fix for hand/face issue)
    if confidence < CONF_THRESHOLD:
        result = "unknown"

    eye_status = get_eye_status(frame)

    # =========================
    # YOLO PHONE DETECTION
    # =========================
    frame_count += 1

    if YOLO_AVAILABLE and frame_count % 5 == 0:
        try:
            phone_detected, phone_boxes = detect_phone(frame)
        except:
            phone_detected = False
            phone_boxes = []

    if YOLO_AVAILABLE:
        frame = draw_phone_boxes(frame, phone_boxes)

    # =========================
    # FINAL DECISION (IMPROVED)
    # =========================
    if phone_detected:
        final = "phone"
    else:
        if result == "unknown":
            final = history[-1] if len(history) > 0 else "focused"
        else:
            final = result

        if eye_status == "drowsy" and confidence > 0.7:
            final = "distracted"

    # 🔥 better smoothing
    history.append(final)
    if len(history) > 5:
        final = max(set(history), key=history.count)

    # =========================
    # SCORES
    # =========================
    focus_history.append(1 if final == "focused" else 0)
    focus_score = int((sum(focus_history) / len(focus_history)) * 100)

    phone_history.append(1 if final == "phone" else 0)
    phone_score = int((sum(phone_history) / len(phone_history)) * 100)

    distract_score = 100 - focus_score

    # =========================
    # FPS
    # =========================
    now = time.time()
    fps = int(1 / (now - prev_time)) if prev_time != 0 else 0
    prev_time = now

    current_time = time.time()

    # =========================
    # PHONE ALERT
    # =========================
    if final == "phone":

        if phone_start is None:
            phone_start = current_time

        t = int(current_time - phone_start)

        cv2.putText(frame, f"Phone Time: {t}s", (10, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        if L1 <= t < L2:
            if can_fire(last_voice_time):
                say("phone")
                last_voice_time = current_time

        elif L2 <= t < L3:
            if can_fire(last_sound_time):
                play_sound_alert()
                say("phone")
                last_sound_time = current_time

        elif t >= L3:
            if can_fire(last_critical_time):
                play_sound_alert()
                say("critical_phone")

                if ENABLE_SCREENSHOT:
                    path = save_screenshot(frame)
                    if ENABLE_TELEGRAM and path:
                        send_telegram_alert(f"🚨 PHONE ALERT ({t}s)")
                        send_telegram_photo(path)

                last_critical_time = current_time

    else:
        phone_start = None

    # =========================
    # DISTRACTION ALERT
    # =========================
    if final == "distracted":

        if distract_start is None:
            distract_start = current_time

        t = int(current_time - distract_start)

        cv2.putText(frame, f"Distracted: {t}s", (10, 280),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if L1 <= t < L2:
            if can_fire(last_voice_time):
                say("distracted")
                last_voice_time = current_time

        elif L2 <= t < L3:
            if can_fire(last_sound_time):
                play_sound_alert()
                say("focus")
                last_sound_time = current_time

        elif t >= L3:
            if can_fire(last_critical_time):
                play_sound_alert()
                say("critical_dist")

                if ENABLE_SCREENSHOT:
                    path = save_screenshot(frame)
                    if ENABLE_TELEGRAM and path:
                        send_telegram_alert(f"🚨 DISTRACTION ALERT ({t}s)")
                        send_telegram_photo(path)

                last_critical_time = current_time

    else:
        distract_start = None

    # =========================
    # DISPLAY
    # =========================
    cv2.putText(frame, f"Status: {final}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Focus: {focus_score}%", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.putText(frame, f"Phone: {phone_score}%", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, f"Distracted Score: {distract_score}%", (10, 160),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.putText(frame, f"FPS: {fps}", (10, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    log_file.write(
        f"{time.strftime('%H:%M:%S')} | {final} | "
        f"Focus:{focus_score}% | Phone:{phone_score}%\n"
    )

    cv2.imshow("Focus Guard AI", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
log_file.close()