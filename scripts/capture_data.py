
import cv2
import os
import time

# 🔁 Change this before each run
label = "distracted"   # focused / distracted / phone

save_path = f"dataset/{label}"
os.makedirs(save_path, exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0

print(f"Capturing for class: {label}")
print("Press 's' to save | 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show label
    cv2.putText(frame, f"Class: {label}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Capture Dataset", frame)

    key = cv2.waitKey(1)

    if key == ord('s'):
        filename = f"{save_path}/{label}_{int(time.time())}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")
        count += 1

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"Total images captured: {count}")