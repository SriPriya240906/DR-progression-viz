import logging
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from fastapi import Body, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from model import predict_details
from backend.enhancement import enhance_image
from backend.disease_landscape import build_disease_landscape
from backend.evidence import build_evidence_summary
from backend.lesions import analyze_lesion_candidates
from backend.quality import analyze_image_quality
from backend.reliability import analyze_prediction_reliability
from backend.structure import analyze_retinal_structure
from progression_engine.gradcam import generate_gradcam
from retrieval_engine.progression_search import get_progression_map
from retrieval_engine.progression_simulator import simulate_progression
from retrieval_engine.similarity_search import search_similar_images
from utils.pdf_report import generate_pdf_report

try:
    from retrieval_engine.progression_model import predict_progression
except Exception:
    predict_progression = None


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dr-progressionviz-api")

ROOT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT_DIR / "outputs" / "api_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

GRADE_LABELS = {
    0: "No Diabetic Retinopathy",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR",
}

RISK_LEVELS = {
    0: "Low",
    1: "Moderate",
    2: "High",
    3: "Very High",
    4: "Critical",
}


@dataclass
class AnalysisRecord:
    directory: Path
    assets: dict[str, Path] = field(default_factory=dict)


analyses: dict[str, AnalysisRecord] = {}

# Workflow state tracking for staged analysis
@dataclass
class WorkflowState:
    analysis_id: str
    uploaded_image_path: Path
    quality_result: dict[str, Any] | None = None
    enhancement_result: dict[str, Any] | None = None
    original_prediction: dict[str, Any] | None = None
    enhanced_prediction: dict[str, Any] | None = None
    structure_result: dict[str, Any] | None = None
    lesion_evidence: dict[str, Any] | None = None
    gradcam_result: dict[str, Any] | None = None
    reliability_result: dict[str, Any] | None = None
    similar_cases: list[dict[str, Any]] | None = None
    progression_map: dict[str, dict[str, Any]] | None = None
    progression_simulation: list[dict[str, Any]] | None = None
    progression_prediction: dict[str, Any] | None = None
    disease_landscape: dict[str, Any] | None = None
    evidence_summary: dict[str, Any] | None = None
    errors: list[dict[str, str]] = field(default_factory=list)

workflow_states: dict[str, WorkflowState] = {}

app = FastAPI(title="DR ProgressionViz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def public_url(request: Request, analysis_id: str, asset_name: str) -> str:
    return str(
        request.url_for(
            "get_image",
            analysis_id=analysis_id,
            asset_name=asset_name,
        )
    )


def copy_asset(
    record: AnalysisRecord,
    source: str | Path,
    asset_name: str,
) -> bool:
    source_path = Path(source).resolve()

    if (
        not source_path.is_file()
        or source_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}
    ):
        logger.warning("Skipping unavailable image asset: %s", source)
        return False

    destination = record.directory / asset_name
    shutil.copy2(source_path, destination)
    record.assets[asset_name] = destination

    return True


def add_error(
    errors: list[dict[str, str]],
    feature: str,
    exc: Exception,
) -> None:
    logger.exception("%s failed", feature)
    errors.append(
        {
            "feature": feature,
            "message": str(exc),
        }
    )


