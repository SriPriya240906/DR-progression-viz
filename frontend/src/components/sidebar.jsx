import React from "react";

const navigationItems = [
  {
    id: "quality-assessment",
    label: "Image Quality Assessment",
    icon: "◉",
    stage: 1,
  },
  {
    id: "disease-prediction",
    label: "Disease Prediction", 
    icon: "⚕",
    stage: 2,
  },
  {
    id: "progression-simulation",
    label: "Progression Simulation",
    icon: "↗",
    stage: 3,
  },
  {
    id: "report-generation",
    label: "Report Generation",
    icon: "▤",
    stage: 4,
  },
];

function Sidebar({ activeSection, onNavigate, workflowState = "INITIAL" }) {
  // Workflow state can be:
  // INITIAL - no image uploaded
  // QUALITY_NOT_ANALYZED - image uploaded, quality not analyzed
  // QUALITY_ANALYZED - quality analyzed, ready for disease prediction  
  // DISEASE_ANALYZED - disease predicted, ready for progression
  // PROGRESSION_ANALYZED - progression analyzed, ready for report
  
  const getStageStatus = (stage) => {
    switch (workflowState) {
      case "INITIAL":
      case "QUALITY_NOT_ANALYZED":
        return stage === 1 ? "active" : "locked";
      case "QUALITY_ANALYZED":
        return stage === 1 ? "completed" : stage === 2 ? "active" : "locked";
      case "DISEASE_ANALYZED":
        return stage <= 2 ? "completed" : stage === 3 ? "active" : "locked";
      case "PROGRESSION_ANALYZED":
        return stage <= 3 ? "completed" : stage === 4 ? "active" : "locked";
      case "COMPLETED":
        return stage <= 4 ? "completed" : "locked";
      default:
        return stage === 1 ? "active" : "locked";
    }
  };

  const isStageAccessible = (stage) => {
    const status = getStageStatus(stage);
    return status === "active" || status === "completed";
  };

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">DR</div>

        <div>
          <div className="sidebar-title">DR-ProgressionViz</div>
          <div className="sidebar-subtitle">
            AI Retinal Intelligence
          </div>
        </div>
      </div>

      <div className="sidebar-divider" />

      <nav
        className="sidebar-navigation"
        aria-label="Workflow navigation"
      >
        <div className="sidebar-section-label">
          WORKFLOW STAGES
        </div>

        {navigationItems.map((item) => {
          const status = getStageStatus(item.stage);
          const isAccessible = isStageAccessible(item.stage);
          
          return (
            <button
              key={item.id}
              type="button"
              className={`sidebar-nav-item ${
                activeSection === item.id ? "active" : ""
              } ${status}`}
              onClick={() => isAccessible && onNavigate(item.id)}
              disabled={!isAccessible}
              title={!isAccessible ? `Complete previous stages to unlock ${item.label}` : item.label}
            >
              <span className="sidebar-nav-icon">
                {status === "completed" ? "✓" : status === "locked" ? "🔒" : item.icon}
              </span>

              <span className="sidebar-nav-text">{item.label}</span>
              
              {status === "active" && (
                <span className="sidebar-nav-status">Current</span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="backend-status">
          <span className="backend-status-dot" />
          <span>Backend Online</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;