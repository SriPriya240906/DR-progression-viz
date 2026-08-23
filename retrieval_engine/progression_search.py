import os
import numpy as np
from retrieval_engine.feature_extractor import extract_features

INDEX_DIR = "retrieval_engine/index"


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def get_progression_map(image_path, top_k=3):

    query_feat = extract_features(image_path)

    progression_map = {}

    for grade in range(5):

        feature_file = os.path.join(INDEX_DIR, f"grade{grade}_features.npy")
        path_file = os.path.join(INDEX_DIR, f"grade{grade}_paths.npy")

        if not os.path.exists(feature_file):
            continue

        features = np.load(feature_file)
        paths = np.load(path_file)

        scores = []

        for feat, path in zip(features, paths):
            score = cosine_similarity(query_feat, feat)
            scores.append((float(score), str(path)))

        scores.sort(reverse=True, key=lambda x: x[0])

        progression_map[grade] = scores[:top_k]

    return progression_map