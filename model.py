import os
import torch
import timm
import torch.nn as nn
from torchvision import transforms
from PIL import Image

# ---------------------------------
# DEVICE
# ---------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------------
# MODEL
# ---------------------------------
model = timm.create_model("efficientnet_b0", pretrained=False)
model.classifier = nn.Linear(model.classifier.in_features, 5)

# ---------------------------------
# LOAD TRAINED MODEL
# ---------------------------------
if os.path.exists("dr_model.pth"):
    model.load_state_dict(torch.load("dr_model.pth", map_location=device))
    print("✅ Trained model loaded.")
else:
    print("⚠️ dr_model.pth not found. Using untrained model.")

model.to(device)
model.eval()

# ---------------------------------
# IMAGE TRANSFORM
# ---------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# ---------------------------------
# CLASS NAMES
# ---------------------------------
CLASS_NAMES = [
    "No DR",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative DR"
]

# ---------------------------------
# PREDICTION FUNCTION
# ---------------------------------
def predict(image_path):

    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image)
        probabilities = torch.softmax(output, dim=1)

    prediction = torch.argmax(probabilities, dim=1).item()
    confidence = probabilities[0][prediction].item() * 100  # Raw softmax probability, not calibrated confidence

    return prediction, confidence


# ---------------------------------
# DETAILED PREDICTION
# ---------------------------------
def predict_details(image_path):

    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output = model(image)
        probabilities = torch.softmax(output, dim=1)[0]

    prediction = torch.argmax(probabilities).item()
    confidence = probabilities[prediction].item() * 100  # Raw softmax probability, not calibrated confidence

    class_probabilities = {
        CLASS_NAMES[i]: round(probabilities[i].item() * 100, 2)
        for i in range(5)
    }

    return {
        "grade": prediction,
        "label": CLASS_NAMES[prediction],
        "confidence": round(confidence, 2),  # Note: This is uncalibrated prediction probability
        "probabilities": class_probabilities
    }