import cv2
import numpy as np
import torch

from progression_engine.simulate_progression import generate_progression


# ----------------------------
# DR Prediction Function
# ----------------------------
def predict_grade(model, image_tensor, device):
    model.eval()
    
    with torch.no_grad():
        outputs = model(image_tensor.to(device))
        probs = torch.softmax(outputs, dim=1)
        pred = torch.argmax(probs, dim=1).item()
    
    return pred, probs.cpu().numpy()


# ----------------------------
# Grad-CAM Placeholder Hook
# (you will replace with your actual Grad-CAM code)
# ----------------------------
def get_gradcam_heatmap(model, image_tensor):
    """
    Replace this with your actual Grad-CAM implementation
    """
    # dummy heatmap for now
    heatmap = np.random.rand(224, 224)
    return heatmap


# ----------------------------
# Main Pipeline
# ----------------------------
def run_full_pipeline(model, image_path, device):

    # Step 1: Read image
    image = cv2.imread(image_path)
    image = cv2.resize(image, (224, 224))

    # Step 2: Convert to tensor
    image_tensor = torch.from_numpy(image).permute(2, 0, 1).float().unsqueeze(0) / 255.0

    # Step 3: Predict DR grade
    grade, probs = predict_grade(model, image_tensor, device)

    # Step 4: Get Grad-CAM (for future lesion guidance)
    cam = get_gradcam_heatmap(model, image_tensor)

    # Step 5: Generate progression images
    progression = generate_progression(image)

    return {
        "grade": grade,
        "probabilities": probs,
        "gradcam": cam,
        "progression": progression
    }