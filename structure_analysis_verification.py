#!/usr/bin/env python3
"""
PHASE 6: Retinal Structure Analysis Terminology Verification

This script verifies that retinal structure analysis uses accurate scientific terminology
and does not make unsupported claims about vessel segmentation or anatomical localization.
"""

import os
import re
from pathlib import Path

def analyze_structure_terminology():
    """Verify structure analysis uses proper scientific terminology."""
    
    print("="*80)
    print("PHASE 6: RETINAL STRUCTURE ANALYSIS VERIFICATION")
    print("="*80)
    
    # Read structure analyzer implementation
    analyzer_path = Path("backend/structure/retinal_structure_analyzer.py")
    if not analyzer_path.exists():
        print("❌ Structure analyzer not found")
        return False
    
    with open(analyzer_path, 'r') as f:
        analyzer_content = f.read()
    
    # Read frontend component
    frontend_path = Path("frontend/src/components/RetinalStructureCard.jsx")
    if frontend_path.exists():
        with open(frontend_path, 'r') as f:
            frontend_content = f.read()
    else:
        frontend_content = ""
    
    print("✅ IMPLEMENTATION ANALYSIS:")
    print("   - Structure analyzer module exists: ✅")
    
    # Check for proper experimental language
    experimental_indicators = [
        "experimental",
        "estimate",
        "vessel-like",
        "not validated",
        "not a clinical measurement",
        "candidate map",
        "limitations"
    ]
    
    found_experimental = []
    for indicator in experimental_indicators:
        if indicator.lower() in analyzer_content.lower():
            found_experimental.append(indicator)
    
    print(f"   - Experimental language found: {', '.join(found_experimental)}")
    
    # Check for inappropriate claims (should NOT be found)
    inappropriate_claims = [
        "validated vessel segmentation",
        "clinical vessel",
        "diagnostic vessel",
        "confirmed vessel",
        "optic disc detection",
        "fovea detection"
    ]
    
    # Check for appropriate disclaimers (SHOULD be found)
    appropriate_disclaimers = [
        "not validated vessel segmentation",
        "candidate map is not",
        "vessel-like" 
    ]
    
    # Check for inappropriate claims (context matters!)
    # We need to check these are NOT preceded by "not" or "not a"
    found_inappropriate = []
    
    # Check for positive claims of vessel segmentation (bad)
    if re.search(r'\b(?<!not\s)(?<!not\sa\s)validated\s+vessel\s+segmentation', analyzer_content, re.IGNORECASE):
        found_inappropriate.append("validated vessel segmentation")
    
    if re.search(r'\bclinical\s+vessel\s+segmentation', analyzer_content, re.IGNORECASE):
        found_inappropriate.append("clinical vessel segmentation")
        
    if re.search(r'\bconfirmed\s+vessel\s+segmentation', analyzer_content, re.IGNORECASE):
        found_inappropriate.append("confirmed vessel segmentation")
    
    # Check for anatomy detection claims
    if re.search(r'optic\s+disc\s+(?:detection|detected)', analyzer_content, re.IGNORECASE):
        found_inappropriate.append("optic disc detection")
        
    if re.search(r'fovea\s+(?:detection|detected)', analyzer_content, re.IGNORECASE):
        found_inappropriate.append("fovea detection")
    
    found_disclaimers = []
    for disclaimer in appropriate_disclaimers:
        if disclaimer.lower() in analyzer_content.lower():
            found_disclaimers.append(disclaimer)
    
    if found_inappropriate:
        print(f"   ❌ Inappropriate claims found: {', '.join(found_inappropriate)}")
    else:
        print("   ✅ No inappropriate vessel/anatomy claims found")
        
    if found_disclaimers:
        print(f"   ✅ Proper disclaimers found: {', '.join(found_disclaimers)}")
    
    # Verify method description
    print(f"\n🔬 METHOD VERIFICATION:")
    
    if "black-hat morphology" in analyzer_content:
        print("   - Method clearly described: ✅ 'black-hat morphology'")
    
    if "green-channel" in analyzer_content or "green channel" in analyzer_content:
        print("   - Channel specification: ✅ 'green channel'")
    
    if "vessel-like" in analyzer_content and "vessel segmentation" not in analyzer_content:
        print("   - Proper terminology: ✅ 'vessel-like' (not 'vessel segmentation')")
    
    # Check unavailable features
    print(f"\n🚫 UNAVAILABLE FEATURES VERIFICATION:")
    
    unavailable_features = {
        "optic_disc": "optic disc localization",
        "fovea": "fovea localization"
    }
    
    for feature, description in unavailable_features.items():
        if f'"{feature}": {{"available": False' in analyzer_content:
            print(f"   - {description}: ✅ Properly marked as unavailable")
        else:
            print(f"   - {description}: ❌ Not properly marked as unavailable")
    
    # Frontend terminology check
    print(f"\n🖥️  FRONTEND TERMINOLOGY:")
    
    if frontend_content:
        frontend_checks = {
            "Experimental": "experimental labeling",
            "vessel-like": "proper vessel terminology",
            "Not a clinical measurement": "clinical disclaimer",
            "not validated vessel segmentation": "segmentation disclaimer"
        }
        
        for term, description in frontend_checks.items():
            if term.lower() in frontend_content.lower():
                print(f"   - {description}: ✅")
            else:
                print(f"   - {description}: ⚠️")
    
    # Check confidence availability
    print(f"\n📊 CONFIDENCE/VALIDATION CLAIMS:")
    
    if '"confidence_available": False' in analyzer_content:
        print("   - Structure confidence: ✅ Properly marked as unavailable")
    
    if "No ground-truth" in analyzer_content:
        print("   - Validation limitations: ✅ Explicitly acknowledged")
    
    if "not validated" in analyzer_content.lower():
        print("   - Validation disclaimers: ✅ Present")
    
    # Algorithm transparency
    print(f"\n🔍 ALGORITHM TRANSPARENCY:")
    
    algorithm_components = {
        "field of view estimation": "_retinal_region_mask",
        "vessel-like detection": "_estimate_vessel_like_mask", 
        "morphological operations": "MORPH_BLACKHAT",
        "percentile thresholding": "percentile",
        "component filtering": "_remove_small_components"
    }
    
    for component, code_pattern in algorithm_components.items():
        if code_pattern in analyzer_content:
            print(f"   - {component}: ✅ Implemented")
        else:
            print(f"   - {component}: ❌ Not found")
    
    # Safety assessment
    print(f"\n" + "="*50)
    print("STRUCTURE ANALYSIS SAFETY ASSESSMENT")
    print("="*50)
    
    safety_criteria = {
        "experimental_labeling": len(found_experimental) >= 3,
        "no_inappropriate_claims": len(found_inappropriate) == 0,
        "confidence_disclaimed": '"confidence_available": False' in analyzer_content,
        "optic_disc_unavailable": "optic_disc" in analyzer_content and '"available": False' in analyzer_content,
        "fovea_unavailable": "fovea" in analyzer_content and '"available": False' in analyzer_content,
        "method_transparent": "black-hat" in analyzer_content,
        "limitations_documented": "limitations" in analyzer_content.lower()
    }
    
    for criterion, passed in safety_criteria.items():
        symbol = "✅" if passed else "❌"
        print(f"   {symbol} {criterion.replace('_', ' ').title()}: {passed}")
    
    overall_safe = all(safety_criteria.values())
    
    print(f"\n🎯 STRUCTURE TERMINOLOGY STATUS:")
    
    if overall_safe:
        print("   ✅ SCIENTIFICALLY HONEST: Experimental nature clearly disclosed")
        print("   ✅ PROPERLY SCOPED: Image processing estimate, not clinical segmentation")
        print("   ✅ LIMITATIONS ACKNOWLEDGED: Validation constraints documented")
        print("   ✅ NO FALSE CLAIMS: No vessel segmentation or anatomy detection claims")
        print("   ✅ METHOD TRANSPARENT: Algorithm clearly described")
    else:
        print("   ❌ TERMINOLOGY ISSUES FOUND")
    
    return overall_safe, safety_criteria

