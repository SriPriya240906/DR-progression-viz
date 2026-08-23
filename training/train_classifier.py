import os
import sys
import copy
import random
import torch
import timm

from tqdm import tqdm
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader, random_split, Subset

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from preprocessing.dataset_loader import DRDataset

# -----------------------------
# Paths
# -----------------------------
CSV_PATH = os.path.join(BASE_DIR, "dataset", "train.csv")
IMAGE_DIR = os.path.join(BASE_DIR, "dataset", "train")
MODEL_PATH = os.path.join(BASE_DIR, "models", "dr_classifier.pth")

# -----------------------------
# Hyperparameters
# -----------------------------
BATCH_SIZE = 8
NUM_CLASSES = 5
EPOCHS = 2
LEARNING_RATE = 1e-4

# -----------------------------
# Load Dataset
# -----------------------------
dataset = DRDataset(
    csv_file=CSV_PATH,
    image_dir=IMAGE_DIR
)

# ------------------------------------------------
# FAST DEVELOPMENT MODE
# Use only 500 images for quick testing
# ------------------------------------------------
random.seed(42)

indices = random.sample(range(len(dataset)), 500)

dataset = Subset(dataset, indices)

# -----------------------------
# Train / Validation Split
# -----------------------------
train_size = int(0.8 * len(dataset))
valid_size = len(dataset) - train_size

train_dataset, valid_dataset = random_split(
    dataset,
    [train_size, valid_size],
    generator=torch.Generator().manual_seed(42)
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0
)

valid_loader = DataLoader(
    valid_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0
)

print("=" * 60)
print("DR-ProgressionViz")
print("=" * 60)

print(f"Training Images   : {len(train_dataset)}")
print(f"Validation Images : {len(valid_dataset)}")

# -----------------------------
# Device
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Using Device :", device)

# -----------------------------
# Load EfficientNet
# -----------------------------
model = timm.create_model(
    "efficientnet_b0",
    pretrained=True,
    num_classes=NUM_CLASSES
)

model = model.to(device)

print("Model Loaded Successfully!")

# -----------------------------
# Loss & Optimizer
# -----------------------------
criterion = nn.CrossEntropyLoss()

optimizer = Adam(
    model.parameters(),
    lr=LEARNING_RATE
)

best_accuracy = 0.0

best_weights = copy.deepcopy(model.state_dict())

# -----------------------------
# Training
# -----------------------------
for epoch in range(EPOCHS):

    print(f"\nEpoch {epoch+1}/{EPOCHS}")

    model.train()

    train_correct = 0
    train_total = 0
    train_loss = 0.0

    train_bar = tqdm(train_loader)

    for images, labels in train_bar:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        train_loss += loss.item()

        _, predicted = outputs.max(1)

        train_total += labels.size(0)

        train_correct += predicted.eq(labels).sum().item()

        train_bar.set_description(
            f"Loss {loss.item():.4f}"
        )

    train_acc = 100 * train_correct / train_total

    # -------------------------
    # Validation
    # -------------------------

    model.eval()

    valid_correct = 0
    valid_total = 0

    with torch.no_grad():

        for images, labels in tqdm(valid_loader):

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            _, predicted = outputs.max(1)

            valid_total += labels.size(0)

            valid_correct += predicted.eq(labels).sum().item()

    valid_acc = 100 * valid_correct / valid_total

    print(f"Train Accuracy      : {train_acc:.2f}%")
    print(f"Validation Accuracy : {valid_acc:.2f}%")

    if valid_acc > best_accuracy:

        best_accuracy = valid_acc

        best_weights = copy.deepcopy(model.state_dict())

# -----------------------------
# Save Model
# -----------------------------
os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)

model.load_state_dict(best_weights)

torch.save(
    model.state_dict(),
    MODEL_PATH
)

print("\n===================================")
print("Training Completed Successfully!")
print("===================================")

print(f"Best Validation Accuracy : {best_accuracy:.2f}%")
print(f"Model Saved At : {MODEL_PATH}")