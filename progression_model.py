import numpy as np
import os
from retrieval_engine.feature_extractor import extract_features
import joblib

MODEL_PATH = "retrieval_engine/progression_model.pkl"


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise Exception("Model not trained yet")
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
        "probabilities": {i: float(probs[i]) for i in range(5)}
    }