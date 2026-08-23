import numpy as np
import os
import joblib

from retrieval_engine.feature_extractor import extract_features

MODEL_PATH = "retrieval_engine/progression_model.pkl"


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise Exception("Progression model not found. Train it first.")
    return joblib.load(MODEL_PATH)


def predict_progression(image_path):

    model = load_model()

    feature = extract_features(image_path).reshape(1, -1)

    probs = model.predict_proba(feature)[0]

    current = int(np.argmax(probs))

    temp = probs.copy()
    temp[current] = -1
    next_stage = int(np.argmax(temp))

    return {
        "current_grade": current,
        "next_likely_stage": next_stage,
        "probabilities": {i: float(p) for i, p in enumerate(probs)}
    }