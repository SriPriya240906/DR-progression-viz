import torch
import torch.nn as nn
import torch.optim as optim
import timm

from torch.utils.data import DataLoader, random_split

from dataset import APTOSDataset

# ---------------------------------
# DEVICE
# ---------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------------
# DATASET
# ---------------------------------
dataset = APTOSDataset(
    csv_file="dataset/train.csv",
    img_dir="dataset/train"
)

# 80% train, 20% validation
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(
    dataset,
    [train_size, val_size]
)

train_loader = DataLoader(
    train_dataset,
    batch_size=8,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=8,
    shuffle=False
)

# ---------------------------------
# MODEL
# ---------------------------------
model = timm.create_model(
    "efficientnet_b0",
    pretrained=True
)

model.classifier = nn.Linear(
    model.classifier.in_features,
    5
)

model.to(device)

# ---------------------------------
# LOSS
# ---------------------------------
criterion = nn.CrossEntropyLoss()

optimizer = optim.Adam(
    model.parameters(),
    lr=1e-4
)

# ---------------------------------
# TRAINING
# ---------------------------------
epochs = 10

best_accuracy = 0

print("Training started...")

for epoch in range(epochs):

    model.train()

    train_loss = 0

    for images, labels in train_loader:

        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        train_loss += loss.item()

    # -----------------------------
    # VALIDATION
    # -----------------------------
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            predictions = torch.argmax(outputs, dim=1)

            correct += (predictions == labels).sum().item()

            total += labels.size(0)

    accuracy = correct / total

    print(
        f"Epoch {epoch+1}/{epochs} | "
        f"Loss: {train_loss:.3f} | "
        f"Validation Accuracy: {accuracy:.4f}"
    )

    if accuracy > best_accuracy:

        best_accuracy = accuracy

        torch.save(
            model.state_dict(),
            "dr_model.pth"
        )

        print("✅ Best model saved.")

print()

print("Training Finished")

print(f"Best Validation Accuracy: {best_accuracy:.4f}")