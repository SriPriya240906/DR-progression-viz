import torch
import timm
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score

from dataset import APTOSDataset

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -----------------------------
# LOAD MODEL
# -----------------------------
model = timm.create_model("efficientnet_b0", pretrained=False)
model.classifier = nn.Linear(model.classifier.in_features, 5)
model.load_state_dict(torch.load("dr_model.pth", map_location=device))
model.eval()


# -----------------------------
# DATA
# -----------------------------
dataset = APTOSDataset(
    csv_file="dataset/train.csv",
    img_dir="dataset/train"
)

loader = DataLoader(dataset, batch_size=4, shuffle=False)


# -----------------------------
# EVALUATION
# -----------------------------
y_true = []
y_pred = []

with torch.no_grad():

    for images, labels in loader:

        outputs = model(images)
        preds = torch.argmax(outputs, dim=1)

        y_true.extend(labels.numpy())
        y_pred.extend(preds.numpy())


acc = accuracy_score(y_true, y_pred)

print("Accuracy:", acc)