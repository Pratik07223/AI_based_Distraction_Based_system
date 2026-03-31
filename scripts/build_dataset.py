import os
import cv2
import random
from icrawler.builtin import GoogleImageCrawler

# =========================
# 📁 CONFIG
# =========================
DATASET_PATH = "dataset"

CLASSES = {
    "focused": [
        "person working laptop front face",
        "student studying focused face"
    ],
    "distracted": [
        "person looking away side face",
        "student distracted not paying attention"
    ],
    "phone": [
        "person using phone looking down face",
        "student using mobile phone front face"
    ]
}

IMAGES_PER_CLASS = 300

# =========================
# 🚀 STEP 1: DOWNLOAD IMAGES
# =========================
def download_images():
    print("📥 Downloading images...")

    for cls, keywords in CLASSES.items():

        save_path = os.path.join(DATASET_PATH, cls)
        os.makedirs(save_path, exist_ok=True)

        crawler = GoogleImageCrawler(storage={'root_dir': save_path})

        for keyword in keywords:
            crawler.crawl(keyword=keyword, max_num=IMAGES_PER_CLASS // len(keywords))

    print("✅ Download complete!")


# =========================
# 🧹 STEP 2: CLEAN DATA
# =========================
def clean_images():
    print("🧹 Cleaning dataset...")

    for cls in os.listdir(DATASET_PATH):
        class_path = os.path.join(DATASET_PATH, cls)

        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)

            try:
                img = cv2.imread(img_path)

                if img is None:
                    os.remove(img_path)
                    continue

                h, w = img.shape[:2]

                if h < 100 or w < 100:
                    os.remove(img_path)

            except:
                os.remove(img_path)

    print("✅ Cleaning done!")


# =========================
# 👤 STEP 3: FILTER FACE ONLY
# =========================
def filter_faces():
    print("👤 Filtering only face images...")

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    for cls in os.listdir(DATASET_PATH):
        class_path = os.path.join(DATASET_PATH, cls)

        for img_name in os.listdir(class_path):
            img_path = os.path.join(class_path, img_name)

            img = cv2.imread(img_path)
            if img is None:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                os.remove(img_path)

    print("✅ Only face images kept!")


# =========================
# ⚖️ STEP 4: BALANCE DATASET
# =========================
def balance_dataset():
    print("⚖️ Balancing dataset...")

    counts = {}
    for cls in os.listdir(DATASET_PATH):
        counts[cls] = len(os.listdir(os.path.join(DATASET_PATH, cls)))

    min_count = min(counts.values())

    for cls in os.listdir(DATASET_PATH):
        class_path = os.path.join(DATASET_PATH, cls)
        images = os.listdir(class_path)

        random.shuffle(images)

        for img in images[min_count:]:
            os.remove(os.path.join(class_path, img))

    print("✅ Dataset balanced!")


# =========================
# 🚀 RUN ALL
# =========================
if __name__ == "__main__":
    download_images()
    clean_images()
    filter_faces()
    balance_dataset()

    print("\n🎉 DATASET READY FOR TRAINING!")