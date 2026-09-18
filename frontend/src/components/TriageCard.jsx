export function TriageCard({ triage }) {
  const statusStyles = {
    GREEN: 'green',
    YELLOW: 'yellow',
    RED: 'red',
    GRAY: 'gray',
  };

  const status = triage?.status || 'GREEN';
  const details = {
    GREEN: {
      reason: 'Image quality acceptable',
      recommendation: 'AI assessment available',
    },
    YELLOW: {
      reason: 'Model uncertainty elevated',
      recommendation: 'Human review recommended',
    },
    RED: {
      reason: 'Referable DR pattern detected',
      recommendation: 'Ophthalmologist review recommended',
    },
    GRAY: {
      reason: 'Image quality insufficient',
      recommendation: 'Recapture required',
    },
  };

  const info = details[status] || details.GREEN;

  return (
    <section className="panel triage-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">AI Screening Triage</p>
          <h2>{status}</h2>
        </div>
        <span className={`status-pill ${statusStyles[status] || 'green'}`}>{status}</span>
      </div>

      <div className="triage-stack">
        <div className="triage-item">
          <span>Status</span>
          <strong>{status}</strong>
        </div>
        <div className="triage-item">
          <span>Reason</span>
          <strong>{triage?.reason || info.reason}</strong>
        </div>
        <div className="triage-item">
          <span>Recommended next step</span>
          <strong>{triage?.recommendation || info.recommendation}</strong>
        </div>
      </div>
    </section>
  );
}
