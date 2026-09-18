function formatFraction(value) {
  return typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : 'Unavailable';
}

function Availability({ label, item }) {
  return (
    <div className="structure-item">
      <span>{label}</span>
      <strong>{item?.available ? 'Available' : 'Unavailable'}</strong>
      <small>{item?.available ? item.method || 'Experimental estimate' : item?.reason || 'No defensible local method available.'}</small>
    </div>
  );
}

export function RetinalStructureCard({ structure }) {
  if (!structure) {
    return (
      <section className="panel structure-panel">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">Retinal Structure</p>
            <h2>Structure analysis unavailable</h2>
          </div>
        </div>
        <p className="muted">No structural estimate was returned. This layer does not affect the DR model input.</p>
      </section>
    );
  }

  const field = structure.field_of_view || {};
  const vessels = structure.vessels || {};
  return (
    <section className="panel structure-panel" id="retinal-structure">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">Retinal Structure</p>
          <h2>Experimental structure review</h2>
        </div>
        <span className="tag">Not a clinical measurement</span>
      </div>

      <p className="quality-assessment">{structure.method_status || 'Experimental image-processing estimate.'}</p>
      <div className="structure-grid">
        <div className="quality-metric"><span>Retinal field estimate</span><strong>{formatFraction(field.fraction)}</strong><small>{field.sufficient_for_analysis ? 'Sufficient for this experimental analysis' : 'Insufficient for vessel-like analysis'}</small></div>
        <div className="quality-metric"><span>Field center</span><strong>{field.center ? `${field.center.x}, ${field.center.y}` : 'Unavailable'}</strong><small>Pixel coordinates in the uploaded image</small></div>
        <div className="quality-metric"><span>Vessel-like fraction</span><strong>{formatFraction(vessels.vessel_like_fraction)}</strong><small>{vessels.confidence_available ? 'Model-supported estimate' : 'No validated confidence available'}</small></div>
      </div>

      <div className="structure-items">
        <Availability label="Vessel structure" item={vessels} />
        <Availability label="Optic disc" item={structure.optic_disc} />
        <Availability label="Fovea" item={structure.fovea} />
      </div>

      {structure.overlay_image_url && (
        <figure className="structure-overlay">
          <img src={structure.overlay_image_url} alt="Experimental vessel-like structure overlay" />
          <figcaption>Experimental vessel-like response overlay; not validated vessel segmentation.</figcaption>
        </figure>
      )}
      <p className="muted">Structure estimates are separate from image quality and model uncertainty. The original image remains the DR classifier input.</p>
    </section>
  );
}
