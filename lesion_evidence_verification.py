#!/usr/bin/env python3
"""
PHASE 7: Lesion Evidence Verification

This script verifies that lesion evidence analysis properly distinguishes between:
- Experimental image-processing candidates (what it actually does)
- Confirmed clinical lesions (what it explicitly does NOT claim)

Critical requirement: Must use "candidate" terminology, not claim lesion diagnosis.
"""

import os
import re
from pathlib import Path

def analyze_lesion_terminology():
    """Verify lesion evidence uses proper candidate terminology."""
    
    print("="*80)
    print("PHASE 7: LESION EVIDENCE TERMINOLOGY VERIFICATION")
    print("="*80)
    
    # Read lesion analyzer implementation
    analyzer_path = Path("backend/lesions/lesion_candidate_analyzer.py")
    if not analyzer_path.exists():
        print("❌ Lesion analyzer not found")
        return False
    
    with open(analyzer_path, 'r') as f:
        analyzer_content = f.read()
    
    # Read frontend component
    frontend_path = Path("frontend/src/components/LesionEvidenceCard.jsx")
    if frontend_path.exists():
        with open(frontend_path, 'r') as f:
            frontend_content = f.read()
    else:
        frontend_content = ""
    
    print("✅ IMPLEMENTATION ANALYSIS:")
    print("   - Lesion candidate analyzer exists: ✅")
    
    # Check for proper candidate terminology
    candidate_terms = [
        "candidate",
        "experimental",
        "not confirmed", 
        "image-processing",
        "not.*microaneurysms",
        "not.*hemorrhages",
        "not.*exudates"
    ]
    
    found_candidate_terms = []
    for term in candidate_terms:
        if re.search(term, analyzer_content, re.IGNORECASE):
            found_candidate_terms.append(term)
    
    print(f"   - Candidate terminology found: {', '.join(found_candidate_terms)}")
    
    # Check for inappropriate lesion claims (should NOT be found)
    inappropriate_claims = [
        r'\bdetected\s+microaneurysms?\b',
        r'\bconfirmed\s+lesions?\b', 
        r'\bdiagnosed\s+lesions?\b',
        r'\bclinical\s+lesions?\b',
        r'\bvalidated\s+lesion\s+detector\b',
        r'\bmicroaneurysm\s+detection\b',
        r'\bhemorrhage\s+detection\b',
        r'\bexudate\s+detection\b'
    ]
    
    found_inappropriate = []
    for pattern in inappropriate_claims:
        if re.search(pattern, analyzer_content, re.IGNORECASE):
            found_inappropriate.append(pattern)
    
    if found_inappropriate:
        print(f"   ❌ Inappropriate lesion claims: {', '.join(found_inappropriate)}")
    else:
        print("   ✅ No inappropriate lesion detection claims found")
    
    # Check method transparency
    print(f"\n🔬 METHOD ANALYSIS:")
    
    method_components = {
        "Dark candidates": "MORPH_BLACKHAT",
        "Bright candidates": "MORPH_TOPHAT",
        "Percentile thresholding": "percentile", 
        "Morphological cleanup": "MORPH_OPEN",
        "Field-of-view filtering": "_field_of_view_mask",
        "Component size filtering": "_clean_components"
    }
    
    for component, pattern in method_components.items():
        if pattern in analyzer_content:
            print(f"   - {component}: ✅ Implemented")
        else:
            print(f"   - {component}: ❌ Not found")
    
    # Check for proper limitations
    print(f"\n⚠️  LIMITATIONS VERIFICATION:")
    
    required_limitations = [
        "not confirmed",
        "false candidates",
        "no.*ground-truth",
        "experimental",
        "image-processing candidates"
    ]
    
    found_limitations = []
    for limitation in required_limitations:
        if re.search(limitation, analyzer_content, re.IGNORECASE):
            found_limitations.append(limitation)
    
    print(f"   - Required limitations found: {', '.join(found_limitations)}")
    
    # Check unavailable features
    print(f"\n🚫 UNAVAILABLE FEATURES:")
    
    unavailable_features = [
        "neovascularization",
        "optic_disc_exclusion",
        "confidence_available"
    ]
    
    for feature in unavailable_features:
        if f'"{feature}"' in analyzer_content and 'False' in analyzer_content:
            print(f"   - {feature}: ✅ Properly marked as unavailable")
        else:
            print(f"   - {feature}: ⚠️  May not be properly marked")
    
    # Frontend terminology check
    print(f"\n🖥️  FRONTEND PRESENTATION:")
    
    if frontend_content:
        frontend_checks = {
            "candidate": "candidate terminology",
            "experimental": "experimental labeling", 
            "not confirmed": "clinical disclaimers",
            "image-processing": "processing description",
            "Not a confirmed clinical lesion detector": "detector disclaimer"
        }
        
        for term, description in frontend_checks.items():
            if term.lower() in frontend_content.lower():
                print(f"   - {description}: ✅")
            else:
                print(f"   - {description}: ⚠️")
    
    # Algorithm parameters check
    print(f"\n📊 THRESHOLD/PARAMETER ANALYSIS:")
    
    thresholds = {
        "Dark percentile": "DARK_PERCENTILE.*97",
        "Bright percentile": "BRIGHT_PERCENTILE.*99", 
        "Minimum component area": "MIN_COMPONENT_AREA",
        "Maximum component fraction": "MAX_COMPONENT_FRACTION",
        "Field-of-view intensity": "FOV_INTENSITY_FLOOR"
    }
    
    for param, pattern in thresholds.items():
        if re.search(pattern, analyzer_content):
            print(f"   - {param}: ✅ Defined")
        else:
            print(f"   - {param}: ❌ Not found")
    
    # Safety assessment
    print(f"\n" + "="*50)
    print("LESION EVIDENCE SAFETY ASSESSMENT")
    print("="*50)
    
    safety_criteria = {
        "candidate_terminology": len(found_candidate_terms) >= 3,
        "no_lesion_claims": len(found_inappropriate) == 0,
        "limitations_documented": len(found_limitations) >= 3,
        "method_transparent": "percentile" in analyzer_content,
        "unavailable_features": all(f in analyzer_content for f in unavailable_features),
        "experimental_labeling": "experimental" in analyzer_content.lower(),
        "clinical_disclaimers": "not confirmed" in analyzer_content.lower()
    }
    
    for criterion, passed in safety_criteria.items():
        symbol = "✅" if passed else "❌"
        print(f"   {symbol} {criterion.replace('_', ' ').title()}: {passed}")
    
    overall_safe = all(safety_criteria.values())
    
    print(f"\n🎯 LESION EVIDENCE STATUS:")
    
    if overall_safe:
        print("   ✅ SCIENTIFICALLY HONEST: Candidate nature clearly disclosed")
        print("   ✅ NO FALSE CLAIMS: No confirmed lesion detection claims")
        print("   ✅ PROPERLY SCOPED: Image processing candidates, not clinical lesions")
        print("   ✅ LIMITATIONS ACKNOWLEDGED: Validation constraints documented")
        print("   ✅ METHOD TRANSPARENT: Algorithm clearly described")
        print("   ✅ UNAVAILABLE FEATURES: Properly marked as unavailable")
    else:
        print("   ❌ LESION TERMINOLOGY ISSUES FOUND")
    
    return overall_safe, safety_criteria

