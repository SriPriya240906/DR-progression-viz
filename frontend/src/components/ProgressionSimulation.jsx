export function ProgressionSimulation({ stages }) {
  const timelineStages = (stages || []).filter((stage) => stage?.image_url || stage?.image);

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Progression Simulation</p>
          <h2>Reference stage timeline</h2>
        </div>
      </div>

      <div className="timeline">
        {timelineStages.map((stage, index) => (
          <div key={`${stage.stage ?? stage.grade ?? index}-${index}`} className="timeline-step">
            <div className="timeline-marker" aria-hidden="true" />
            {index < timelineStages.length - 1 && <div className="timeline-line" aria-hidden="true" />}
            <div className="timeline-card">
              <img src={stage.image_url || stage.image} alt={`${stage.label || `Stage ${stage.stage ?? stage.grade ?? index}`} reference`} />
              <div className="timeline-copy">
                <span>{stage.label || `Stage ${stage.stage ?? stage.grade ?? index}`}</span>
                <small>{stage.synthetic ? 'Backend reference' : 'Current'}</small>
              </div>
            </div>
          </div>
        ))}

        {timelineStages.length === 0 && <p className="muted">No progression simulation data available for this case.</p>}
      </div>
    </section>
  );
}
