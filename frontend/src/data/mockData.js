const createRetinaSvg = ({ tint = '#8ecae6', accent = '#d7f5ff', seed = 1, dark = '#091a22' } = {}) => {
  const vesselPaths = [
    'M 350 120 C 420 160, 450 210, 430 260 S 390 330, 350 350',
    'M 350 120 C 300 150, 280 200, 290 260 S 310 330, 350 350',
    'M 350 110 C 305 175, 260 220, 220 260 S 240 330, 290 370',
    'M 350 110 C 400 175, 455 220, 500 260 S 470 330, 420 370',
    'M 350 180 C 315 220, 300 250, 310 295',
    'M 350 180 C 385 220, 395 250, 390 295',
    'M 200 250 C 260 300, 300 310, 350 315',
    'M 500 250 C 440 300, 395 312, 350 315',
  ];

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
      <defs>
        <radialGradient id="bg${seed}" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="${accent}" />
          <stop offset="38%" stop-color="${tint}" />
          <stop offset="100%" stop-color="${dark}" />
        </radialGradient>
      </defs>
      <rect width="800" height="600" fill="${dark}"/>
      <circle cx="400" cy="300" r="210" fill="url(#bg${seed})" opacity="1"/>
      <circle cx="400" cy="300" r="170" fill="rgba(255,255,255,0.06)"/>
      <g opacity="0.85">
        ${vesselPaths
          .map(
            (path, index) => `
              <path d="${path}" stroke="rgba(14, 35, 45, ${0.8 + index * 0.02})" stroke-width="${8 + (index % 3)}" fill="none" stroke-linecap="round"/>
            `,
          )
          .join('')}
      </g>
      <g opacity="0.6">
        <circle cx="305" cy="260" r="18" fill="rgba(255,255,255,0.12)" />
        <circle cx="495" cy="260" r="18" fill="rgba(255,255,255,0.12)" />
        <circle cx="400" cy="185" r="15" fill="rgba(255,255,255,0.1)" />
        <circle cx="400" cy="425" r="15" fill="rgba(255,255,255,0.1)" />
      </g>
      <g opacity="0.8">
        <circle cx="400" cy="300" r="12" fill="rgba(25,55,70,0.95)" />
      </g>
    </svg>
  `;

  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
};

const gradeLabels = {
  0: 'No Diabetic Retinopathy',
  1: 'Mild',
  2: 'Moderate',
  3: 'Severe',
  4: 'Proliferative DR',
};

const gradePalette = {
  0: '#66d4a9',
  1: '#9ddb7e',
  2: '#f3c86b',
  3: '#f39a6d',
  4: '#d65f52',
};

const progressionCase = (grade, index, similarity) => ({
  image_url: createRetinaSvg({
    tint: `hsl(${200 + grade * 16}, 55%, 62%)`,
    accent: `hsl(${210 + grade * 8}, 80%, 80%)`,
    seed: grade + index + 3,
  }),
  similarity,
  grade,
});

export const mockCaseData = {
  similar_cases: [
    { image_url: createRetinaSvg({ seed: 101, tint: '#8fd6dd', accent: '#dff6ff' }), similarity: 0.9512, grade: 2 },
    { image_url: createRetinaSvg({ seed: 102, tint: '#9ec4ff', accent: '#dfefff' }), similarity: 0.9365, grade: 2 },
    { image_url: createRetinaSvg({ seed: 103, tint: '#b4d7a8', accent: '#ebfee5' }), similarity: 0.9248, grade: 1 },
    { image_url: createRetinaSvg({ seed: 104, tint: '#f1c87d', accent: '#fff5e3' }), similarity: 0.9094, grade: 3 },
  ],
  progression_map: {
    stage_0: [
      progressionCase(0, 0, 0.9871),
      progressionCase(0, 1, 0.9748),
      progressionCase(0, 2, 0.9687),
    ],
    stage_1: [
      progressionCase(1, 0, 0.9521),
      progressionCase(1, 1, 0.9474),
      progressionCase(1, 2, 0.9439),
    ],
    stage_2: [
      progressionCase(2, 0, 0.9682),
      progressionCase(2, 1, 0.9613),
      progressionCase(2, 2, 0.9574),
      progressionCase(2, 3, 0.9541),
    ],
    stage_3: [
      progressionCase(3, 0, 0.9194),
      progressionCase(3, 1, 0.9126),
      progressionCase(3, 2, 0.9078),
    ],
    stage_4: [
      progressionCase(4, 0, 0.8950),
      progressionCase(4, 1, 0.8884),
      progressionCase(4, 2, 0.8822),
    ],
  },
  disease_landscape: {
    points: [
      { id: 'g0-1', x: 12, y: 18, grade: 0, is_current: false },
      { id: 'g0-2', x: 30, y: 32, grade: 0, is_current: false },
      { id: 'g0-3', x: 24, y: 48, grade: 0, is_current: false },
      { id: 'g1-1', x: 41, y: 28, grade: 1, is_current: false },
      { id: 'g1-2', x: 52, y: 46, grade: 1, is_current: false },
      { id: 'g2-1', x: 60, y: 34, grade: 2, is_current: true },
      { id: 'g2-2', x: 68, y: 52, grade: 2, is_current: false },
      { id: 'g2-3', x: 74, y: 41, grade: 2, is_current: false },
      { id: 'g3-1', x: 78, y: 64, grade: 3, is_current: false },
      { id: 'g3-2', x: 68, y: 76, grade: 3, is_current: false },
      { id: 'g4-1', x: 84, y: 88, grade: 4, is_current: false },
      { id: 'g4-2', x: 90, y: 74, grade: 4, is_current: false },
    ],
  },
  progression_simulation: {
    stages: [
      { stage: 0, image_url: createRetinaSvg({ seed: 201, tint: '#95d7d7', accent: '#e0fbff' }), label: 'Current', synthetic: false },
      { stage: 1, image_url: createRetinaSvg({ seed: 202, tint: '#accff0', accent: '#eff8ff' }), label: 'Reference Stage 1', synthetic: true },
      { stage: 2, image_url: createRetinaSvg({ seed: 203, tint: '#d5d8a2', accent: '#f8f7d7' }), label: 'Reference Stage 2', synthetic: true },
      { stage: 3, image_url: createRetinaSvg({ seed: 204, tint: '#dca77c', accent: '#ffe4ce' }), label: 'Reference Stage 3', synthetic: true },
      { stage: 4, image_url: createRetinaSvg({ seed: 205, tint: '#d06d67', accent: '#ffd8d1' }), label: 'Reference Stage 4', synthetic: true },
    ],
  },
};

export const buildMockAnalysis = (fileName = 'retinal_scan.png') => {
  const uploadedImage = createRetinaSvg({ seed: 999, tint: '#8bc6d8', accent: '#e3f8ff' });

  const currentGrade = 2;
  const analysis = {
    analysis_id: `demo-${Math.random().toString(36).slice(2, 8)}`,
    uploaded_image_url: uploadedImage,
    prediction: {
      grade: currentGrade,
      label: `${gradeLabels[currentGrade]}`,
      confidence: 91.4,
      risk_level: 'High',
    },
    image_quality: {
      overall: 'GOOD',
      focus: 82,
      illumination: 91,
      contrast: 74,
      field_of_view: 96,
      message: 'Suitable for AI analysis',
    },
    gradcam: {
      image_url: createRetinaSvg({
        seed: 777,
        tint: '#7ec2d1',
        accent: '#fbd661',
        dark: '#112835',
      }),
    },
    similar_cases: mockCaseData.similar_cases,
    digital_twin: {
      state: 'Current-state representation',
      feature_vector: [0.82, 0.67, 0.74, 0.91, 0.59, 0.71],
    },
    disease_landscape: mockCaseData.disease_landscape,
    progression_map: mockCaseData.progression_map,
    progression_simulation: mockCaseData.progression_simulation,
    triage: {
      status: 'YELLOW',
      reason: 'Model uncertainty elevated',
      recommendation: 'Human review recommended',
    },
    file_name: fileName,
  };

  return analysis;
};

export const getGradeColor = (grade) => gradePalette[grade] || '#b4c9d6';

export const gradeMeta = [
  { grade: 0, title: 'No Diabetic Retinopathy', description: 'No visible diabetic retinopathy' },
  { grade: 1, title: 'Mild', description: 'Mild retinal changes' },
  { grade: 2, title: 'Moderate', description: 'Moderate disease burden' },
  { grade: 3, title: 'Severe', description: 'Severe retinal disease' },
  { grade: 4, title: 'Proliferative DR', description: 'Advanced proliferative disease' },
];

export const defaultReportSummary = {
  patient_id: 'CASE-2026-041',
  diagnosis: 'Moderate DR',
  confidence: 91.4,
  quality: 'GOOD',
  triage: 'YELLOW',
  digital_twin: 'Current-state representation',
  explainability: 'AI explainability available',
  progression: 'Reference progression map displayed',
};
