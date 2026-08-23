import os
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from unet_autoencoder import RetinaUNet
from progression_network import ProgressionNetwork
from progression_dataset import ProgressionDataset

# ==========================================================
# Configuration
# ==========================================================
IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCHS = 10
LEARNING_RATE = 1e-4

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("=" * 60)
print("Device:", device)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
print("=" * 60)

# ==========================================================
# Dataset
# ==========================================================
dataset = ProgressionDataset(
    csv_file="dataset/train.csv",
    image_dir="dataset/train",
    image_size=IMAGE_SIZE
)

loader = DataLoader(
    dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

# ==========================================================
# Load Trained U-Net
# ==========================================================
unet = RetinaUNet().to(device)

unet.load_state_dict(
    torch.load(
        "progression_engine/retina_unet.pth",
        map_location=device
    )
)

# Freeze U-Net
for param in unet.parameters():
    param.requires_grad = False

unet.eval()

# ==========================================================
# Progression Network
# ==========================================================
progression = ProgressionNetwork().to(device)

criterion = nn.MSELoss()

optimizer = torch.optim.Adam(
    progression.parameters(),
    lr=LEARNING_RATE
)

print("\nTraining Progression Network...\n")

# ==========================================================
# Training Loop
# ==========================================================
for epoch in range(EPOCHS):

    progression.train()

    total_loss = 0

    progress_bar = tqdm(loader)

    for current, future, strength in progress_bar:

        current = current.to(device)
        future = future.to(device)
        strength = strength.to(device)

        # -------------------------
        # Encode
        # -------------------------
        with torch.no_grad():

            x1, x2, x3, x4, latent = unet.encode(current)

            _, _, _, _, future_latent = unet.encode(future)

        # -------------------------
        # Predict Future Latent
        # -------------------------
        predicted_latent = progression(
            latent,
            strength.view(-1, 1, 1, 1)
        )

        loss = criterion(
            predicted_latent,
            future_latent
        )

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

        progress_bar.set_description(
            f"Epoch {epoch+1}/{EPOCHS}"
        )

        progress_bar.set_postfix(
            Loss=f"{loss.item():.5f}"
        )

    print(
        f"Epoch {epoch+1}: "
        f"{total_loss/len(loader):.6f}"
    )

# ==========================================================
# Save Model
# ==========================================================
os.makedirs("progression_engine", exist_ok=True)

torch.save(
    progression.state_dict(),
    "progression_engine/progression_network.pth"
)

print("\nProgression Network Trained Successfully!")