import torch
import timm
import torch.nn as nn
import numpy as np

from torch.utils.data import DataLoader, Subset
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)

from dataset import APTOSDataset


# ==========================================
# DEVICE
# ==========================================
device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Device:", device)


# ==========================================
# CLASS NAMES
# ==========================================
CLASS_NAMES = [
    "No DR",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative DR"
]


# ==========================================
# LOAD DATASET
# ==========================================
dataset = APTOSDataset(
    csv_file="dataset/train.csv",
    img_dir="dataset/train"
)

labels = dataset.data["diagnosis"].values
indices = np.arange(len(dataset))


# ==========================================
# STRATIFIED 80/20 SPLIT
# ==========================================
train_indices, val_indices = train_test_split(
    indices,
    test_size=0.20,
    random_state=42,
    stratify=labels
)

val_dataset = Subset(
    dataset,
    val_indices
)

val_loader = DataLoader(
    val_dataset,
    batch_size=8,
    shuffle=False
)

print("Total images:", len(dataset))
print("Evaluation images:", len(val_dataset))


# ==========================================
# LOAD TRAINED MODEL
# ==========================================
model = timm.create_model(
    "efficientnet_b0",
    pretrained=False
)

model.classifier = nn.Linear(
    model.classifier.in_features,
    5
)

model.load_state_dict(
    torch.load(
        "dr_model.pth",
        map_location=device
    )
)

model.to(device)
model.eval()

print("Trained model loaded successfully.")


# ==========================================
# PREDICTIONS
# ==========================================
y_true = []
y_pred = []


with torch.no_grad():

    for images, labels_batch in val_loader:

        images = images.to(device)

        outputs = model(images)

        predictions = torch.argmax(
            outputs,
            dim=1
        )

        y_true.extend(
            labels_batch.numpy()
        )

        y_pred.extend(
            predictions.cpu().numpy()
        )


# ==========================================
# OVERALL METRICS
# ==========================================
accuracy = accuracy_score(
    y_true,
    y_pred
)

balanced_accuracy = balanced_accuracy_score(
    y_true,
    y_pred
)

precision, recall, f1, support = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=[0, 1, 2, 3, 4],
        zero_division=0
    )
)

macro_precision = precision.mean()
macro_recall = recall.mean()
macro_f1 = f1.mean()


# ==========================================
# CONFUSION MATRIX
# ==========================================
conf_matrix = confusion_matrix(
    y_true,
    y_pred,
    labels=[0, 1, 2, 3, 4]
)


# ==========================================
# RESULTS
# ==========================================
print()
print("=" * 65)
print("DR MODEL EVALUATION")
print("=" * 65)

print(f"Accuracy:           {accuracy:.4f}")
print(f"Balanced Accuracy:  {balanced_accuracy:.4f}")
print(f"Macro Precision:    {macro_precision:.4f}")
print(f"Macro Recall:       {macro_recall:.4f}")
print(f"Macro F1:           {macro_f1:.4f}")


# ==========================================
# PER-CLASS RESULTS
# ==========================================
print()
print("-" * 65)
print("PER-CLASS RESULTS")
print("-" * 65)

for i, name in enumerate(CLASS_NAMES):

    print()
    print(name)
    print(f"  Precision: {precision[i]:.4f}")
    print(f"  Recall:    {recall[i]:.4f}")
    print(f"  F1:        {f1[i]:.4f}")
    print(f"  Support:   {support[i]}")


# ==========================================
# CONFUSION MATRIX
# ==========================================
print()
print("-" * 65)
print("CONFUSION MATRIX")
print("-" * 65)

print("Rows = Actual")
print("Columns = Predicted")
print()

print(
    "             " +
    " ".join(f"{i:^8}" for i in range(5))
)

for i, row in enumerate(conf_matrix):

    print(
        f"{i:^8}      " +
        " ".join(f"{value:^8}" for value in row)
    )


# ==========================================
# CLASSIFICATION REPORT
# ==========================================
print()
print("-" * 65)
print("CLASSIFICATION REPORT")
print("-" * 65)

print(
    classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES,
        zero_division=0
    )
)


print()
print("=" * 65)
print("Evaluation complete.")
print("=" * 65)