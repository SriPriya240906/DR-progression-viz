import os
import numpy as np

from retrieval_engine.feature_extractor import extract_features
INDEX_DIR = "retrieval_engine/index"


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def search_similar_images(image_path, top_k=5):

    query_feature = extract_features(image_path)

    similarities = []

    for grade in range(5):

        feature_file = os.path.join(INDEX_DIR, f"grade{grade}_features.npy")
        path_file = os.path.join(INDEX_DIR, f"grade{grade}_paths.npy")

        if not os.path.exists(feature_file):
            continue

        features = np.load(feature_file)
        paths = np.load(path_file)

        for feature, path in zip(features, paths):
            score = cosine_similarity(query_feature, feature)
            similarities.append((float(score), str(path)))

    similarities.sort(key=lambda x: x[0], reverse=True)

    return similarities[:top_k]