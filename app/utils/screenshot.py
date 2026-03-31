import cv2
import os
import time
import datetime

# 📁 Folder to store screenshots
SAVE_FOLDER = "alerts"

# ✅ Create folder if not exists
os.makedirs(SAVE_FOLDER, exist_ok=True)


def save_screenshot(frame):
    """
    Save screenshot with timestamp
    Returns file path
    """

    if frame is None:
        print("❌ No frame to save")
        return None

    # 🕒 Timestamp for filename
    timestamp = int(time.time())

    # 🕒 Readable time for image text
    readable_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 🖊️ Add timestamp on image
    cv2.putText(
        frame,
        readable_time,
        (10, 450),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    # 📁 File path
    file_path = os.path.join(SAVE_FOLDER, f"alert_{timestamp}.jpg")

    # 💾 Save image
    success = cv2.imwrite(file_path, frame)

    if success:
        print(f"📸 Screenshot saved: {file_path}")
        return file_path
    else:
        print("❌ Failed to save screenshot")
        return None