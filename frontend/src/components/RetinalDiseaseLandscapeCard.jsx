function statusLabel(status) {
  if (status === 'supported') return 'Available';
  if (status === 'experimental') return 'Experimental';
  if (status === 'reference-only') return 'Reference-only';
  return 'Not available';
}

export function RetinalDiseaseLandscapeCard({ landscape }) {
  if (!landscape) {
    return (
      <section className="panel disease-landscape-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">Retinal Disease Landscape</p>
            <h2>Capability map unavailable</h2>
          </div>
        </div>
        <p className="muted">Disease-specific capability information was unavailable. This does not indicate absence of any disease.</p>
      </section>
    );
  }

  const diseases = Array.isArray(landscape.diseases) ? landscape.diseases : [];
  return (
    <section className="panel disease-landscape-panel" id="disease-landscape">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">Retinal Disease Landscape</p>
          <h2>Capability map</h2>
        </div>
        <span className="tag">No multi-disease score</span>
      </div>
      <p className="quality-assessment">{landscape.current_supported_scope || 'Capabilities are reported from the models and data available in this repository.'}</p>
      <div className="disease-landscape-list">
        {diseases.map((disease) => (
          <article className={`disease-capability ${disease.status === 'supported' ? 'supported' : ''}`} key={disease.name}>
            <div className="disease-capability-heading">
              <h3>{disease.name}</h3>
              <span className="tag">{statusLabel(disease.status)}</span>
            </div>
            <div className="disease-capability-details">
              <span>Prediction: {disease.prediction_available ? 'Available' : 'Unavailable'}</span>
              <span>Model: {disease.model_available ? 'Available' : 'Unavailable'}</span>
            </div>
            {disease.labels?.length > 0 && <p className="muted">Labels: {disease.labels.join(', ')}</p>}
            <p className="muted">{disease.notes}</p>
          </article>
        ))}
      </div>
      <p className="muted">An unavailable disease-specific model does not indicate absence of that disease. Disease-specific clinical assessment requires appropriate examination and testing.</p>
    </section>
  );
}
