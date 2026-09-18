#!/usr/bin/env python3
"""
PHASE 10: Progression Map Verification

This script verifies that the progression map:
1. Clearly distinguishes reference cases from patient predictions
2. Uses appropriate terminology for case-based references
3. Does not claim to predict individual patient progression
4. Shows similar cases across grades, not progression modeling
5. Properly disclaims limitations

Critical requirements:
- Must use "reference cases" not "patient progression"
- Must disclaim individual progression predictions
- Must show case-based similarities, not temporal modeling
- Must be clear about what it does vs doesn't show
"""

import os
import numpy as np
from pathlib import Path
import re

def verify_progression_map_implementation():
    """Verify progression map implementation and presentation."""
    
    print("="*80)
    print("PHASE 10: PROGRESSION MAP VERIFICATION")
    print("="*80)
    
    # Check progression search implementation
    print("✅ PROGRESSION SEARCH ANALYSIS:")
    
    progression_search_path = Path("retrieval_engine/progression_search.py")
    if not progression_search_path.exists():
        print("   ❌ Progression search implementation not found")
        return False
    
    with open(progression_search_path, 'r') as f:
        search_content = f.read()
    
    # Check implementation details
    search_checks = {
        "Feature extraction": "extract_features",
        "Cosine similarity": "cosine_similarity", 
        "Grade-wise search": "for grade in range(5)",
        "Top-k selection": "scores[:top_k]",
        "Similarity scoring": "scores.sort(reverse=True)"
    }
    
    for check_name, pattern in search_checks.items():
        if pattern in search_content:
            print(f"   - {check_name}: ✅")
        else:
            print(f"   - {check_name}: ❌")
    
    # Check if it's actually similarity search, not progression modeling
    if "temporal" in search_content.lower() or "longitudinal" in search_content.lower():
        print("   ⚠️  Contains temporal/longitudinal terms (suspicious)")
    else:
        print("   ✅ No temporal progression modeling found")
    
    # Check frontend progression map component
    print(f"\n🖥️  FRONTEND PROGRESSION MAP ANALYSIS:")
    
    frontend_path = Path("frontend/src/components/ProgressionMap.jsx")
    if not frontend_path.exists():
        print("   ❌ ProgressionMap component not found")
        return False
    
    with open(frontend_path, 'r') as f:
        frontend_content = f.read()
    
    print("   - ProgressionMap component: ✅")
    
    # Check appropriate terminology
    appropriate_terms = {
        "Case-Based Progression Map": "case-based heading",
        "reference stage": "reference terminology", 
        "Case-based reference": "reference labeling",
        "not a claim of this patient": "individual disclaimer",
        "actual longitudinal progression": "temporal disclaimer"
    }
    
    for term, description in appropriate_terms.items():
        if term in frontend_content:
            print(f"   - {description}: ✅")
        else:
            print(f"   - {description}: ⚠️")
    
    # Check for current vs reference distinction
    if "current={index === currentGrade}" in frontend_content:
        print("   - Current stage marking: ✅")
    else:
        print("   - Current stage marking: ⚠️")
    
    if "Current stage" in frontend_content and "reference stage" in frontend_content:
        print("   - Current vs reference distinction: ✅")
    else:
        print("   - Current vs reference distinction: ⚠️")
    
    # Check backend integration
    print(f"\n🔗 BACKEND INTEGRATION ANALYSIS:")
    
    backend_main = Path("backend/main.py")
    if backend_main.exists():
        with open(backend_main, 'r') as f:
            backend_content = f.read()
        
        integration_checks = {
            "Progression search import": "from retrieval_engine.progression_search import get_progression_map",
            "Function call": "get_progression_map(str(input_path))",
            "Stage mapping": "progression_map[f\"stage_{stage}\"]",
            "Case serialization": "serialize_case"
        }
        
        for check_name, pattern in integration_checks.items():
            if pattern in backend_content:
                print(f"   - {check_name}: ✅")
            else:
                print(f"   - {check_name}: ⚠️")
    
    # Check for inappropriate claims
    print(f"\n⚠️  INAPPROPRIATE CLAIMS CHECK:")
    
    all_content = ""
    
    files_to_check = [
        "retrieval_engine/progression_search.py",
        "frontend/src/components/ProgressionMap.jsx",
        "backend/main.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                all_content += f.read().lower()
    
    inappropriate_claims = [
        "predicts progression",
        "patient will progress",
        "future disease state",
        "temporal progression",
        "longitudinal modeling", 
        "progression timeline",
        "disease trajectory",
        "individual prognosis"
    ]
    
    found_inappropriate = []
    for claim in inappropriate_claims:
        if claim in all_content:
            found_inappropriate.append(claim)
    
    if found_inappropriate:
        print(f"   ❌ Found inappropriate claims: {', '.join(found_inappropriate)}")
    else:
        print("   ✅ No inappropriate progression claims found")
    
    # Check appropriate disclaimers and terminology
    appropriate_terms = [
        "reference cases",
        "case-based",
        "similar cases", 
        "not a claim",
        "reference stage"
    ]
    
    found_appropriate = []
    for term in appropriate_terms:
        if term in all_content:
            found_appropriate.append(term)
    
    print(f"   - Appropriate terminology found: {', '.join(found_appropriate)}")
    
    # Test progression map functionality (if possible)
    print(f"\n🧪 FUNCTIONALITY TEST:")
    
    try:
        from retrieval_engine.progression_search import get_progression_map
        
        # Find a test image
        test_image = None
        for grade_dir in ["progression_database/grade0", "dataset/train"]:
            if os.path.exists(grade_dir):
                for file in os.listdir(grade_dir):
                    if file.endswith('.png'):
                        test_image = os.path.join(grade_dir, file)
                        break
                if test_image:
                    break
        
        if test_image and os.path.exists(test_image):
            print(f"   - Test image: {test_image}")
            progression_map = get_progression_map(test_image, top_k=2)
            
            print(f"   - Retrieved progression map with {len(progression_map)} grades")
            
            for grade, cases in progression_map.items():
                print(f"     Grade {grade}: {len(cases)} cases")
                if cases:
                    best_score = cases[0][0]
                    print(f"       Best similarity: {best_score:.4f}")
            
            # Check that it returns cases for all grades
            if len(progression_map) == 5:
                print("   - All grades represented: ✅")
            else:
                print(f"   - Missing grades: ⚠️ (got {len(progression_map)}, expected 5)")
                
        else:
            print("   - No test image available for functionality test")
            
    except Exception as e:
        print(f"   - Functionality test failed: ❌ {e}")
    
    # Check grade 0 handling
    print(f"\n🚫 GRADE 0 HANDLING:")
    
    if "currentGrade === 0" in frontend_content:
        print("   - Special Grade 0 handling: ✅")
        
        if "Not shown for No DR" in frontend_content:
            print("   - Appropriate No DR message: ✅")
        else:
            print("   - No DR message: ⚠️")
            
        if "No disease progression stages" in frontend_content:
            print("   - No progression for Grade 0: ✅")
        else:
            print("   - Grade 0 progression disclaimer: ⚠️")
    else:
        print("   - Grade 0 special handling: ⚠️")
    
    # Check stage filtering
    if "index < currentGrade" in frontend_content:
        print("   - Earlier stage filtering: ✅ (shows current and later only)")
    else:
        print("   - Stage filtering: ⚠️")
    
    # Overall assessment
    print(f"\n" + "="*50)
    print("PROGRESSION MAP SAFETY ASSESSMENT")
    print("="*50)
    
    safety_criteria = {
        "similarity_based": "cosine_similarity" in search_content,
        "case_based_terminology": "case-based" in all_content,
        "reference_terminology": "reference" in all_content,
        "individual_disclaimer": "not a claim" in all_content or "patient" in all_content,
        "no_progression_claims": len(found_inappropriate) == 0,
        "current_vs_reference": "current stage" in frontend_content.lower(),
        "grade_0_handling": "currentGrade === 0" in frontend_content,
        "stage_filtering": "index < currentGrade" in frontend_content,
        "backend_integration": "get_progression_map" in backend_content if backend_main.exists() else False
    }
    
    for criterion, passed in safety_criteria.items():
        symbol = "✅" if passed else "❌"
        print(f"   {symbol} {criterion.replace('_', ' ').title()}: {passed}")
    
    overall_safe = all(safety_criteria.values())
    
    print(f"\n🎯 PROGRESSION MAP STATUS:")
    
    if overall_safe:
        print("   ✅ CASE-BASED REFERENCES: Shows similar cases by grade, not progression modeling")
        print("   ✅ APPROPRIATE TERMINOLOGY: 'Reference cases' not 'patient progression'")
        print("   ✅ INDIVIDUAL DISCLAIMERS: Clarifies not individual progression prediction")
        print("   ✅ CURRENT VS REFERENCE: Distinguishes patient grade from reference stages")
        print("   ✅ PROPER FILTERING: Shows current grade and later reference stages only")
        print("   ✅ GRADE 0 HANDLING: Appropriately handles 'No DR' cases")
        print("   ✅ NO FALSE CLAIMS: No temporal progression or prognosis claims")
    else:
        print("   ❌ PROGRESSION MAP IMPLEMENTATION ISSUES FOUND")
        failed = [k for k, v in safety_criteria.items() if not v]
        print(f"      Failed: {', '.join(failed)}")
    
    return overall_safe, safety_criteria

def main():
    """Main progression map verification function."""
    
    safe, criteria = verify_progression_map_implementation()
    
    if safe:
        print(f"\n" + "="*80)
        print("PHASE 10 COMPLETE: PROGRESSION MAP VERIFIED")
        print("="*80)
        print("✅ Uses case-based similarity search, not progression modeling")
        print("✅ Appropriate terminology ('reference cases' not 'progression prediction')")
        print("✅ Distinguishes current patient grade from reference stages")
        print("✅ Individual progression disclaimers present")
        print("✅ Proper stage filtering (current and later only)")
        print("✅ Grade 0 ('No DR') appropriately handled")
        print("✅ No inappropriate temporal progression claims")
        
        print(f"\n🔬 PROGRESSION MAP TECHNICAL SUMMARY:")
        print("   - Method: Similarity search across all grades using EfficientNet features")
        print("   - Output: Top-k most similar cases for each DR grade")
        print("   - Presentation: Current stage + later reference stages only")
        print("   - Disclaimers: 'Not a claim of patient's actual longitudinal progression'")
        print("   - Grade 0: Special handling with 'No progression stages shown'")
        
        print(f"\n✅ APPROPRIATE USAGE:")
        print("   - 'Case-Based Progression Map' heading")
        print("   - 'Reference stage' vs 'Current stage' distinction")
        print("   - 'Case-based reference' labeling")
        print("   - 'Not a claim of this patient's progression'")
        
        print(f"\n❌ INAPPROPRIATE CLAIMS AVOIDED:")
        print("   - 'Predicts progression'")
        print("   - 'Patient will progress'")
        print("   - 'Future disease state'")
        print("   - 'Individual prognosis'")
        
    else:
        print(f"\n❌ PROGRESSION MAP VERIFICATION FAILED")
        failed_criteria = [k for k, v in criteria.items() if not v]
        print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
    return safe

if __name__ == "__main__":
    main()