export function WhatIfExplorer() {
  const current = 'Current';
  const lower = 'Reference Lower-Severity State';
  const higher = 'Reference Higher-Severity State';

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow warm">What-If Retinal State Explorer</p>
          <h2>Counterfactual reference states</h2>
        </div>
      </div>

      <div className="whatif-flow">
        <div className="whatif-node current-node">
          <span>{current}</span>
        </div>
        <div className="whatif-branch">
          <div className="whatif-node lower-node">
            <span>{lower}</span>
          </div>
          <div className="whatif-node higher-node">
            <span>{higher}</span>
          </div>
        </div>
      </div>

      <p className="explanation-copy">
        AI visualization / synthetic reference. Not a prediction of the patient&apos;s actual future retina.
      </p>
    </section>
  );
}
