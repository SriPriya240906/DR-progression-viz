const evidence = [
  'Model prediction',
  'Retinal similarity',
  'Feature representation',
  'Image quality',
  'Structural evidence',
];

export function EvidencePanel() {
  return (
    <section className="panel evidence-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">AI Evidence</p>
          <h2>Evidence Streams</h2>
        </div>
      </div>
      <div className="evidence-list">
        {evidence.map((item) => (
          <div key={item} className="evidence-item">
            <span className="evidence-dot" aria-hidden="true" />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
