import cv2
import os
import random
from progression_engine.simulate_progression import generate_progression


print("Searching dataset images...")

dataset_path = r".\dataset"

image_paths = []

for root, dirs, files in os.walk(dataset_path):
    for file in files:
        if file.lower().endswith(".png"):
            image_paths.append(os.path.join(root, file))

if len(image_paths) == 0:
    raise Exception("No images found in dataset folder")

image_path = random.choice(image_paths)

print("Using image:", image_path)


image = cv2.imread(image_path)

if image is None:
    raise Exception("Failed to read image")

image = cv2.resize(image, (224, 224))


print("Generating progression...")

progression = generate_progression(image)

print("Done! Stages:", len(progression))


for i, img in enumerate(progression):
    cv2.imwrite(f"year_{i}.png", img)

print("Saved year_0.png to year_3.png")