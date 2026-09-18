function formatFraction(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : 'Unavailable';
}

function CandidateMetric({ label, candidate }) {
  return (
    <div className="quality-metric">
      <span>{label}</span>
      <strong>{candidate?.count ?? 'Unavailable'} regions</strong>
      <small>{formatFraction(candidate?.fraction)} of estimated retinal field</small>
    </div>
  );
}

export function LesionEvidenceCard({ evidence }) {
  if (!evidence) {
    return (
      <section className="panel lesion-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">Lesion-Level Evidence</p>
            <h2>Candidate localization unavailable</h2>
          </div>
        </div>
        <p className="muted">No experimental candidate evidence was returned. The DR model output remains separate.</p>
      </section>
    );
  }

  const overlays = evidence.overlay_image_urls || {};
  return (
    <section className="panel lesion-panel" id="lesion-evidence">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">Lesion-Level Evidence</p>
          <h2>Experimental candidate localization</h2>
        </div>
        <span className="tag">Not a confirmed clinical lesion detector</span>
      </div>

      <p className="quality-assessment">Dark and bright candidate regions are image-processing evidence only. They are not confirmed microaneurysms, hemorrhages, or exudates.</p>
      <div className="lesion-metrics-grid">
        <CandidateMetric label="Dark candidate regions" candidate={evidence.dark_candidates} />
        <CandidateMetric label="Bright candidate regions" candidate={evidence.bright_candidates} />
      </div>

      <div className="structure-items">
        <div className="structure-item"><span>Neovascularization</span><strong>Unavailable</strong><small>{evidence.neovascularization?.reason}</small></div>
        <div className="structure-item"><span>Optic-disc exclusion</span><strong>Unavailable</strong><small>{evidence.optic_disc_exclusion?.reason}</small></div>
      </div>

      <div className="lesion-overlays">
        {['dark', 'bright', 'combined'].map((kind) => overlays[kind] && (
          <figure key={kind}>
            <img src={overlays[kind]} alt={`${kind} experimental candidate overlay`} />
            <figcaption>{kind} candidates</figcaption>
          </figure>
        ))}
      </div>
      <p className="muted">Candidate localization is separate from Grad-CAM, vessel-like structure estimation, model reliability, and DR prediction. No disease score is calculated.</p>
    </section>
  );
}
