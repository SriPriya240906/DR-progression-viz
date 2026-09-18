# Image Quality Assessment Methodology

## Overview

The DR-ProgressionViz system includes an image quality assessment component that analyzes uploaded retinal images using computer vision metrics. **This assessment is experimental and not clinically validated.**

## Important Disclaimers

⚠️ **CRITICAL: This is NOT a clinical gradability assessment**
- These metrics are heuristic image-processing calculations
- Thresholds are experimental and derived from a small sample
- Clinical image quality requires expert human evaluation
- Results should not be used for clinical decision-making

## Methodology

### Data Source for Thresholds

**Source**: 200 images randomly sampled from `dataset/train` during Phase 2 development
**Sample Statistics**: 
- Minimum sample: 200 images from 3,662 total training images
- Sampling method: Random selection for threshold exploration
- **NOT a clinical quality validation dataset**
- **NOT labeled for image quality by clinical experts**

### Metrics Calculated

#### 1. Resolution Analysis
- **Metric**: Image width and height in pixels
- **Threshold**: 224×224 pixels (minimum)
- **Rationale**: Matches model input size requirement
- **Status**: Engineering constraint, not clinical adequacy

#### 2. Focus Assessment  
- **Metric**: Variance of Laplacian (grayscale)
- **Formula**: `cv2.Laplacian(gray, cv2.CV_64F).var()`
- **Thresholds**:
  - Poor: < 5.0
  - Borderline: 5.0 to < 10.0  
  - Good: ≥ 10.0
- **Source**: Empirically derived from 200-image sample
- **Limitations**: 
  - Affected by image texture, noise, compression
  - Not validated against clinical focus assessment
  - Different cameras/acquisition may have different ranges

#### 3. Illumination Assessment
- **Metrics**: 
  - Grayscale mean brightness
  - Dark pixel fraction (≤ 8 intensity)
  - Bright pixel fraction (≥ 247 intensity)
- **Thresholds**:
  - Poor: Mean < 20 or > 220, dark fraction ≥ 65%, bright fraction ≥ 35%
  - Borderline: Mean < 35 or > 195, dark fraction ≥ 60%, bright fraction ≥ 20%
  - Good: Otherwise
- **Source**: Empirically derived from 200-image sample
- **Limitations**:
  - Dark fundus background affects interpretation
  - Camera exposure settings vary between systems
  - No clinical correlation with diagnostic adequacy

#### 4. Contrast Assessment
- **Metric**: Grayscale standard deviation
- **Formula**: `gray.std()`
- **Thresholds**:
  - Poor: < 17.0
  - Borderline: 17.0 to < 25.0
  - Good: ≥ 25.0
- **Source**: Empirically derived from 200-image sample
- **Limitations**:
  - Affected by illumination and field-of-view
  - Not correlated with clinical contrast adequacy

#### 5. Field-of-View Estimation
- **Method**: Morphological operations to estimate retinal region
- **Process**:
  1. Threshold grayscale > 12
  2. Morphological opening (5×5 kernel)
  3. Morphological closing (15×15 kernel)  
  4. Find largest connected component
- **Outputs**:
  - Estimated region fraction
  - Visibility fraction within estimated region
- **Status**: **Heuristic only** - not validated retinal segmentation

## Threshold Derivation Process

### Sample Analysis (Phase 2)
From the 200-image sample of `dataset/train`:

**Variance of Laplacian (Focus)**:
- Minimum: 3.3992
- 10th percentile: 5.4098  
- Median: 14.2547
- 90th percentile: 46.955

**Grayscale Mean (Brightness)**:
- Minimum: 19.2496
- 10th percentile: 42.0717
- Median: 62.8898  
- 90th percentile: 87.2127

**Grayscale Standard Deviation (Contrast)**:
- Minimum: 16.8147
- 10th percentile: 24.9024
- Median: 37.8334
- 90th percentile: 51.154

### Threshold Selection Logic
- **Conservative approach**: Set thresholds to be permissive rather than restrictive
- **Engineering-focused**: Based on typical digital image ranges
- **Sample-informed**: Used percentiles from training data for reference
- **NOT validated**: No correlation with clinical expert ratings

