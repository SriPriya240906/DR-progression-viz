import json
import os

# ---------------------------------------
# Risk Mapping Based on DR Grade
# ---------------------------------------
risk_model = {
    0: {
        "grade": "No DR",
        "risk": {
            "1_year": "Low",
            "2_year": "Low",
            "3_year": "Moderate"
        }
    },
    1: {
        "grade": "Mild DR",
        "risk": {
            "1_year": "Low",
            "2_year": "Moderate",
            "3_year": "High"
        }
    },
    2: {
        "grade": "Moderate DR",
        "risk": {
            "1_year": "Moderate",
            "2_year": "High",
            "3_year": "High"
        }
    },
    3: {
        "grade": "Severe DR",
        "risk": {
            "1_year": "High",
            "2_year": "High",
            "3_year": "Very High"
        }
    },
    4: {
        "grade": "Proliferative DR",
        "risk": {
            "1_year": "Very High",
            "2_year": "Very High",
            "3_year": "Critical"
        }
    }
}

# ---------------------------------------
# Save Model
# ---------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "models", "risk_model")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.json")

with open(MODEL_PATH, "w") as f:
    json.dump(risk_model, f, indent=4)

print("=" * 50)
print("Risk Model Created Successfully!")
print("=" * 50)
print(f"Saved to: {MODEL_PATH}")