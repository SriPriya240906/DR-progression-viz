#!/usr/bin/env python3
"""Check similarity index structure."""

import numpy as np
import os

for grade in range(5):
    features_file = f"retrieval_engine/index/grade{grade}_features.npy"
    paths_file = f"retrieval_engine/index/grade{grade}_paths.npy"
    
    if os.path.exists(features_file) and os.path.exists(paths_file):
        features = np.load(features_file)
        paths = np.load(paths_file)
        
        print(f"Grade {grade}:")
        print(f"  Features shape: {features.shape}")
        print(f"  Paths count: {len(paths)}")
        if len(paths) > 0:
            print(f"  Sample path: {paths[0]}")
        print()
    else:
        print(f"Grade {grade}: Files missing")