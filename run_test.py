import torch
import cv2

from progression_engine.pipeline import run_full_pipeline

# ------------------------
# LOAD YOUR IMAGE
# ------------------------
image_path = "test.jpg"  # put any retina image here

# ------------------------
# LOAD DEVICE
# ------------------------
device = torch.device("cpu")

# ------------------------
# LOAD MODEL (TEMP PLACEHOLDER)
# ------------------------
model = torch.nn.Sequential(
    torch.nn.Flatten(),
    torch.nn.Linear(224*224*3, 5)
)

# ------------------------
# RUN PIPELINE
# ------------------------
result = run_full_pipeline(model, image_path, device)

print("Predicted Grade:", result["grade"])
print("Probabilities:", result["probabilities"])

print("Progression images generated:", len(result["progression"]))