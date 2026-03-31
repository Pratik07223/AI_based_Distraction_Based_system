import os
import hashlib

def get_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def remove_duplicates(folder):
    hashes = {}
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            file_hash = get_hash(path)
            if file_hash in hashes:
                os.remove(path)
                print(f"Removed duplicate: {file}")
            else:
                hashes[file_hash] = file
        except:
            pass

folders = ["dataset/focused", "dataset/distracted", "dataset/phone"]

for f in folders:
    remove_duplicates(f)

print("✅ Duplicate cleanup done")