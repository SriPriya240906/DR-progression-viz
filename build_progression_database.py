import os
import shutil
import pandas as pd

# -----------------------------
# PATHS
# -----------------------------
CSV_PATH = "dataset/train.csv"
IMAGE_FOLDER = "dataset/train"
OUTPUT_FOLDER = "progression_database"

# -----------------------------
# CREATE OUTPUT FOLDERS
# -----------------------------
for grade in range(5):
    os.makedirs(os.path.join(OUTPUT_FOLDER, f"grade{grade}"), exist_ok=True)

# -----------------------------
# READ CSV
# -----------------------------
df = pd.read_csv(CSV_PATH)

print(f"Found {len(df)} images")

# -----------------------------
# COPY IMAGES
# -----------------------------
copied = 0

for _, row in df.iterrows():

    image_id = row["id_code"]
    grade = int(row["diagnosis"])

    src = os.path.join(IMAGE_FOLDER, image_id + ".png")
    dst = os.path.join(
        OUTPUT_FOLDER,
        f"grade{grade}",
        image_id + ".png"
    )

    if os.path.exists(src):
        shutil.copy2(src, dst)
        copied += 1

print(f"\nSuccessfully copied {copied} images.")
print("\nProgression database created successfully!")