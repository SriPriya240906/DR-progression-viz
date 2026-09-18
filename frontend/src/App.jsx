import { useEffect, useState } from 'react';

import {
  Activity,
  ArrowRight,
  CheckCircle2,
  FileText,
  RefreshCcw,
  ShieldAlert,
} from 'lucide-react';

import {
  uploadImage,
  analyzeImageQuality,
  predictDisease,
  analyzeProgression,
  generateEvidenceSummary,
  generateReport,
  getHealthStatus,
} from './services/api';

import Sidebar from './components/sidebar';
import { ImageUpload } from './components/ImageUpload';
import { LoadingState } from './components/LoadingState';
import { ErrorState } from './components/ErrorState';
import { PredictionCard } from './components/PredictionCard';
import { GradCAMViewer } from './components/GradCAMViewer';
import { SimilarCases } from './components/SimilarCases';
import { ProgressionMap } from './components/ProgressionMap';
import { ProgressionSimulation } from './components/ProgressionSimulation';
import { ReportPanel } from './components/ReportPanel';
import { ImageQualityCard } from './components/ImageQualityCard';
import { ReliabilityCard } from './components/ReliabilityCard';
import { RetinalStructureCard } from './components/RetinalStructureCard';
import { LesionEvidenceCard } from './components/LesionEvidenceCard';
import { ClinicalEvidenceCard } from './components/ClinicalEvidenceCard';
import { RetinalDiseaseLandscapeCard } from './components/RetinalDiseaseLandscapeCard';

