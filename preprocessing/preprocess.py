import tensorflow as tf

IMG_SIZE = (224, 224)
BATCH_SIZE = 32

train_path = "dataset/train/1000images"

train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    train_path,
    validation_split=0.2,
    subset="training",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

validation_dataset = tf.keras.preprocessing.image_dataset_from_directory(
    train_path,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_dataset.class_names

print("Classes:")
print(class_names)

print("\nTraining batches:", len(train_dataset))
print("Validation batches:", len(validation_dataset))