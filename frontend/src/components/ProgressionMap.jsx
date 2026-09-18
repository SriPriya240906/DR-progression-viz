export function ProgressionStage({ title, items, stageIndex, current = false }) {
  const representative = items?.[0];

  return (
    <div className="stage-row">
      <div className="stage-title">
        <span>Stage {stageIndex}</span>
        <div>
          <h3>{title}</h3>
          <small>{current ? 'Current stage' : 'Later reference stage'}</small>
        </div>
      </div>

      <div className="case-grid compact-grid">
        {representative ? (
          <article className="case-card compact-card">
            <img src={representative.image_url} alt={`${title} reference stage`} />
            <div className="case-meta">
              <span>Similarity</span>
              <strong>{Number(representative.similarity).toFixed(4)}</strong>
            </div>
            <div className="case-meta muted-meta">
              <span>Case-based reference</span>
              <strong>{title}</strong>
            </div>
          </article>
        ) : (
          <p className="muted">No reference image returned for this stage.</p>
        )}
      </div>
    </div>
  );
}

export function ProgressionMap({ progressionMap, currentGrade }) {
  const stageTitles = {
    stage_0: 'No Diabetic Retinopathy',
    stage_1: 'Mild',
    stage_2: 'Moderate',
    stage_3: 'Severe',
    stage_4: 'Proliferative DR',
  };

  const hasCases = Object.values(progressionMap || {}).some((stage) => {
    const cases = Array.isArray(stage?.cases) ? stage.cases : stage;
    return Array.isArray(cases) && cases.length > 0;
  });

  if (currentGrade === 0 || !hasCases) {
    return (
      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow warm">Case-Based Progression Map</p>
            <h2>{currentGrade === 0 ? 'Not shown for No DR' : 'Unavailable for this analysis'}</h2>
          </div>
        </div>
        <p className="muted">
          {currentGrade === 0
            ? 'No disease progression stages are shown for a No Diabetic Retinopathy assessment.'
            : 'The backend did not return progression-map cases.'}
        </p>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Case-Based Progression Map</p>
          <h2>Stages 0 to 4</h2>
        </div>
      </div>

      <p className="muted">Current stage and later case-based reference stages, not a claim of this patient&apos;s actual longitudinal progression.</p>

      <div className="stage-list">
        {Object.entries(stageTitles).map(([key, label], index) => {
          if (index < currentGrade) return null;

          const items = Array.isArray(progressionMap?.[key]?.cases)
            ? progressionMap[key].cases
            : Array.isArray(progressionMap?.[key])
              ? progressionMap[key]
              : [];

          return <ProgressionStage key={key} title={label} items={items} stageIndex={index} current={index === currentGrade} />;
        })}
      </div>
    </section>
  );
}
