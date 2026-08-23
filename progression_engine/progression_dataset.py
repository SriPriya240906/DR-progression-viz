import os
import random
import pandas as pd
from PIL import Image

import torch
from torch.utils.data import Dataset
from torchvision import transforms


class ProgressionDataset(Dataset):

    def __init__(
        self,
        csv_file="dataset/train.csv",
        image_dir="dataset/train",
        image_size=128
    ):

        self.image_dir = image_dir

        self.df = pd.read_csv(csv_file)

        # APTOS column names
        self.df = self.df[self.df["diagnosis"] < 4]

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor()
        ])

        # Group images by DR grade
        self.grade_dict = {}

        for grade in range(5):

            ids = self.df[self.df["diagnosis"] == grade]["id_code"].tolist()

            self.grade_dict[grade] = ids

        # Create progression pairs
        self.samples = []

        for grade in range(4):

            current_images = self.grade_dict[grade]
            next_images = self.grade_dict.get(grade + 1, [])

            if len(next_images) == 0:
                continue

            for img in current_images:

                target = random.choice(next_images)

                self.samples.append((img, target, grade))

        print(f"Created {len(self.samples)} progression pairs.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        current_img, future_img, grade = self.samples[index]

        current_path = os.path.join(
            self.image_dir,
            current_img + ".png"
        )

        future_path = os.path.join(
            self.image_dir,
            future_img + ".png"
        )

        current = Image.open(current_path).convert("RGB")
        future = Image.open(future_path).convert("RGB")

        current = self.transform(current)
        future = self.transform(future)

        strength = torch.tensor(
            [(grade + 1) / 5.0],
            dtype=torch.float32
        )

        return current, future, strength