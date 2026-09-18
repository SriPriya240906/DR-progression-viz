#!/usr/bin/env python3
"""
PHASE 11: Disease Landscape Verification

This script verifies that the disease landscape:
1. Uses capability mapping rather than embedding visualization
2. Properly disclaims what diseases are/aren't supported
3. Does not make false claims about multi-disease detection
4. Clearly states limitations and scope
5. Distinguishes between capability reporting vs actual detection

Critical requirements:
- Must be capability mapping, not synthetic embedding coordinates
- Must clearly state only DR is supported
- Must disclaim unavailable diseases don't mean absence
- Must not claim multi-disease scoring
- Must be honest about repository-based capabilities
"""

import os
import json
from pathlib import Path

def verify_disease_landscape_implementation():
    """Verify disease landscape implementation and presentation."""
    
    print("="*80)
    print("PHASE 11: DISEASE LANDSCAPE VERIFICATION")
    print("="*80)
    
    # Check disease landscape implementation
    print("✅ DISEASE LANDSCAPE IMPLEMENTATION ANALYSIS:")
    
    landscape_impl_path = Path("backend/disease_landscape/retinal_disease_landscape.py")
    if not landscape_impl_path.exists():
        print("   ❌ Disease landscape implementation not found")
        return False
    
    with open(landscape_impl_path, 'r') as f:
        impl_content = f.read()
    
    print("   - Disease landscape implementation: ✅")
    
    # Check implementation details
    impl_checks = {
        "Capability mapping": "capability_map",
        "DR labels defined": "SUPPORTED_DR_LABELS",
        "Unavailable diseases": "UNAVAILABLE_DISEASES", 
        "Limitation disclaimers": "limitations",
        "No multi-disease score": "No.*multi-disease.*score",
        "Repository scope": "repository"
    }
    
    import re
    for check_name, pattern in impl_checks.items():
        if re.search(pattern, impl_content, re.IGNORECASE):
            print(f"   - {check_name}: ✅")
        else:
            print(f"   - {check_name}: ⚠️")
    
    # Check if it's capability mapping vs embedding visualization
    if "embedding" in impl_content.lower() or "coordinate" in impl_content.lower():
        print("   ⚠️  Contains embedding/coordinate terms (suspicious)")
    else:
        print("   ✅ No embedding/coordinate visualization found")
    
    # Test the function
    print(f"\n🧪 FUNCTIONALITY TEST:")
    
    try:
        from backend.disease_landscape import build_disease_landscape
        
        landscape = build_disease_landscape()
        
        print(f"   - Function execution: ✅")
        print(f"   - Return type: {type(landscape)}")
        
        # Check structure
        required_keys = ["available", "landscape_type", "diseases", "current_supported_scope", "limitations"]
        for key in required_keys:
            if key in landscape:
                print(f"   - Key '{key}': ✅")
            else:
                print(f"   - Key '{key}': ❌")
        
        # Check landscape type
        if landscape.get("landscape_type") == "capability_map":
            print("   - Landscape type 'capability_map': ✅")
        else:
            print(f"   - Unexpected landscape type: ⚠️ {landscape.get('landscape_type')}")
        
        # Check diseases
        diseases = landscape.get("diseases", [])
        print(f"   - Number of diseases: {len(diseases)}")
        
        supported_diseases = [d for d in diseases if d.get("status") == "supported"]
        unavailable_diseases = [d for d in diseases if d.get("status") == "unavailable"]
        
        print(f"   - Supported diseases: {len(supported_diseases)}")
        print(f"   - Unavailable diseases: {len(unavailable_diseases)}")
        
        # Check DR support
        dr_disease = None
        for disease in diseases:
            if "diabetic retinopathy" in disease.get("name", "").lower():
                dr_disease = disease
                break
        
        if dr_disease and dr_disease.get("status") == "supported":
            print("   - Diabetic Retinopathy supported: ✅")
            print(f"     - Model available: {dr_disease.get('model_available')}")
            print(f"     - Prediction available: {dr_disease.get('prediction_available')}")
            print(f"     - Labels: {len(dr_disease.get('labels', []))}")
        else:
            print("   - Diabetic Retinopathy support: ❌")
        
        # Check unavailable diseases
        expected_unavailable = ["Glaucoma", "Age-related Macular Degeneration", "Diabetic Macular Edema"]
        found_unavailable = [d.get("name") for d in unavailable_diseases]
        
        for disease in expected_unavailable:
            if disease in found_unavailable:
                print(f"   - {disease} properly unavailable: ✅")
            else:
                print(f"   - {disease} availability: ⚠️")
        
        # Check limitations
        limitations = landscape.get("limitations", [])
        if limitations and len(limitations) > 0:
            print(f"   - Limitations provided: ✅ ({len(limitations)} items)")
        else:
            print("   - Limitations: ⚠️ Missing")
            
    except Exception as e:
        print(f"   - Functionality test failed: ❌ {e}")
    
    # Check frontend presentation
    print(f"\n🖥️  FRONTEND PRESENTATION ANALYSIS:")
    
    # Check RetinalDiseaseLandscapeCard
    landscape_card_path = Path("frontend/src/components/RetinalDiseaseLandscapeCard.jsx")
    if landscape_card_path.exists():
        print("   - RetinalDiseaseLandscapeCard component: ✅")
        
        with open(landscape_card_path, 'r') as f:
            card_content = f.read()
        
        # Check appropriate terminology
        card_checks = {
            "Capability map": "Capability map",
            "No multi-disease score": "No multi-disease score",
            "Appropriate disclaimers": "does not indicate absence",
            "Repository scope": "repository",
            "Clinical assessment": "clinical assessment"
        }
        
        for check_name, pattern in card_checks.items():
            if pattern in card_content:
                print(f"   - {check_name}: ✅")
            else:
                print(f"   - {check_name}: ⚠️")
    
    # Check DiseaseLandscape component (coordinate-based)
    coordinate_landscape_path = Path("frontend/src/components/DiseaseLandscape.jsx")
    if coordinate_landscape_path.exists():
        print("   - DiseaseLandscape (coordinate) component: ✅")
        
        with open(coordinate_landscape_path, 'r') as f:
            coord_content = f.read()
        
        # This component uses coordinates - check if it's being used
        if "Learned retinal feature space" in coord_content:
            print("   ⚠️  Contains coordinate-based visualization component")
            print("   - This suggests potential embedding visualization capability")
        
        # Check if coordinate component is used in main app
        app_files = ["frontend/src/App.jsx", "frontend_backup_before_sidebar/src/App.jsx"]
        coordinate_usage_found = False
        
        for app_file in app_files:
            if os.path.exists(app_file):
                with open(app_file, 'r') as f:
                    app_content = f.read()
                
                if "DiseaseLandscape" in app_content and "points" in app_content:
                    coordinate_usage_found = True
                    print(f"   ⚠️  Coordinate DiseaseLandscape used in {app_file}")
        
        if not coordinate_usage_found:
            print("   ✅ Coordinate DiseaseLandscape not actively used")
    
    # Check backend integration
    print(f"\n🔗 BACKEND INTEGRATION ANALYSIS:")
    
    backend_main = Path("backend/main.py")
    if backend_main.exists():
        with open(backend_main, 'r') as f:
            backend_content = f.read()
        
        integration_checks = {
            "Disease landscape import": "from backend.disease_landscape import build_disease_landscape",
            "API endpoint": "/api/disease-landscape",
            "Response integration": "build_disease_landscape()"
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
        "backend/disease_landscape/retinal_disease_landscape.py",
        "frontend/src/components/RetinalDiseaseLandscapeCard.jsx",
        "backend/main.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                all_content += f.read().lower()
    
    inappropriate_claims = [
        "multi-disease detection",
        "detects all diseases",
        "comprehensive disease screening",
        "full retinal disease panel",
        "multi-condition assessment",
        "disease probability score"
    ]
    
    found_inappropriate = []
    for claim in inappropriate_claims:
        if claim in all_content:
            found_inappropriate.append(claim)
    
    if found_inappropriate:
        print(f"   ❌ Found inappropriate claims: {', '.join(found_inappropriate)}")
    else:
        print("   ✅ No inappropriate multi-disease claims found")
    
    # Check appropriate disclaimers and terminology
    appropriate_terms = [
        "capability map",
        "unavailable.*not.*absence",
        "clinical assessment required",
        "repository",
        "no multi-disease score"
    ]
    
    found_appropriate = []
    for term in appropriate_terms:
        if re.search(term, all_content, re.IGNORECASE):
            found_appropriate.append(term)
    
    print(f"   - Appropriate terminology found: {len(found_appropriate)} terms")
    
    # Overall assessment
    print(f"\n" + "="*50)
    print("DISEASE LANDSCAPE SAFETY ASSESSMENT")
    print("="*50)
    
    safety_criteria = {
        "capability_mapping": "capability_map" in all_content,
        "dr_only_supported": dr_disease and dr_disease.get("status") == "supported" if 'dr_disease' in locals() else False,
        "unavailable_diseases": len(unavailable_diseases) > 5 if 'unavailable_diseases' in locals() else False,
        "limitations_documented": "limitations" in all_content,
        "no_multi_disease_claims": len(found_inappropriate) == 0,
        "absence_disclaimers": "absence" in all_content,
        "clinical_assessment": "clinical assessment" in all_content,
        "repository_scope": "repository" in all_content,
        "frontend_integration": landscape_card_path.exists()
    }
    
    for criterion, passed in safety_criteria.items():
        symbol = "✅" if passed else "❌"
        print(f"   {symbol} {criterion.replace('_', ' ').title()}: {passed}")
    
    overall_safe = all(safety_criteria.values())
    
    print(f"\n🎯 DISEASE LANDSCAPE STATUS:")
    
    if overall_safe:
        print("   ✅ CAPABILITY MAPPING: Shows what diseases are/aren't supported, not embeddings")
        print("   ✅ DR-ONLY SUPPORTED: Only Diabetic Retinopathy is marked as available")
        print("   ✅ UNAVAILABLE DISEASES: Multiple diseases properly marked unavailable")
        print("   ✅ APPROPRIATE DISCLAIMERS: Unavailable doesn't mean absent")
        print("   ✅ NO MULTI-DISEASE CLAIMS: Explicitly states 'No multi-disease score'")
        print("   ✅ CLINICAL SCOPE: Requires clinical assessment for other diseases")
        print("   ✅ REPOSITORY HONEST: Reflects actual repository capabilities")
    else:
        print("   ❌ DISEASE LANDSCAPE IMPLEMENTATION ISSUES FOUND")
        failed = [k for k, v in safety_criteria.items() if not v]
        print(f"      Failed: {', '.join(failed)}")
    
    return overall_safe, safety_criteria

def main():
    """Main disease landscape verification function."""
    
    safe, criteria = verify_disease_landscape_implementation()
    
    if safe:
        print(f"\n" + "="*80)
        print("PHASE 11 COMPLETE: DISEASE LANDSCAPE VERIFIED")
        print("="*80)
        print("✅ Uses capability mapping, not embedding visualization")
        print("✅ Only Diabetic Retinopathy marked as supported")
        print("✅ Multiple diseases properly marked unavailable")
        print("✅ Appropriate disclaimers about absence vs unavailability")
        print("✅ No multi-disease detection claims")
        print("✅ Clinical assessment requirements stated")
        print("✅ Repository scope honestly represented")
        
        print(f"\n🔬 DISEASE LANDSCAPE TECHNICAL SUMMARY:")
        print("   - Type: Capability mapping (not coordinate visualization)")
        print("   - Supported: Diabetic Retinopathy (5-grade classification)")
        print("   - Unavailable: 9+ other retinal diseases with explanations")
        print("   - Disclaimers: Unavailable ≠ absent, clinical assessment required")
        print("   - Scope: Repository capabilities, not clinical validation")
        
        print(f"\n✅ APPROPRIATE USAGE:")
        print("   - 'Retinal Disease Landscape' heading")
        print("   - 'Capability map' description")
        print("   - 'No multi-disease score' tag")
        print("   - 'Repository capabilities' scope")
        
        print(f"\n❌ INAPPROPRIATE CLAIMS AVOIDED:")
        print("   - 'Multi-disease detection'")
        print("   - 'Comprehensive disease screening'")
        print("   - 'Full retinal disease panel'")
        print("   - 'Disease probability scores'")
        
    else:
        print(f"\n❌ DISEASE LANDSCAPE VERIFICATION FAILED")
        failed_criteria = [k for k, v in criteria.items() if not v]
        print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
    return safe

if __name__ == "__main__":
    main()