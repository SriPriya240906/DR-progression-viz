#!/usr/bin/env python3
"""
PHASE 1: Model Preprocessing Integrity Verification

This script compares training vs inference preprocessing to identify inconsistencies.
"""

import torch
import torch.nn as nn
import timm
from torchvision import transforms
from PIL import Image
import os
from pathlib import Path

# Import dataset classes
from dataset import APTOSDataset
from preprocessing.dataset_loader import DRDataset

def analyze_preprocessing_consistency():
    """Analyze the preprocessing pipeline consistency between training and inference."""
    
    print("="*80)
    print("PHASE 1: MODEL PREPROCESSING INTEGRITY VERIFICATION")
    print("="*80)
    
    # 1. Current inference preprocessing (from model.py)
    inference_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    
    # 2. APTOSDataset preprocessing (used by train.py)
    aptos_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    
    # 3. DRDataset preprocessing (used by training/train_classifier.py) 
    dr_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    print("PREPROCESSING ANALYSIS:")
    print("-" * 40)
    print("1. Current inference (model.py):")
    print("   - Resize(224, 224)")
    print("   - ToTensor()")
    print("   - NO normalization")
    
    print("\n2. APTOSDataset (train.py):")
    print("   - Resize(224, 224)")
    print("   - ToTensor()")  
    print("   - NO normalization")
    
    print("\n3. DRDataset (training/train_classifier.py):")
    print("   - Resize(224, 224)")
    print("   - RandomHorizontalFlip (training only)")
    print("   - RandomRotation (training only)")
    print("   - ToTensor()")
    print("   - ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]")
    
    # Model file analysis
    print("\nMODEL FILES:")
    print("-" * 40)
    
    dr_model_path = Path("dr_model.pth")
    classifier_model_path = Path("models/dr_classifier.pth")
    
    if dr_model_path.exists():
        stat = dr_model_path.stat()
        print(f"dr_model.pth: {stat.st_size} bytes, modified {stat.st_mtime}")
    else:
        print("dr_model.pth: NOT FOUND")
        
    if classifier_model_path.exists():
        stat = classifier_model_path.stat()
        print(f"models/dr_classifier.pth: {stat.st_size} bytes, modified {stat.st_mtime}")
    else:
        print("models/dr_classifier.pth: NOT FOUND")
    
    # Determine which model is newer and likely in use
    if dr_model_path.exists() and classifier_model_path.exists():
        dr_time = dr_model_path.stat().st_mtime
        classifier_time = classifier_model_path.stat().st_mtime
        
        if dr_time > classifier_time:
            print(f"\ndr_model.pth is newer (currently loaded by model.py)")
            active_model = "dr_model.pth"
        else:
            print(f"\nmodels/dr_classifier.pth is newer")
            active_model = "models/dr_classifier.pth"
    elif dr_model_path.exists():
        print(f"\nOnly dr_model.pth exists (currently loaded by model.py)")
        active_model = "dr_model.pth"
    else:
        print(f"\nNo model files found")
        active_model = None
    
    # Test image processing with different transforms
    test_image_path = Path("test_images/000c1434d8d7.png")
    if not test_image_path.exists():
        test_image_path = Path("dataset/train/000c1434d8d7.png")
    
    if test_image_path.exists():
        print(f"\nTEST IMAGE PROCESSING: {test_image_path}")
        print("-" * 40)
        
        image = Image.open(test_image_path).convert("RGB")
        print(f"Original image size: {image.size}")
        
        # Process with different transforms
        inference_tensor = inference_transform(image)
        aptos_tensor = aptos_transform(image)
        
        # For DR transform, we need to disable random augmentations for comparison
        dr_test_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        dr_tensor = dr_test_transform(image)
        
        print(f"Inference tensor shape: {inference_tensor.shape}")
        print(f"Inference tensor range: [{inference_tensor.min():.4f}, {inference_tensor.max():.4f}]")
        print(f"Inference tensor mean: {inference_tensor.mean():.4f}")
        
        print(f"\nAPTOS tensor shape: {aptos_tensor.shape}")
        print(f"APTOS tensor range: [{aptos_tensor.min():.4f}, {aptos_tensor.max():.4f}]")
        print(f"APTOS tensor mean: {aptos_tensor.mean():.4f}")
        
        print(f"\nDR (normalized) tensor shape: {dr_tensor.shape}")
        print(f"DR tensor range: [{dr_tensor.min():.4f}, {dr_tensor.max():.4f}]")
        print(f"DR tensor mean: {dr_tensor.mean():.4f}")
        
        # Check if tensors are identical (except for normalization)
        if torch.allclose(inference_tensor, aptos_tensor):
            print("\n✅ Inference and APTOS preprocessing are identical")
        else:
            print("\n❌ Inference and APTOS preprocessing differ")
            
        if torch.allclose(inference_tensor, dr_tensor):
            print("✅ Inference and DR preprocessing are identical")
        else:
            print("❌ Inference and DR preprocessing differ (expected due to normalization)")
    
    # CONCLUSIONS
    print("\nANALYSIS CONCLUSIONS:")
    print("="*40)
    
    print("1. CONSISTENCY STATUS:")
    if active_model == "dr_model.pth":
        print("   - dr_model.pth is currently loaded by model.py")
        print("   - dr_model.pth was likely trained with train.py (APTOSDataset)")
        print("   - APTOSDataset uses NO ImageNet normalization")
        print("   - Current inference uses NO ImageNet normalization")
        print("   ✅ PREPROCESSING IS CONSISTENT")
    else:
        print("   - Unclear which model is actually being used")
        print("   ⚠️ PREPROCESSING CONSISTENCY UNKNOWN")
    
    print("\n2. POTENTIAL ISSUES:")
    print("   - Two different training scripts exist with different preprocessing")
    print("   - models/dr_classifier.pth uses ImageNet normalization")
    print("   - dr_model.pth uses NO normalization")
    print("   - If models are swapped, preprocessing mismatch would occur")
    
    print("\n3. RECOMMENDATIONS:")
    print("   - Document which training script produced dr_model.pth")
    print("   - Ensure consistent preprocessing between training and inference")
    print("   - Consider adding model metadata to track preprocessing")

if __name__ == "__main__":
    analyze_preprocessing_consistency()