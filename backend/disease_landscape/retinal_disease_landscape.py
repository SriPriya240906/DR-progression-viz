from __future__ import annotations

from typing import Any


SUPPORTED_DR_LABELS = [
    "No Diabetic Retinopathy",
    "Mild",
    "Moderate",
    "Severe",
    "Proliferative DR",
]

UNAVAILABLE_DISEASES = [
    ("Glaucoma", "No validated local glaucoma model, paired labels, or evaluation set was identified."),
    ("Age-related Macular Degeneration", "No validated local AMD model, paired labels, or evaluation set was identified."),
    ("Diabetic Macular Edema", "No validated local DME model, paired labels, or evaluation set was identified."),
    ("Cataract", "No validated local cataract model, paired labels, or evaluation set was identified."),
    ("Retinal Vein Occlusion", "No validated local RVO model, paired labels, or evaluation set was identified."),
    ("Hypertensive Retinopathy", "No validated local hypertensive-retinopathy model, paired labels, or evaluation set was identified."),
    ("Retinal Detachment", "No validated local retinal-detachment model, paired labels, or evaluation set was identified."),
    ("Pathological Myopia", "No validated local pathological-myopia model, paired labels, or evaluation set was identified."),
    ("Other retinal diseases", "No validated local disease-specific model or paired labels were identified."),
]


def build_disease_landscape() -> dict[str, Any]:
    """Describe disease capabilities without producing additional disease predictions."""
    diseases = [
        {
            "name": "Diabetic Retinopathy",
            "status": "supported",
            "prediction_available": True,
            "model_available": True,
            "label_source": "Existing APTOS-style dataset labels in dataset/train.csv",
            "model": "EfficientNet-B0 with the existing root-level dr_model.pth checkpoint",
            "labels": SUPPORTED_DR_LABELS.copy(),
            "notes": "The active application provides AI-assisted five-grade diabetic retinopathy classification.",
        }
    ]
    diseases.extend(
        {
            "name": name,
            "status": "unavailable",
            "prediction_available": False,
            "model_available": False,
            "label_source": None,
            "model": None,
            "labels": [],
            "notes": notes,
        }
        for name, notes in UNAVAILABLE_DISEASES
    )
    return {
        "available": True,
        "landscape_type": "capability_map",
        "diseases": diseases,
        "current_supported_scope": "AI-assisted diabetic retinopathy grading only.",
        "limitations": [
            "An unavailable disease-specific model does not indicate absence of that disease.",
            "No additional disease probability, risk score, or combined retinal-health score is calculated.",
            "Disease-specific clinical assessment requires appropriate examination and testing.",
            "The listed capability statuses reflect repository evidence, not clinical validation.",
        ],
    }