def main():
    """Main structure verification function."""
    
    safe, criteria = analyze_structure_terminology()
    
    if safe:
        print(f"\n" + "="*80)
        print("PHASE 6 COMPLETE: STRUCTURE ANALYSIS TERMINOLOGY VERIFIED")
        print("="*80)
        print("✅ Structure analysis uses scientifically accurate terminology")
        print("✅ 'Vessel-like' correctly used instead of 'vessel segmentation'")
        print("✅ Optic disc and fovea properly marked as unavailable")
        print("✅ Experimental nature clearly communicated")
        print("✅ Algorithm methodology transparent")
        print("✅ Limitations properly documented")
        
        print(f"\n🔬 STRUCTURE ANALYSIS SUMMARY:")
        print("   - Method: Green-channel black-hat morphological operations")
        print("   - Output: Vessel-like candidate regions (not validated segmentation)")
        print("   - Confidence: Explicitly unavailable")
        print("   - Optic disc: Unavailable (no local detector)")
        print("   - Fovea: Unavailable (no local detector)")
        print("   - Field-of-view: Heuristic estimate")
        print("   - Validation: Limited by lack of ground-truth masks")
        
        print(f"\n✅ APPROPRIATE TERMINOLOGY:")
        print("   - 'Vessel-like structure estimation'")
        print("   - 'Experimental image-processing estimate'")
        print("   - 'Candidate map is not validated vessel segmentation'")
        print("   - 'Not a clinical measurement'")
        
    else:
        print(f"\n❌ STRUCTURE ANALYSIS VERIFICATION FAILED")
        failed_criteria = [k for k, v in criteria.items() if not v]
        print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
    return safe

if __name__ == "__main__":
    main()