## API Response Structure

```json
{
  "status": "GOOD|BORDERLINE|POOR",
  "overall_assessment": "Description of overall quality",
  "resolution": {
    "width": 3216,
    "height": 2136,
    "aspect_ratio": 1.5056,
    "assessment": "Resolution meets the experimental minimum band."
  },
  "focus": {
    "metric": "variance_of_laplacian", 
    "value": 6.2588,
    "assessment": "Focus metric is borderline."
  },
  "illumination": {
    "metric": "grayscale_mean",
    "value": 51.3887,
    "dark_pixel_fraction": 0.3821,
    "bright_pixel_fraction": 0.0003,
    "assessment": "Illumination is within the experimental reference band."
  },
  "contrast": {
    "metric": "grayscale_standard_deviation",
    "value": 31.3033,
    "assessment": "Contrast is within the experimental reference band."
  },
  "field_of_view": {
    "estimated_region_fraction": 0.746177,
    "assessment": "A visually non-empty image region was detected; field-of-view assessment is heuristic."
  },
  "retinal_visibility": {
    "estimated_visible_fraction": 0.892456,
    "assessment": "A meaningful non-empty image region is suggested by this heuristic."
  },
  "warnings": [
    "Focus may affect AI-assisted analysis."
  ],
  "recommendation": "Image quality may affect AI-assisted analysis; review the image and consider reacquisition if needed.",
  "methodology": {
    "threshold_type": "heuristic / experimental",
    "validated_clinically": false,
    "dataset_used": "200 images sampled from dataset/train during Phase 2 inspection."
  }
}
```

## Interpretation Guidelines

### ✅ Appropriate Uses
- **Technical screening**: Filter obviously corrupted/unusable images
- **Development workflow**: Identify potential image processing issues
- **Research prototype**: Demonstrate image analysis capabilities
- **Quality flags**: Alert users to potential technical issues

### ❌ Inappropriate Uses
- **Clinical gradability**: Do not use for clinical image quality decisions
- **Diagnostic adequacy**: Cannot determine if image is suitable for diagnosis
- **Patient care**: Results should not influence clinical decisions
- **Validation claims**: Do not claim clinical validation

### 🔬 Scientific Limitations

1. **Small validation sample**: Only 200 images used for threshold setting
2. **Single dataset source**: All samples from same training dataset
3. **No clinical labels**: No expert quality ratings for validation
4. **Acquisition domain**: May not generalize to different cameras/settings
5. **Heuristic thresholds**: Not optimized for clinical outcomes
6. **Image-only analysis**: Cannot assess true retinal visibility

## Recommendations for Clinical Use

To make this component clinically suitable:

1. **Clinical validation dataset**: Collect images with expert quality ratings
2. **Multi-center validation**: Include diverse acquisition systems
3. **Correlation analysis**: Compare metrics with clinical image adequacy
4. **Threshold optimization**: Optimize thresholds for clinical outcomes
5. **Expert comparison**: Validate against ophthalmologist assessments
6. **Real-world testing**: Test on clinical workflow images

## Code Implementation

The quality analysis is implemented in:
- `backend/quality/quality_analyzer.py` - Core analysis logic
- `backend/main.py` - API integration  
- `frontend/src/components/ImageQualityCard.jsx` - UI display

Key functions:
- `analyze_image_quality(image)` - Main analysis function
- `_status_for_focus()` - Focus threshold logic
- `_status_for_illumination()` - Brightness threshold logic  
- `_status_for_contrast()` - Contrast threshold logic
- `_field_of_view_metrics()` - Field estimation heuristic

## Version History

- **Phase 2**: Initial implementation with experimental thresholds
- **Phase 4**: Added comprehensive methodology documentation
- **Current**: Clearly labeled as experimental, not clinically validated

---

**Summary**: The image quality assessment provides useful technical metrics for research and development, but should not be considered a substitute for clinical image quality evaluation. All thresholds are experimental and require clinical validation for patient care applications.