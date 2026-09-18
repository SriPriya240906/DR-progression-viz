# Phase 7 — Explainability + Clinical Evidence

## Status

Phase 7 is complete. This phase adds an evidence presentation and interpretation layer only. No Phase 8 or later feature was implemented.

## 1. Objective

Create a transparent AI-assisted evidence summary that organizes the independently generated outputs from Phases 2 through 6 and the existing Grad-CAM, retrieval, progression, and prediction responses.

The summary does not create a new model, change the DR prediction, combine signals into a medical score, or make an autonomous diagnosis.

## 2. Existing evidence sources inspected

The active `/api/analyze` flow was traced and the exact fields reused are:

- `prediction`
- `quality`
- `enhancement`
- `reliability`
- `structure`
- `lesion_evidence`
- `gradcam`
- `similar_cases`
- `progression_map`
- `progression_simulation`
- `progression_prediction`
- `errors`

The existing React page already renders individual quality, enhancement, reliability, structure, lesion, prediction, Grad-CAM, retrieval, progression, and report components. The existing PDF generator produces a simple report from the report request payload and was inspected before deciding whether to extend it.

## 3. Evidence-summary architecture

Added:

- `backend/evidence/__init__.py`
- `backend/evidence/clinical_evidence_summary.py`

`build_evidence_summary(analysis)` consumes existing response fields and returns separate sections:

- `prediction`
- `model_uncertainty`
- `image_quality`
- `model_explanation`
- `retinal_structure`
- `lesion_evidence`
- `clinical_review`
- `limitations`

There is no overall AI score, clinical evidence score, disease probability, diagnostic confidence score, trust score, or weighted fusion.

## 4. Prediction presentation

The summary preserves the existing grade, label, and confidence values. It uses wording such as:

> AI model predicts Moderate.

It does not call the prediction a confirmed diagnosis and does not alter the classifier output.

The verified sample remained:

- Grade: 2
- Label: Moderate
- Existing confidence: 100.0

## 5. Uncertainty presentation

The summary reuses Phase 4 values:

- top probability
- second probability
- probability margin
- predictive entropy
- normalized predictive entropy
- calibration status

The summary states that probability-distribution uncertainty is not clinical certainty. When calibration is unavailable it states:

> Calibration has not been established because a defensible held-out calibration set is unavailable.

No reliability or correctness probability is fabricated.

## 6. Image-quality presentation

The summary reuses Phase 2 status and metrics, including focus, illumination, contrast, resolution, field of view, retinal visibility, and warnings. It explains that image quality can affect interpretation of AI-assisted analysis without inventing a clinical-quality threshold.

## 7. Grad-CAM explanation

The summary reports existing Grad-CAM availability and states:

> Grad-CAM highlights image regions that contributed to the model prediction. These regions are not confirmed lesions.

Grad-CAM generation was not modified. Grad-CAM was not converted into lesion boxes or a lesion score.

## 8. Retinal structure evidence

The summary reuses Phase 5 structure output and labels it:

> Experimental vessel-like structure estimation

It explicitly states that the output is not a validated vessel segmentation model. Existing optic-disc and fovea unavailable states remain unchanged.

## 9. Lesion candidate evidence

The summary reuses Phase 6 dark and bright candidate counts, fractions, and overlay URLs. It labels them:

> Experimental lesion candidate localization

It explicitly states that candidate regions are not confirmed microaneurysms, hemorrhages, or exudates. No lesion score or disease score is created.

## 10. Clinical wording and separation

The new frontend component `ClinicalEvidenceCard.jsx` separates:

### AI Model Output

- predicted grade
- model label
- model confidence
- top-2 margin
- predictive entropy
- calibration status

### Supporting Image Evidence

- image quality
- Grad-CAM availability
- experimental vessel-like structure
- experimental dark/bright candidate counts

### Clinical Limitation

- clinical review required
- confidence is not clinical certainty
- candidate findings are not confirmed lesions
- the evidence summary is not a standalone diagnosis