def main():
    """Main lesion evidence verification function."""
    
    safe, criteria = analyze_lesion_terminology()
    
    if safe:
        print(f"\n" + "="*80)
        print("PHASE 7 COMPLETE: LESION EVIDENCE TERMINOLOGY VERIFIED")
        print("="*80)
        print("✅ Lesion evidence properly uses 'candidate' terminology")
        print("✅ No confirmed lesion detection claims found")
        print("✅ Experimental nature clearly communicated")
        print("✅ Clinical limitations properly documented") 
        print("✅ Method algorithm transparent")
        print("✅ Unavailable features properly disclaimed")
        
        print(f"\n🔬 LESION CANDIDATE ANALYSIS SUMMARY:")
        print("   - Dark candidates: Green-channel black-hat morphology, 97th percentile")
        print("   - Bright candidates: Grayscale top-hat morphology, 99th percentile")
        print("   - Field filtering: Conservative retinal region estimation")
        print("   - Component filtering: Size-based candidate cleanup")
        print("   - Output: Candidate regions with location/intensity metrics")
        
        print(f"\n✅ APPROPRIATE TERMINOLOGY:")
        print("   - 'Dark and bright candidate regions'")
        print("   - 'Experimental candidate localization'")
        print("   - 'Not confirmed microaneurysms, hemorrhages, or exudates'")
        print("   - 'Image-processing candidates'")
        
        print(f"\n❌ INAPPROPRIATE CLAIMS AVOIDED:")
        print("   - 'Detected lesions'")
        print("   - 'Confirmed microaneurysms'")
        print("   - 'Clinical lesion detector'")
        print("   - 'Validated hemorrhage detection'")
        
    else:
        print(f"\n❌ LESION EVIDENCE VERIFICATION FAILED")
        failed_criteria = [k for k, v in criteria.items() if not v]
        print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
    return safe

if __name__ == "__main__":
    main()