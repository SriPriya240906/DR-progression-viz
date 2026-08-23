import os
from PIL import Image

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from autoencoder import RetinaAutoencoder


# -----------------------------
# CHANGE THIS TO YOUR DATASET
# -----------------------------
DATASET_PATH = r"dataset/train"


# -----------------------------
# Dataset
# -----------------------------
class RetinaDataset(Dataset):

    def __init__(self, root):

        self.images = []

        for folder in os.listdir(root):

            folder_path = os.path.join(root, folder)

            if os.path.isdir(folder_path):

                for file in os.listdir(folder_path):

                    if file.lower().endswith((".png", ".jpg", ".jpeg")):

                        self.images.append(
                            os.path.join(folder_path, file)
                        )

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):

        img = Image.open(self.images[index]).convert("RGB")

        img = self.transform(img)

        return img


# -----------------------------
# Device
# -----------------------------
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using:", device)


# -----------------------------
# Dataset
# -----------------------------
dataset = RetinaDataset(DATASET_PATH)

loader = DataLoader(
    dataset,
    batch_size=16,
    shuffle=True
)


# -----------------------------
# Model
# -----------------------------
model = RetinaAutoencoder().to(device)

criterion = nn.MSELoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=0.001
)


# -----------------------------
# Training
# -----------------------------
EPOCHS = 20

for epoch in range(EPOCHS):

    total_loss = 0

    for images in loader:

        images = images.to(device)

        outputs = model(images)

        loss = criterion(outputs, images)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    print(
        f"Epoch {epoch+1}/{EPOCHS}  Loss: {total_loss/len(loader):.5f}"
    )


# -----------------------------
# Save
# -----------------------------
torch.save(
    model.state_dict(),
    "progression_engine/retina_autoencoder.pth"
)

print("\nAutoencoder trained successfully!")
print("Saved as:")
print("progression_engine/retina_autoencoder.pth")