function App() {
  /*
   * Workflow states:
   *
   * INITIAL
   * QUALITY_NOT_ANALYZED
   * QUALITY_ANALYZED
   * DISEASE_ANALYZED
   * PROGRESSION_ANALYZED
   * COMPLETED
   */
  const [workflowState, setWorkflowState] = useState('INITIAL');

  const [activeSection, setActiveSection] = useState(
    'quality-assessment'
  );

  /* Analysis session */
  const [analysisId, setAnalysisId] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');

  /* Stage 1 */
  const [qualityResult, setQualityResult] = useState(null);
  const [enhancementResult, setEnhancementResult] = useState(null);

  /* Stage 2 */
  const [originalPrediction, setOriginalPrediction] = useState(null);
  const [enhancedPrediction, setEnhancedPrediction] = useState(null);
  const [reliabilityResult, setReliabilityResult] = useState(null);
  const [structureResult, setStructureResult] = useState(null);
  const [lesionEvidence, setLesionEvidence] = useState(null);
  const [gradcamResult, setGradcamResult] = useState(null);

  /* Stage 3 */
  const [progressionResults, setProgressionResults] = useState(null);
  const [evidenceSummary, setEvidenceSummary] = useState(null);

  /* UI */
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reportLoading, setReportLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');

  /* ---------------------------------------------------------
     Backend health
  --------------------------------------------------------- */

  useEffect(() => {
    let isMounted = true;

    getHealthStatus()
      .then(() => {
        if (isMounted) {
          setBackendStatus('ok');
        }
      })
      .catch(() => {
        if (isMounted) {
          setBackendStatus('offline');
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  /* ---------------------------------------------------------
     Reset case state
  --------------------------------------------------------- */

  const resetAnalysisState = () => {
    setAnalysisId(null);

    setQualityResult(null);
    setEnhancementResult(null);

    setOriginalPrediction(null);
    setEnhancedPrediction(null);
    setReliabilityResult(null);
    setStructureResult(null);
    setLesionEvidence(null);
    setGradcamResult(null);

    setProgressionResults(null);
    setEvidenceSummary(null);

    setError('');
  };

  /* ---------------------------------------------------------
     File selection
  --------------------------------------------------------- */

  const handleFileSelect = (event) => {
    const nextFile = event.target.files?.[0];

    if (!nextFile) {
      return;
    }

    resetAnalysisState();

    setSelectedFile(nextFile);

    const nextPreviewUrl = URL.createObjectURL(nextFile);
    setPreviewUrl(nextPreviewUrl);

    setWorkflowState('QUALITY_NOT_ANALYZED');
    setActiveSection('quality-assessment');
  };

  /* ---------------------------------------------------------
     Remove / reset upload
  --------------------------------------------------------- */

  const clearUpload = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setSelectedFile(null);
    setPreviewUrl('');

    resetAnalysisState();

    setWorkflowState('INITIAL');
    setActiveSection('quality-assessment');
  };

  /* ---------------------------------------------------------
     Upload image
  --------------------------------------------------------- */

  const handleImageUpload = async () => {
    if (!selectedFile) {
      setError(
        'Please choose a retinal image before uploading.'
      );
      return;
    }

    setLoading(true);
    setError('');

    try {
      const uploadResult = await uploadImage(selectedFile);

      setAnalysisId(uploadResult.analysis_id);

      setWorkflowState('QUALITY_NOT_ANALYZED');
    } catch (exception) {
      setError(
        exception?.message ||
          'Failed to upload image.'
      );
    } finally {
      setLoading(false);
    }
  };

  /* ---------------------------------------------------------
     Stage 1
     Image Quality Assessment
  --------------------------------------------------------- */

  const handleQualityAnalysis = async () => {
    if (!analysisId) {
      /*
       * The current ImageUpload component may call onAnalyze
       * directly after file selection. In that case upload the
       * image first, then perform quality analysis.
       */
      if (!selectedFile) {
        setError(
          'Please choose a retinal image first.'
        );
        return;
      }

      setLoading(true);
      setError('');

      try {
        const uploadResult = await uploadImage(selectedFile);

        setAnalysisId(uploadResult.analysis_id);

        const result = await analyzeImageQuality(
          uploadResult.analysis_id
        );

        setQualityResult(result.quality);
        setEnhancementResult(result.enhancement);

        setWorkflowState('QUALITY_ANALYZED');
      } catch (exception) {
        setError(
          exception?.message ||
            'Quality analysis failed.'
        );
      } finally {
        setLoading(false);
      }

      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await analyzeImageQuality(
        analysisId
      );

      setQualityResult(result.quality);
      setEnhancementResult(result.enhancement);

      setWorkflowState('QUALITY_ANALYZED');
    } catch (exception) {
      setError(
        exception?.message ||
          'Quality analysis failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  /* ---------------------------------------------------------
     Stage 2
     Disease Prediction
  --------------------------------------------------------- */

  const handleDiseasePrediction = async () => {
    if (!analysisId || !qualityResult) {
      setError(
        'Please complete image quality assessment first.'
      );
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await predictDisease(
        analysisId
      );

      setOriginalPrediction(
        result.original_prediction
      );

      setEnhancedPrediction(
        result.enhanced_prediction || null
      );

      setReliabilityResult(
        result.reliability || null
      );

      setStructureResult(
        result.structure || null
      );

      setLesionEvidence(
        result.lesion_evidence || null
      );

      setGradcamResult(
        result.gradcam || null
      );

      setWorkflowState('DISEASE_ANALYZED');
    } catch (exception) {
      setError(
        exception?.message ||
          'Disease prediction failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  /* ---------------------------------------------------------
     Stage 3
     Progression + Similar Cases
  --------------------------------------------------------- */

  const handleProgressionAnalysis = async () => {
    if (!analysisId || !originalPrediction) {
      setError(
        'Please complete disease prediction first.'
      );
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await analyzeProgression(
        analysisId
      );

      setProgressionResults(result);

      /*
       * Evidence summary remains part of the existing
       * analytical engine.
       */
      try {
        const evidenceResult =
          await generateEvidenceSummary(
            analysisId
          );

        setEvidenceSummary(
          evidenceResult?.evidence_summary ||
            null
        );
      } catch (evidenceException) {
        /*
         * Do not fail the complete progression stage
         * just because the optional evidence summary
         * request failed.
         */
        setEvidenceSummary(null);
      }

      setWorkflowState(
        'PROGRESSION_ANALYZED'
      );
    } catch (exception) {
      setError(
        exception?.message ||
          'Progression analysis failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  /* ---------------------------------------------------------
     Stage 4
     Report Generation
  --------------------------------------------------------- */

  const handleReportGenerate = async () => {
    if (
      !analysisId ||
      !qualityResult ||
      !originalPrediction ||
      !progressionResults
    ) {
      setError(
        'Please complete the previous workflow stages before generating the report.'
      );
      return;
    }

    setReportLoading(true);
    setError('');

    try {
      const reportData = {
        analysis_id: analysisId,

        /* Stage 1 */
        image_quality: qualityResult,
        enhancement: enhancementResult,

        /* Stage 2 */
        original_prediction: originalPrediction,
        enhanced_prediction:
          enhancedPrediction,
        dual_predictions:
          enhancedPrediction !== null,

        reliability: reliabilityResult,
        structure: structureResult,
        lesion_evidence: lesionEvidence,
        gradcam: gradcamResult,

        /* Stage 3 */
        progression_map:
          progressionResults?.progression_map,

        progression_simulation:
          progressionResults?.progression_simulation,

        progression_prediction:
          progressionResults?.progression_prediction,

        similar_cases:
          progressionResults?.similar_cases,

        disease_landscape:
          progressionResults?.disease_landscape,

        evidence_summary:
          evidenceSummary,

        /* Workflow metadata */
        workflow_completed: true,

        quality_status:
          qualityResult?.status,

        prediction_strategy:
          qualityResult?.status === 'GOOD'
            ? 'single'
            : 'dual',

        /* Existing primary prediction */
        grade:
          originalPrediction?.grade,

        confidence:
          originalPrediction?.confidence,

        risk:
          originalPrediction?.risk_level,

        recommendation:
          'Review this research output with a qualified ophthalmologist. This is an experimental AI system and should not be used as the sole basis for clinical decisions.',
      };

      const pdfBlob = await generateReport(
        analysisId,
        reportData
      );

      const pdfUrl =
        URL.createObjectURL(pdfBlob);

      const newTab = window.open(
        pdfUrl,
        '_blank'
      );

      if (!newTab) {
        window.location.href = pdfUrl;
      }

      setWorkflowState('COMPLETED');
    } catch (exception) {
      setError(
        exception?.message ||
          'Report generation failed.'
      );
    } finally {
      setReportLoading(false);
    }
  };

  /* ---------------------------------------------------------
     Navigation
  --------------------------------------------------------- */

  const handleNavigate = (sectionId) => {
    const stageOrder = [
      'quality-assessment',
      'disease-prediction',
      'progression-simulation',
      'report-generation',
    ];

    const stageIndex =
      stageOrder.indexOf(sectionId);

    if (stageIndex === -1) {
      setError(
        'Invalid section requested.'
      );
      return;
    }

    /*
     * Determine the highest stage the user has
     * actually completed.
     */
    let completedStage = -1;

    if (
      workflowState ===
        'QUALITY_NOT_ANALYZED'
    ) {
      completedStage = -1;
    }

    if (
      workflowState ===
        'QUALITY_ANALYZED'
    ) {
      completedStage = 0;
    }

    if (
      workflowState ===
        'DISEASE_ANALYZED'
    ) {
      completedStage = 1;
    }

    if (
      workflowState ===
        'PROGRESSION_ANALYZED'
    ) {
      completedStage = 2;
    }

    if (
      workflowState ===
        'COMPLETED'
    ) {
      completedStage = 3;
    }

    /*
     * Current stage can always be opened.
     * Previously completed stages can always
     * be revisited.
     *
     * The next locked stage cannot be opened
     * until its prerequisite is completed.
     */
    if (stageIndex <= completedStage) {
      setActiveSection(sectionId);
      setError('');
      return;
    }

    /*
     * Stage 1 is accessible when an image has
     * been selected, even before quality analysis.
     */
    if (
      sectionId ===
        'quality-assessment' &&
      (selectedFile || workflowState === 'INITIAL')
    ) {
      setActiveSection(sectionId);
      setError('');
      return;
    }

    const stageNames = {
      'quality-assessment':
        'Image Quality Assessment',

      'disease-prediction':
        'Disease Prediction',

      'progression-simulation':
        'Progression Simulation',

      'report-generation':
        'Report Generation',
    };

    let prerequisiteMessage =
      'Please complete the previous workflow stage first.';

    if (
      stageIndex === 1
    ) {
      prerequisiteMessage =
        'Please complete Image Quality Assessment before opening Disease Prediction.';
    }

    if (
      stageIndex === 2
    ) {
      prerequisiteMessage =
        'Please complete Disease Prediction before opening Progression Simulation.';
    }

    if (
      stageIndex === 3
    ) {
      prerequisiteMessage =
        'Please complete Progression Simulation before opening Report Generation.';
    }

    setError(
      `${prerequisiteMessage}`
    );
  };

  /* ---------------------------------------------------------
     Render
  --------------------------------------------------------- */

  return (
    <div className="app-container">
      <Sidebar
        activeSection={activeSection}
        onNavigate={handleNavigate}
        workflowState={workflowState}
      />

      <main className="app-shell">
        {/* Header */}
        <header className="topbar">
          <div className="brand-wrap">
            <div className="brand-mark">
              <Activity size={18} />
            </div>

            <div>
              <p className="eyebrow">
                Research prototype
              </p>

              <h1>
                DR-ProgressionViz
              </h1>
            </div>
          </div>

          <div
            className={`status-badge ${
              backendStatus === 'ok'
                ? 'status-online'
                : backendStatus ===
                    'offline'
                  ? 'status-offline'
                  : ''
            }`}
          >
            <span className="dot" />

            {backendStatus === 'ok'
              ? 'Backend online'
              : backendStatus ===
                  'offline'
                ? 'Backend offline'
                : 'Checking backend...'}
          </div>
        </header>

        {/* Hero */}
        <section className="hero-block">
          <div>
            <p className="eyebrow warm">
              AI-powered retinal screening &
              disease intelligence
            </p>

            <h2>
              4-Stage Sequential Workflow
              for Comprehensive Analysis
            </h2>
          </div>

          <p className="hero-copy">
            Upload → Image Quality Assessment
            → Disease Prediction →
            Progression Simulation → Report
            Generation
          </p>
        </section>

        <div className="workspace-grid">
          <div className="workspace-main">
            {/* =================================================
                STAGE 1
            ================================================= */}

            {activeSection ===
              'quality-assessment' && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      Stage 1
                    </p>

                    <h2>
                      Image Quality Assessment
                    </h2>
                  </div>
                </div>

                <ImageUpload
                  file={selectedFile}
                  previewUrl={previewUrl}
                  onFileSelect={
                    handleFileSelect
                  }
                  onRemove={clearUpload}
                  onAnalyze={
                    !qualityResult
                      ? handleQualityAnalysis
                      : null
                  }
                  isLoading={loading}
                  disabled={!selectedFile}
                  analyzeButtonText={
                    qualityResult
                      ? 'Quality Analysis Complete'
                      : 'Analyze Image Quality'
                  }
                  uploadOnly={
                    workflowState ===
                    'INITIAL'
                  }
                />

                {loading && (
                  <LoadingState
                    message="Analyzing image quality..."
                  />
                )}

                {error && (
                  <ErrorState
                    message={error}
                  />
                )}

                {qualityResult && (
                  <>
                    <ImageQualityCard
                      quality={qualityResult}
                      enhancement={
                        enhancementResult
                      }
                    />

                    <div className="stage-actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                          setActiveSection(
                            'disease-prediction'
                          )
                        }
                      >
                        <ArrowRight
                          size={16}
                        />

                        Proceed to Disease
                        Prediction
                      </button>
                    </div>
                  </>
                )}
              </section>
            )}

            {/* =================================================
                STAGE 2
            ================================================= */}

            {activeSection ===
              'disease-prediction' && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      Stage 2
                    </p>

                    <h2>
                      Disease Prediction
                    </h2>
                  </div>
                </div>

                {workflowState ===
                  'QUALITY_ANALYZED' && (
                  <div className="stage-actions">
                    <button
                      type="button"
                      className="primary-button"
                      onClick={
                        handleDiseasePrediction
                      }
                      disabled={loading}
                    >
                      {loading
                        ? 'Analyzing...'
                        : 'Run Disease Prediction'}
                    </button>
                  </div>
                )}

                {loading && (
                  <LoadingState
                    message="Analyzing diabetic retinopathy..."
                  />
                )}

                {error && (
                  <ErrorState
                    message={error}
                  />
                )}

                {originalPrediction && (
                  <>
                    {qualityResult && (
                      <section className="panel info-panel">
                        <div className="section-heading compact-heading">
                          <div>
                            <p className="eyebrow">
                              Prediction Strategy
                            </p>

                            <h3>
                              {qualityResult.status ===
                              'GOOD'
                                ? 'Single Prediction (Good Quality)'
                                : 'Dual Prediction (Quality Concern)'}
                            </h3>
                          </div>
                        </div>

                        <p>
                          {qualityResult.status ===
                          'GOOD'
                            ? 'Image quality is good. The original uploaded image is used for DR prediction.'
                            : `Image quality is ${String(
                                qualityResult.status ||
                                  ''
                              ).toLowerCase()}. Both the original and enhanced images are analyzed separately.`}
                        </p>
                      </section>
                    )}

                    {/* Original prediction */}
                    <div className="summary-grid">
                      <div className="panel image-panel">
                        <div className="panel-label">
                          Original Image
                        </div>

                        <img
                          src={previewUrl}
                          alt="Original retinal image"
                        />
                      </div>

                      <PredictionCard
                        prediction={
                          originalPrediction
                        }
                        title="Original Image Prediction"
                      />
                    </div>

                    {/* Enhanced prediction */}
                    {enhancedPrediction && (
                      <>
                        <div className="summary-grid">
                          <div className="panel image-panel">
                            <div className="panel-label">
                              Enhanced Image
                            </div>

                            {enhancementResult?.enhanced_image_url ? (
                              <img
                                src={
                                  enhancementResult.enhanced_image_url
                                }
                                alt="Enhanced retinal image"
                              />
                            ) : (
                              <p>
                                Enhanced image
                                unavailable.
                              </p>
                            )}
                          </div>

                          <PredictionCard
                            prediction={
                              enhancedPrediction
                            }
                            title="Enhanced Image Prediction"
                          />
                        </div>

                        <section className="panel comparison-panel">
                          <div className="section-heading compact-heading">
                            <div>
                              <p className="eyebrow warn">
                                Comparison Analysis
                              </p>

                              <h3>
                                Original vs Enhanced
                                Predictions
                              </h3>
                            </div>
                          </div>

                          <div className="comparison-grid">
                            <div className="comparison-item">
                              <h4>
                                Original Image
                              </h4>

                              <p>
                                Grade{' '}
                                {
                                  originalPrediction.grade
                                }
                                :{' '}
                                {
                                  originalPrediction.label
                                }
                              </p>

                              <p>
                                Confidence:{' '}
                                {Number(
                                  originalPrediction.confidence ||
                                    0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>

                            <div className="comparison-item">
                              <h4>
                                Enhanced Image
                              </h4>

                              <p>
                                Grade{' '}
                                {
                                  enhancedPrediction.grade
                                }
                                :{' '}
                                {
                                  enhancedPrediction.label
                                }
                              </p>

                              <p>
                                Confidence:{' '}
                                {Number(
                                  enhancedPrediction.confidence ||
                                    0
                                ).toFixed(1)}
                                %
                              </p>
                            </div>
                          </div>

                          <p className="comparison-note">
                            Both predictions are
                            displayed independently.
                            The enhanced prediction
                            does not replace the
                            original-image prediction.
                          </p>
                        </section>
                      </>
                    )}

                    {/* Existing analysis components */}

                    {reliabilityResult && (
                      <ReliabilityCard
                        reliability={
                          reliabilityResult
                        }
                        prediction={
                          originalPrediction
                        }
                      />
                    )}

                    {structureResult && (
                      <RetinalStructureCard
                        structure={
                          structureResult
                        }
                      />
                    )}

                    {lesionEvidence && (
                      <LesionEvidenceCard
                        evidence={
                          lesionEvidence
                        }
                      />
                    )}

                    {gradcamResult && (
                      <section className="content-grid two-col">
                        <div className="stack-col">
                          <GradCAMViewer
                            imageUrl={
                              gradcamResult.url ||
                              gradcamResult.image_url ||
                              previewUrl
                            }
                            available={Boolean(
                              gradcamResult.available ??
                                gradcamResult.url ??
                                gradcamResult.image_url
                            )}
                          />
                        </div>
                      </section>
                    )}

                    <div className="stage-actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                          setActiveSection(
                            'progression-simulation'
                          )
                        }
                      >
                        <ArrowRight
                          size={16}
                        />

                        Continue to
                        Progression Simulation
                      </button>
                    </div>
                  </>
                )}
              </section>
            )}

            {/* =================================================
                STAGE 3
            ================================================= */}

            {activeSection ===
              'progression-simulation' && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      Stage 3
                    </p>

                    <h2>
                      Progression Simulation
                    </h2>
                  </div>
                </div>

                {workflowState ===
                  'DISEASE_ANALYZED' && (
                  <div className="stage-actions">
                    <button
                      type="button"
                      className="primary-button"
                      onClick={
                        handleProgressionAnalysis
                      }
                      disabled={loading}
                    >
                      {loading
                        ? 'Analyzing...'
                        : 'Run Progression Analysis'}
                    </button>
                  </div>
                )}

                {loading && (
                  <LoadingState
                    message="Analyzing progression and similar cases..."
                  />
                )}

                {error && (
                  <ErrorState
                    message={error}
                  />
                )}

                {progressionResults && (
                  <>
                    <section className="panel warning-panel">
                      <div className="section-heading compact-heading">
                        <div>
                          <p className="eyebrow warn">
                            Scientific Limitation
                          </p>

                          <h3>
                            Cross-sectional
                            Reference Analysis
                          </h3>
                        </div>
                      </div>

                      <p>
                        This progression analysis
                        uses cross-sectional
                        dataset references and
                        does not represent true
                        longitudinal patient
                        progression. Retrieved
                        cases show similar
                        patterns at different
                        disease stages but are
                        not a longitudinal
                        prediction of this specific
                        patient's future
                        progression. Clinical review
                        and longitudinal monitoring
                        are required for actual
                        progression assessment.
                      </p>
                    </section>

                    <section className="content-grid single-col">
                      <ProgressionMap
                        progressionMap={
                          progressionResults.progression_map ||
                          {}
                        }
                        currentGrade={
                          originalPrediction?.grade
                        }
                      />
                    </section>

                    {progressionResults.progression_simulation?.available && (
                      <section className="content-grid single-col">
                        <ProgressionSimulation
                          stages={
                            progressionResults
                              .progression_simulation
                              .results ||
                            progressionResults
                              .progression_simulation
                              .stages ||
                            []
                          }
                        />
                      </section>
                    )}

                    <section className="content-grid single-col">
                      <SimilarCases
                        cases={
                          progressionResults.similar_cases ||
                          []
                        }
                      />
                    </section>

                    {progressionResults.disease_landscape && (
                      <RetinalDiseaseLandscapeCard
                        landscape={
                          progressionResults.disease_landscape
                        }
                      />
                    )}

                    {progressionResults.progression_prediction && (
                      <section className="panel">
                        <div className="section-heading">
                          <div>
                            <p className="eyebrow">
                              Progression Prediction
                            </p>

                            <h3>
                              Future Progression
                              Assessment
                            </h3>
                          </div>
                        </div>

                        <div className="prediction-summary">
                          <p>
                            <strong>
                              Predicted Risk Level:
                            </strong>{' '}
                            {progressionResults
                              .progression_prediction
                              .risk_level ||
                              'Not available'}
                          </p>

                          <p>
                            <strong>
                              Time Horizon:
                            </strong>{' '}
                            {progressionResults
                              .progression_prediction
                              .time_horizon ||
                              'Not specified'}
                          </p>

                          {progressionResults
                            .progression_prediction
                            .confidence !==
                            undefined &&
                            progressionResults
                              .progression_prediction
                              .confidence !==
                              null && (
                              <p>
                                <strong>
                                  Model Confidence:
                                </strong>{' '}
                                {
                                  progressionResults
                                    .progression_prediction
                                    .confidence
                                }
                                %
                              </p>
                            )}
                        </div>

                        <p className="disclaimer-note">
                          <strong>
                            Experimental feature:
                          </strong>{' '}
                          This progression prediction
                          is based on cross-sectional
                          data patterns and should not
                          be used as the sole basis for
                          clinical decisions.
                        </p>
                      </section>
                    )}

                    {evidenceSummary && (
                      <ClinicalEvidenceCard
                        summary={
                          evidenceSummary
                        }
                      />
                    )}

                    <div className="stage-actions">
                      <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                          setActiveSection(
                            'report-generation'
                          )
                        }
                      >
                        <FileText
                          size={16}
                        />

                        Generate Comprehensive
                        Report
                      </button>
                    </div>
                  </>
                )}
              </section>
            )}

            {/* =================================================
                STAGE 4
            ================================================= */}

            {activeSection ===
              'report-generation' && (
              <section className="panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">
                      Stage 4
                    </p>

                    <h2>
                      Report Generation
                    </h2>
                  </div>
                </div>

                {analysisId &&
                  workflowState !==
                    'QUALITY_NOT_ANALYZED' && (
                    <>
                      <section className="workflow-status">
                        <div className="status-header">
                          <CheckCircle2
                            size={20}
                            className="text-success"
                          />

                          <h3>
                            4-Stage Analysis
                            Workflow
                          </h3>
                        </div>

                        <div className="status-grid">
                          <div className="status-item">
                            <span className="status-label">
                              Quality Assessment
                            </span>

                            <span
                              className={`status-value ${
                                qualityResult?.status?.toLowerCase() ||
                                'pending'
                              }`}
                            >
                              {qualityResult?.status ||
                                'Pending'}
                            </span>
                          </div>

                          <div className="status-item">
                            <span className="status-label">
                              Disease Prediction
                            </span>

                            <span className="status-value completed">
                              {originalPrediction
                                ? enhancedPrediction
                                  ? 'Dual Analysis'
                                  : 'Complete'
                                : 'Pending'}
                            </span>
                          </div>

                          <div className="status-item">
                            <span className="status-label">
                              Progression
                            </span>

                            <span
                              className={`status-value ${
                                progressionResults
                                  ? 'completed'
                                  : 'pending'
                              }`}
                            >
                              {progressionResults
                                ? 'Complete'
                                : 'Pending'}
                            </span>
                          </div>

                          <div className="status-item">
                            <span className="status-label">
                              Report
                            </span>

                            <span
                              className={`status-value ${
                                workflowState ===
                                'COMPLETED'
                                  ? 'completed'
                                  : 'pending'
                              }`}
                            >
                              {workflowState ===
                              'COMPLETED'
                                ? 'Generated'
                                : 'Ready'}
                            </span>
                          </div>
                        </div>
                      </section>

                      <div className="results-header">
                        <div>
                          <p className="eyebrow warm">
                            Analysis ID
                          </p>

                          <h3>
                            {analysisId}
                          </h3>
                        </div>

                        <button
                          type="button"
                          className="primary-button"
                          onClick={
                            handleReportGenerate
                          }
                          disabled={
                            reportLoading ||
                            !qualityResult ||
                            !originalPrediction ||
                            !progressionResults
                          }
                        >
                          {reportLoading
                            ? 'Generating PDF...'
                            : 'Generate PDF Report'}
                        </button>
                      </div>

                      <ReportPanel
                        analysisId={analysisId}
                        onGenerate={
                          handleReportGenerate
                        }
                        originalPrediction={
                          originalPrediction
                        }
                        enhancedPrediction={
                          enhancedPrediction
                        }
                        qualityResult={
                          qualityResult
                        }
                        progressionResults={
                          progressionResults
                        }
                      />

                      {workflowState ===
                        'COMPLETED' && (
                        <section className="panel success-panel">
                          <div className="empty-state">
                            <CheckCircle2
                              size={22}
                              className="text-success"
                            />

                            <div>
                              <h3>
                                Analysis Complete
                              </h3>

                              <p>
                                Comprehensive
                                retinal analysis
                                has been completed
                                successfully.
                              </p>

                              <ul className="completion-list">
                                <li>
                                  • Image quality
                                  assessment and
                                  enhancement details
                                </li>

                                <li>
                                  •{' '}
                                  {enhancedPrediction
                                    ? 'Dual prediction analysis (original + enhanced)'
                                    : 'Disease prediction analysis'}
                                </li>

                                <li>
                                  • Model reliability
                                  and uncertainty
                                  metrics
                                </li>

                                <li>
                                  • Retinal structure
                                  and lesion evidence
                                </li>

                                <li>
                                  • Grad-CAM
                                  explanations
                                </li>

                                <li>
                                  • Progression mapping
                                  and similar case
                                  references
                                </li>

                                <li>
                                  • Clinical evidence
                                  summary and
                                  limitations
                                </li>
                              </ul>

                              <p className="completion-note">
                                <strong>
                                  Research Use
                                  Only:
                                </strong>{' '}
                                This AI-generated
                                report is for research
                                and educational
                                purposes. Clinical
                                validation and expert
                                review are required for
                                diagnostic applications.
                              </p>
                            </div>
                          </div>
                        </section>
                      )}
                    </>
                  )}

                {!analysisId && (
                  <section className="panel empty-panel">
                    <div className="empty-state">
                      <FileText size={22} />

                      <div>
                        <h3>
                          No Analysis Available
                        </h3>

                        <p>
                          Complete the previous
                          workflow stages to
                          generate a comprehensive
                          report.
                        </p>
                      </div>
                    </div>
                  </section>
                )}

                {error && (
                  <ErrorState
                    message={error}
                  />
                )}
              </section>
            )}

            {/* =================================================
                INITIAL EMPTY STATE
            ================================================= */}

            {workflowState === 'INITIAL' &&
              activeSection ===
                'quality-assessment' &&
              !selectedFile && (
                <section className="panel empty-panel">
                  <div className="empty-state">
                    <RefreshCcw size={22} />

                    <div>
                      <h3>
                        Start Your Analysis
                      </h3>

                      <p>
                        Upload a retinal image to
                        begin the 4-stage
                        comprehensive analysis
                        workflow.
                      </p>
                    </div>
                  </div>
                </section>
              )}
          </div>

          {/* =================================================
              RIGHT SIDE INFORMATION
          ================================================= */}

          <aside className="workspace-side">
            <div className="side-card">
              <div className="side-header">
                <ShieldAlert size={18} />

                <span>
                  Medical Safety
                </span>
              </div>

              <p>
                AI-assisted screening
                prototype. This frontend does
                not replace ophthalmologist
                review and is intended for
                research workflow demonstration.
              </p>
            </div>

            <div className="side-card">
              <div className="side-header">
                <CheckCircle2 size={18} />

                <span>
                  Frontend readiness
                </span>
              </div>

              <ul>
                <li>
                  Live backend analysis
                </li>

                <li>
                  Case-based stage references
                </li>

                <li>
                  Similar-case retrieval
                </li>

                <li>
                  Grad-CAM and PDF report
                </li>
              </ul>
            </div>

            <div className="side-card">
              <div className="side-header">
                <ArrowRight size={18} />

                <span>
                  Workflow
                </span>
              </div>

              <p>
                Complete each analysis stage
                sequentially. Previously
                completed stages can be revisited
                without restarting the case.
              </p>
            </div>
          </aside>
        </div>

        <footer className="footer-bar">
          <div>
            <FileText size={15} />

            <span>
              AI Screening Report
            </span>
          </div>

          <span>
            Research prototype only
          </span>
        </footer>
      </main>
    </div>
  );
}

export default App;