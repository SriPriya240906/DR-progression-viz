# CURRENT SYSTEM BASELINE

Inspection date: 2026-09-16

This document records the existing working baseline. Inspection was read-only except for creation of this report. No application code, model, dataset, test, configuration, or generated artifact was modified. No new feature was implemented.

## 1. Backend architecture

The active backend is FastAPI in `backend/main.py`, launched by `run_api.ps1` with Uvicorn on port 8000. It imports the root classifier from `model.py`, retrieval modules from `retrieval_engine/`, Grad-CAM from `progression_engine/gradcam.py`, and PDF generation from `utils/pdf_report.py`.

The backend creates an in-memory `analyses` registry and an analysis directory under `outputs/api_results/<analysis_id>/`. Uploaded and generated image assets are copied there and served through a registered-asset image route. Analysis metadata is not persisted outside the running process.

Other runtime or alternate layers present in the repository:

- Legacy Streamlit entry point: `app.py`.
- Alternate prediction scripts: `prediction/`.
- Training scripts: `training/` and root-level `train.py`.
- Preprocessing modules: `preprocessing/`.
- Progression-engine training/generation modules: `progression_engine/`.
- Root-level legacy helpers: `dataset.py`, `progression_model.py`, `retrieval_engine.py`, `evaluate.py`.

The FastAPI path does not use every module or checkpoint in the repository.

## 2. Frontend architecture

The active frontend is a Vite React application under `frontend/`.

- Entry point: `frontend/src/main.jsx`.
- Main application page and state owner: `frontend/src/App.jsx`.
- Routing: no React Router; navigation uses hash anchors for Assessment, Progression, Similar Cases, Explainability, and Report.
- Upload: `frontend/src/components/ImageUpload.jsx`.
- Prediction: `PredictionCard.jsx`.
- Grad-CAM: `GradCAMViewer.jsx`.
- Similar cases: `SimilarCases.jsx`.
- Progression map: `ProgressionMap.jsx`.
- Report: `ReportPanel.jsx` plus the report handler in `App.jsx`.
- Loading/error states: `LoadingState.jsx` and `ErrorState.jsx`.
- Central CSS/UI: `frontend/src/styles.css`.
- Type contracts: `frontend/src/types.ts`.
- Active API client: `frontend/src/services/api.ts`.
- Duplicate older API wrapper, not imported by `App.jsx`: `frontend/src/api.js`.

Defined but not mounted by the current `App.jsx` include `ProgressionSimulation`, `ImageQualityCard`, `TriageCard`, `EvidencePanel`, `WhatIfExplorer`, `DigitalTwinCard`, and `DiseaseLandscape`.

React state is local to `App`: selected file, preview URL, analysis payload, loading/error state, report loading state, and backend health status. The client sends `FormData` to FastAPI, normalizes the JSON response, stores it in React state, and renders the result components. Report generation sends JSON and receives a PDF blob.

## 3. API endpoints

### `GET /api/health`

- Handler: `backend.main.health()`.
- Request: none.
- Response: `{"status": "ok"}`.
- Downstream: none.
- Frontend caller: `getHealthStatus()` in `frontend/src/services/api.ts`.

### `POST /api/analyze`

- Handler: `backend.main.analyze(request, file)`.
- Request: multipart form with required `file: UploadFile`; the backend requires an `image/*` MIME type.
- Response: JSON containing `analysis_id`, `uploaded_image_url`, `prediction`, `gradcam`, `similar_cases`, `progression_map`, `progression_simulation`, optional `progression_prediction`, and `errors`.
- Downstream: `predict_details`, `generate_gradcam`, `search_similar_images`, `get_progression_map`, `simulate_progression`, and conditional `predict_progression`.
- Frontend caller: `analyzeRetinalImage()` in `frontend/src/services/api.ts`.

### `GET /api/results/{analysis_id}/images/{asset_name}`