No prohibited claims such as confirmed lesions, disease probability, clinical certainty, treatment recommendation, or surgery requirement were added.

## 11. API changes

`POST /api/analyze` now includes additive:

```text
evidence_summary
```

All existing fields remain present.

Added:

```text
POST /api/evidence/summary
```

The endpoint accepts either:

- an existing analysis JSON object and returns an organized summary, or
- a retinal image upload and computes the existing prediction/evidence outputs for summary presentation.

The image endpoint does not fit calibration or create new model outputs. It reuses existing inference and independent evidence functions.

## 12. PDF changes

`utils/pdf_report.py` was inspected. The PDF generator has a narrow existing contract that accepts grade, confidence, risk, progression, and recommendation. The evidence summary API/UI integration was kept isolated and the PDF generator was left unchanged to avoid changing the established report structure or introducing uncalibrated experimental lesion/structure wording into a clinical-style PDF.

PDF regression remained successful.

## 13. Tests

Added:

- `tests/test_clinical_evidence_summary.py`
- `tests/test_evidence_summary_api.py`

Coverage includes:

- complete analysis summary
- missing quality, reliability, structure, lesion, and Grad-CAM signals
- deterministic output
- prediction and confidence preservation
- no arbitrary score generation
- mandatory clinical review
- JSON summary endpoint
- image summary endpoint
- unsupported MIME type
- corrupted image
- additive full-analysis behavior

Full focused test command:

```powershell
.\\venv\\Scripts\\python.exe -m pytest -q tests
```

Result: `53 passed`.

## 14. Real-image regression

Using `test_images/000c1434d8d7.png`:

- `/api/health`: HTTP 200.
- `/api/analyze`: HTTP 200.
- `/api/evidence/summary`: HTTP 200.
- `/api/report/{analysis_id}`: HTTP 200, `application/pdf`.
- Prediction: Grade 2 / Moderate.
- Confidence: 100.0.
- Quality: present.
- Enhancement: present and remains preview-only.
- Reliability: present; calibration unavailable as documented.
- Structure: present.
- Lesion evidence: present.
- Grad-CAM: present.
- Similar cases: present.
- Progression map: present.
- Progression simulation: present.
- Optional errors: empty.
- Evidence summary prediction grade/confidence matched the original prediction.
- Clinical review: required.

This single-image regression is not clinical validation.

## 15. Frontend

Added `frontend/src/components/ClinicalEvidenceCard.jsx` and mounted it in the existing analysis page. Added additive TypeScript types and API normalization, plus compact responsive styles.

Command:

```powershell
npm --prefix frontend run build
```

Result: Vite production build passed.

Touched files reported no diagnostics.

## 16. Files added

- `backend/evidence/__init__.py`
- `backend/evidence/clinical_evidence_summary.py`
- `frontend/src/components/ClinicalEvidenceCard.jsx`
- `tests/test_clinical_evidence_summary.py`
- `tests/test_evidence_summary_api.py`
- `PHASE_7_EXPLAINABILITY_CLINICAL_EVIDENCE_CHECKPOINT.md`

## 17. Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No classifier, checkpoint, preprocessing, prediction logic, Grad-CAM generation, retrieval, progression, quality, enhancement, reliability, structure, lesion, or PDF implementation was modified.

## 18. Limitations

- Model confidence is not clinical certainty.
- Calibration remains unavailable because no defensible held-out calibration set exists.
- Grad-CAM shows model-contributing regions and does not prove a lesion exists.
- Phase 5 vessel-like structure output is experimental and not validated segmentation.
- Phase 6 dark/bright candidates are not confirmed clinical lesions.
- No combined evidence score or disease probability is calculated.
- Clinical review remains required.
- No clinical validation or external validation was performed.
- PDF evidence integration was intentionally not added because the existing PDF contract is narrow and changing it would increase regression and interpretation risk.

Phase 8 and all later phases were not implemented.
