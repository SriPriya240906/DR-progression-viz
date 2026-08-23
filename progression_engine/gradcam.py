import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

from model import model, device

# ---------------------------------
# IMAGE TRANSFORM
# ---------------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# ---------------------------------
# TARGET LAYER
# EfficientNet-B0 last convolution block
# ---------------------------------
target_layers = [model.conv_head]

# ---------------------------------
# GENERATE GRADCAM
# ---------------------------------
def generate_gradcam(image_path):

    pil_image = Image.open(image_path).convert("RGB")

    rgb_img = np.array(pil_image.resize((224,224))).astype(np.float32)/255.0

    input_tensor = transform(pil_image).unsqueeze(0).to(device)

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

    return visualization