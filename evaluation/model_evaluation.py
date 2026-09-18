#!/usr/bin/env python3
"""
PHASE 2: Model Evaluation Script

Creates reproducible evaluation of the DR classification model with proper metrics.
Does NOT modify the existing model or create fake validation data.
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
    confusion_matrix, classification_report, roc_auc_score
)
from torch.utils.data import DataLoader, Subset
import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from dataset import APTOSDataset

class ModelEvaluator:
    """Evaluate the DR classification model with proper scientific metrics."""
    
    def __init__(self, model_path="dr_model.pth", csv_path="dataset/train.csv", img_dir="dataset/train"):
        self.model_path = model_path
        self.csv_path = csv_path
        self.img_dir = img_dir
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # DR class names
        self.class_names = [
            "No DR",
            "Mild", 
            "Moderate",
            "Severe",
            "Proliferative DR"
        ]
        
        # Load model
        self.model = self._load_model()
        
        # Create reproducible splits
        self.train_indices, self.val_indices, self.test_indices = self._create_splits()
        
        print(f"Dataset splits created:")
        print(f"  Train: {len(self.train_indices)} samples")
        print(f"  Validation: {len(self.val_indices)} samples") 
        print(f"  Test: {len(self.test_indices)} samples")
    
    def _load_model(self):
        """Load the trained model."""
        model = timm.create_model("efficientnet_b0", pretrained=False)
        model.classifier = nn.Linear(model.classifier.in_features, 5)
        
        if os.path.exists(self.model_path):
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            print(f"✅ Model loaded from {self.model_path}")
        else:
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
        model.to(self.device)
        model.eval()
        return model
    
    def _create_splits(self, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15, random_seed=42):
        """Create reproducible train/validation/test splits."""
        
        # Load dataset to get total size
        df = pd.read_csv(self.csv_path)
        total_size = len(df)
        
        # Calculate split sizes
        train_size = int(total_size * train_ratio)
        val_size = int(total_size * val_ratio) 
        test_size = total_size - train_size - val_size
        
        # Create reproducible random indices
        np.random.seed(random_seed)
        indices = np.random.permutation(total_size)
        
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        return train_indices.tolist(), val_indices.tolist(), test_indices.tolist()
    
    def _get_predictions(self, indices):
        """Get model predictions for given indices."""
        
        # Create dataset subset
        dataset = APTOSDataset(csv_file=self.csv_path, img_dir=self.img_dir)
        subset = Subset(dataset, indices)
        dataloader = DataLoader(subset, batch_size=16, shuffle=False)
        
        all_predictions = []
        all_probabilities = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in dataloader:
                images = images.to(self.device)
                
                # Get model outputs
                outputs = self.model(images)
                probabilities = torch.softmax(outputs, dim=1)
                predictions = torch.argmax(probabilities, dim=1)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_probabilities.extend(probabilities.cpu().numpy())
                all_labels.extend(labels.numpy())
        
        return np.array(all_predictions), np.array(all_probabilities), np.array(all_labels)
    
    def evaluate_multiclass_metrics(self, y_true, y_pred, y_proba):
        """Calculate multiclass classification metrics."""
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'macro_precision': precision_score(y_true, y_pred, average='macro'),
            'macro_recall': recall_score(y_true, y_pred, average='macro'),
            'macro_f1': f1_score(y_true, y_pred, average='macro'),
            'weighted_precision': precision_score(y_true, y_pred, average='weighted'),
            'weighted_recall': recall_score(y_true, y_pred, average='weighted'),
            'weighted_f1': f1_score(y_true, y_pred, average='weighted')
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Per-class metrics
        per_class_report = classification_report(y_true, y_pred, target_names=self.class_names, output_dict=True)
        metrics['per_class'] = per_class_report
        
        # Multiclass AUROC if possible
        try:
            auroc = roc_auc_score(y_true, y_proba, multi_class='ovr', average='macro')
            metrics['macro_auroc'] = auroc
        except:
            metrics['macro_auroc'] = None
            
        return metrics
    
    def evaluate_referable_dr_metrics(self, y_true, y_pred, y_proba):
        """Calculate referable DR binary classification metrics."""
        
        # Define referable DR
        # non-referable = Grade 0 + Grade 1 (No DR, Mild)
        # referable = Grade 2 + Grade 3 + Grade 4 (Moderate, Severe, Proliferative)
        
        y_true_binary = (y_true >= 2).astype(int)  # 0,1 -> 0; 2,3,4 -> 1
        y_pred_binary = (y_pred >= 2).astype(int)
        
        # Probability of referable DR (sum of grades 2,3,4)
        y_proba_binary = y_proba[:, 2:].sum(axis=1)
        
        metrics = {
            'accuracy': accuracy_score(y_true_binary, y_pred_binary),
            'sensitivity': recall_score(y_true_binary, y_pred_binary, pos_label=1),
            'specificity': recall_score(y_true_binary, y_pred_binary, pos_label=0),
            'precision': precision_score(y_true_binary, y_pred_binary, pos_label=1),
            'f1': f1_score(y_true_binary, y_pred_binary, pos_label=1)
        }
        
        # Binary AUROC
        try:
            auroc = roc_auc_score(y_true_binary, y_proba_binary)
            metrics['auroc'] = auroc
        except:
            metrics['auroc'] = None
            
        # Confusion matrix for binary case
        cm_binary = confusion_matrix(y_true_binary, y_pred_binary)
        metrics['confusion_matrix'] = cm_binary.tolist()
        
        return metrics
    
    def plot_confusion_matrix(self, cm, title, class_names, save_path):
        """Plot and save confusion matrix."""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(title)
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    
    def run_full_evaluation(self):
        """Run complete model evaluation."""
        
        print("\n" + "="*80)
        print("PHASE 2: MODEL EVALUATION")
        print("="*80)
        
        results = {
            'evaluation_date': datetime.now().isoformat(),
            'model_path': self.model_path,
            'dataset_info': {
                'csv_path': self.csv_path,
                'img_dir': self.img_dir,
                'total_samples': len(self.train_indices) + len(self.val_indices) + len(self.test_indices)
            },
            'split_info': {
                'train_size': len(self.train_indices),
                'val_size': len(self.val_indices), 
                'test_size': len(self.test_indices),
                'random_seed': 42
            }
        }
        
        # Create results directory
        results_dir = Path("evaluation/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Evaluate on validation set
        print("\nEvaluating on VALIDATION set...")
        val_pred, val_proba, val_true = self._get_predictions(self.val_indices)
        
        val_multiclass = self.evaluate_multiclass_metrics(val_true, val_pred, val_proba)
        val_referable = self.evaluate_referable_dr_metrics(val_true, val_pred, val_proba)
        
        results['validation'] = {
            'multiclass': val_multiclass,
            'referable_dr': val_referable
        }
        
        # Evaluate on test set
        print("Evaluating on TEST set...")
        test_pred, test_proba, test_true = self._get_predictions(self.test_indices)
        
        test_multiclass = self.evaluate_multiclass_metrics(test_true, test_pred, test_proba)
        test_referable = self.evaluate_referable_dr_metrics(test_true, test_pred, test_proba)
        
        results['test'] = {
            'multiclass': test_multiclass,
            'referable_dr': test_referable
        }
        
        # Print summary results
        print("\n" + "="*50)
        print("VALIDATION SET RESULTS")
        print("="*50)
        print(f"Multiclass Accuracy: {val_multiclass['accuracy']:.4f}")
        print(f"Macro F1: {val_multiclass['macro_f1']:.4f}")
        print(f"Macro AUROC: {val_multiclass.get('macro_auroc', 'N/A')}")
        print(f"\nReferable DR Binary Classification:")
        print(f"  Sensitivity: {val_referable['sensitivity']:.4f}")
        print(f"  Specificity: {val_referable['specificity']:.4f}")
        print(f"  AUROC: {val_referable.get('auroc', 'N/A')}")
        
        print("\n" + "="*50)
        print("TEST SET RESULTS")
        print("="*50)
        print(f"Multiclass Accuracy: {test_multiclass['accuracy']:.4f}")
        print(f"Macro F1: {test_multiclass['macro_f1']:.4f}")
        print(f"Macro AUROC: {test_multiclass.get('macro_auroc', 'N/A')}")
        print(f"\nReferable DR Binary Classification:")
        print(f"  Sensitivity: {test_referable['sensitivity']:.4f}")
        print(f"  Specificity: {test_referable['specificity']:.4f}")
        print(f"  AUROC: {test_referable.get('auroc', 'N/A')}")
        
        # Plot confusion matrices
        self.plot_confusion_matrix(
            np.array(test_multiclass['confusion_matrix']),
            'Test Set - Multiclass Confusion Matrix',
            self.class_names,
            results_dir / 'test_multiclass_confusion_matrix.png'
        )
        
        self.plot_confusion_matrix(
            np.array(test_referable['confusion_matrix']),
            'Test Set - Referable DR Confusion Matrix',
            ['Non-referable', 'Referable'],
            results_dir / 'test_referable_confusion_matrix.png'
        )
        
        # Save full results
        results_file = results_dir / f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✅ Full results saved to: {results_file}")
        print(f"✅ Confusion matrices saved to: {results_dir}")
        
        return results

def main():
    """Main evaluation function."""
    
    # Verify model exists
    if not os.path.exists("dr_model.pth"):
        print("❌ dr_model.pth not found. Please ensure the model exists.")
        return
        
    # Verify dataset exists
    if not os.path.exists("dataset/train.csv") or not os.path.exists("dataset/train"):
        print("❌ Dataset not found. Please ensure dataset/train.csv and dataset/train/ exist.")
        return
    
    try:
        evaluator = ModelEvaluator()
        results = evaluator.run_full_evaluation()
        
        print("\n" + "="*80)
        print("EVALUATION COMPLETE")
        print("="*80)
        print("✅ Reproducible train/validation/test splits created")
        print("✅ Multiclass metrics calculated")
        print("✅ Referable DR binary metrics calculated")
        print("✅ Results saved with timestamp")
        print("\nIMPORTANT: This evaluation does NOT modify the existing model.")
        print("The purpose is measurement, not metric manipulation.")
        
    except Exception as e:
        print(f"❌ Evaluation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()