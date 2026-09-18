# Phase 2 — Image Quality Assessment

## Objective

Add an independent, lightweight image-quality assessment for uploaded retinal images without modifying or gating the existing DR classifier, Grad-CAM, retrieval, progression, or PDF behavior.

The assessment is advisory. It uses image-level heuristics and does not claim clinical gradability or ungradability.

## Implemented

- Added independent OpenCV quality analysis using the already decoded image from `/api/analyze`.
- Added an additive `quality` object to the existing analysis response.
- Added `POST /api/quality/analyze` for quality-only requests.
- Added cautious GOOD, BORDERLINE, and POOR statuses.
- Added warnings and recommendations that refer to possible effects on AI-assisted analysis.
- Added non-destructive synthetic scenario tests.
- Added the existing frontend analysis flow's Image Quality card.
- Preserved the existing DR prediction and downstream response fields.

## Backend

### Module

- `backend/quality/quality_analyzer.py`
- `backend/quality/__init__.py`

Public function:

```python
analyze_image_quality(image: numpy.ndarray) -> dict
```

The function accepts the BGR OpenCV image already decoded by the backend. It does not load EfficientNet, invoke the DR classifier, or create another model instance.

### API integration

Existing `POST /api/analyze` flow is now:

```text
upload
-> existing cv2 readability validation
-> image quality analysis
-> existing DR prediction
-> existing Grad-CAM
-> existing similar cases
-> existing progression
-> response
```

Quality failure is added to the existing optional `errors` list and does not block DR analysis.

New endpoint:

- `POST /api/quality/analyze`
- Request: multipart image field `file`.
- Valid response: `{"quality": {...}}`.
- Unsupported MIME type: HTTP 415.
- Corrupted/unreadable image: HTTP 400.
- Extremely small image under 16x16 pixels: HTTP 400.
- Processing failure: HTTP 500 with `Image quality analysis unavailable.`.

## Frontend

### Components

- Updated `frontend/src/components/ImageQualityCard.jsx` with the active quality schema and unavailable state.
- Updated `frontend/src/App.jsx` to render the card after the uploaded image and before the existing DR result panels.
- Updated `frontend/src/services/api.ts` to normalize `quality` and retain compatibility with the older mock `image_quality` shape.
- Updated `frontend/src/types.ts` with the quality response fields.
- Updated `frontend/src/styles.css` with focused quality-card, metric, warning, and recommendation styles.

The loading state now says `Analyzing image quality and retinal image...`. If the quality field is unavailable, the card says that quality analysis is unavailable while the rest of the analysis remains visible.

## Metrics

### Resolution

Reports actual width, height, and aspect ratio. The experimental minimum band is 224x224 for the resolution assessment. Images below 16x16 are rejected as too small to process; images between 16x16 and 223 pixels in either dimension are reported as low resolution rather than silently rejected.

### Focus

Uses variance of the grayscale Laplacian. The raw value is returned as `focus.value` with metric name `variance_of_laplacian`.

### Illumination

Returns grayscale mean brightness, dark-pixel fraction, and bright-pixel fraction. These support possible underexposure and overexposure warnings without claiming clinical exposure adequacy.

### Contrast

Uses grayscale standard deviation. The raw value is returned as `contrast.value`.

### Field of View

Uses a conservative connected-region estimate after simple morphology. The result includes an estimated region fraction and explicitly states that the field-of-view assessment is heuristic. It is not a clinical retinal-field or gradability assessment.

### Retinal Visibility

Reports the fraction of pixels above the simple visibility floor inside the estimated region. If a stable region is not found, the result says visibility is limited. This is an image-only heuristic and does not identify retinal anatomy.

## Threshold methodology

All thresholds are marked in the response as `heuristic / experimental` and `validated_clinically: false`.

- Resolution: 224x224 is the existing classifier transform size, so it is used as an engineering reference band, not a clinical adequacy claim. A 16x16 processing floor prevents meaningless metric calculations.
- Focus: a 200-image sample from `dataset/train` was inspected. Observed variance-of-Laplacian values had a minimum of 3.3992, 10th percentile of 5.4098, median of 14.2547, and 90th percentile of 46.955. Experimental bands use below 5 as poor, 5 to below 10 as borderline, and 10 or higher as good.
- Brightness: the same sample had grayscale mean minimum 19.2496, 10th percentile 42.0717, median 62.8898, and 90th percentile 87.2127. Mean below 20 or above 220 is poor; near-boundary means below 35 or above 195 are borderline. Dark and bright pixel fractions are used as supporting exposure signals. The dark fraction is deliberately tolerant of normal fundus backgrounds and only becomes poor at 65% or more.
- Contrast: the sample had standard-deviation minimum 16.8147, 10th percentile 24.9024, median 37.8334, and 90th percentile 51.154. Below 17 is poor, 17 to below 25 is borderline, and 25 or higher is good.
- Field of view and retinal visibility: no clinically labeled quality dataset or validated retinal segmentation was available. These outputs remain heuristic descriptions and do not use a clinical threshold.

