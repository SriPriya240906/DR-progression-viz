import { AlertTriangle, CheckCircle2 } from 'lucide-react';

const statusCopy = {
  GOOD: 'Good quality',
  BORDERLINE: 'Quality concern',
  POOR: 'Poor quality',
};

function metricAssessment(metric) {
  return metric?.assessment || 'Unavailable';
}

function QualityMetric({ label, value, detail }) {
  return (
    <div className="quality-metric">
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <small>{detail}</small>
    </div>
  );
}

function ComparisonMetric({ label, original, enhanced }) {
  return (
    <div className="comparison-row">
      <span>{label}</span>
      <strong>{original ?? 'n/a'}</strong>
      <strong>{enhanced ?? 'n/a'}</strong>
    </div>
  );
}

export function ImageQualityCard({ quality, enhancement }) {
  if (!quality) {
    return (
      <section className="panel quality-panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow warm">Image Quality</p>
            <h2>Quality assessment unavailable</h2>
          </div>
        </div>
        <p className="muted">Image quality analysis was unavailable; the existing analysis results remain available.</p>
      </section>
    );
  }

  const status = quality.status || 'BORDERLINE';
  const StatusIcon = status === 'GOOD' ? CheckCircle2 : AlertTriangle;
  const resolution = quality.resolution || {};
  const focus = quality.focus || {};
  const illumination = quality.illumination || {};
  const contrast = quality.contrast || {};
  const fieldOfView = quality.field_of_view || {};
  const visibility = quality.retinal_visibility || {};

  return (
    <section className="panel quality-panel" id="image-quality">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">Image Quality</p>
          <h2>Assessment before model review</h2>
        </div>
        <span className={`quality-status ${status.toLowerCase()}`}>
          <StatusIcon size={16} />
          {statusCopy[status] || status}
        </span>
      </div>

      <p className="quality-assessment">{quality.overall_assessment}</p>
      <div className="quality-metrics-grid">
        <QualityMetric label="Focus" value={metricAssessment(focus)} detail={`${focus.value ?? 'n/a'} variance of Laplacian`} />
        <QualityMetric label="Illumination" value={metricAssessment(illumination)} detail={`${illumination.value ?? 'n/a'} mean brightness`} />
        <QualityMetric label="Contrast" value={metricAssessment(contrast)} detail={`${contrast.value ?? 'n/a'} grayscale standard deviation`} />
        <QualityMetric label="Resolution" value={`${resolution.width ?? 'n/a'} x ${resolution.height ?? 'n/a'}`} detail={resolution.assessment} />
        <QualityMetric label="Field of view" value="Heuristic" detail={fieldOfView.assessment} />
        <QualityMetric label="Retinal visibility" value="Heuristic" detail={visibility.assessment} />
      </div>

      {quality.warnings?.length > 0 && (
        <div className="quality-warnings">
          <strong>Warnings</strong>
          <ul>
            {quality.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
      )}

      <div className={`quality-recommendation ${status.toLowerCase()}`}>
        <strong>Recommendation</strong>
        <span>{quality.recommendation}</span>
      </div>

      <section className="enhancement-section" aria-label="Adaptive enhancement">
        <div className="section-heading compact-heading">
          <div>
            <p className="eyebrow warm">Adaptive Enhancement</p>
            <h3>{enhancement?.attempted ? 'Candidate comparison' : quality.status === 'GOOD' ? 'Not required' : 'Not attempted'}</h3>
          </div>
          {!enhancement?.attempted && <span className="tag">Original image will be used</span>}
        </div>

        {enhancement?.attempted ? (
          <>
            <div className="enhancement-images">
              <figure>
                <img src={enhancement.original_image_url || ''} alt="Original retinal image" />
                <figcaption>Original</figcaption>
              </figure>
              {enhancement.enhanced_image_url && (
                <figure>
                  <img src={enhancement.enhanced_image_url} alt="Adaptive enhancement preview" />
                  <figcaption>Enhanced preview</figcaption>
                </figure>
              )}
            </div>
            <div className="comparison-table">
              <div className="comparison-row comparison-header"><span>Metric</span><strong>Original</strong><strong>Enhanced</strong></div>
              <ComparisonMetric label="Focus" original={enhancement.original_quality?.focus?.value} enhanced={enhancement.enhanced_quality?.focus?.value} />
              <ComparisonMetric label="Contrast" original={enhancement.original_quality?.contrast?.value} enhanced={enhancement.enhanced_quality?.contrast?.value} />
              <ComparisonMetric label="Illumination" original={enhancement.original_quality?.illumination?.value} enhanced={enhancement.enhanced_quality?.illumination?.value} />
            </div>
            <p className={`enhancement-result ${enhancement.improved ? 'improved' : 'rejected'}`}>
              {enhancement.improved ? 'Quality metrics improved under the experimental comparison.' : 'No meaningful quality improvement detected.'}
            </p>
            <p className="muted">Method: {enhancement.method || 'Unavailable'}. The original image remains the DR model input.</p>
            <p className="quality-assessment">{enhancement.recommendation}</p>
          </>
        ) : (
          <p className="muted">{enhancement?.recommendation || 'Enhancement was not required. The original image will be used.'}</p>
        )}
      </section>
    </section>
  );
}
