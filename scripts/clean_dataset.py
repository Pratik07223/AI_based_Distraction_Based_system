import os
import cv2
from PIL import Image
import imagehash

DATASET_PATH = "dataset"

def is_blurry(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var() < 80

hashes = set()

for class_name in os.listdir(DATASET_PATH):
    folder = os.path.join(DATASET_PATH, class_name)

    print(f"\nCleaning {class_name}...")

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        try:
            img = cv2.imread(path)

            # ❌ Remove invalid
            if img is None:
                os.remove(path)
                continue

            # ❌ Remove blurry
            if is_blurry(img):
                os.remove(path)
                continue

            # ❌ Remove duplicates
            h = imagehash.phash(Image.open(path))
            if h in hashes:
                os.remove(path)
                continue

            hashes.add(h)

        except:
            os.remove(path)

print("\n✅ Dataset cleaned!")