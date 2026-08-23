import os
from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms

from unet_autoencoder import RetinaUNet

# ============================================================
# Dataset Location
# ============================================================
DATASET_PATH = "dataset/train"

# ============================================================
# Hyperparameters
# ============================================================
IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 5
LEARNING_RATE = 1e-4

# ============================================================
# Device
# ============================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

torch.backends.cudnn.benchmark = True

print("=" * 60)
print("Using Device:", device)

if torch.cuda.is_available():
    print("GPU :", torch.cuda.get_device_name(0))

print("=" * 60)


# ============================================================
# Dataset
# ============================================================
class RetinaDataset(Dataset):

    def __init__(self, root):

        self.images = []

        for file in os.listdir(root):
            if file.lower().endswith((".png", ".jpg", ".jpeg")):
                self.images.append(os.path.join(root, file))

        print(f"Found {len(self.images)} images.")

        if len(self.images) == 0:
            raise RuntimeError("Dataset is empty.")

        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):

        image = Image.open(self.images[idx]).convert("RGB")
        image = self.transform(image)

        return image


# ============================================================
# Main
# ============================================================
def main():

    dataset = RetinaDataset(DATASET_PATH)

    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,

        # Windows safe settings
        num_workers=0,
        pin_memory=True
    )

    print("Training Images :", len(dataset))
    print("Batches :", len(loader))

    model = RetinaUNet().to(device)

    criterion = nn.MSELoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE
    )

    scaler = torch.amp.GradScaler("cuda")

    print("\nStarting Training...\n")

    for epoch in range(EPOCHS):

        model.train()

        running_loss = 0

        progress = tqdm(
            loader,
            desc=f"Epoch {epoch+1}/{EPOCHS}"
        )

        for images in progress:

            images = images.to(
                device,
                non_blocking=True
            )

            optimizer.zero_grad()

            with torch.amp.autocast("cuda"):

                outputs = model(images)

                loss = criterion(outputs, images)

            scaler.scale(loss).backward()

            scaler.step(optimizer)

            scaler.update()

            running_loss += loss.item()

            progress.set_postfix(
                Loss=f"{loss.item():.5f}"
            )

        avg_loss = running_loss / len(loader)

        print(
            f"\nEpoch {epoch+1}/{EPOCHS} Average Loss = {avg_loss:.6f}"
        )

    os.makedirs("progression_engine", exist_ok=True)

    MODEL_PATH = "progression_engine/retina_unet.pth"

    torch.save(
        model.state_dict(),
        MODEL_PATH
    )

    print("\n" + "=" * 60)
    print("Training Completed Successfully!")
    print("Model saved to:", MODEL_PATH)
    print("=" * 60)


if __name__ == "__main__":
    main()