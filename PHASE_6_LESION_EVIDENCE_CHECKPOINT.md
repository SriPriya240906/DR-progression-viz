# Phase 6 — Lesion-Level Evidence

## 1. Objective

Add an experimental localized image-evidence layer for dark and bright candidate regions while preserving the existing DR classifier and all Phase 2 through Phase 5 behavior.

The output is candidate localization only. It does not diagnose lesions, calculate disease probabilities, calculate severity, or modify the classifier prediction.

No Phase 7 or later feature was implemented.

## 2. Repository inspection

The repository was searched for lesion models, lesion weights, microaneurysm, hemorrhage, exudate, neovascularization, lesion annotations, masks, bounding boxes, and fundus lesion datasets.

The only lesion-named implementation found was synthetic lesion drawing in `prediction/progression_generator.py`. That code creates artificial progression visuals and is not a lesion detector or lesion annotation source. Existing U-Net/progression artifacts are not lesion models.

No local validated lesion model, lesion-specific weights, paired lesion annotations, lesion masks, lesion bounding boxes, or lesion-specific evaluation split were available. No external model or weights were downloaded.

## 3. Selected path

Path C was selected:

> Experimental Lesion Candidate Localization

The implementation is isolated in `backend/lesions/lesion_candidate_analyzer.py` and uses the original BGR retinal image. It does not use the enhanced Phase 3 preview, the DR classifier, Grad-CAM, or Phase 5 vessel-like output as a lesion detector.

## 4. Implemented algorithm

Processing is bounded to a maximum 1024-pixel working dimension to avoid multi-minute processing on high-resolution fundus images. Candidate boxes and overlays are mapped back to original image dimensions.

### Field-of-view filtering

A conservative Phase 2-style field-of-view estimate is created using grayscale intensity above 12, morphological opening/closing, and the largest connected contour. Candidate responses outside that region are discarded.

### Dark candidates

- Green-channel morphological black-hat response with a 9x9 elliptical kernel.
- Threshold at the 97th percentile of response values inside the estimated retinal field, with a minimum response of 1.
- 3x3 morphological cleanup.
- Connected components retained between 8 pixels and 2% of the working image area.

### Bright candidates

- Grayscale morphological top-hat response with a 15x15 elliptical kernel.
- Threshold at the 99th percentile of response values inside the estimated retinal field, with a minimum response of 1.
- 3x3 morphological cleanup.
- The same conservative component-size bounds are used.

These are engineering heuristics chosen to keep the method deterministic and compact. They are not clinical thresholds and were not fit to lesion labels.

Candidate names remain `dark_candidate` and `bright_candidate` in the interpretation. The system does not call them microaneurysms, hemorrhages, or exudates.

## 5. Output

The analyzer returns:

- dark candidate count, fraction, and regions
- bright candidate count, fraction, and regions
- original-image coordinates and dimensions for each region
- area, centroid, relative centroid, mean intensity, and local fraction
- finite bounded values
- separate dark, bright, and combined visualization overlays
- `confidence_available: false`
- explicit limitations

All boxes are clipped to the original image bounds. Candidate fractions are relative to the estimated field-of-view pixels and are constrained to `[0, 1]`.

### Optic disc and neovascularization

No validated optic-disc detector exists, so the response explicitly returns:

- `optic_disc_exclusion.available: false`
- reason that candidate regions are not disc-excluded

No validated neovascularization detector exists, so:

- `neovascularization.available: false`

No optic-disc coordinates or neovascularization claims are fabricated.

## 6. Visualization

The dedicated endpoint and full analysis use the existing process-local analysis asset mechanism for:

- dark candidate overlay
- bright candidate overlay
- combined candidate overlay

The original upload is preserved unchanged. Overlay captions and frontend labels use experimental candidate terminology.

## 7. API changes

Added:

```text
POST /api/lesions/analyze
```

The endpoint accepts an image upload and returns `lesion_evidence`, original image URL, and controlled overlay URLs.

`POST /api/analyze` now includes additive `lesion_evidence` while retaining:

- quality
- enhancement
- prediction
- reliability
- structure
- Grad-CAM
- similar cases
- progression map
- progression simulation
- progression prediction
- errors

Lesion candidates are not fused into DR prediction or reliability.

## 8. Frontend changes

Added `LesionEvidenceCard.jsx` and mounted it in the existing result flow.

The card displays:

- experimental method status
- dark candidate count/fraction
- bright candidate count/fraction
- dark, bright, and combined overlays
- unavailable neovascularization and optic-disc exclusion states
- explicit disclaimer that candidates are not confirmed clinical lesions

