import os
import sys

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from preprocessing.dataset_loader import DRDataset

dataset = DRDataset(
    csv_file=os.path.join(BASE_DIR, "dataset", "train.csv"),
    image_dir=os.path.join(BASE_DIR, "dataset", "train")
)

print("=" * 50)
print("Dataset Size:", len(dataset))

image, label = dataset[0]

print("Image Shape:", image.shape)
print("Label:", label)