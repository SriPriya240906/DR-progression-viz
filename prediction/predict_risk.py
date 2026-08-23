import os
import sys
import json
import torch
import timm

from PIL import Image
from torchvision import transforms

# ---------------------------------------
# Project Paths
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

MODEL_PATH = os.path.join(BASE_DIR, "models", "dr_classifier.pth")
RISK_PATH = os.path.join(BASE_DIR, "models", "risk_model", "risk_model.json")
IMAGE_PATH = os.path.join(BASE_DIR, "test_images", "000c1434d8d7.png")

# ---------------------------------------
# Device
# ---------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------------------
# Load Model
# ---------------------------------------
model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=5
)

model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

# ---------------------------------------
# Image Transform
# ---------------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

image = Image.open(IMAGE_PATH).convert("RGB")
image = transform(image).unsqueeze(0).to(device)

# ---------------------------------------
# Prediction
# ---------------------------------------
with torch.no_grad():
    output = model(image)
    prediction = torch.argmax(output, dim=1).item()

# ---------------------------------------
# Load Risk Model
# ---------------------------------------
with open(RISK_PATH, "r") as f:
    risk_model = json.load(f)

risk = risk_model[str(prediction)]

# ---------------------------------------
# Print Report
# ---------------------------------------
print("=" * 50)
print("DR Progression Risk Assessment")
print("=" * 50)

print(f"\nPredicted Grade : {risk['grade']}")

print("\nEstimated Progression Risk")
print("---------------------------")
print(f"1 Year : {risk['risk']['1_year']}")
print(f"2 Years: {risk['risk']['2_year']}")
print(f"3 Years: {risk['risk']['3_year']}")