Existing image quality, enhancement, reliability, structure, prediction, Grad-CAM, retrieval, progression, and report cards remain present.

## 9. Ground-truth availability

The repository contains the populated `dataset/train` image set but no paired lesion annotations or ground-truth lesion masks. The `dataset/valid` and `dataset/test` directories were empty during the prior project inspection.

No quantitative lesion detection accuracy can be established from the available repository data.

No sensitivity, specificity, accuracy, Dice, IoU, precision, recall, lesion confidence, or disease probability is reported.

## 10. Real-image sanity results

A sequential sample of five images from `dataset/train` was processed without modifying source images:

- Processed: 5
- Successful: 5
- Failures: 0
- Mean processing time: 0.5232 seconds/image
- Median processing time: 0.3902 seconds/image
- Mean dark candidate count: 82.4
- Mean bright candidate count: 21.2
- Mean dark candidate fraction: 0.012348
- Mean bright candidate fraction: 0.005346

Per-image counts were:

| Image | Dark candidates | Bright candidates | Dark fraction | Bright fraction |
| --- | ---: | ---: | ---: | ---: |
| `000c1434d8d7.png` | 8 | 1 | 0.012726 | 0.008413 |
| `001639a390f0.png` | 20 | 6 | 0.026247 | 0.009375 |
| `0024cdab0c1e.png` | 45 | 11 | 0.006050 | 0.003539 |
| `002c21358ce6.png` | 334 | 86 | 0.015257 | 0.002732 |
| `005b95c28852.png` | 5 | 2 | 0.001459 | 0.002669 |

These are descriptive engineering statistics only. Candidate counts must not be interpreted as disease severity or lesion prevalence.

## 11. Tests

Focused Phase 6 command:

```powershell
python -m pytest -q tests/test_lesion_candidate_analyzer.py tests/test_lesion_api.py
```

Result: `8 passed`.

Coverage includes valid real-image analysis, invalid and tiny inputs, deterministic output, bounded regions, finite values, field-of-view filtering, overlay dimensions, unsupported MIME type, corrupted upload, overlay URL delivery, unavailable optic-disc/neovascularization states, and additive `/api/analyze` output.

## 12. Regression

- Phase 2 quality remains in the full analysis response.
- Phase 3 enhancement remains preview-only; the original image remains classifier input.
- Phase 4 reliability remains separate; calibration remains unavailable where no defensible calibration split exists.
- Phase 5 structure remains separate; vessel-like overlay and optic-disc/fovea unavailable states remain intact.
- DR prediction logic and checkpoint were not modified.
- Grad-CAM, similar retrieval, progression map, progression simulation, PDF, and health routes remain unchanged in behavior.
- Frontend build passed with `npm --prefix frontend run build`.
- Touched files reported no diagnostics.

The full `tests` suite was run with `python -m pytest -q tests` and passed with `47 passed`. A root-level `python -m pytest -q` run is expected to retain two previously known unrelated legacy collector failures: `run_retrieval_test.py` imports unavailable `DRRetrieval`, and `run_test.py` requires missing `test.jpg`. These are unrelated to Phase 6.

## 13. Files added

- `backend/lesions/__init__.py`
- `backend/lesions/lesion_candidate_analyzer.py`
- `frontend/src/components/LesionEvidenceCard.jsx`
- `tests/test_lesion_candidate_analyzer.py`
- `tests/test_lesion_api.py`
- `PHASE_6_LESION_EVIDENCE_CHECKPOINT.md`

## 14. Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No model weights, DR classifier architecture, DR preprocessing, training pipeline, Grad-CAM implementation, retrieval engine, progression engine, PDF generator, Phase 2 analyzer, Phase 3 enhancer, Phase 4 reliability module, or Phase 5 structure algorithm was modified.

## 15. Scientific limitations

- Candidate localization is not a validated clinical lesion detector.
- Dark candidates are not confirmed microaneurysms or hemorrhages.
- Bright candidates are not confirmed exudates.
- Candidate responses may be caused by vessels, illumination, lesions, borders, compression, pigmentation, or artifacts.
- No validated optic-disc detector is available, so optic-disc exclusion is unavailable.
- No validated neovascularization detector is available.
- No lesion ground truth exists for quantitative evaluation.
- No confidence score, disease probability, severity score, or diagnostic claim is produced.
- No external validation or clinical validation was performed.
- Grad-CAM, Phase 5 structure output, and lesion candidates remain separate evidence types.

Phase 7 and all later features were not implemented.
