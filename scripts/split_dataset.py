import os
import shutil
import random

# 📁 Source dataset
SOURCE_DIR = "dataset"

# 📁 Destination
DEST_DIR = "dataset_clean"

TRAIN_RATIO = 0.8  # 80% train

# Create folders
for split in ["train", "val"]:
    for class_name in os.listdir(SOURCE_DIR):
        path = os.path.join(DEST_DIR, split, class_name)
        os.makedirs(path, exist_ok=True)

# Process each class
for class_name in os.listdir(SOURCE_DIR):

    class_path = os.path.join(SOURCE_DIR, class_name)

    if not os.path.isdir(class_path):
        continue

    images = os.listdir(class_path)
    random.shuffle(images)

    split_index = int(len(images) * TRAIN_RATIO)

    train_images = images[:split_index]
    val_images = images[split_index:]

    # Copy files
    for img in train_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(DEST_DIR, "train", class_name, img)
        shutil.copy(src, dst)

    for img in val_images:
        src = os.path.join(class_path, img)
        dst = os.path.join(DEST_DIR, "val", class_name, img)
        shutil.copy(src, dst)

    print(f"✅ {class_name}: {len(train_images)} train, {len(val_images)} val")

print("🎉 Dataset split complete!")