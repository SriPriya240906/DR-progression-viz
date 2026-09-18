function formatProbability(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : 'Unavailable';
}

function formatMetric(value) {
  return typeof value === 'number' ? value.toFixed(3) : 'Unavailable';
}

export function ReliabilityCard({ reliability, prediction }) {
  if (!reliability) {
    return (
      <section className="panel reliability-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">Model Reliability &amp; Uncertainty</p>
            <h2>Reliability analysis unavailable</h2>
          </div>
        </div>
        <p className="muted">Probability-distribution metrics were unavailable. Model confidence is not diagnostic certainty.</p>
      </section>
    );
  }

  const calibration = reliability.calibration || {};
  return (
    <section className="panel reliability-panel" id="reliability">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">Model Reliability &amp; Uncertainty</p>
          <h2>Probability distribution review</h2>
        </div>
        <span className="tag">No clinical reliability score</span>
      </div>

      <p className="quality-assessment">Predicted class: <strong>{reliability.predicted_label || prediction?.label || 'Unknown'}</strong></p>
      <div className="reliability-metrics-grid">
        <div className="quality-metric"><span>Model confidence</span><strong>{formatProbability(reliability.confidence)}</strong><small>Maximum model probability</small></div>
        <div className="quality-metric"><span>Top-2 margin</span><strong>{formatProbability(reliability.probability_margin)}</strong><small>Top probability minus second probability</small></div>
        <div className="quality-metric"><span>Predictive entropy</span><strong>{formatMetric(reliability.predictive_entropy)}</strong><small>Distribution entropy in nats</small></div>
        <div className="quality-metric"><span>Normalized entropy</span><strong>{formatMetric(reliability.normalized_predictive_entropy)}</strong><small>Scaled from 0 to 1 for this class count</small></div>
      </div>

      <div className="reliability-calibration">
        <strong>Calibration</strong>
        <span>{calibration.available ? `Evaluated with ${calibration.method || 'a documented method'}.` : 'Unavailable: no defensible held-out calibration split was available.'}</span>
      </div>
      <p className="muted">{reliability.interpretation || 'Model confidence is not diagnostic certainty. Clinical review remains required.'}</p>
    </section>
  );
}
