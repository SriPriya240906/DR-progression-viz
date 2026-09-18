export function DigitalTwinCard({ twin, grade, confidence, qualityLabel }) {
  return (
    <section className="panel twin-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Retinal Digital Twin</p>
          <h2>AI-derived representation of the current retinal disease state</h2>
        </div>
      </div>

      <div className="twin-layout">
        <div className="twin-state-card">
          <span className="mini-label">Current State</span>
          <h3>{grade >= 0 ? `Grade ${grade}` : 'Pending analysis'}</h3>
          <p>{twin?.state || 'Current-state representation'}</p>
          <div className="twin-metrics">
            <div>
              <span>Confidence</span>
              <strong>{confidence.toFixed(1)}%</strong>
            </div>
            <div>
              <span>Image Quality</span>
              <strong>{qualityLabel}</strong>
            </div>
          </div>
        </div>

        <div className="fingerprint-card">
          <span className="mini-label">Retinal Feature Fingerprint</span>
          <div className="fingerprint-visual" aria-label="AI-derived retinal feature representation">
            {[0.52, 0.64, 0.72, 0.78, 0.88, 0.92, 0.84, 0.71].map((value, index) => (
              <span key={index} style={{ height: `${value * 100}%` }} />
            ))}
          </div>
          <p>AI-derived retinal feature representation</p>
        </div>
      </div>
    </section>
  );
}
