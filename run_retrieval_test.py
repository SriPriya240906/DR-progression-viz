from retrieval_engine import DRRetrieval

import cv2

dataset_path = "./dataset"

engine = DRRetrieval(dataset_path)

# simulate predicted grade
predicted_grade = 2

print("\nShowing progression:\n")

progression = engine.get_progression(predicted_grade)

for grade, img in progression:
    print("Grade:", grade)
    cv2.imwrite(f"grade_{grade}.png", img)

print("\nSaved progression images.")