- Handler: `backend.main.get_image(analysis_id, asset_name)`.
- Request: analysis ID and registered asset name in the URL.
- Response: `FileResponse` for an asset registered in the process-local `AnalysisRecord`.
- Downstream: filesystem read from the analysis directory.
- Used for uploaded, Grad-CAM, similar-case, stage, and simulation image URLs.

### `POST /api/report/{analysis_id}`

- Handler: `backend.main.report(analysis_id, data)`.
- Request: JSON dictionary. Current frontend supplies `grade`, `confidence`, `risk`, `progression`, and `recommendation`.
- Response: PDF `FileResponse` named `DR_Report.pdf`.
- Downstream: `utils.pdf_report.generate_pdf_report()`.
- Frontend caller: `generateReport()` in `frontend/src/services/api.ts`.

CORS currently allows localhost ports 5173 and 5175. No API route was changed.

## 4. DR prediction pipeline

The active execution flow is:

1. `ImageUpload.jsx` selects a PNG/JPG/JPEG and `App.handleAnalyze()` calls `analyzeRetinalImage()`.
2. `frontend/src/services/api.ts` sends the file as multipart field `file` to `/api/analyze`.
3. `backend.main.analyze()` validates the MIME prefix, creates an analysis ID, and writes the upload to `outputs/api_results/<analysis_id>/uploaded.png`.
4. `cv2.imread()` validates that the written file is readable.
5. `model.predict_details()` loads the image, preprocesses it, runs EfficientNet-B0, applies softmax, selects the argmax class, calculates confidence, and returns class probabilities.
6. `backend.main` adds API labels and risk level, then independently attempts Grad-CAM, similar-case search, progression mapping, progression simulation, and optional progression classification.
7. Generated assets are copied into the analysis directory and exposed through the image route.
8. The combined response is normalized by the React API client and rendered by the components.

Optional downstream failures are caught and returned in `errors`; upload and classifier failures fail the request.

## 5. Model/checkpoint

The active classifier is defined and loaded in `model.py`:

- Architecture: `timm.create_model("efficientnet_b0", pretrained=False)`.
- Classifier head: `nn.Linear(model.classifier.in_features, 5)`.
- Active checkpoint: root-level `dr_model.pth`.
- Loading: `torch.load("dr_model.pth", map_location=device)` at module import.
- Device: CUDA when available, otherwise CPU.
- Prediction function: `predict(image_path)`.
- API prediction function: `predict_details(image_path)`.

Class mapping is:

- 0: No DR / No Diabetic Retinopathy
- 1: Mild
- 2: Moderate
- 3: Severe
- 4: Proliferative DR

The API maps these grades to Low, Moderate, High, Very High, and Critical risk levels. Confidence is the winning softmax probability multiplied by 100 and rounded to two decimals. It is not calibrated confidence.

There is a separate classifier/training path in `training/train_classifier.py` that saves `models/dr_classifier.pth`; it is not used by the active FastAPI API.

## 6. Image preprocessing

Active inference preprocessing in `model.py`:

```text
PIL.Image.open(path).convert("RGB")
Resize((224, 224))
ToTensor()
```

No ImageNet normalization is applied by the active API classifier. `progression_engine/gradcam.py` uses the same transform. Retrieval feature extraction in `retrieval_engine/feature_extractor.py` also uses RGB, resize to 224x224, and `ToTensor()` with no normalization.

The training loader in `preprocessing/dataset_loader.py` additionally applies random horizontal flip, random rotation, and ImageNet normalization. This is a baseline risk because the active inference transform does not match that loader's normalization behavior. The root `dataset.py` is a separate loader and should not be assumed to describe the active API checkpoint without further provenance.

## 7. Grad-CAM

Active function: `progression_engine.gradcam.generate_gradcam(image_path)`.

