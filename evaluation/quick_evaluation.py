#!/usr/bin/env python3
"""
PHASE 2: Quick Model Evaluation Script

Creates a fast evaluation of the DR classification model with proper metrics on a sample.
Does NOT modify the existing model.
"""

import os
import sys
import torch
import torch.nn as nn
import timm
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from torch.utils.data import DataLoader, Subset
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from dataset import APTOSDataset

def quick_model_evaluation(sample_size=200):
    """Quick evaluation on a sample of the dataset."""
    
    print("="*80)
    print("PHASE 2: QUICK MODEL EVALUATION")
    print("="*80)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load model
    model = timm.create_model("efficientnet_b0", pretrained=False)
    model.classifier = nn.Linear(model.classifier.in_features, 5)
    
    if os.path.exists("dr_model.pth"):
        model.load_state_dict(torch.load("dr_model.pth", map_location=device))
        print(f"✅ Model loaded from dr_model.pth")
    else:
        raise FileNotFoundError("dr_model.pth not found")
        
    model.to(device)
    model.eval()
    
    # Load dataset
    dataset = APTOSDataset(csv_file="dataset/train.csv", img_dir="dataset/train")
    
    # Create reproducible sample
    np.random.seed(42)
    sample_indices = np.random.choice(len(dataset), size=sample_size, replace=False)
    subset = Subset(dataset, sample_indices)
    dataloader = DataLoader(subset, batch_size=16, shuffle=False)
    
    # Get predictions
    all_predictions = []
    all_probabilities = []
    all_labels = []
    
    print(f"Evaluating on {sample_size} samples...")
    
    with torch.no_grad():
        for images, labels in dataloader:
            images = images.to(device)
            
            outputs = model(images)
            probabilities = torch.softmax(outputs, dim=1)
            predictions = torch.argmax(probabilities, dim=1)
            
            all_predictions.extend(predictions.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    y_true = np.array(all_labels)
    y_pred = np.array(all_predictions)
    y_proba = np.array(all_probabilities)
    
    class_names = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
    
    # Multiclass metrics
    print("\n" + "="*50)
    print("MULTICLASS METRICS")
    print("="*50)
    
    accuracy = accuracy_score(y_true, y_pred)
    macro_precision = precision_score(y_true, y_pred, average='macro', zero_division=0)
    macro_recall = recall_score(y_true, y_pred, average='macro', zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro Precision: {macro_precision:.4f}")
    print(f"Macro Recall: {macro_recall:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print(f"\nConfusion Matrix:")
    print("Pred:  ", end="")
    for i, name in enumerate(class_names):
        print(f"{i:>4}", end="")
    print()
    for i, (true_name, row) in enumerate(zip(class_names, cm)):
        print(f"True {i}: ", end="")
        for val in row:
            print(f"{val:>4}", end="")
        print(f"  {true_name}")
    
    # Referable DR metrics
    print("\n" + "="*50)
    print("REFERABLE DR BINARY METRICS")
    print("="*50)
    
    # Define referable: 0,1 -> non-referable, 2,3,4 -> referable
    y_true_binary = (y_true >= 2).astype(int)
    y_pred_binary = (y_pred >= 2).astype(int)
    
    ref_accuracy = accuracy_score(y_true_binary, y_pred_binary)
    ref_sensitivity = recall_score(y_true_binary, y_pred_binary, pos_label=1, zero_division=0)
    ref_specificity = recall_score(y_true_binary, y_pred_binary, pos_label=0, zero_division=0)
    ref_precision = precision_score(y_true_binary, y_pred_binary, pos_label=1, zero_division=0)
    ref_f1 = f1_score(y_true_binary, y_pred_binary, pos_label=1, zero_division=0)
    
    print(f"Accuracy: {ref_accuracy:.4f}")
    print(f"Sensitivity (Recall): {ref_sensitivity:.4f}")
    print(f"Specificity: {ref_specificity:.4f}")
    print(f"Precision: {ref_precision:.4f}")
    print(f"F1: {ref_f1:.4f}")
    
    # Binary confusion matrix
    cm_binary = confusion_matrix(y_true_binary, y_pred_binary)
    print(f"\nBinary Confusion Matrix:")
    print("           Pred Non-ref  Pred Ref")
    print(f"True Non-ref     {cm_binary[0,0]:>4}      {cm_binary[0,1]:>4}")
    print(f"True Ref         {cm_binary[1,0]:>4}      {cm_binary[1,1]:>4}")
    
    # Label distribution
    print("\n" + "="*50)
    print("SAMPLE LABEL DISTRIBUTION")
    print("="*50)
    unique, counts = np.unique(y_true, return_counts=True)
    for label, count in zip(unique, counts):
        print(f"Grade {label} ({class_names[label]}): {count} samples ({count/len(y_true)*100:.1f}%)")
    
    # Save results
    results = {
        'evaluation_date': datetime.now().isoformat(),
        'sample_size': sample_size,
        'multiclass': {
            'accuracy': float(accuracy),
            'macro_precision': float(macro_precision),
            'macro_recall': float(macro_recall),
            'macro_f1': float(macro_f1),
            'confusion_matrix': cm.tolist()
        },
        'referable_dr': {
            'accuracy': float(ref_accuracy),
            'sensitivity': float(ref_sensitivity),
            'specificity': float(ref_specificity),
            'precision': float(ref_precision),
            'f1': float(ref_f1),
            'confusion_matrix': cm_binary.tolist()
        },
        'label_distribution': dict(zip([int(x) for x in unique], [int(x) for x in counts]))
    }
    
    # Save results
    results_dir = Path("evaluation/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = results_dir / f"quick_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {results_file}")
    
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print("✅ Model evaluation completed on sample data")
    print("✅ Multiclass and binary referable DR metrics calculated") 
    print("✅ Results are measurement only - model was NOT modified")
    print(f"✅ Baseline performance established on {sample_size} samples")
    
    return results

if __name__ == "__main__":
    if not os.path.exists("dr_model.pth"):
        print("❌ dr_model.pth not found")
        exit(1)
    if not os.path.exists("dataset/train.csv"):
        print("❌ dataset/train.csv not found")
        exit(1)
        
    quick_model_evaluation()