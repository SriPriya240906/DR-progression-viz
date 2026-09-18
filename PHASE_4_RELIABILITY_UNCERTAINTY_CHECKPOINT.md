# Phase 4 — Model Reliability & Uncertainty

## Status

Phase 4 is complete within the evidence available in this repository. No Phase 5 or later feature was implemented.

## Implementation

### Model and checkpoint inspected

The active API classifier remains unchanged:

- Architecture: `timm.create_model("efficientnet_b0", pretrained=False)` with a five-class linear classifier head.
- Checkpoint: root-level `dr_model.pth`, loaded by `model.py`.
- Class mapping: 0 No DR, 1 Mild, 2 Moderate, 3 Severe, 4 Proliferative DR.
- Active inference preprocessing: PIL RGB conversion, resize to 224x224, `ToTensor()`; no ImageNet normalization.
- Existing prediction authority: `model.predict_details()`.
- Existing confidence: winning softmax probability multiplied by 100 and rounded to two decimals.

No model weights, model architecture, training code, or preprocessing was modified.

### New module

Added `backend/reliability/uncertainty.py` with `analyze_prediction_reliability()`.

It validates and normalizes the existing model probability distribution, then reports:

- predicted class index and label
- model confidence / top probability
- second probability
- top-2 probability margin
- predictive entropy in nats
- normalized predictive entropy from 0 to 1 for the class count
- cautious interpretation text
- calibration availability and reason

No combined image-quality/model-confidence score was created. No clinical reliability score or arbitrary threshold label was created.

### Calibration method

Temperature scaling was investigated but not fitted. The repository does not contain a populated `dataset/valid` or `dataset/test` split, and the training script's deterministic 400/100 split over a random 500-image subset is not persisted as a reusable calibration artifact. The active checkpoint's training provenance is also not sufficient to reconstruct that split safely.

Therefore:

- no temperature parameter was learned
- no calibration artifact was saved
- no validation or test data was used to fit calibration
- `calibration.available` is explicitly `false`
- ECE, MCE, Brier score, reliability diagrams, and before/after calibration metrics are `N/A`, not fabricated

### API

Existing `POST /api/analyze` retains all existing fields and adds:

```json
{
  "reliability": {
    "available": true,
    "predicted_index": 2,
    "predicted_label": "Moderate",
    "confidence": 1.0,
    "top_probability": 1.0,
    "second_probability": 0.0,
    "probability_margin": 1.0,
    "predictive_entropy": 0.0,
    "normalized_predictive_entropy": 0.0,
    "calibration": {
      "available": false,
      "method": "temperature_scaling",
      "reason": "No populated, persisted held-out validation or evaluation split was available."
    }
  }
}
```

The example values above describe the verified baseline sample output shape; the running API computes values from each uploaded image and does not hard-code them.

Added `POST /api/reliability/analyze`, which performs the existing model inference for the uploaded image and returns the prediction details plus the uncertainty metrics. It does not fit calibration on the uploaded image.

### Frontend

Added a separate Model Reliability & Uncertainty card. It displays:

- predicted class
- model confidence
- top-2 margin
- predictive entropy
- normalized entropy
- calibration availability
- cautious interpretation

The UI explicitly states that model confidence is not diagnostic certainty and does not combine reliability with Phase 2 image quality.

### PDF

The PDF generator was left unchanged. Reliability is additive to the API and frontend, while the existing report structure and behavior remain stable. Adding uncalibrated uncertainty values to the clinical-style report without a validated interpretation layer would introduce avoidable reporting risk.

## Scientific methodology and data availability

The repository contains one populated labeled dataset at `dataset/train.csv` with images in `dataset/train`. The `dataset/valid` and `dataset/test` directories were empty during inspection.

The training script uses a random 500-image subset and a deterministic 400/100 split with seed 42, but it does not persist the selected indices, the fitted checkpoint provenance, logits, or calibration artifact. That split cannot be treated as an independently held-out evaluation set for the existing root checkpoint.

Consequently, no rigorous baseline accuracy, macro precision, macro recall, macro F1, confusion matrix, ECE, MCE, Brier score, reliability diagram, or calibration temperature is reported in this phase. Reporting metrics computed on the populated training directory would be in-sample and would not satisfy the requested held-out calibration evidence.

## Observed uncertainty output

The existing sample `test_images/000c1434d8d7.png` was processed through the unchanged API model:

- predicted grade: 2 / Moderate
- existing prediction confidence: 100.0 percent
- top probability: 1.0 after normalization of the existing returned probability map
- second probability: 0.0
- top-2 margin: 1.0
- predictive entropy: 0.0 nats
- normalized predictive entropy: 0.0
- calibration: unavailable

These values describe the model output distribution for one sample. They do not establish diagnostic certainty, calibration, or clinical reliability.

## Tests and regression

### Focused automated tests

Command:

```powershell
python -m pytest -q tests/test_reliability.py tests/test_reliability_api.py tests/test_quality_analyzer.py tests/test_image_enhancement.py tests/test_enhancement_api.py
```

Result: `30 passed`.

Coverage includes probability normalization, top-1/top-2 ranking, margin, entropy extremes, malformed and non-finite values, predicted-index consistency, calibration-unavailable behavior, dedicated API behavior, and prior Phase 2/3 tests.

### Frontend

Command:

```powershell
cd frontend
npm run build
```

Result: Vite production build passed.

### Existing API regression

Using `test_images/000c1434d8d7.png` and the project virtual environment:

- `GET /api/health`: HTTP 200.
- `POST /api/analyze`: HTTP 200.
- Prediction: Grade 2 / Moderate, confidence 100.0 percent.
- Image quality: present.
- Adaptive enhancement: present; original remains the DR model input.
- Grad-CAM: present.
- Similar cases: present.
- Progression map: present.
- Progression simulation: present.
- Optional errors: empty.
- PDF report: HTTP 200, `application/pdf`.
- `POST /api/reliability/analyze`: HTTP 200 with prediction and uncertainty metrics.

The enhanced preview is not passed to `predict_details()`; Phase 3's original-input rule remains intact.

The complete repository pytest command still encounters two unrelated legacy collection failures in `run_retrieval_test.py` and `run_test.py`: an unavailable `DRRetrieval` import and a missing `test.jpg` input. These scripts were not modified.

## Files added

- `backend/reliability/__init__.py`
- `backend/reliability/uncertainty.py`
- `frontend/src/components/ReliabilityCard.jsx`
- `tests/test_reliability.py`
- `tests/test_reliability_api.py`
- `PHASE_4_RELIABILITY_UNCERTAINTY_CHECKPOINT.md`

## Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No model weights, EfficientNet architecture, training pipeline, Phase 2 quality analyzer, Phase 3 enhancement algorithm, retrieval engine, progression engine, Grad-CAM implementation, or PDF generator was modified.

## Limitations

- Model confidence is not diagnostic certainty.
- Calibration depends on the evaluation population and cannot be established from this repository's current split structure.
- APTOS-style data and this checkpoint's unknown provenance may not generalize to clinical deployment.
- Predictive entropy and probability margins are model-dependent output-distribution metrics, not clinical uncertainty measures.
- No clinical validation or external validation was performed.
- Image quality remains an independent Phase 2 signal and is not combined with uncertainty.
- No uncertainty thresholds or reliability labels were invented without validation.
- The active inference preprocessing mismatch documented in the baseline remains unchanged and was not repaired in this phase.

Phase 5 and all later features were not implemented.
