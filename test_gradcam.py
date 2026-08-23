import cv2

from progression_engine.gradcam import generate_gradcam

image = generate_gradcam("dataset/train/000c1434d8d7.png")

cv2.imwrite("gradcam_result.png", image)

print("GradCAM Generated Successfully!")