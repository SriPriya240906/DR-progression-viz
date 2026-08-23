import os
import pandas as pd
from PIL import Image

import torch
from torch.utils.data import Dataset

from torchvision import transforms


class DRDataset(Dataset):

    def __init__(self, csv_file, image_dir, train=True):

        self.df = pd.read_csv(csv_file)
        self.image_dir = image_dir
        self.train = train

        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485,0.456,0.406],
                std=[0.229,0.224,0.225]
            )
        ])

    def __len__(self):
        return len(self.df)

    def __getitem__(self,index):

        row = self.df.iloc[index]

        image_path = os.path.join(
            self.image_dir,
            row["id_code"] + ".png"
        )

        image = Image.open(image_path).convert("RGB")

        image = self.transform(image)

        label = int(row["diagnosis"])

        return image,label