import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

INDEX_DIR = "retrieval_engine/index"

X = []
y = []

for grade in range(5):

    feat_path = os.path.join(INDEX_DIR, f"grade{grade}_features.npy")

    if not os.path.exists(feat_path):
        continue

    features = np.load(feat_path)

    for f in features:
        X.append(f)
        y.append(grade)

X = np.array(X)
y = np.array(y)

print("Training progression model...")
print("Samples:", len(X))

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "retrieval_engine/progression_model.pkl")

print("Model saved successfully!")