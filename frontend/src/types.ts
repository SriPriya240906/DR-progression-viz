export type RiskLevel = "Low" | "Moderate" | "High" | "Critical" | string;

export type ImageQualityOverall = "GOOD" | "BORDERLINE" | "UNGRADABLE" | string;

export interface BackendErrorItem {
  feature?: string;
  message?: string;
}

export interface PredictionProbabilities {
  [key: string]: number;
}

export interface PredictionSummary {
  grade: number;
  label: string;
  confidence: number;
  risk_level: RiskLevel;
  probabilities?: PredictionProbabilities;
}

export interface ImageQualityResult {
  status?: "GOOD" | "BORDERLINE" | "POOR" | string;
  overall_assessment?: string;
  overall?: ImageQualityOverall;
  message?: string;
  resolution?: { width?: number; height?: number; aspect_ratio?: number; assessment?: string };
  focus?: { metric?: string; value?: number; assessment?: string };
  illumination?: { metric?: string; value?: number; assessment?: string };
  contrast?: { metric?: string; value?: number; assessment?: string };
  field_of_view?: { assessment?: string; estimated_region_fraction?: number };
  retinal_visibility?: { assessment?: string; estimated_visible_fraction?: number };
  warnings?: string[];
  recommendation?: string;
  methodology?: { threshold_type?: string; validated_clinically?: boolean; dataset_used?: string };
}

export interface EnhancementResult {
  attempted: boolean;
  method?: string;
  improved?: boolean;
  accepted?: boolean;
  original_quality?: ImageQualityResult;
  enhanced_quality?: ImageQualityResult;
  changes?: Record<string, number>;
  enhanced_image_url?: string;
  original_image_url?: string;
  recommendation?: string;
  message?: string;
}

export interface ReliabilityResult {
  available?: boolean;
  predicted_index?: number;
  predicted_label?: string;
  confidence?: number;
  top_probability?: number;
  second_probability?: number;
  probability_margin?: number;
  predictive_entropy?: number;
  normalized_predictive_entropy?: number;
  calibration?: {
    available?: boolean;
    method?: string;
    temperature?: number;
    reason?: string;
  };
  interpretation?: string;
}

export interface RetinalStructureResult {
  available?: boolean;
  method_status?: string;
  overlay_image_url?: string;
  confidence_available?: boolean;
  field_of_view?: {
    available?: boolean;
    fraction?: number;
    sufficient_for_analysis?: boolean;
    dimensions?: { width?: number; height?: number };
    center?: { x?: number; y?: number };
    extent?: { x_min?: number; y_min?: number; x_max?: number; y_max?: number };
  };
  vessels?: {
    available?: boolean;
    method?: string;
    confidence_available?: boolean;
    vessel_like_fraction?: number;
    density?: number;
    reason?: string;
    limitations?: string[];
  };
  optic_disc?: { available?: boolean; reason?: string };
  fovea?: { available?: boolean; reason?: string };
  limitations?: string[];
}

export interface LesionCandidate {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  area?: number;
  centroid?: { x?: number; y?: number };
  relative_centroid?: { x?: number; y?: number };
  mean_intensity?: number;
  local_fraction?: number;
}

export interface LesionEvidenceResult {
  available?: boolean;
  method_status?: string;
  confidence_available?: boolean;
  overlay_image_urls?: { dark?: string; bright?: string; combined?: string };
  dark_candidates?: { count?: number; fraction?: number; regions?: LesionCandidate[] };
  bright_candidates?: { count?: number; fraction?: number; regions?: LesionCandidate[] };
  neovascularization?: { available?: boolean; reason?: string };
  optic_disc_exclusion?: { available?: boolean; reason?: string };
  limitations?: string[];
}

export interface ClinicalEvidenceSummary {
  available?: boolean;
  prediction?: { grade?: number; label?: string; confidence?: number; statement?: string };
  model_uncertainty?: {
    available?: boolean;
    top_probability?: number;
    second_probability?: number;
    probability_margin?: number;
    predictive_entropy?: number;
    normalized_predictive_entropy?: number;
    calibration_status?: string;
    summary?: string;
  };
  image_quality?: { available?: boolean; status?: string; warnings?: string[]; summary?: string };
  model_explanation?: { gradcam_available?: boolean; summary?: string };
  retinal_structure?: { available?: boolean; summary?: string };
  lesion_evidence?: { available?: boolean; dark_candidate_count?: number; bright_candidate_count?: number; summary?: string };
  clinical_review?: { required?: boolean; reason?: string };
  limitations?: string[];
}

export interface DiseaseLandscapeEntry {
  name: string;
  status: 'supported' | 'experimental' | 'reference-only' | 'unavailable' | string;
  prediction_available: boolean;
  model_available: boolean;
  label_source?: string | null;
  model?: string | null;
  labels?: string[];
  notes?: string;
}

export interface DiseaseLandscapeResult {
  available?: boolean;
  landscape_type?: string;
  current_supported_scope?: string;
  diseases?: DiseaseLandscapeEntry[];
  limitations?: string[];
}

export interface SimilarCase {
  image_url: string;
  similarity: number;
  grade?: number;
}

export interface ProgressionCase {
  image_url: string;
  similarity: number;
  grade?: number;
}

export interface DiseaseCapability {
  name: string;
  status: string;
  prediction_available: boolean;
  model_available: boolean;
  label_source?: string | null;
  model?: string | null;
  labels?: string[];
  notes?: string;
}

export interface DiseaseLandscape {
  available?: boolean;
  landscape_type?: string;
  current_supported_scope?: string;
  diseases?: DiseaseCapability[];
  limitations?: string[];
}

export interface ProgressionStagePreview {
  stage: number;
  image_url: string;
  label: string;
  synthetic: boolean;
}

export interface AnalysisResult {
  analysis_id: string;
  uploaded_image_url?: string;
  prediction: PredictionSummary;
  image_quality?: ImageQualityResult;
  enhancement?: EnhancementResult;
  reliability?: ReliabilityResult;
  structure?: RetinalStructureResult;
  lesion_evidence?: LesionEvidenceResult;
  evidence_summary?: ClinicalEvidenceSummary;
  disease_landscape?: DiseaseLandscapeResult;
  gradcam?: {
    image_url?: string;
    available?: boolean;
    url?: string;
  };
  similar_cases: SimilarCase[];
  digital_twin?: {
    state: string;
    feature_vector?: number[];
  };
  disease_landscape?: DiseaseLandscape;
  progression_map: {
    stage_0?: ProgressionCase[];
    stage_1?: ProgressionCase[];
    stage_2?: ProgressionCase[];
    stage_3?: ProgressionCase[];
    stage_4?: ProgressionCase[];
  };
  progression_simulation?: {
    available?: boolean;
    results?: ProgressionStagePreview[];
    stages?: ProgressionStagePreview[];
  };
  triage?: {
    status: string;
    reason: string;
    recommendation: string;
  };
  errors?: BackendErrorItem[];
}
