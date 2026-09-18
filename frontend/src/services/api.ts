import type { AnalysisResult, PredictionSummary } from '../types';
import { buildMockAnalysis } from '../data/mockData';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true' || import.meta.env.MOCK_MODE === 'true';

// New staged API functions
export async function uploadImage(file: File): Promise<{analysis_id: string, uploaded_image_url: string}> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 300));
    return {
      analysis_id: 'mock-' + Date.now(),
      uploaded_image_url: URL.createObjectURL(file)
    };
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Failed to upload image.');
  }

  return payload;
}

export async function analyzeImageQuality(analysisId: string): Promise<any> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    return {
      analysis_id: analysisId,
      quality: { status: 'GOOD' },
      enhancement: null,
      ready_for_prediction: true
    };
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze-quality/${analysisId}`, {
    method: 'POST',
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Quality analysis failed.');
  }

  return payload;
}

export async function predictDisease(analysisId: string): Promise<any> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    return {
      analysis_id: analysisId,
      original_prediction: { grade: 2, label: 'Moderate', confidence: 85 },
      enhanced_prediction: null,
      ready_for_progression: true
    };
  }

  const response = await fetch(`${API_BASE_URL}/api/predict-disease/${analysisId}`, {
    method: 'POST',
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Disease prediction failed.');
  }

  return payload;
}

export async function analyzeProgression(analysisId: string): Promise<any> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    return {
      analysis_id: analysisId,
      similar_cases: [],
      progression_map: {},
      progression_simulation: { available: false, results: [] },
      ready_for_report: true
    };
  }

  const response = await fetch(`${API_BASE_URL}/api/analyze-progression/${analysisId}`, {
    method: 'POST',
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Progression analysis failed.');
  }

  return payload;
}

export async function generateEvidenceSummary(analysisId: string): Promise<any> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return {
      analysis_id: analysisId,
      evidence_summary: { summary: 'Mock evidence summary' }
    };
  }

  const response = await fetch(`${API_BASE_URL}/api/generate-evidence-summary/${analysisId}`, {
    method: 'POST',
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Evidence summary generation failed.');
  }

  return payload;
}

export async function getCompleteAnalysis(analysisId: string): Promise<AnalysisResult> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    const analysis = buildMockAnalysis('retinal_scan.png');
    return analysis as AnalysisResult;
  }

  const response = await fetch(`${API_BASE_URL}/api/analysis/${analysisId}`);

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'Failed to get analysis results.');
  }

  return normalizeAnalysisResponse(payload);
}

function normalizeProbabilityMap(probabilities: Record<string, number> | undefined): Record<string, number> | undefined {
  if (!probabilities || typeof probabilities !== 'object') {
    return undefined;
  }

  return Object.fromEntries(
    Object.entries(probabilities).map(([key, value]) => [key, Number(value)])
  );
}

function normalizeQuality(rawQuality: any): AnalysisResult['image_quality'] {
  if (!rawQuality) return undefined;
  if (rawQuality.status || rawQuality.resolution?.width) return rawQuality;

  const status = rawQuality.overall === 'UNGRADABLE' ? 'POOR' : rawQuality.overall || 'BORDERLINE';
  return {
    status,
    overall: status,
    overall_assessment: rawQuality.message || 'Quality assessment is available.',
    focus: { value: Number(rawQuality.focus ?? 0), assessment: 'Legacy quality score' },
    illumination: { value: Number(rawQuality.illumination ?? 0), assessment: 'Legacy quality score' },
    contrast: { value: Number(rawQuality.contrast ?? 0), assessment: 'Legacy quality score' },
    field_of_view: { assessment: `Legacy quality score: ${Number(rawQuality.field_of_view ?? 0)}%` },
    retinal_visibility: { assessment: 'Legacy quality payload did not include this metric.' },
    warnings: [],
    recommendation: rawQuality.message || 'Review the image quality before AI-assisted analysis.',
  };
}

function normalizeAnalysisResponse(raw: any): AnalysisResult {
  const prediction = raw.prediction ?? {};
  const normalizedProgressionMap: AnalysisResult['progression_map'] = {
    stage_0: [],
    stage_1: [],
    stage_2: [],
    stage_3: [],
    stage_4: [],
  };

  const stages = ['stage_0', 'stage_1', 'stage_2', 'stage_3', 'stage_4'];
  stages.forEach((stageKey) => {
    const stage = raw.progression_map?.[stageKey];
    const cases = Array.isArray(stage?.cases)
      ? stage.cases
      : Array.isArray(stage)
        ? stage
        : [];

    normalizedProgressionMap[stageKey as keyof AnalysisResult['progression_map']] = cases.map((item: any) => ({
      image_url: item.image_url ?? item.image ?? '',
      similarity: Number(item.similarity ?? 0),
      grade: item.grade ?? undefined,
    }));
  });

  const gradcam = raw.gradcam ?? {};
  const simulationResults = Array.isArray(raw.progression_simulation?.results)
    ? raw.progression_simulation.results
    : Array.isArray(raw.progression_simulation)
      ? raw.progression_simulation
      : [];

  const displayPrediction: PredictionSummary = {
    grade: Number(prediction.grade ?? 0),
    label: prediction.label ?? 'Unknown',
    confidence: Number(prediction.confidence ?? 0),
    risk_level: prediction.risk_level ?? 'Unknown',
    probabilities: normalizeProbabilityMap(prediction.probabilities),
  };

  return {
    analysis_id: raw.analysis_id ?? 'unknown',
    uploaded_image_url: raw.uploaded_image_url ?? '',
    prediction: displayPrediction,
    image_quality: normalizeQuality(raw.quality ?? raw.image_quality),
    enhancement: raw.enhancement ?? undefined,
    reliability: raw.reliability ?? undefined,
    structure: raw.structure ?? undefined,
    lesion_evidence: raw.lesion_evidence ?? undefined,
    evidence_summary: raw.evidence_summary ?? undefined,
    disease_landscape: raw.disease_landscape ?? undefined,
    gradcam: {
      available: Boolean(gradcam.available),
      url: gradcam.url ?? gradcam.image_url ?? '',
      image_url: gradcam.url ?? gradcam.image_url ?? '',
    },
    similar_cases: Array.isArray(raw.similar_cases)
      ? raw.similar_cases.map((item: any) => ({
          image_url: item.image_url ?? '',
          similarity: Number(item.similarity ?? 0),
          grade: item.grade ?? undefined,
        }))
      : [],
    progression_map: normalizedProgressionMap,
    progression_simulation: {
      available: Boolean(raw.progression_simulation?.available),
      results: simulationResults.map((item: any) => ({
        stage: Number(item.grade ?? item.stage ?? 0),
        image_url: item.image_url ?? item.image ?? '',
        label: item.label ?? `Stage ${item.grade ?? item.stage ?? 0}`,
        synthetic: Boolean(item.synthetic ?? false),
      })),
      stages: simulationResults.map((item: any) => ({
        stage: Number(item.grade ?? item.stage ?? 0),
        image_url: item.image_url ?? item.image ?? '',
        label: item.label ?? `Stage ${item.grade ?? item.stage ?? 0}`,
        synthetic: Boolean(item.synthetic ?? false),
      })),
    },
    triage: raw.triage ?? undefined,
    errors: Array.isArray(raw.errors) ? raw.errors : [],
  };
}

export async function getHealthStatus(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('The backend is unavailable.');
  }

  const payload = await response.json().catch(() => ({}));
  return { status: payload.status || 'ok' };
}

export async function analyzeRetinalImage(file: File): Promise<AnalysisResult> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 700));
    const analysis = buildMockAnalysis(file?.name || 'retinal_scan.png');
    return analysis as AnalysisResult;
  }

  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || 'The backend could not analyze this image.');
  }

  return normalizeAnalysisResponse(payload);
}

export async function generateReport(id: string, data: Record<string, unknown>): Promise<Blob> {
  if (USE_MOCK_API) {
    await new Promise((resolve) => setTimeout(resolve, 500));
    return new Blob(['mock-pdf'], { type: 'application/pdf' });
  }

  const response = await fetch(`${API_BASE_URL}/api/report/${id}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'The PDF report could not be generated.');
  }

  return response.blob();
}