- Input: uploaded image path.
- Dependencies: global classifier and device from `model.py`, TorchVision transforms, `pytorch_grad_cam.GradCAM`, OpenCV/PIL/NumPy.
- Target layer: `model.conv_head`, the EfficientNet-B0 final convolution block used here.
- Output: a 224x224 RGB heatmap overlay returned as a NumPy array.
- API behavior: writes `gradcam.png` and returns its registered URL.
- Frontend behavior: `GradCAMViewer` displays the returned overlay as “Original / overlay”; the backend does not return separate original and heatmap images.

Failures are non-fatal and appear in the API `errors` array.

## 8. Similar cases

`retrieval_engine/feature_extractor.py::extract_features()` uses a separate ImageNet-pretrained EfficientNet-B0 with its classifier replaced by `nn.Identity()`. It returns a NumPy embedding.

`retrieval_engine/similarity_search.py::search_similar_images(image_path, top_k=5)` loads `retrieval_engine/index/grade0..4_features.npy` and matching path arrays, calculates cosine similarity, sorts globally, and returns the five highest-scoring `(score, path)` pairs.

`backend.main.serialize_case()` copies each valid image into the analysis directory and returns its URL, similarity, and grade inferred from a `grade0`-through-`grade4` path segment.

## 9. Progression

`retrieval_engine/progression_search.py::get_progression_map(image_path, top_k=3)` computes the same retrieval embedding and returns up to three nearest reference cases independently for each grade. The backend serializes them under `stage_0` through `stage_4` with labels.

`retrieval_engine/progression_simulator.py::simulate_progression(image_path)` chooses one nearest indexed reference image for each available grade and returns `grade`, `image`, and `score`. These are case-based reference images, not generated images or a longitudinal prediction of the uploaded patient. Existing diffusion, pix2pix, UNet, and autoencoder artifacts are not used by this active API path.

The optional `retrieval_engine/progression_model.py::predict_progression()` loads `retrieval_engine/progression_model.pkl`, predicts from the retrieval embedding, and returns current grade, next likely stage, and probabilities. It is a persisted stage classifier, not a validated longitudinal progression model. The root-level `progression_model.py` is a separate inactive implementation for this API.

The frontend currently renders `ProgressionMap`; `ProgressionSimulation.jsx` exists but is not mounted in `App.jsx`.

## 10. PDF report

`backend.main.report()` calls `utils/pdf_report.py::generate_pdf_report(output_path, data)` after checking the analysis ID. The generator requires ReportLab and writes a simple PDF containing:

- Title and timestamp.
- Predicted grade.
- Confidence.
- Risk level.
- Supplied progression value.
- Clinical recommendation.

The current frontend sends `progression: null` and a fixed research-prototype recommendation. The report does not currently embed the uploaded image, Grad-CAM, similar cases, or progression images.

## 11. Existing datasets and artifacts

Verified inventory from the workspace:

- `dataset/`: 3,664 files, including `train.csv` and the populated `train/` image set.
- `dataset/valid/` and `dataset/test/`: present but empty on inspection.
- `dataset/pix2pix/`: present.
- `datasets/aptos/`, `datasets/ddr/`, `datasets/eyepacs/`, and `datasets/idrid/`: present but empty on inspection.
- `progression_database/grade0` through `grade4`: directories present; no image files were listed there.
- `retrieval_engine/index/`: ten feature/path `.npy` files for grades 0 through 4.
- `test_images/000c1434d8d7.png`: existing sample image.
- Active classifier checkpoint: `dr_model.pth`.
- Alternate classifier checkpoint: `models/dr_classifier.pth`.
- Progression-engine checkpoint: `progression_engine/retina_unet.pth`.
- Optional progression model: `retrieval_engine/progression_model.pkl`.
- Inactive risk artifact: `models/risk_model/risk_model.json`.
- Runtime outputs: `outputs/` contains existing API and generated artifacts.
- `uploads/` and `reports/` were present with no files listed during inventory.

No data was downloaded, deleted, or regenerated.

## 12. Existing tests and baseline checks

There is no dedicated `tests/` directory and no pytest-style assertion suite. Existing scripts include:

