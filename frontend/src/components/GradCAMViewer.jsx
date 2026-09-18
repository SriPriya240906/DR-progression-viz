export function GradCAMViewer({ imageUrl, available = true }) {
  return (
    <section className="panel gradcam-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">AI Explainability</p>
          <h2>Grad-CAM Explanation</h2>
        </div>
        <span className="tag">Original / overlay</span>
      </div>

      {available && imageUrl ? (
        <div className="gradcam-grid">
          <figure className="compare-card">
            <img src={imageUrl} alt="Original retinal image" />
            <figcaption>Original / overlay</figcaption>
          </figure>
        </div>
      ) : (
        <div className="muted">Grad-CAM unavailable for this analysis.</div>
      )}

      <p className="explanation-copy">
        {available
          ? 'Highlighted regions represent image areas that contributed strongly to the model\'s prediction.'
          : 'The backend did not return a Grad-CAM image for this case.'}
      </p>
    </section>
  );
}
