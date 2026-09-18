#!/usr/bin/env python3
"""
PHASE 3: Fix Confidence/Uncertainty Terminology

This script identifies and fixes misleading confidence terminology throughout the system.
The main issues:
1. Raw softmax maximum is incorrectly called "confidence" 
2. No distinction between model probability and calibrated confidence
3. Frontend uses misleading "confidence" labels

Changes needed:
- Change "confidence" to "prediction_probability" in backend
- Update frontend to use "Prediction Probability" instead of "Confidence"
- Preserve existing API structure while clarifying meaning
- Add calibration infrastructure for future use
"""

import os
import re
from pathlib import Path

def analyze_confidence_usage():
    """Analyze current confidence usage throughout the codebase."""
    
    print("="*80)
    print("PHASE 3: CONFIDENCE/UNCERTAINTY TERMINOLOGY ANALYSIS")
    print("="*80)
    
    # Files to check
    files_to_check = [
        "model.py",
        "backend/reliability/uncertainty.py",
        "backend/evidence/clinical_evidence_summary.py", 
        "frontend/src/types.ts",
        "frontend/src/components/PredictionCard.jsx",
        "frontend/src/components/ReliabilityCard.jsx",
        "frontend/src/components/ClinicalEvidenceCard.jsx",
        "utils/pdf_report.py"
    ]
    
    confidence_usage = {}
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Count confidence references
            confidence_matches = re.findall(r'confidence', content, re.IGNORECASE)
            confidence_usage[file_path] = len(confidence_matches)
            
            print(f"\n{file_path}:")
            print(f"  - {len(confidence_matches)} references to 'confidence'")
            
            # Show context for some matches
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'confidence' in line.lower() and not line.strip().startswith('#'):
                    context = line.strip()
                    if len(context) > 80:
                        context = context[:77] + "..."
                    print(f"    Line {i+1}: {context}")
                    if i > 5:  # Limit output
                        remaining = sum(1 for l in lines[i+1:] if 'confidence' in l.lower())
                        if remaining > 0:
                            print(f"    ... and {remaining} more references")
                        break
    
    print(f"\n" + "="*50)
    print("TERMINOLOGY ISSUES IDENTIFIED")
    print("="*50)
    
    print("1. BACKEND ISSUES:")
    print("   - model.py: Raw softmax max called 'confidence'")  
    print("   - uncertainty.py: Uses 'confidence' for top probability")
    print("   - PDF report: Uses 'confidence' in output")
    
    print("\n2. FRONTEND ISSUES:")
    print("   - PredictionCard: Shows 'Confidence' dial")
    print("   - Types: prediction.confidence field")
    print("   - Multiple components use 'confidence' labels")
    
    print("\n3. CORRECT TERMINOLOGY:")
    print("   - Raw softmax max → 'prediction_probability' or 'model_probability'")
    print("   - Calibrated confidence → 'calibrated_confidence' (when available)")
    print("   - Frontend labels → 'Prediction Probability'")
    
    print(f"\n" + "="*50)
    print("RECOMMENDED CHANGES")
    print("="*50)
    
    print("1. PRESERVE API COMPATIBILITY:")
    print("   - Keep existing 'confidence' field in API responses")
    print("   - Add new 'prediction_probability' field with same value")
    print("   - Add disclaimer about terminology")
    
    print("\n2. UPDATE INTERNAL NAMING:")
    print("   - Use prediction_probability in new code")
    print("   - Update comments and documentation")
    
    print("\n3. UPDATE FRONTEND LABELS:")
    print("   - Change 'Confidence' → 'Prediction Probability'")
    print("   - Add explanatory text about calibration")
    
    print("\n4. ADD CALIBRATION INFRASTRUCTURE:")
    print("   - Temperature scaling implementation")
    print("   - Calibrated confidence when validation data available")
    
    return confidence_usage

