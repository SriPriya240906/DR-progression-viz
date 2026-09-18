import { getGradeColor, gradeMeta } from '../data/mockData';

export function PredictionCard({ prediction, title }) {
  if (!prediction) {
    return null;
  }

  const meta = gradeMeta[prediction.grade] || gradeMeta[0];

  const probabilities = Array.isArray(prediction.probabilities)
    ? prediction.probabilities
    : [];

  const gradeLabels = [
    'No DR',
    'Mild NPDR',
    'Moderate NPDR',
    'Severe NPDR',
    'Proliferative DR',
  ];

  return (
    <section className="panel prediction-panel">
      <div className="section-heading compact-heading">
        <div>
          <p className="eyebrow warm">{title || 'DR Assessment'}</p>
          <h2>{meta.title}</h2>
        </div>

        <span
          className="grade-badge"
          style={{
            background: getGradeColor(prediction.grade),
          }}
        >
          Grade {prediction.grade}
        </span>
      </div>

      <div className="prediction-layout">
        <div className="prediction-main">
          <div className="metric-row">
            <span>Predicted stage</span>
            <strong>
              {prediction.label || meta.title}
            </strong>
          </div>

          <div className="metric-row">
            <span>Confidence</span>
            <strong>
              {Number(prediction.confidence || 0).toFixed(1)}%
            </strong>
          </div>

          <div className="metric-row">
            <span>Risk Level</span>
            <strong>
              {prediction.risk_level}
            </strong>
          </div>
        </div>

        <div
          className="confidence-dial"
          aria-label={`Prediction confidence ${Number(
            prediction.confidence || 0
          ).toFixed(1)} percent`}
        >
          <div
            className="dial-ring"
            style={{
              '--progress': `${Number(
                prediction.confidence || 0
              )}%`,
            }}
          >
            <span>
              {Number(prediction.confidence || 0).toFixed(1)}%
            </span>
          </div>

          <small>Confidence</small>
        </div>
      </div>

      {probabilities.length > 0 && (
        <div className="probability-section">
          <div className="probability-heading">
            <span>Grade probabilities</span>
            <small>Model output</small>
          </div>

          <div className="probability-list">
            {probabilities.map((probability, index) => {
              const percentage =
                Number(probability) <= 1
                  ? Number(probability) * 100
                  : Number(probability);

              const label =
                gradeLabels[index] ||
                `Grade ${index}`;

              return (
                <div
                  className="probability-row"
                  key={index}
                >
                  <div className="probability-label">
                    <span>
                      Grade {index}
                    </span>
                    <small>{label}</small>
                  </div>

                  <div className="probability-bar">
                    <div
                      className="probability-fill"
                      style={{
                        width: `${Math.min(
                          Math.max(percentage, 0),
                          100
                        )}%`,
                        background: getGradeColor(index),
                      }}
                    />
                  </div>

                  <strong>
                    {percentage.toFixed(1)}%
                  </strong>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}