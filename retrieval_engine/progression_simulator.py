import os
import numpy as np
from retrieval_engine.feature_extractor import extract_features

INDEX_DIR = "retrieval_engine/index"


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def simulate_progression(image_path):

    query = extract_features(image_path)

    progression = []

    # Go through severity stages in order
    for grade in range(5):

        feature_file = os.path.join(INDEX_DIR, f"grade{grade}_features.npy")
        path_file = os.path.join(INDEX_DIR, f"grade{grade}_paths.npy")

        if not os.path.exists(feature_file):
            continue

        features = np.load(feature_file)
        paths = np.load(path_file)

        best_score = -1
        best_img = None

        # find MOST similar image in this grade
        for feat, path in zip(features, paths):
            score = cosine(query, feat)

            if score > best_score:
                best_score = score
                best_img = path

        if best_img:
            progression.append({
                "grade": grade,
                "image": best_img,
                "score": float(best_score)
            })

    return progression