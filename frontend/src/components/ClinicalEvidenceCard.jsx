function valueOrUnavailable(value, suffix = '') {
  return value === null || value === undefined ? 'Unavailable' : `${value}${suffix}`;
}

function Signal({ label, children }) {
  return (
    <div className="evidence-signal">
      <span>{label}</span>
      <strong>{children}</strong>
    </div>
  );
}

export function ClinicalEvidenceCard({ summary }) {
  if (!summary) {
    return (
      <section className="panel clinical-evidence-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">AI-Assisted Evidence Summary</p>
            <h2>Evidence summary unavailable</h2>
          </div>
        </div>
        <p className="muted">Independent evidence outputs remain available in their individual sections.</p>
      </section>
    );
  }

  const uncertainty = summary.model_uncertainty || {};
  const quality = summary.image_quality || {};
  const explanation = summary.model_explanation || {};
  const structure = summary.retinal_structure || {};
  const lesions = summary.lesion_evidence || {};
  return (
    <section className="panel clinical-evidence-panel" id="evidence-summary">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">AI-Assisted Evidence Summary</p>
          <h2>Independent signals, clearly separated</h2>
        </div>
        <span className="tag">No combined medical score</span>
      </div>

      <div className="evidence-block ai-output-block">
        <p className="mini-label">AI Model Output</p>
        <div className="evidence-grid">
          <Signal label="Predicted grade">{valueOrUnavailable(summary.prediction?.grade)}</Signal>
          <Signal label="Model label">{summary.prediction?.label || 'Unavailable'}</Signal>
          <Signal label="Model confidence">{valueOrUnavailable(summary.prediction?.confidence, '%')}</Signal>
          <Signal label="Top-2 margin">{valueOrUnavailable(uncertainty.probability_margin)}</Signal>
          <Signal label="Predictive entropy">{valueOrUnavailable(uncertainty.predictive_entropy)}</Signal>
          <Signal label="Calibration">{uncertainty.calibration_status || 'Unavailable'}</Signal>
        </div>
        <p className="muted">{summary.prediction?.statement} Confidence is not clinical certainty.</p>
      </div>

      <div className="evidence-block">
        <p className="mini-label">Supporting Image Evidence</p>
        <div className="evidence-grid">
          <Signal label="Image quality">{quality.status || 'Unavailable'}</Signal>
          <Signal label="Grad-CAM">{explanation.gradcam_available ? 'Available' : 'Unavailable'}</Signal>
          <Signal label="Vessel-like structure">{structure.available ? 'Experimental estimate' : 'Unavailable'}</Signal>
          <Signal label="Dark candidates">{valueOrUnavailable(lesions.dark_candidate_count)}</Signal>
          <Signal label="Bright candidates">{valueOrUnavailable(lesions.bright_candidate_count)}</Signal>
          <Signal label="Calibration">{uncertainty.calibration_status || 'Unavailable'}</Signal>
        </div>
        <p className="muted">{explanation.summary}</p>
        <p className="muted">{structure.summary}</p>
        <p className="muted">{lesions.summary}</p>
      </div>

      <div className="evidence-block clinical-limitation-block">
        <p className="mini-label">Clinical Limitation</p>
        <strong>Clinical review required</strong>
        <p className="muted">{summary.clinical_review?.reason || 'AI-assisted assessment requires clinical review.'}</p>
        <p className="muted">Supporting image-processing findings are experimental and are not confirmed clinical lesions or a standalone diagnosis.</p>
      </div>
    </section>
  );
}
