import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMAGE_PATH = os.path.join(BASE_DIR, "test_images", "000c1434d8d7.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "progression")

os.makedirs(OUTPUT_DIR, exist_ok=True)

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise FileNotFoundError("Test image not found.")

np.random.seed(42)


def add_microaneurysms(img, count):
    out = img.copy()

    h, w = out.shape[:2]

    for _ in range(count):
        x = np.random.randint(40, w - 40)
        y = np.random.randint(40, h - 40)

        cv2.circle(
            out,
            (x, y),
            2,
            (0, 0, 150),
            -1
        )

    return out


def add_hemorrhages(img, count):

    out = img.copy()

    h, w = out.shape[:2]

    for _ in range(count):

        x = np.random.randint(40, w - 40)
        y = np.random.randint(40, h - 40)

        axes = (
            np.random.randint(6, 14),
            np.random.randint(3, 8)
        )

        angle = np.random.randint(0, 180)

        cv2.ellipse(
            out,
            (x, y),
            axes,
            angle,
            0,
            360,
            (20, 20, 170),
            -1
        )

    return out


def add_exudates(img, count):

    out = img.copy()

    h, w = out.shape[:2]

    for _ in range(count):

        x = np.random.randint(40, w - 40)
        y = np.random.randint(40, h - 40)

        radius = np.random.randint(4, 10)

        cv2.circle(
            out,
            (x, y),
            radius,
            (200, 230, 255),
            -1
        )

    return out


def add_cotton_wool(img, count):

    out = img.copy()

    h, w = out.shape[:2]

    for _ in range(count):

        x = np.random.randint(40, w - 40)
        y = np.random.randint(40, h - 40)

        axes = (
            np.random.randint(15, 25),
            np.random.randint(8, 15)
        )

        angle = np.random.randint(0, 180)

        cv2.ellipse(
            out,
            (x, y),
            axes,
            angle,
            0,
            360,
            (245, 245, 245),
            -1
        )

        out = cv2.GaussianBlur(out, (5, 5), 0)

    return out


def simulate(img, severity):

    out = img.copy()

    # ----------------------------------
    # Load Grad-CAM Heatmap
    # ----------------------------------
    heatmap_path = os.path.join(
        BASE_DIR,
        "outputs",
        "gradcam",
        "heatmap.png"
    )

    heatmap = cv2.imread(heatmap_path)

    if heatmap is None:
        raise FileNotFoundError("Grad-CAM heatmap not found.")

    heatmap = cv2.resize(
        heatmap,
        (img.shape[1], img.shape[0])
    )

    gray = cv2.cvtColor(
        heatmap,
        cv2.COLOR_BGR2GRAY
    )

    # High-attention regions only
    _, mask = cv2.threshold(
        gray,
        180,
        255,
        cv2.THRESH_BINARY
    )

    ys, xs = np.where(mask > 0)

    if len(xs) == 0:
        return out

    rng = np.random.default_rng(42)

    if severity == 1:
        micro = 30
        hemorrhage = 5
        exudate = 8
        cotton = 0

    elif severity == 2:
        micro = 70
        hemorrhage = 20
        exudate = 20
        cotton = 4

    else:
        micro = 120
        hemorrhage = 45
        exudate = 35
        cotton = 12

    # ----------------------------
    # Microaneurysms
    # ----------------------------
    for _ in range(micro):

        i = rng.integers(len(xs))

        x = int(xs[i])
        y = int(ys[i])

        cv2.circle(
            out,
            (x, y),
            2,
            (0, 0, 170),
            -1
        )

    # ----------------------------
    # Hemorrhages
    # ----------------------------
    for _ in range(hemorrhage):

        i = rng.integers(len(xs))

        x = int(xs[i])
        y = int(ys[i])

        cv2.ellipse(
            out,
            (x, y),
            (
                rng.integers(6, 12),
                rng.integers(3, 8)
            ),
            rng.integers(0,180),
            0,
            360,
            (20,20,170),
            -1
        )

    # ----------------------------
    # Exudates
    # ----------------------------
    for _ in range(exudate):

        i = rng.integers(len(xs))

        x = int(xs[i])
        y = int(ys[i])

        cv2.circle(
            out,
            (x,y),
            rng.integers(4,9),
            (220,240,255),
            -1
        )

    # ----------------------------
    # Cotton Wool Spots
    # ----------------------------
    for _ in range(cotton):

        i = rng.integers(len(xs))

        x = int(xs[i])
        y = int(ys[i])

        cv2.ellipse(
            out,
            (x,y),
            (
                rng.integers(15,25),
                rng.integers(8,15)
            ),
            rng.integers(0,180),
            0,
            360,
            (245,245,245),
            -1
        )

    return out

year1 = simulate(image, 1)
year2 = simulate(image, 2)
year3 = simulate(image, 3)

cv2.imwrite(os.path.join(OUTPUT_DIR, "year1.png"), year1)
cv2.imwrite(os.path.join(OUTPUT_DIR, "year2.png"), year2)
cv2.imwrite(os.path.join(OUTPUT_DIR, "year3.png"), year3)

print("=" * 60)
print("Progression Images Generated Successfully")
print("=" * 60)
print("Saved in outputs/progression/")