from retrieval_engine.feature_extractor import extract_features

image = "dataset/train/000c1434d8d7.png"

features = extract_features(image)

print("Feature vector shape:", features.shape)