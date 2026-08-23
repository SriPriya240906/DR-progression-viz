import os
import cv2
import random


# -----------------------------
# LOAD DATASET STRUCTURE
# -----------------------------
class DRRetrieval:

    def __init__(self, dataset_path):

        self.dataset_path = dataset_path
        self.class_map = {0: [], 1: [], 2: [], 3: [], 4: []}

        self._load_images()


    def _load_images(self):

        print("Loading dataset for retrieval...")

        for root, _, files in os.walk(self.dataset_path):

            for file in files:

                if file.endswith(".png") or file.endswith(".jpg"):

                    path = os.path.join(root, file)

                    # infer grade from folder name
                    if "No_DR" in root:
                        self.class_map[0].append(path)
                    elif "Mild" in root:
                        self.class_map[1].append(path)
                    elif "Moderate" in root:
                        self.class_map[2].append(path)
                    elif "Severe" in root:
                        self.class_map[3].append(path)
                    elif "Proliferative" in root:
                        self.class_map[4].append(path)

        print("Dataset loaded:")
        for k, v in self.class_map.items():
            print(f"Grade {k}: {len(v)} images")


    def get_similar(self, grade, n=3):

        return random.sample(self.class_map[grade], min(n, len(self.class_map[grade])))


    def get_progression(self, grade):

        progression = []

        for g in range(grade, min(grade + 3, 5)):

            imgs = self.get_similar(g, 1)

            if imgs:
                img = cv2.imread(imgs[0])
                img = cv2.resize(img, (224, 224))
                progression.append((g, img))

        return progression