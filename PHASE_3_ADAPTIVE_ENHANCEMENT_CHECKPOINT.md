# Phase 3 — Adaptive Image Enhancement

## Objective

Add a conservative, adaptive enhancement preview after Phase 2 image-quality assessment. Enhancement is attempted only when Phase 2 reports `BORDERLINE` or `POOR`; `GOOD` images bypass enhancement. The original image remains the input to the existing DR classifier, Grad-CAM, retrieval, progression, and PDF workflow.

No Phase 4 or later feature was implemented.

## Enhancement methods investigated

The existing project and Phase 2 implementation use OpenCV image-level metrics. Candidate methods considered for this phase were CLAHE, illumination normalization, denoising, and brightness correction.

Only CLAHE was implemented. It is applied conservatively to the luminance channel in LAB color space with `clipLimit=1.5` and an 8x8 tile grid. No neural enhancement model, aggressive sharpening, denoising, or color-channel transformation was added.

Images with no measurable structure or dimensions too small for a useful preview are not enhanced. They retain the original quality result and receive a reacquisition recommendation.

## Methods implemented

Module:

- `backend/enhancement/image_enhancer.py`
- `backend/enhancement/__init__.py`

Public function:

```python
enhance_image(image, quality_result)
```

The module reuses `backend.quality.analyze_image_quality()` for both original and candidate metrics. It returns:

- `attempted`
- `method`
- `improved`
- `accepted`
- `original_quality`
- `enhanced_quality`
- metric `changes`
- candidate image for controlled preview storage
- recommendation and decision message

## Decision logic

```text
Phase 2 status GOOD
-> do not attempt enhancement
-> retain original image

Phase 2 status BORDERLINE or POOR
-> create conservative CLAHE candidate
-> reassess candidate with Phase 2 analyzer
-> compare original and candidate metrics
-> accept preview only as an improved candidate when criteria pass
-> never use candidate for DR inference
```

For the candidate to be considered improved:

1. Enhanced quality status must improve, or at least two relevant metrics must improve while the overall status stays the same.
2. The focus metric must not materially deteriorate. The acceptance floor is 80% of the original variance-of-Laplacian value.
3. If focus safety fails, the candidate is rejected even if contrast or brightness increases.
4. A higher contrast or brightness value alone is not treated as improvement.

The `accepted` flag describes the quality-preview decision only. It does not authorize replacing the classifier input.

## Quality comparison methodology

The original and candidate are both passed through the existing Phase 2 analyzer. Comparisons include:

- Focus: variance of Laplacian delta.
- Contrast: grayscale standard-deviation delta.
- Illumination: grayscale-mean delta.
- Retinal visibility: estimated visible-fraction delta.
- Field of view: reported in each quality object; enhancement does not claim to improve field coverage.
- Overall status: Phase 2 heuristic status before and after.

Example real-image result for `test_images/000c1434d8d7.png`:

- Original status: `BORDERLINE`.
- Enhancement: attempted with CLAHE.
- Focus delta: `+28.5132`.
- Contrast delta: `+2.3651`.
- Illumination delta: `+7.0027`.
- Retinal visibility delta: `-0.0001`.
- Candidate decision: improved under the experimental comparison.

The result is a quality-metric comparison, not evidence of improved DR classification or diagnostic accuracy.

## Acceptance/rejection criteria

- GOOD input: no candidate is created; `attempted=false`, `accepted=false`, and the original-image recommendation is returned.
- BORDERLINE/POOR input with recoverable image structure: CLAHE candidate is generated and reassessed.
- Flat or too-small POOR input: enhancement is not attempted because a useful preview cannot be justified; recapture is recommended.
- Candidate with material focus loss: rejected.
- Candidate with no meaningful status or multi-metric improvement: reported as no improvement.
- Candidate with acceptable focus safety and status or multi-metric improvement: accepted as an enhanced preview only.
- Invalid or too-small input: returns an API error and does not replace the original.

## Real retinal image results

A sequential sample of the first 100 images in `dataset/train` was processed without modifying source files:

- 58 images were `GOOD` and correctly bypassed enhancement.
- 42 `BORDERLINE`/`POOR` images were enhanced and passed the experimental improvement rule.
- 0 real-image candidates in this sample were rejected for no improvement.

The first 12-image trace included both bypass and attempted cases:

- `000c1434d8d7.png`: BORDERLINE, attempted, improved.
- `001639a390f0.png`: POOR, attempted, improved.
- `0024cdab0c1e.png`: BORDERLINE, attempted, improved.
- `002c21358ce6.png`: GOOD, bypassed.
- `005b95c28852.png`: BORDERLINE, attempted, improved.
- `0083ee8054ee.png`: GOOD, bypassed.
- `0097f532ac9f.png`: POOR, attempted, improved.
- `00a8624548a9.png`: POOR, attempted, improved.
- `00b74780d31d.png`: POOR, attempted, improved.
- `00cc2b75cddd.png`: GOOD, bypassed.

