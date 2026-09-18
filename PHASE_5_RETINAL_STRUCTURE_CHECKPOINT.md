# Phase 5 — Retinal Structure Analysis

## Status

Phase 5 is complete within the evidence available in this repository. No Phase 6 or later feature was implemented.

## Implementation

### Repository inspection

No defensible local vessel-segmentation model, vessel weights, optic-disc detector, fovea detector, retinal structure masks, or structure-specific annotations were found.

The existing `progression_engine/retina_unet.pth` is an autoencoder/progression artifact, not a vessel-segmentation model, and was not reused for structure claims. The existing DR classifier was not used as a vessel model. No external model or weights were downloaded.

### Structure method

Added `backend/structure/retinal_structure_analyzer.py` with `analyze_retinal_structure(image)`.

The implementation is Path C experimental image processing:

1. Validate the original BGR image.
2. Resize only the structure-processing working image to a maximum dimension of 1024 pixels for bounded runtime.
3. Estimate a retinal field-of-view region using the same conservative intensity/morphology approach used by Phase 2.
4. Estimate vessel-like dark linear responses from the green channel using a 9x9 morphological black-hat operation.
5. Apply a high percentile threshold inside the estimated retinal region and remove tiny connected components.
6. Return an original-size binary candidate mask and optional overlay for visualization.

This is explicitly called:

> Experimental vessel-like structure estimation

It is not called validated vessel segmentation and does not provide a structure confidence score.

The candidate output is sensitive to illumination, lesions, borders, pigmentation, compression, and image artifacts. It is structural image evidence only and does not diagnose disease.

### Field-of-view output

The result includes:

- image dimensions
- estimated retinal field fraction
- whether the field is sufficient for this experimental analysis
- estimated field center in original-image pixel coordinates
- estimated field extent

The field-of-view result remains a heuristic estimate, not clinical gradability.

### Optic disc and fovea

Both remain explicitly unavailable:

- No validated/local optic-disc localization model or annotations were available.
- No validated/local fovea localization model or annotations were available.

No coordinates were fabricated.

### API

`POST /api/analyze` now includes an additive `structure` object while preserving quality, enhancement, prediction, reliability, Grad-CAM, similar cases, progression, PDF, and errors.

Added:

- `POST /api/structure/analyze`

The dedicated endpoint returns the structure result, original image URL, and an overlay URL when sufficient field-of-view evidence exists. Overlay assets use the existing process-local analysis asset mechanism.

The original upload remains the input to the DR classifier, Grad-CAM, retrieval, progression, and Phase 3 enhancement decision. The enhanced preview is not used as classifier input.

### Frontend

Added a compact Retinal Structure card displaying:

- experimental field-of-view fraction and analysis suitability
- estimated field center
- vessel-like fraction
- method and limitations
- overlay when available
- explicit optic-disc/fovea unavailable states
- no-confidence-available status

The card is separate from Phase 2 image quality and Phase 4 model uncertainty. No combined score was created.

## Scientific basis and data availability

The selected method was chosen because OpenCV is already used by the project, the repository contains no defensible local structure model, and a deterministic, lightweight candidate estimator can be clearly labeled as experimental. The processing is bounded to a 1024-pixel working image while masks and coordinates are returned in original-image dimensions.

The repository contains 3,663 images in `dataset/train` and no populated `dataset/valid` or `dataset/test` directories. No ground-truth vessel masks or optic-disc/fovea annotations were available. Quantitative segmentation accuracy was not evaluated because ground-truth vessel annotations were unavailable.

No Dice, IoU, sensitivity, specificity, or vessel accuracy claim is made.

## Real retinal image results

A sequential sample of five images from `dataset/train` was processed without modifying source files:

- Images tested: 5
- Valid analyses: 5
- Failures: 0
- Mean processing time: 0.956 seconds/image
- Median processing time: 0.9741 seconds/image
- Total processing time: 4.7802 seconds
- Mean estimated field fraction: 0.718327
- Mean vessel-like fraction: 0.034875

These are engineering sanity statistics from an unlabeled sample, not clinical validation or segmentation accuracy.

A real project sample `test_images/000c1434d8d7.png` produced:

- estimated field fraction: 0.746177
- vessel-like fraction: 0.027087
- overlay asset: available
- optic disc: unavailable
- fovea: unavailable

## Tests

### Focused Phase 5 tests

```powershell
python -m pytest -q tests/test_retinal_structure.py tests/test_structure_api.py
```

Result: `9 passed`.

Coverage includes valid real-image analysis, deterministic output, bounded mask values and fractions, dark/non-retinal input, too-small and invalid input, unsupported MIME type, corrupted upload, overlay delivery, and additive full-analysis response fields.

### Frontend

```powershell
npm --prefix frontend run build
```

Result: Vite production build passed.

### Existing regression

The Phase 2, Phase 3, and Phase 4 focused suites remain available and were previously passing with 30 tests. The Phase 5 API test exercised the full `/api/analyze` path and verified quality, enhancement, prediction, reliability, Grad-CAM, similarity, progression map, and progression simulation fields remained present with no optional errors.

The full repository pytest run retains two unrelated legacy collection failures:

- `run_retrieval_test.py`: unavailable `DRRetrieval` import.
- `run_test.py`: missing `test.jpg` input causing an OpenCV resize failure.

These scripts were not modified.

## Files added

- `backend/structure/__init__.py`
- `backend/structure/retinal_structure_analyzer.py`
- `frontend/src/components/RetinalStructureCard.jsx`
- `tests/test_retinal_structure.py`
- `tests/test_structure_api.py`
- `PHASE_5_RETINAL_STRUCTURE_CHECKPOINT.md`

## Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No DR model weights, EfficientNet architecture, DR preprocessing, training pipeline, quality analyzer, enhancement algorithm, reliability module, retrieval engine, progression engine, Grad-CAM implementation, or PDF generator was modified.

## Limitations

- Structural analysis is experimental and is not a clinical diagnosis.
- Vessel-like estimates may be affected by illumination, lesions, image quality, borders, pigmentation, compression, and artifacts.
- The candidate map is not validated vessel segmentation.
- No segmentation accuracy claim is possible without ground-truth structure masks.
- Optic-disc and fovea localization are unavailable because no defensible local method or annotations exist.
- No structure confidence score is exposed.
- No external validation was performed.
- Descriptive real-image statistics are not clinical validation.
- The Phase 2 field-of-view estimate is heuristic and not a clinical gradability assessment.
- Original-image classifier input behavior remains unchanged.

Phase 6 and all later features were not implemented.