def source_grade(source: str | Path) -> int | None:
    match = re.search(
        r"(?:^|[\\/])grade([0-4])(?:[\\/]|$)",
        str(source),
        re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


def serialize_case(
    request: Request,
    record: AnalysisRecord,
    analysis_id: str,
    source: str | Path,
    similarity: float,
    asset_name: str,
) -> dict[str, Any] | None:
    if not copy_asset(record, source, asset_name):
        return None

    return {
        "image_url": public_url(
            request,
            analysis_id,
            asset_name,
        ),
        "similarity": round(float(similarity), 4),
        "grade": source_grade(source),
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload")
def upload_image(request: Request, file: UploadFile = File(...)) -> dict[str, Any]:
    """Stage 1: Upload image and initialize analysis session"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Upload a PNG, JPG, or JPEG retinal image.")

    analysis_id = uuid.uuid4().hex
    record = AnalysisRecord(RESULTS_DIR / analysis_id)
    record.directory.mkdir(parents=True, exist_ok=True)
    analyses[analysis_id] = record
    
    input_path = record.directory / "uploaded.png"
    
    try:
        with input_path.open("wb") as output:
            shutil.copyfileobj(file.file, output)
        
        image = cv2.imread(str(input_path))
        if image is None:
            raise ValueError("The uploaded file is not a readable image.")
        
        record.assets["uploaded.png"] = input_path
        
        # Initialize workflow state
        workflow_states[analysis_id] = WorkflowState(
            analysis_id=analysis_id,
            uploaded_image_path=input_path
        )
        
        return {
            "analysis_id": analysis_id,
            "uploaded_image_url": public_url(request, analysis_id, "uploaded.png"),
            "message": "Image uploaded successfully. Ready for quality analysis."
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Image upload failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/analyze-quality/{analysis_id}")
def analyze_quality_stage(request: Request, analysis_id: str) -> dict[str, Any]:
    """Stage 1: Analyze image quality and enhancement"""
    record = analyses.get(analysis_id)
    workflow_state = workflow_states.get(analysis_id)
    
    if not record or not workflow_state:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    
    try:
        image = cv2.imread(str(workflow_state.uploaded_image_path))
        if image is None:
            raise ValueError("Could not read uploaded image.")
        
        # Image quality analysis - preserve existing functionality
        quality = None
        try:
            quality = analyze_image_quality(image)
            workflow_state.quality_result = quality
        except Exception as exc:
            add_error(workflow_state.errors, "image_quality", exc)
        
        # Adaptive enhancement - preserve existing functionality  
        enhancement = None
        if quality:
            try:
                enhancement = _serialize_enhancement(
                    request,
                    record,
                    enhance_image(image, quality),
                )
                workflow_state.enhancement_result = enhancement
            except Exception as exc:
                add_error(workflow_state.errors, "adaptive_enhancement", exc)
        
        return {
            "analysis_id": analysis_id,
            "uploaded_image_url": public_url(request, analysis_id, "uploaded.png"),
            "quality": quality,
            "enhancement": enhancement,
            "errors": workflow_state.errors,
            "ready_for_prediction": quality is not None
        }
        
    except Exception as exc:
        logger.exception("Quality analysis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/predict-disease/{analysis_id}")
def predict_disease_stage(request: Request, analysis_id: str) -> dict[str, Any]:
    """Stage 2: Disease prediction with dual prediction logic"""
    record = analyses.get(analysis_id)
    workflow_state = workflow_states.get(analysis_id)
    
    if not record or not workflow_state:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    
    if not workflow_state.quality_result:
        raise HTTPException(status_code=400, detail="Quality analysis must be completed first.")
    
    try:
        image = cv2.imread(str(workflow_state.uploaded_image_path))
        if image is None:
            raise ValueError("Could not read uploaded image.")
        
        # Helper function to build prediction (preserve existing logic)
        def build_prediction(prediction_path: Path) -> dict[str, Any]:
            prediction_details = predict_details(str(prediction_path))
            prediction_grade = int(prediction_details["grade"])
            return {
                **prediction_details,
                "grade": prediction_grade,
                "label": GRADE_LABELS.get(prediction_grade, prediction_details.get("label", "Unknown")),
                "risk_level": RISK_LEVELS.get(prediction_grade, "Unknown"),
            }
        
        # Always run original image prediction
        original_prediction = build_prediction(workflow_state.uploaded_image_path)
        workflow_state.original_prediction = original_prediction
        
        # For BORDERLINE/POOR quality, also run enhanced prediction
        enhanced_prediction = None
        quality_status = workflow_state.quality_result.get("status", "POOR")
        
        if quality_status != "GOOD" and workflow_state.enhancement_result:
            enhanced_path = record.directory / "enhanced-preview.png"
            if enhanced_path.is_file():
                try:
                    enhanced_prediction = build_prediction(enhanced_path)
                    workflow_state.enhanced_prediction = enhanced_prediction
                except Exception as exc:
                    add_error(workflow_state.errors, "enhanced_prediction", exc)
        
        # Reliability analysis - preserve existing functionality
        reliability = None
        try:
            reliability = analyze_prediction_reliability(
                original_prediction["probabilities"],
                predicted_index=original_prediction["grade"],
                predicted_label=original_prediction["label"],
            )
            workflow_state.reliability_result = reliability
        except Exception as exc:
            add_error(workflow_state.errors, "reliability", exc)
        
        # Retinal structure analysis - preserve existing functionality
        structure = None
        try:
            structure = _serialize_structure(request, record, analyze_retinal_structure(image))
            workflow_state.structure_result = structure
        except Exception as exc:
            add_error(workflow_state.errors, "retinal_structure", exc)
        
        # Lesion evidence analysis - preserve existing functionality
        lesion_evidence = None
        try:
            lesion_evidence = _serialize_lesion_evidence(request, record, analyze_lesion_candidates(image))
            workflow_state.lesion_evidence = lesion_evidence
        except Exception as exc:
            add_error(workflow_state.errors, "lesion_evidence", exc)
        
        # Grad-CAM - preserve existing functionality
        gradcam = {"available": False, "url": None}
        try:
            cam = generate_gradcam(str(workflow_state.uploaded_image_path))
            gradcam_path = record.directory / "gradcam.png"
            if not cv2.imwrite(str(gradcam_path), np.asarray(cam)):
                raise RuntimeError("Grad-CAM image could not be written.")
            record.assets["gradcam.png"] = gradcam_path
            gradcam = {"available": True, "url": public_url(request, analysis_id, "gradcam.png")}
            workflow_state.gradcam_result = gradcam
        except Exception as exc:
            add_error(workflow_state.errors, "gradcam", exc)
        
        return {
            "analysis_id": analysis_id,
            "uploaded_image_url": public_url(request, analysis_id, "uploaded.png"),
            "quality": workflow_state.quality_result,
            "enhancement": workflow_state.enhancement_result,
            "original_prediction": original_prediction,
            "enhanced_prediction": enhanced_prediction,
            "reliability": reliability,
            "structure": structure,
            "lesion_evidence": lesion_evidence,
            "gradcam": gradcam,
            "errors": workflow_state.errors,
            "ready_for_progression": True
        }
        
    except Exception as exc:
        logger.exception("Disease prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/disease-landscape")
def disease_landscape() -> dict[str, Any]:
    return {
        "disease_landscape": build_disease_landscape()
    }


@app.post("/api/analyze-progression/{analysis_id}")
def analyze_progression_stage(request: Request, analysis_id: str) -> dict[str, Any]:
    """Stage 3: Progression simulation and similar cases"""
    record = analyses.get(analysis_id)
    workflow_state = workflow_states.get(analysis_id)
    
    if not record or not workflow_state:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    
    if not workflow_state.original_prediction:
        raise HTTPException(status_code=400, detail="Disease prediction must be completed first.")
    
    try:
        # Similar cases - preserve existing functionality
        similar_cases: list[dict[str, Any]] = []
        try:
            for index, (score, path) in enumerate(search_similar_images(str(workflow_state.uploaded_image_path))):
                case = serialize_case(request, record, analysis_id, path, score, f"similar-{index}{Path(path).suffix.lower()}")
                if case:
                    similar_cases.append(case)
            workflow_state.similar_cases = similar_cases
        except Exception as exc:
            add_error(workflow_state.errors, "similar_cases", exc)
        
        # Progression map - preserve existing functionality
        progression_map: dict[str, dict[str, Any]] = {}
        try:
            raw_map = get_progression_map(str(workflow_state.uploaded_image_path))
            for stage in range(5):
                cases = []
                for index, (score, path) in enumerate(raw_map.get(stage, [])):
                    case = serialize_case(
                        request,
                        record,
                        analysis_id,
                        path,
                        score,
                        f"stage-{stage}-{index}{Path(path).suffix.lower()}",
                    )
                    if case:
                        cases.append(case)
                progression_map[f"stage_{stage}"] = {
                    "label": GRADE_LABELS[stage],
                    "cases": cases,
                }
            workflow_state.progression_map = progression_map
        except Exception as exc:
            add_error(workflow_state.errors, "progression_map", exc)
        
        # Progression simulation - preserve existing functionality
        simulation: list[dict[str, Any]] = []
        try:
            for index, step in enumerate(simulate_progression(str(workflow_state.uploaded_image_path))):
                source = step.get("image")
                if not source:
                    continue
                asset_name = f"simulation-{index}{Path(source).suffix.lower()}"
                if copy_asset(record, source, asset_name):
                    simulation.append(
                        {
                            **step,
                            "grade": int(step["grade"]),
                            "image_url": public_url(request, analysis_id, asset_name),
                        }
                    )
            workflow_state.progression_simulation = simulation
        except Exception as exc:
            add_error(workflow_state.errors, "progression_simulation", exc)
        
        # Progression prediction - preserve existing functionality
        progression_prediction = None
        if predict_progression:
            try:
                progression_prediction = predict_progression(str(workflow_state.uploaded_image_path))
                workflow_state.progression_prediction = progression_prediction
            except Exception as exc:
                add_error(workflow_state.errors, "progression_prediction", exc)
        
        # Disease landscape - preserve existing functionality
        try:
            disease_landscape_data = build_disease_landscape()
            workflow_state.disease_landscape = disease_landscape_data
        except Exception as exc:
            add_error(workflow_state.errors, "disease_landscape", exc)
        
        return {
            "analysis_id": analysis_id,
            "similar_cases": similar_cases,
            "progression_map": progression_map,
            "progression_simulation": {"available": bool(simulation), "results": simulation},
            "progression_prediction": progression_prediction,
            "disease_landscape": workflow_state.disease_landscape,
            "errors": workflow_state.errors,
            "ready_for_report": True
        }
        
    except Exception as exc:
        logger.exception("Progression analysis failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/generate-evidence-summary/{analysis_id}")
def generate_evidence_summary_stage(analysis_id: str) -> dict[str, Any]:
    """Generate evidence summary for completed analysis"""
    workflow_state = workflow_states.get(analysis_id)
    
    if not workflow_state:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    
    try:
        # Build comprehensive analysis payload for evidence summary
        analysis_payload = {
            "analysis_id": analysis_id,
            "prediction": workflow_state.original_prediction,
            "enhanced_prediction": workflow_state.enhanced_prediction,
            "quality": workflow_state.quality_result,
            "enhancement": workflow_state.enhancement_result,
            "reliability": workflow_state.reliability_result,
            "structure": workflow_state.structure_result,
            "lesion_evidence": workflow_state.lesion_evidence,
            "gradcam": workflow_state.gradcam_result,
            "similar_cases": workflow_state.similar_cases,
            "progression_map": workflow_state.progression_map,
            "progression_simulation": workflow_state.progression_simulation,
            "progression_prediction": workflow_state.progression_prediction,
            "disease_landscape": workflow_state.disease_landscape,
        }
        
        evidence_summary = build_evidence_summary(analysis_payload)
        workflow_state.evidence_summary = evidence_summary
        
        return {
            "analysis_id": analysis_id,
            "evidence_summary": evidence_summary
        }
        
    except Exception as exc:
        logger.exception("Evidence summary generation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/analysis/{analysis_id}")
def get_complete_analysis(request: Request, analysis_id: str) -> dict[str, Any]:
    """Get complete analysis results for report generation"""
    record = analyses.get(analysis_id)
    workflow_state = workflow_states.get(analysis_id)
    
    if not record or not workflow_state:
        raise HTTPException(status_code=404, detail="Analysis session not found.")
    
    return {
        "analysis_id": analysis_id,
        "uploaded_image_url": public_url(request, analysis_id, "uploaded.png"),
        "quality": workflow_state.quality_result,
        "enhancement": workflow_state.enhancement_result,
        "original_prediction": workflow_state.original_prediction,
        "enhanced_prediction": workflow_state.enhanced_prediction,
        "prediction": workflow_state.original_prediction,  # For backward compatibility
        "reliability": workflow_state.reliability_result,
        "structure": workflow_state.structure_result,
        "lesion_evidence": workflow_state.lesion_evidence,
        "evidence_summary": workflow_state.evidence_summary,
        "disease_landscape": workflow_state.disease_landscape,
        "gradcam": workflow_state.gradcam_result,
        "similar_cases": workflow_state.similar_cases,
        "progression_map": workflow_state.progression_map,
        "progression_simulation": {"available": bool(workflow_state.progression_simulation), "results": workflow_state.progression_simulation or []},
        "progression_prediction": workflow_state.progression_prediction,
        "errors": workflow_state.errors,
    }


def _decode_uploaded_image(contents: bytes) -> np.ndarray:
    image = cv2.imdecode(
        np.frombuffer(contents, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError("The uploaded file is not a readable image.")

    return image


def _serialize_enhancement(
    request: Request,
    record: AnalysisRecord,
    result: dict[str, Any],
    asset_name: str = "enhanced-preview.png",
) -> dict[str, Any]:
    preview = result.pop("image", None)

    if preview is not None:
        preview_path = record.directory / asset_name

        if not cv2.imwrite(
            str(preview_path),
            np.asarray(preview),
        ):
            raise RuntimeError(
                "Enhanced preview could not be written."
            )

        record.assets[asset_name] = preview_path

        result["enhanced_image_url"] = public_url(
            request,
            record.directory.name,
            asset_name,
        )

        original_asset = (
            "uploaded.png"
            if "uploaded.png" in record.assets
            else "original.png"
        )

        if original_asset in record.assets:
            result["original_image_url"] = public_url(
                request,
                record.directory.name,
                original_asset,
            )

    return result


def _serialize_structure(
    request: Request,
    record: AnalysisRecord,
    result: dict[str, Any],
    asset_name: str = "structure-overlay.png",
) -> dict[str, Any]:
    visualization = result.pop("_visualization", None)
    result.pop("_mask", None)

    if visualization is not None:
        overlay_path = record.directory / asset_name

        if not cv2.imwrite(
            str(overlay_path),
            np.asarray(visualization),
        ):
            raise RuntimeError(
                "Structure overlay could not be written."
            )

        record.assets[asset_name] = overlay_path

        result["overlay_image_url"] = public_url(
            request,
            record.directory.name,
            asset_name,
        )

    return result


def _serialize_lesion_evidence(
    request: Request,
    record: AnalysisRecord,
    result: dict[str, Any],
) -> dict[str, Any]:
    assets = {
        "dark": (
            "_dark_overlay",
            "lesion-dark-candidates.png",
        ),
        "bright": (
            "_bright_overlay",
            "lesion-bright-candidates.png",
        ),
        "combined": (
            "_combined_overlay",
            "lesion-combined-candidates.png",
        ),
    }

    for key, (private_key, asset_name) in assets.items():
        visualization = result.pop(private_key, None)

        if visualization is None:
            continue

        asset_path = record.directory / asset_name

        if not cv2.imwrite(
            str(asset_path),
            np.asarray(visualization),
        ):
            raise RuntimeError(
                f"Lesion {key} overlay could not be written."
            )

        record.assets[asset_name] = asset_path

        result.setdefault(
            "overlay_image_urls",
            {},
        )[key] = public_url(
            request,
            record.directory.name,
            asset_name,
        )

    result.pop("_dark_mask", None)
    result.pop("_bright_mask", None)
    result.pop("_fov_mask", None)

    return result


@app.post("/api/analyze")
def analyze(
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    analysis_id = uuid.uuid4().hex

    record = AnalysisRecord(
        RESULTS_DIR / analysis_id
    )

    record.directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    analyses[analysis_id] = record

    input_path = record.directory / "uploaded.png"

    errors: list[dict[str, str]] = []

    try:
        with input_path.open("wb") as output:
            shutil.copyfileobj(
                file.file,
                output,
            )

        image = cv2.imread(
            str(input_path)
        )

        if image is None:
            raise ValueError(
                "The uploaded file is not a readable image."
            )

        record.assets["uploaded.png"] = input_path

        # ---------------------------------------------------------
        # IMAGE QUALITY ANALYSIS
        # ---------------------------------------------------------

        quality = None

        try:
            quality = analyze_image_quality(image)
        except Exception as exc:
            add_error(
                errors,
                "image_quality",
                exc,
            )

        # ---------------------------------------------------------
        # ADAPTIVE ENHANCEMENT
        #
        # Existing behavior is preserved:
        # enhancement is generated whenever quality analysis succeeds.
        #
        # The enhanced image is used for prediction ONLY when
        # quality is BORDERLINE or POOR.
        # ---------------------------------------------------------

        enhancement = None

        if quality:
            try:
                enhancement = _serialize_enhancement(
                    request,
                    record,
                    enhance_image(
                        image,
                        quality,
                    ),
                )
            except Exception as exc:
                add_error(
                    errors,
                    "adaptive_enhancement",
                    exc,
                )

        # ---------------------------------------------------------
        # RETINAL STRUCTURE
        # ---------------------------------------------------------

        structure = None

        try:
            structure = _serialize_structure(
                request,
                record,
                analyze_retinal_structure(image),
            )
        except Exception as exc:
            add_error(
                errors,
                "retinal_structure",
                exc,
            )

        # ---------------------------------------------------------
        # LESION EVIDENCE
        # ---------------------------------------------------------

        lesion_evidence = None

        try:
            lesion_evidence = _serialize_lesion_evidence(
                request,
                record,
                analyze_lesion_candidates(image),
            )
        except Exception as exc:
            add_error(
                errors,
                "lesion_evidence",
                exc,
            )

        # ---------------------------------------------------------
        # DR PREDICTION
        #
        # GOOD:
        #   Original image -> ONE prediction
        #
        # BORDERLINE / POOR:
        #   Original image  -> prediction 1
        #   Enhanced image -> prediction 2
        # ---------------------------------------------------------

        def build_prediction(
            prediction_path: Path,
        ) -> dict[str, Any]:

            prediction_details = predict_details(
                str(prediction_path)
            )

            prediction_grade = int(
                prediction_details["grade"]
            )

            return {
                **prediction_details,
                "grade": prediction_grade,
                "label": GRADE_LABELS.get(
                    prediction_grade,
                    prediction_details.get(
                        "label",
                        "Unknown",
                    ),
                ),
                "risk_level": RISK_LEVELS.get(
                    prediction_grade,
                    "Unknown",
                ),
            }

        # Always run the original-image prediction first.
        original_prediction = build_prediction(
            input_path
        )

        # Default:
        # GOOD quality -> no enhanced prediction.
        enhanced_prediction = None

        # Only BORDERLINE / POOR quality images receive
        # the second prediction on the enhanced image.
        if (
            quality
            and quality.get("status") != "GOOD"
        ):
            if (
                enhancement
                and "enhanced_image_url" in enhancement
            ):
                enhanced_path = (
                    record.directory
                    / "enhanced-preview.png"
                )

                if enhanced_path.is_file():
                    try:
                        enhanced_prediction = build_prediction(
                            enhanced_path
                        )
                    except Exception as exc:
                        add_error(
                            errors,
                            "enhanced_prediction",
                            exc,
                        )
                else:
                    add_error(
                        errors,
                        "enhanced_prediction",
                        FileNotFoundError(
                            "Enhanced image was not available "
                            "for prediction."
                        ),
                    )

        # ---------------------------------------------------------
        # RELIABILITY
        #
        # Reliability remains based on the ORIGINAL prediction.
        # ---------------------------------------------------------

        reliability = None

        try:
            reliability = analyze_prediction_reliability(
                original_prediction["probabilities"],
                predicted_index=original_prediction["grade"],
                predicted_label=original_prediction["label"],
            )
        except Exception as exc:
            add_error(
                errors,
                "reliability",
                exc,
            )

        # ---------------------------------------------------------
        # GRAD-CAM
        # ---------------------------------------------------------

        gradcam = {
            "available": False,
            "url": None,
        }

        try:
            cam = generate_gradcam(
                str(input_path)
            )

            gradcam_path = (
                record.directory / "gradcam.png"
            )

            if not cv2.imwrite(
                str(gradcam_path),
                np.asarray(cam),
            ):
                raise RuntimeError(
                    "Grad-CAM image could not be written."
                )

            record.assets["gradcam.png"] = gradcam_path

            gradcam = {
                "available": True,
                "url": public_url(
                    request,
                    analysis_id,
                    "gradcam.png",
                ),
            }

        except Exception as exc:
            add_error(
                errors,
                "gradcam",
                exc,
            )

        # ---------------------------------------------------------
        # SIMILAR CASES
        # ---------------------------------------------------------

        similar_cases: list[dict[str, Any]] = []

        try:
            for index, (score, path) in enumerate(
                search_similar_images(
                    str(input_path)
                )
            ):
                case = serialize_case(
                    request,
                    record,
                    analysis_id,
                    path,
                    score,
                    f"similar-{index}"
                    f"{Path(path).suffix.lower()}",
                )

                if case:
                    similar_cases.append(case)

        except Exception as exc:
            add_error(
                errors,
                "similar_cases",
                exc,
            )

        # ---------------------------------------------------------
        # PROGRESSION MAP
        # ---------------------------------------------------------

        progression_map: dict[
            str,
            dict[str, Any],
        ] = {}

        try:
            raw_map = get_progression_map(
                str(input_path)
            )

            for stage in range(5):
                cases = []

                for index, (score, path) in enumerate(
                    raw_map.get(stage, [])
                ):
                    case = serialize_case(
                        request,
                        record,
                        analysis_id,
                        path,
                        score,
                        f"stage-{stage}-{index}"
                        f"{Path(path).suffix.lower()}",
                    )

                    if case:
                        cases.append(case)

                progression_map[f"stage_{stage}"] = {
                    "label": GRADE_LABELS[stage],
                    "cases": cases,
                }

        except Exception as exc:
            add_error(
                errors,
                "progression_map",
                exc,
            )

        # ---------------------------------------------------------
        # PROGRESSION SIMULATION
        # ---------------------------------------------------------

        simulation: list[dict[str, Any]] = []

        try:
            for index, step in enumerate(
                simulate_progression(
                    str(input_path)
                )
            ):
                source = step.get("image")

                if not source:
                    continue

                asset_name = (
                    f"simulation-{index}"
                    f"{Path(source).suffix.lower()}"
                )

                if copy_asset(
                    record,
                    source,
                    asset_name,
                ):
                    simulation.append(
                        {
                            **step,
                            "grade": int(
                                step["grade"]
                            ),
                            "image_url": public_url(
                                request,
                                analysis_id,
                                asset_name,
                            ),
                        }
                    )

        except Exception as exc:
            add_error(
                errors,
                "progression_simulation",
                exc,
            )

        # ---------------------------------------------------------
        # PROGRESSION PREDICTION
        # ---------------------------------------------------------

        progression_prediction = None

        if predict_progression:
            try:
                progression_prediction = predict_progression(
                    str(input_path)
                )
            except Exception as exc:
                add_error(
                    errors,
                    "progression_prediction",
                    exc,
                )

        # ---------------------------------------------------------
        # FINAL RESPONSE
        # ---------------------------------------------------------

        response_payload = {
            "analysis_id": analysis_id,
            "uploaded_image_url": public_url(
                request,
                analysis_id,
                "uploaded.png",
            ),
            "quality": quality,
            "enhancement": enhancement,
            "structure": structure,
            "lesion_evidence": lesion_evidence,

            # Original-image prediction
            "prediction": original_prediction,

            # GOOD quality -> None
            # BORDERLINE / POOR -> enhanced-image prediction
            "enhanced_prediction": enhanced_prediction,

            "reliability": reliability,
            "gradcam": gradcam,
            "similar_cases": similar_cases,
            "progression_map": progression_map,
            "progression_simulation": {
                "available": bool(simulation),
                "results": simulation,
            },
            "progression_prediction": progression_prediction,
            "errors": errors,
        }

        response_payload["disease_landscape"] = (
            build_disease_landscape()
        )

        response_payload["evidence_summary"] = (
            build_evidence_summary(
                response_payload
            )
        )

        return response_payload

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@app.post("/api/quality/analyze")
async def analyze_quality(
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    try:
        image = _decode_uploaded_image(
            await file.read()
        )

        return {
            "quality": analyze_image_quality(image)
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Image quality analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Image quality analysis unavailable.",
        ) from exc


def _summary_inputs_from_image(
    image: np.ndarray,
) -> dict[str, Any]:

    temporary_path = None

    with tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False,
    ) as temporary_file:
        temporary_path = Path(
            temporary_file.name
        )

    try:
        if not cv2.imwrite(
            str(temporary_path),
            image,
        ):
            raise RuntimeError(
                "Image could not be written "
                "for evidence summary."
            )

        details = predict_details(
            str(temporary_path)
        )

        grade = int(
            details["grade"]
        )

        prediction = {
            **details,
            "grade": grade,
            "label": GRADE_LABELS.get(
                grade,
                details.get(
                    "label",
                    "Unknown",
                ),
            ),
            "risk_level": RISK_LEVELS.get(
                grade,
                "Unknown",
            ),
        }

        reliability = analyze_prediction_reliability(
            details["probabilities"],
            predicted_index=grade,
            predicted_label=prediction["label"],
        )

        gradcam_available = False

        try:
            gradcam_available = (
                generate_gradcam(
                    str(temporary_path)
                )
                is not None
            )
        except Exception:
            gradcam_available = False

        return {
            "prediction": prediction,
            "quality": analyze_image_quality(image),
            "reliability": reliability,
            "structure": analyze_retinal_structure(image),
            "lesion_evidence": analyze_lesion_candidates(image),
            "gradcam": {
                "available": gradcam_available
            },
        }

    finally:
        if temporary_path:
            temporary_path.unlink(
                missing_ok=True
            )


@app.post("/api/evidence/summary")
async def evidence_summary(
    request: Request,
) -> dict[str, Any]:

    content_type = request.headers.get(
        "content-type",
        "",
    )

    try:
        if content_type.startswith(
            "application/json"
        ):
            payload = await request.json()

            return {
                "evidence_summary": build_evidence_summary(
                    payload.get(
                        "analysis",
                        payload,
                    )
                )
            }

        if not content_type.startswith(
            "multipart/form-data"
        ):
            raise HTTPException(
                status_code=415,
                detail=(
                    "Provide an analysis JSON object "
                    "or an image upload."
                ),
            )

        form = await request.form()

        file = form.get("file")

        if file is None or not hasattr(
            file,
            "read",
        ):
            raise HTTPException(
                status_code=400,
                detail="An image file is required.",
            )

        if (
            not file.content_type
            or not file.content_type.startswith("image/")
        ):
            raise HTTPException(
                status_code=415,
                detail="Upload a PNG, JPG, or JPEG retinal image.",
            )

        image = _decode_uploaded_image(
            await file.read()
        )

        return {
            "evidence_summary": build_evidence_summary(
                _summary_inputs_from_image(image)
            )
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Evidence summary failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Evidence summary unavailable.",
        ) from exc


@app.post("/api/reliability/analyze")
async def analyze_reliability(
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    try:
        image = _decode_uploaded_image(
            await file.read()
        )

        temporary_path = None

        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(
                temporary_file.name
            )

        try:
            if not cv2.imwrite(
                str(temporary_path),
                image,
            ):
                raise RuntimeError(
                    "Image could not be written "
                    "for reliability analysis."
                )

            details = predict_details(
                str(temporary_path)
            )

        finally:
            if temporary_path:
                temporary_path.unlink(
                    missing_ok=True
                )

        reliability = analyze_prediction_reliability(
            details["probabilities"],
            predicted_index=int(
                details["grade"]
            ),
            predicted_label=details.get(
                "label"
            ),
        )

        return {
            "prediction": details,
            "reliability": reliability,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Model reliability analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Model reliability analysis unavailable.",
        ) from exc


@app.post("/api/structure/analyze")
async def analyze_structure(
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    analysis_id = uuid.uuid4().hex

    record = AnalysisRecord(
        RESULTS_DIR / analysis_id
    )

    record.directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    analyses[analysis_id] = record

    try:
        image = _decode_uploaded_image(
            await file.read()
        )

        original_path = (
            record.directory / "original.png"
        )

        if not cv2.imwrite(
            str(original_path),
            image,
        ):
            raise RuntimeError(
                "Original image could not be written."
            )

        record.assets["original.png"] = original_path

        structure = _serialize_structure(
            request,
            record,
            analyze_retinal_structure(image),
        )

        structure["analysis_id"] = analysis_id

        structure["original_image_url"] = public_url(
            request,
            analysis_id,
            "original.png",
        )

        return {
            "structure": structure
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Retinal structure analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Retinal structure analysis unavailable.",
        ) from exc


@app.post("/api/lesions/analyze")
async def analyze_lesions(
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    analysis_id = uuid.uuid4().hex

    record = AnalysisRecord(
        RESULTS_DIR / analysis_id
    )

    record.directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    analyses[analysis_id] = record

    try:
        image = _decode_uploaded_image(
            await file.read()
        )

        original_path = (
            record.directory / "original.png"
        )

        if not cv2.imwrite(
            str(original_path),
            image,
        ):
            raise RuntimeError(
                "Original image could not be written."
            )

        record.assets["original.png"] = original_path

        evidence = _serialize_lesion_evidence(
            request,
            record,
            analyze_lesion_candidates(image),
        )

        evidence["analysis_id"] = analysis_id

        evidence["original_image_url"] = public_url(
            request,
            analysis_id,
            "original.png",
        )

        return {
            "lesion_evidence": evidence
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Lesion candidate analysis failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Lesion candidate analysis unavailable.",
        ) from exc


@app.post("/api/quality/enhance")
async def enhance_quality(
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:

    if (
        not file.content_type
        or not file.content_type.startswith("image/")
    ):
        raise HTTPException(
            status_code=415,
            detail="Upload a PNG, JPG, or JPEG retinal image.",
        )

    analysis_id = uuid.uuid4().hex

    record = AnalysisRecord(
        RESULTS_DIR / analysis_id
    )

    record.directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    analyses[analysis_id] = record

    try:
        contents = await file.read()

        image = _decode_uploaded_image(
            contents
        )

        original_path = (
            record.directory / "original.png"
        )

        if not cv2.imwrite(
            str(original_path),
            image,
        ):
            raise RuntimeError(
                "Original image could not be written."
            )

        record.assets["original.png"] = original_path

        quality = analyze_image_quality(
            image
        )

        result = _serialize_enhancement(
            request,
            record,
            enhance_image(
                image,
                quality,
            ),
        )

        result["analysis_id"] = analysis_id

        result["original_image_url"] = public_url(
            request,
            analysis_id,
            "original.png",
        )

        return {
            "enhancement": result
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Adaptive enhancement failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Adaptive enhancement unavailable.",
        ) from exc


@app.get(
    "/api/results/{analysis_id}/images/{asset_name}",
    name="get_image",
)
def get_image(
    analysis_id: str,
    asset_name: str,
) -> FileResponse:

    record = analyses.get(
        analysis_id
    )

    if (
        not record
        or asset_name not in record.assets
    ):
        raise HTTPException(
            status_code=404,
            detail="Analysis image not found.",
        )

    return FileResponse(
        record.assets[asset_name]
    )


@app.post("/api/report/{analysis_id}")
def report(
    analysis_id: str,
    data: dict[str, Any] = Body(...),
) -> FileResponse:

    record = analyses.get(
        analysis_id
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail=(
                "Analysis not found. "
                "Run an analysis first."
            ),
        )

    report_path = (
        record.directory / "DR_Report.pdf"
    )

    try:
        generate_pdf_report(
            str(report_path),
            data,
        )

    except Exception as exc:
        logger.exception(
            "PDF report failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return FileResponse(
        report_path,
        media_type="application/pdf",
        filename="DR_Report.pdf",
    )