- `training/test_dataset.py`: dataset loader smoke test.
- `test_feature.py` and `retrieval_engine/test_feature.py`: feature extraction smoke tests.
- `test_similarity.py`: retrieval smoke test.
- `test_gradcam.py`: writes a Grad-CAM artifact.
- `run.py`: classifier inference smoke test.
- `run_safe_test.py`: writes generated progression images.
- `run_test.py`: progression test script with output behavior and a referenced test image dependency.
- `evaluate.py`: full evaluation behavior.

Safe checks run during this inspection:

- `python training/test_dataset.py` passed: dataset size 3,662; first tensor shape `torch.Size([3, 224, 224])`; first label `2`.
- `python -c "from model import predict_details; ..."` passed against `test_images/000c1434d8d7.png`: Grade 2 / Moderate; confidence 100.0% under the current model output.

No server was started, no frontend build was run, no writing test scripts were run, and no tests were modified. Image upload, Grad-CAM, retrieval, progression, PDF, and frontend/backend integration have scripts or live paths but do not have a comprehensive automated integration test in the repository.

## 13. Files that must NOT be modified during enhancement

The following protected baseline surfaces must retain their current behavior and contracts unless a future instruction explicitly approves a migration:

- `model.py` and the active `dr_model.pth` checkpoint.
- Existing request/response behavior in `backend/main.py`, especially `/api/analyze` and its current prediction fields.
- Existing retrieval index files under `retrieval_engine/index/`.
- Existing retrieval and progression behavior in `retrieval_engine/`.
- Existing Grad-CAM behavior in `progression_engine/gradcam.py`.
- Existing report generation behavior in `utils/pdf_report.py`.
- Existing frontend upload, prediction, Grad-CAM, similar-case, progression, and report components.
- Existing datasets, checkpoints, generated outputs, and test scripts.

Enhancements should be additive and should preserve current fields and routes.

## 14. Safe extension points

The cleanest additive boundaries are:

- Backend orchestration: add an isolated result-producing step in `backend.main.analyze()` after `cv2.imread()` validation and before `predict_details()`, while preserving the current prediction and error behavior.
- API contract: add optional response fields rather than changing existing fields or routes.
- Frontend contract: extend `frontend/src/types.ts`, normalize optional fields in `frontend/src/services/api.ts`, and add a dedicated result component without redesigning the existing page.
- Reports: pass optional new data through the existing report request only after the API contract is stable.
- Tests: add isolated checks around the new result function and response normalization before any integration wiring.

## 15. Potential risks

- The classifier checkpoint's training provenance and validation quality are not documented.
- Active inference does not use the normalization used by `preprocessing/dataset_loader.py`.
- Relative model/index paths depend on starting the process from the repository root.
- Retrieval index provenance and preprocessing are not stored with the embeddings.
- The process-local analysis registry loses image/report lookup state after an API restart.
- Confidence is raw maximum softmax probability and is not calibrated.
- Progression outputs are reference retrievals, not patient-specific longitudinal forecasts.
- The frontend contains future-oriented types/components whose contracts are not active backend behavior.
- Optional feature failures are intentionally swallowed into `errors`, so consumers must inspect that field.
- Importing the API loads heavy ML dependencies and models at module import time.

## Recommended Phase 2 integration point

For the next enhancement phase, the recommended integration point is the existing `backend.main.analyze()` orchestration immediately after the uploaded file passes `cv2.imread()` validation and before `model.predict_details()` runs. A new isolated analysis function can receive the validated image path and return an optional result; the current classifier and all existing downstream stages can remain unchanged. The result can then be exposed as an additive response field, normalized in `frontend/src/services/api.ts`, and displayed by a new component in the existing `App.jsx` flow.

This recommendation is an architectural boundary only. No Image Quality Assessment, uncertainty, vessel analysis, lesion detection, Digital Twin, or other enhancement was implemented in Phase 1.