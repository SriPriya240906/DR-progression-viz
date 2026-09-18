#!/usr/bin/env python3
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