This sample is not a clinical validation set and was not used to claim diagnostic improvement.

## Synthetic test results

Synthetic tests were used only for algorithmic sanity checks:

- Good textured image: enhancement bypassed.
- Retinal-like borderline image: candidate generated and reassessed.
- Low-contrast textured image: candidate comparison returned a boolean decision without claiming success.
- Dark, overexposed, and too-small images: enhancement was declined when no useful structure or preview could be justified.
- Uneven illumination image: CLAHE was attempted and the result was reported without claiming improvement.
- Blurred retinal-like image: candidate generated and focus delta reported.
- Invalid image: rejected with `ValueError`.

The test suite also retains all Phase 2 cases for dark, overexposed, low-contrast, low-resolution, and invalid images. Synthetic behavior must not be interpreted as clinical performance.

## API

### Existing `POST /api/analyze`

Adds an additive `enhancement` object after Phase 2 quality analysis. The existing classifier continues to receive `uploaded.png`, the original image written by the existing pipeline.

When enhancement is attempted, controlled assets are stored in the existing process-local analysis directory and returned as:

- `original_image_url`
- `enhanced_image_url`

The original `quality`, `prediction`, `gradcam`, `similar_cases`, `progression_map`, `progression_simulation`, `progression_prediction`, and `errors` fields remain present.

### New `POST /api/quality/enhance`

Request:

- Multipart image field `file`.

Response:

- `enhancement` comparison object.
- Original and enhanced preview URLs when a candidate is attempted.
- Original and enhanced quality measurements.
- Metric changes, method, improvement decision, and recommendation.

Errors:

- Unsupported MIME type: HTTP 415.
- Invalid/corrupted/too-small image: HTTP 400.
- Processing failure: HTTP 500 with a non-fatal enhancement-unavailable message.

## Frontend

Updated the existing `ImageQualityCard` rather than redesigning the application.

The card now displays:

- Whether enhancement was required.
- Original and enhanced preview images when available.
- Focus, contrast, and illumination original-versus-enhanced values.
- Method used.
- Improvement or no-improvement result.
- Recommendation that the original remains the DR model input.

No enhancement failure crashes the existing result view. Existing loading/error behavior remains compatible with the quality card.

## Regression testing

### Automated tests

Command:

```powershell
python -m pytest -q tests/test_quality_analyzer.py tests/test_image_enhancement.py tests/test_enhancement_api.py
```

Result: `18 passed`.

### Frontend

Command:

```powershell
cd frontend
npm run build
```

Result: Vite production build passed.

### Existing API regression

The existing `/api/analyze` was exercised with `test_images/000c1434d8d7.png` after integration:

- HTTP 200: PASS.
- DR prediction Grade 2 / Moderate: PASS.
- Confidence 100.0: PASS and unchanged from baseline smoke output.
- Grad-CAM field and asset: PASS.
- Similar cases: PASS.
- Progression map: PASS.
- Progression simulation: PASS.
- Additive enhancement metadata: PASS.
- Original and enhanced preview assets returned HTTP 200: PASS.

The existing health route and PDF route were previously verified in the project virtual environment during Phase 2. No classifier, Grad-CAM, retrieval, progression, or report implementation was modified in Phase 3.

## Limitations

- CLAHE parameters and acceptance bands are engineering heuristics, not clinically validated thresholds.
- Phase 2 quality metrics themselves are heuristic and not clinical gradability measures.
- Improved visual or metric quality does not prove improved DR classification, calibration, or diagnostic accuracy.
- The quality analyzer's focus metric can respond to texture and noise; the focus-safety check reduces but does not eliminate this risk.
- Field-of-view coverage cannot be repaired by CLAHE; the enhancement does not claim to improve it.
- A 100-image real retinal sample is not a representative validation cohort and contained no rejected real-image candidates.
- Enhancement previews are stored using the existing process-local analysis asset mechanism; long-term cleanup and persistence remain baseline concerns.
- The enhanced candidate is never sent to the existing DR model in this phase.
- Camera, acquisition, compression, illumination, and domain differences may change results.
- No clinical reader study or external benchmark was performed.

## Files added

- `backend/enhancement/__init__.py`
- `backend/enhancement/image_enhancer.py`
- `tests/test_image_enhancement.py`
- `tests/test_enhancement_api.py`
- `PHASE_3_ADAPTIVE_ENHANCEMENT_CHECKPOINT.md`

## Files modified

- `backend/main.py`
- `frontend/src/App.jsx`
- `frontend/src/components/ImageQualityCard.jsx`
- `frontend/src/services/api.ts`
- `frontend/src/types.ts`
- `frontend/src/styles.css`

No model weights, training datasets, EfficientNet code, prediction logic, Grad-CAM implementation, retrieval engine, progression engine, or PDF generator was modified.
