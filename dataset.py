import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms


class APTOSDataset(Dataset):

    def __init__(self, csv_file, img_dir):

        self.data = pd.read_csv(csv_file)
        self.img_dir = img_dir

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])


    def __len__(self):
        return len(self.data)


    def __getitem__(self, idx):

        row = self.data.iloc[idx]

        img_path = os.path.join(self.img_dir, row["id_code"] + ".png")
        label = int(row["diagnosis"])

        image = Image.open(img_path).convert("RGB")
        image = self.transform(image)

        return image, label