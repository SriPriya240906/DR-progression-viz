export function SimilarCases({ cases }) {
  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Similar Retinal Cases</p>
          <h2>Nearest reference cases</h2>
        </div>
      </div>

      <div className="case-grid">
        {cases && cases.length > 0 ? (
          cases.map((caseItem, index) => (
            <article key={`${caseItem.image_url}-${index}`} className="case-card">
              <img src={caseItem.image_url} alt={`Similar retinal case ${index + 1}`} />
              <div className="case-meta">
                <span>Similarity</span>
                <strong>{caseItem.similarity.toFixed(4)}</strong>
              </div>
              <div className="case-meta muted-meta">
                <span>Stage</span>
                <strong>{caseItem.grade === undefined ? 'Unavailable' : caseItem.grade === 0 ? 'No DR' : `Grade ${caseItem.grade}`}</strong>
              </div>
            </article>
          ))
        ) : (
          <p className="muted">No similar cases available.</p>
        )}
      </div>
    </section>
  );
}