def create_temperature_scaling_implementation():
    """Create temperature scaling implementation for future calibration."""
    
    calibration_code = '''#!/usr/bin/env python3
"""
Temperature Scaling Calibration Implementation

This module implements temperature scaling for probability calibration.
It is ready to use when proper validation data becomes available.

Temperature scaling: P_calibrated = softmax(logits / T)
where T is learned on validation data to minimize calibration error.
"""

import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import log_loss
from scipy.optimize import minimize_scalar


class TemperatureScaling:
    """Temperature scaling for model calibration."""
    
    def __init__(self):
        self.temperature = 1.0
        self.is_fitted = False
    
    def fit(self, logits, labels):
        """
        Fit temperature parameter on validation data.
        
        Args:
            logits: Raw model outputs (not softmax) for validation set
            labels: True labels for validation set
        """
        logits = np.array(logits)
        labels = np.array(labels)
        
        def temperature_loss(temperature):
            """Compute cross-entropy loss with temperature scaling."""
            if temperature <= 0:
                return float('inf')
            
            # Apply temperature scaling
            scaled_logits = logits / temperature
            
            # Compute softmax probabilities
            exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=1, keepdims=True))
            probabilities = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
            # Compute cross-entropy loss
            return log_loss(labels, probabilities)
        
        # Optimize temperature parameter
        result = minimize_scalar(temperature_loss, bounds=(0.01, 10.0), method='bounded')
        
        self.temperature = result.x
        self.is_fitted = True
        
        print(f"Temperature scaling fitted: T = {self.temperature:.4f}")
        return self
    
    def predict_proba(self, logits):
        """Apply temperature scaling to get calibrated probabilities."""
        if not self.is_fitted:
            raise ValueError("Temperature scaling must be fitted before prediction")
            
        logits = np.array(logits)
        
        # Apply temperature scaling
        scaled_logits = logits / self.temperature
        
        # Compute softmax probabilities
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits, axis=1, keepdims=True))
        probabilities = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        
        return probabilities
    
    def get_calibrated_confidence(self, logits):
        """Get calibrated confidence (max probability after temperature scaling)."""
        probabilities = self.predict_proba(logits.reshape(1, -1))
        return float(np.max(probabilities))


def compute_calibration_metrics(y_true, y_prob, n_bins=10):
    """
    Compute Expected Calibration Error (ECE) and other calibration metrics.
    
    Args:
        y_true: True labels
        y_prob: Predicted probabilities (N x C array)
        n_bins: Number of bins for ECE calculation
    
    Returns:
        dict with calibration metrics
    """
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    
    # Get predicted class and confidence
    y_pred = np.argmax(y_prob, axis=1)
    confidences = np.max(y_prob, axis=1)
    
    # Compute accuracy
    accuracies = (y_pred == y_true).astype(float)
    
    # Expected Calibration Error (ECE)
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_lowers = bin_boundaries[:-1]
    bin_uppers = bin_boundaries[1:]
    
    ece = 0.0
    for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = in_bin.mean()
        
        if prop_in_bin > 0:
            accuracy_in_bin = accuracies[in_bin].mean()
            avg_confidence_in_bin = confidences[in_bin].mean()
            ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
    
    # Brier Score (for multiclass)
    n_classes = y_prob.shape[1]
    y_true_onehot = np.eye(n_classes)[y_true]
    brier_score = np.mean(np.sum((y_prob - y_true_onehot) ** 2, axis=1))
    
    return {
        'ece': ece,
        'brier_score': brier_score,
        'accuracy': accuracies.mean(),
        'avg_confidence': confidences.mean()
    }


# Example usage (when validation data becomes available):
"""
# 1. Collect validation logits and labels
val_logits = []  # Raw model outputs (before softmax)
val_labels = []  # True labels

# 2. Fit temperature scaling
ts = TemperatureScaling()
ts.fit(val_logits, val_labels)

# 3. Get calibrated predictions
calibrated_probs = ts.predict_proba(test_logits)
calibrated_confidence = ts.get_calibrated_confidence(single_logit)

# 4. Evaluate calibration
metrics = compute_calibration_metrics(test_labels, calibrated_probs)
print(f"ECE before calibration: {metrics_before['ece']:.4f}")
print(f"ECE after calibration: {metrics_after['ece']:.4f}")
"""
'''
    
    # Create calibration directory and file
    calib_dir = Path("calibration")
    calib_dir.mkdir(exist_ok=True)
    
    calib_file = calib_dir / "temperature_scaling.py"
    with open(calib_file, 'w') as f:
        f.write(calibration_code)
    
    print(f"✅ Temperature scaling implementation created: {calib_file}")
    return calib_file

def main():
    """Main function to analyze and document confidence terminology issues."""
    
    # Analyze current usage
    usage = analyze_confidence_usage()
    
    # Create calibration infrastructure
    calib_file = create_temperature_scaling_implementation()
    
    print(f"\n" + "="*80)
    print("PHASE 3 SUMMARY")
    print("="*80)
    
    print("✅ ANALYZED: Confidence terminology usage throughout system")
    print("✅ IDENTIFIED: Raw softmax maximum incorrectly labeled as 'confidence'")
    print("✅ CREATED: Temperature scaling infrastructure for future calibration")
    
    print(f"\n📋 TERMINOLOGY CORRECTIONS NEEDED:")
    print(f"   - Backend: Keep 'confidence' for API compatibility, add disclaimers")
    print(f"   - Frontend: Change labels to 'Prediction Probability'")
    print(f"   - Documentation: Clarify that values are uncalibrated model probabilities")
    
    print(f"\n🔄 CALIBRATION STATUS:")
    print(f"   - Infrastructure: READY (temperature_scaling.py created)")  
    print(f"   - Implementation: PENDING (awaiting proper validation split)")
    print(f"   - Current values: UNCALIBRATED model probabilities")
    
    print(f"\n⚠️  IMPORTANT:")
    print(f"   - Do NOT claim calibrated confidence without proper validation")
    print(f"   - Do NOT change API field names (breaks compatibility)")
    print(f"   - DO update user-facing terminology and explanations")

if __name__ == "__main__":
    main()