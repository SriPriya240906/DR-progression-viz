import cv2
import numpy as np


# -----------------------------
# GLOBAL CONTRAST + DARKENING
# -----------------------------
def retinal_darkening(img, intensity):
    img = img.astype(np.float32)

    # simulate retinal pigment damage
    factor = 1.0 - (0.35 * intensity)

    img *= factor

    # slight red channel dominance (diabetic effect)
    img[:, :, 2] *= (1 + 0.15 * intensity)

    return np.clip(img, 0, 255).astype(np.uint8)


# -----------------------------
# VESSEL BLUR SIMULATION
# -----------------------------
def vessel_degradation(img, intensity):
    blurred = cv2.GaussianBlur(img, (0, 0), 3 + intensity * 5)

    mask = cv2.GaussianBlur(
        np.ones(img.shape[:2], dtype=np.float32),
        (21, 21),
        0
    )

    mask = mask[..., None]

    return (img * (1 - intensity * 0.5) + blurred * intensity * 0.5).astype(np.uint8)


# -----------------------------
# LESION TEXTURE (NOT DOTS)
# -----------------------------
def lesion_texture(img, intensity):
    h, w = img.shape[:2]

    noise = np.random.normal(0, 25 * intensity, (h, w, 3))

    noise = noise.astype(np.float32)

    img = img.astype(np.float32)

    # smooth lesion-like patches
    img += noise

    return np.clip(img, 0, 255).astype(np.uint8)


# -----------------------------
# FINAL COMBINATION
# -----------------------------
def generate_progression(image):

    results = []

    for year in range(4):

        intensity = year / 3.0

        img = image.copy()

        # step 1: darkening
        img = retinal_darkening(img, intensity)

        # step 2: lesion texture
        img = lesion_texture(img, intensity)

        # step 3: vessel degradation
        img = vessel_degradation(img, intensity)

        # final smoothing (important for realism)
        img = cv2.bilateralFilter(img, 9, 75, 75)

        results.append(img)

    return results