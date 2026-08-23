import os
import sys
import cv2
import torch
import timm
import numpy as np

from PIL import Image
from torchvision import transforms

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

# --------------------------------------------------
# Project Paths
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

MODEL_PATH = os.path.join(BASE_DIR, "models", "dr_classifier.pth")
IMAGE_PATH = os.path.join(BASE_DIR, "test_images", "000c1434d8d7.png")
OUTPUT_PATH = os.path.join(BASE_DIR, "outputs", "gradcam", "heatmap.png")

# --------------------------------------------------
# Device
# --------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --------------------------------------------------
# Load Model
# --------------------------------------------------
model = timm.create_model(
    "efficientnet_b0",
    pretrained=False,
    num_classes=5
)

model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.eval()

print("Model Loaded Successfully!")

# --------------------------------------------------
# Image Transform
# --------------------------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# --------------------------------------------------
# Load Image
# --------------------------------------------------
pil_image = Image.open(IMAGE_PATH).convert("RGB")

input_tensor = transform(pil_image).unsqueeze(0).to(device)

rgb_img = np.array(pil_image.resize((224, 224))).astype(np.float32) / 255.0

# --------------------------------------------------
# Prediction
# --------------------------------------------------
with torch.no_grad():
    output = model(input_tensor)
    prediction = torch.argmax(output, dim=1).item()

print("Predicted DR Grade:", prediction)

# --------------------------------------------------
# Grad-CAM
# --------------------------------------------------
target_layers = [model.conv_head]

cam = GradCAM(
    model=model,
    target_layers=target_layers
)

grayscale_cam = cam(input_tensor=input_tensor)[0]

visualization = show_cam_on_image(
    rgb_img,
    grayscale_cam,
    use_rgb=True
)

# --------------------------------------------------
# Save
# --------------------------------------------------
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

cv2.imwrite(
    OUTPUT_PATH,
    cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR)
)

print("Grad-CAM saved to:")
print(OUTPUT_PATH)