Dataset used for threshold inspection: 200 images sampled from the existing `dataset/train` directory. The sample is not a quality-labeled validation set, and no clinical validation was performed.

## Test cases

The test file `tests/test_quality_analyzer.py` covers:

1. Normal retinal-like image.
2. Blurred retinal-like image.
3. Dark image.
4. Overexposed image.
5. Low-contrast image.
6. Low-resolution image.
7. Invalid image input.

Additional API checks covered a valid project retinal image, unsupported MIME type, and corrupted image bytes.

## Test results

### Unit/synthetic quality tests

Command:

```powershell
python -m pytest -q tests/test_quality_analyzer.py
```

Result: `7 passed`.

Representative synthetic outputs after the final heuristic adjustment:

| Scenario | Status | Focus | Brightness | Contrast | Warnings |
| --- | --- | ---: | ---: | ---: | ---: |
| Normal retinal-like | BORDERLINE | 185.2504 | 36.1182 | 49.3633 | 1 |
| Blurred | POOR | 0.4016 | 36.1070 | 47.3459 | 2 |
| Dark | POOR | 0.0000 | 0.0000 | 0.0000 | 4 |
| Overexposed | POOR | 0.0000 | 255.0000 | 0.0000 | 3 |
| Low contrast | POOR | 0.0000 | 80.0000 | 0.0000 | 2 |
| Low resolution | POOR | 1793.9883 | 36.3330 | 49.5975 | 2 |

The existing sample `test_images/000c1434d8d7.png` returned `BORDERLINE`, with resolution 3216x2136, focus 6.2588, brightness 51.3887, and contrast 31.3033.

### API tests

Using `httpx.AsyncClient` with FastAPI ASGI transport and the project virtual environment:

- `POST /api/quality/analyze` with the existing sample: HTTP 200, quality status `BORDERLINE`.
- Unsupported `text/plain` upload: HTTP 415.
- Corrupted image bytes with image MIME type: HTTP 400.
- Existing `POST /api/analyze`: HTTP 200 with `quality`, `prediction`, `gradcam`, `similar_cases`, `progression_map`, and `progression_simulation`; optional errors were empty for the sample run.
- `GET /api/health`: HTTP 200 with `{"status": "ok"}`.

### Frontend build

Command:

```powershell
cd frontend
npm run build
```

Result: Vite production build passed.

### PDF regression

Using the project virtual environment, the existing report route returned HTTP 200 with `application/pdf` and a 1,836-byte PDF for a generated analysis ID.

The system Python environment lacks ReportLab, so a report check run outside the project virtual environment returned HTTP 500. This is an environment dependency issue in the unchanged baseline report module; the project virtual environment check passed.

## Regression testing

- DR prediction: PASS. Existing sample classified as Grade 2 / Moderate with the active `dr_model.pth` path; the full API response retained prediction fields.
- Confidence: PASS. Existing prediction confidence field remained present and unchanged in the full analysis response.
- Grad-CAM: PASS. Existing full analysis response included Grad-CAM output with no optional processing errors.
- Similar cases: PASS. Existing full analysis response included `similar_cases`.
- Progression map: PASS. Existing full analysis response included `progression_map`.
- Progression simulation: PASS. Existing full analysis response included `progression_simulation`.
- PDF: PASS in the project virtual environment; baseline dependency is absent from system Python.
- Existing API routes: PASS for health, analyze, quality, and report smoke checks.
- React frontend: PASS. Vite production build completed successfully.
- Existing React navigation and unrelated components: preserved; no redesign or later-phase component was added.

The first frontend build attempt exposed a duplicate export in the pre-existing `ImageQualityCard.jsx`; the file already contained an unused older implementation. It was consolidated into the single active cautious implementation so the build could pass.

## Limitations

- Thresholds are heuristic/experimental and not clinically validated.
- The threshold sample was 200 training images, not a quality-labeled validation cohort.
- Image source, camera, field-of-view, compression, and acquisition domain differences can change all raw metrics.
- Variance of Laplacian is affected by image size, texture, and compression and is not a clinical focus grader.
- Brightness and contrast summaries can be influenced by the dark fundus surround.
- Field-of-view and retinal visibility are simple image-level estimates; no optic-disc, vessel, lesion, or retinal anatomy segmentation was implemented.
- The quality result is advisory and does not block or alter DR prediction.
- Existing analysis state remains process-local as documented by Phase 1.

## Files added

- `backend/quality/__init__.py`
- `backend/quality/quality_analyzer.py`
- `tests/test_quality_analyzer.py`
- `PHASE_2_IMAGE_QUALITY_CHECKPOINT.md`

## Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/components/ImageQualityCard.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No classifier, checkpoint, Grad-CAM implementation, retrieval module, progression module, PDF generator, dataset, or existing test script was modified.

## Phase boundary

Phase 3 was not implemented. No adaptive enhancement, uncertainty/reliability scoring, vessel segmentation, lesion detection, disease landscape, Digital Twin, what-if prediction, or telemedicine simulation was added.
