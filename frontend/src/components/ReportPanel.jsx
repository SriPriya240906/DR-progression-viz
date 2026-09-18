import { FileText, Download, CheckCircle2, AlertTriangle, Eye, Activity } from 'lucide-react';

export function ReportPanel({ 
  analysisId, 
  onGenerate, 
  originalPrediction,
  enhancedPrediction,
  qualityResult,
  progressionResults 
}) {
  const hasEnhancedPrediction = enhancedPrediction && qualityResult?.status !== 'GOOD';
  
  return (
    <section className="panel report-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">AI Screening Report</p>
          <h2>Comprehensive Analysis Summary</h2>
        </div>
      </div>

      {/* Report Summary Grid */}
      <div className="report-summary-grid">
        {/* Stage 1 Summary */}
        <div className="report-stage-card">
          <div className="stage-icon">
            <Eye size={20} />
          </div>
          <div className="stage-content">
            <h4>Image Quality</h4>
            <p className={`status-badge ${qualityResult?.status?.toLowerCase() || 'unknown'}`}>
              {qualityResult?.status || 'Not Available'}
            </p>
            <small>
              {qualityResult?.status === 'GOOD' 
                ? 'Excellent quality for analysis'
                : qualityResult?.status === 'BORDERLINE'
                  ? 'Adequate quality, enhanced analysis provided'
                  : qualityResult?.status === 'POOR'
                    ? 'Poor quality, enhancement attempted'
                    : 'Quality assessment pending'
              }
            </small>
          </div>
        </div>

        {/* Stage 2 Summary */}
        <div className="report-stage-card">
          <div className="stage-icon">
            <Activity size={20} />
          </div>
          <div className="stage-content">
            <h4>Disease Assessment</h4>
            {originalPrediction ? (
              <>
                <p className={`grade-badge grade-${originalPrediction.grade}`}>
                  Grade {originalPrediction.grade}: {originalPrediction.label}
                </p>
                <small>
                  {hasEnhancedPrediction 
                    ? `Dual predictions available (Original & Enhanced)`
                    : `Single prediction analysis`
                  }
                </small>
              </>
            ) : (
              <p className="status-badge unknown">Assessment Pending</p>
            )}
          </div>
        </div>

        {/* Stage 3 Summary */}
        <div className="report-stage-card">
          <div className="stage-icon">
            <CheckCircle2 size={20} />
          </div>
          <div className="stage-content">
            <h4>Progression Analysis</h4>
            {progressionResults ? (
              <>
                <p className="status-badge completed">Analysis Complete</p>
                <small>
                  Similar cases: {progressionResults.similar_cases?.length || 0}, 
                  Progression map: {Object.keys(progressionResults.progression_map || {}).length} stages
                </small>
              </>
            ) : (
              <p className="status-badge pending">Analysis Pending</p>
            )}
          </div>
        </div>
      </div>

      {/* Dual Prediction Notice */}
      {hasEnhancedPrediction && (
        <div className="dual-prediction-notice">
          <AlertTriangle size={16} />
          <div>
            <strong>Dual Prediction Analysis</strong>
            <p>
              Due to {qualityResult.status.toLowerCase()} image quality, both original and enhanced image 
              predictions are included in this report for comprehensive clinical review.
            </p>
          </div>
        </div>
      )}

      {/* Report Generation Section */}
      <div className="report-generation">
        <div className="report-cta">
          <FileText size={34} />
          <div className="report-details">
            <strong>Comprehensive AI Screening Report</strong>
            <p>
              Complete 4-stage analysis including quality assessment, disease prediction
              {hasEnhancedPrediction ? ' (dual predictions)' : ''}, progression analysis, 
              and clinical evidence summary.
            </p>
            <ul className="report-includes">
              <li>• Quality metrics and enhancement details</li>
              <li>• {hasEnhancedPrediction ? 'Dual prediction' : 'Disease prediction'} results with confidence scores</li>
              <li>• Grad-CAM visualizations and model explainability</li>
              <li>• Retinal structure and lesion analysis</li>
              <li>• Progression mapping and similar case references</li>
              <li>• Clinical evidence summary and limitations</li>
            </ul>
          </div>
        </div>
        
        <div className="report-actions">
          <button 
            type="button" 
            className="primary-button report-button" 
            onClick={() => onGenerate(analysisId)}
          >
            <Download size={16} /> 
            Generate Complete PDF Report
          </button>
          
          <div className="report-disclaimer">
            <p>
              <strong>Research Prototype:</strong> This report is generated from an experimental 
              AI system for research purposes. Clinical review and validation are required before 
              any diagnostic decisions.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
