import os
import numpy as np

from retrieval_engine.feature_extractor import extract_features

DATABASE_DIR = "progression_database"
OUTPUT_DIR = "retrieval_engine/index"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for grade in range(5):

    folder = os.path.join(DATABASE_DIR, f"grade{grade}")

    feature_vectors = []
    image_paths = []

    print(f"\nProcessing Grade {grade}...")

    for file in os.listdir(folder):

        if file.endswith(".png"):

            path = os.path.join(folder, file)

            feature = extract_features(path)

            feature_vectors.append(feature)
            image_paths.append(path)

    np.save(
        os.path.join(OUTPUT_DIR, f"grade{grade}_features.npy"),
        np.array(feature_vectors)
    )

    np.save(
        os.path.join(OUTPUT_DIR, f"grade{grade}_paths.npy"),
        np.array(image_paths)
    )

    print(f"Saved {len(feature_vectors)} features.")

print("\n✅ Feature index created successfully.")