import { useMemo } from 'react';

export function DiseaseLandscape({ points }) {
  const preparedPoints = useMemo(() => {
    return (points || []).map((point) => ({
      ...point,
      x: point.x * 2.6,
      y: point.y * 3.2,
    }));
  }, [points]);

  return (
    <section className="panel landscape-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Retinal Disease Landscape</p>
          <h2>Learned retinal feature space</h2>
        </div>
      </div>

      <div className="landscape-wrapper">
        <svg viewBox="0 0 360 260" role="img" aria-label="Disease landscape visualization">
          <defs>
            <radialGradient id="landscapeGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(24, 87, 112, 0.28)" />
              <stop offset="100%" stopColor="rgba(24, 87, 112, 0.02)" />
            </radialGradient>
          </defs>
          <rect x="0" y="0" width="360" height="260" rx="12" fill="url(#landscapeGlow)" />
          {[0, 1, 2, 3, 4].map((band) => (
            <line key={band} x1="18" x2="340" y1={30 + band * 52} y2={30 + band * 52} stroke="rgba(110,145,150,0.18)" strokeDasharray="5 6" />
          ))}
          {[0, 1, 2, 3, 4].map((band) => (
            <line key={`v-${band}`} x1={20 + band * 72} x2={20 + band * 72} y1="12" y2="240" stroke="rgba(110,145,150,0.12)" strokeDasharray="5 6" />
          ))}

          {preparedPoints.map((point) => (
            <g key={point.id}>
              <circle
                cx={point.x + 28}
                cy={point.y + 20}
                r={point.is_current ? 8 : 5.6}
                fill={point.is_current ? '#f4c86f' : ['#74c9d9', '#90c26d', '#e3bb69', '#d39776', '#d76d6d'][point.grade]}
                stroke={point.is_current ? '#fff' : 'rgba(255,255,255,0.7)'}
                strokeWidth={point.is_current ? 2.2 : 1.3}
              />
              {point.is_current && <text x={point.x + 42} y={point.y + 15} fill="#d9dfd7" fontSize="10">Current patient</text>}
            </g>
          ))}
        </svg>
      </div>
    </section>
  );
}
