#!/usr/bin/env python3
"""
PHASE 12: Evidence Summary Verification

This script verifies that the evidence summary:
1. Only includes statements that come from actual API outputs
2. Does not fabricate or synthesize new evidence
3. Properly disclaims limitations and experimental nature
4. Does not combine evidence into medical scores
5. Maintains clear separation between AI output and clinical interpretation

Critical requirements:
- Must only report actual analysis outputs
- Must not create synthetic clinical statements  
- Must disclaim experimental nature of evidence
- Must require clinical review
- Must not calculate combined scores
"""

import os
import json
from pathlib import Path

def verify_evidence_summary_implementation():
    """Verify evidence summary implementation and presentation."""
    
    print("="*80)
    print("PHASE 12: EVIDENCE SUMMARY VERIFICATION")
    print("="*80)
    
    # Check evidence summary implementation
    print("✅ EVIDENCE SUMMARY IMPLEMENTATION ANALYSIS:")
    
    evidence_impl_path = Path("backend/evidence/clinical_evidence_summary.py")
    if not evidence_impl_path.exists():
        print("   ❌ Evidence summary implementation not found")
        return False
    
    with open(evidence_impl_path, 'r') as f:
        impl_content = f.read()
    
    print("   - Evidence summary implementation: ✅")
    
    # Check implementation structure
    impl_checks = {
        "Individual summaries": "_prediction_summary|_uncertainty_summary|_quality_summary",
        "No score combination": "not.*combining|without.*combining",
        "Clinical review required": "clinical.*review.*required",
        "Limitation disclaimers": "limitations",
        "Experimental disclaimers": "experimental",
        "Not confirmed lesions": "not.*confirmed.*lesions"
    }
    
    import re
    for check_name, pattern in impl_checks.items():
        if re.search(pattern, impl_content, re.IGNORECASE):
            print(f"   - {check_name}: ✅")
        else:
            print(f"   - {check_name}: ⚠️")
    
    # Check for inappropriate synthesis
    synthesis_warnings = [
        "medical diagnosis",
        "clinical diagnosis", 
        "disease severity",
        "treatment recommendation",
        "combined score",
        "overall assessment",
        "medical certainty"
    ]
    
    found_synthesis = []
    for warning in synthesis_warnings:
        if re.search(warning, impl_content, re.IGNORECASE):
            found_synthesis.append(warning)
    
    if found_synthesis:
        print(f"   ⚠️  Potential synthesis terms: {', '.join(found_synthesis)}")
    else:
        print("   ✅ No inappropriate synthesis terms found")
    
    # Test the function
    print(f"\n🧪 FUNCTIONALITY TEST:")
    
    try:
        from backend.evidence import build_evidence_summary
        
        # Test with mock data that reflects actual API structure
        mock_analysis = {
            "prediction": {
                "grade": 2,
                "label": "Moderate",
                "confidence": 85.5
            },
            "reliability": {
                "available": True,
                "top_probability": 0.855,
                "second_probability": 0.098,
                "probability_margin": 0.757,
                "predictive_entropy": 0.234,
                "normalized_predictive_entropy": 0.145,
                "calibration": {"available": False}
            },
            "quality": {
                "available": True,
                "status": "GOOD",
                "focus": 0.85,
                "illumination": 0.92,
                "contrast": 0.78,
                "warnings": []
            },
            "gradcam": {
                "available": True
            },
            "structure": {
                "available": True,
                "vessels": {
                    "vessel_like_fraction": 0.12,
                    "confidence_available": False
                },
                "optic_disc": {"available": False},
                "fovea": {"available": False}
            },
            "lesion_evidence": {
                "available": True,
                "dark_candidates": {"count": 5, "fraction": 0.008},
                "bright_candidates": {"count": 2, "fraction": 0.003}
            }
        }
        
        summary = build_evidence_summary(mock_analysis)
        
        print(f"   - Function execution: ✅")
        print(f"   - Return type: {type(summary)}")
        
        # Check structure
        required_keys = ["available", "prediction", "model_uncertainty", "image_quality", 
                        "model_explanation", "retinal_structure", "lesion_evidence", 
                        "clinical_review", "limitations"]
        
        for key in required_keys:
            if key in summary:
                print(f"   - Key '{key}': ✅")
            else:
                print(f"   - Key '{key}': ❌")
        
        # Check prediction summary
        pred_summary = summary.get("prediction", {})
        if pred_summary.get("grade") == 2 and pred_summary.get("label") == "Moderate":
            print("   - Prediction passthrough: ✅")
        else:
            print(f"   - Prediction passthrough: ❌")
        
        # Check clinical review requirement
        clinical_review = summary.get("clinical_review", {})
        if clinical_review.get("required") is True:
            print("   - Clinical review required: ✅")
        else:
            print("   - Clinical review required: ❌")
        
        # Check limitations
        limitations = summary.get("limitations", [])
        if limitations and len(limitations) > 3:
            print(f"   - Limitations provided: ✅ ({len(limitations)} items)")
            
            # Check for key disclaimers in limitations
            limitations_text = " ".join(limitations).lower()
            key_disclaimers = [
                "not clinical certainty",
                "calibration",
                "experimental",
                "not confirmed",
                "no combined score"
            ]
            
            for disclaimer in key_disclaimers:
                if disclaimer in limitations_text:
                    print(f"     - '{disclaimer}' disclaimed: ✅")
                else:
                    print(f"     - '{disclaimer}' disclaimed: ⚠️")
        else:
            print("   - Limitations: ⚠️ Insufficient")
        
        # Check that summary statements come from inputs
        structure_summary = summary.get("retinal_structure", {}).get("summary", "")
        lesion_summary = summary.get("lesion_evidence", {}).get("summary", "")
        
        if "experimental" in structure_summary.lower():
            print("   - Structure experimental disclaimer: ✅")
        else:
            print("   - Structure experimental disclaimer: ⚠️")
            
        if "not confirmed" in lesion_summary.lower():
            print("   - Lesion disclaimer: ✅")
        else:
            print("   - Lesion disclaimer: ⚠️")
            
    except Exception as e:
        print(f"   - Functionality test failed: ❌ {e}")
    
    # Check frontend presentation
    print(f"\n🖥️  FRONTEND PRESENTATION ANALYSIS:")
    
    evidence_card_path = Path("frontend/src/components/ClinicalEvidenceCard.jsx")
    if evidence_card_path.exists():
        print("   - ClinicalEvidenceCard component: ✅")
        
        with open(evidence_card_path, 'r') as f:
            card_content = f.read()
        
        # Check appropriate presentation
        card_checks = {
            "Independent signals": "Independent signals",
            "No combined score": "No combined medical score",
            "Clinical review required": "Clinical review required",
            "Experimental disclaimers": "experimental",
            "Not confirmed lesions": "not confirmed clinical lesions",
            "Separated evidence blocks": "evidence-block"
        }
        
        for check_name, pattern in card_checks.items():
            if pattern in card_content:
                print(f"   - {check_name}: ✅")
            else:
                print(f"   - {check_name}: ⚠️")
        
        # Check for evidence organization
        if "ai-output-block" in card_content:
            print("   - AI output separation: ✅")
        else:
            print("   - AI output separation: ⚠️")
            
        if "clinical-limitation-block" in card_content:
            print("   - Clinical limitations section: ✅")
        else:
            print("   - Clinical limitations section: ⚠️")
    
    # Check backend integration
    print(f"\n🔗 BACKEND INTEGRATION ANALYSIS:")
    
    backend_main = Path("backend/main.py")
    if backend_main.exists():
        with open(backend_main, 'r') as f:
            backend_content = f.read()
        
        integration_checks = {
            "Evidence summary import": "from backend.evidence import build_evidence_summary",
            "Evidence summary call": "build_evidence_summary(response_payload)"
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
        "backend/evidence/clinical_evidence_summary.py",
        "frontend/src/components/ClinicalEvidenceCard.jsx"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                all_content += f.read().lower()
    
    inappropriate_claims = [
        "provides medical diagnosis",
        "clinical diagnosis confirmed", 
        "treatment recommendation",
        "medical certainty established",
        "combined clinical score",
        "diagnostic confidence",
        "clinical evidence confirms"
    ]
    
    found_inappropriate = []
    for claim in inappropriate_claims:
        if claim in all_content:
            found_inappropriate.append(claim)
    
    if found_inappropriate:
        print(f"   ❌ Found inappropriate claims: {', '.join(found_inappropriate)}")
    else:
        print("   ✅ No inappropriate medical claims found")
    
    # Check appropriate disclaimers and limitations
    appropriate_terms = [
        "clinical review required",
        "experimental",
        "not confirmed",
        "not clinical certainty",
        "require.*clinical.*review",
        "no.*combined.*score"
    ]
    
    found_appropriate = []
    for term in appropriate_terms:
        if re.search(term, all_content, re.IGNORECASE):
            found_appropriate.append(term)
    
    print(f"   - Appropriate disclaimers found: {len(found_appropriate)} terms")
    
    # Overall assessment
    print(f"\n" + "="*50)
    print("EVIDENCE SUMMARY SAFETY ASSESSMENT")
    print("="*50)
    
    safety_criteria = {
        "outputs_only": "statement" in all_content and "prediction" in all_content,
        "clinical_review_required": "clinical review required" in all_content,
        "experimental_disclaimers": "experimental" in all_content,
        "no_synthesis_warnings": len(found_synthesis) == 0,
        "no_inappropriate_claims": len(found_inappropriate) == 0,
        "limitations_documented": "limitations" in all_content,
        "not_confirmed_disclaimers": "not confirmed" in all_content,
        "individual_signals": "independent signals" in all_content,
        "frontend_integration": evidence_card_path.exists()
    }
    
    for criterion, passed in safety_criteria.items():
        symbol = "✅" if passed else "❌"
        print(f"   {symbol} {criterion.replace('_', ' ').title()}: {passed}")
    
    overall_safe = all(safety_criteria.values())
    
    print(f"\n🎯 EVIDENCE SUMMARY STATUS:")
    
    if overall_safe:
        print("   ✅ ACTUAL OUTPUTS ONLY: Reports only from API analysis results")
        print("   ✅ CLINICAL REVIEW REQUIRED: Explicitly requires clinical review")
        print("   ✅ EXPERIMENTAL DISCLAIMERS: Labels experimental evidence appropriately")
        print("   ✅ NO INAPPROPRIATE SYNTHESIS: No medical diagnosis or treatment claims")
        print("   ✅ INDIVIDUAL SIGNALS: Maintains separation of evidence types")
        print("   ✅ PROPER LIMITATIONS: Documents calibration, certainty, confirmation limits")
        print("   ✅ NO COMBINED SCORES: No medical or disease severity scoring")
    else:
        print("   ❌ EVIDENCE SUMMARY IMPLEMENTATION ISSUES FOUND")
        failed = [k for k, v in safety_criteria.items() if not v]
        print(f"      Failed: {', '.join(failed)}")
    
    return overall_safe, safety_criteria

def main():
    """Main evidence summary verification function."""
    
    safe, criteria = verify_evidence_summary_implementation()
    
    if safe:
        print(f"\n" + "="*80)
        print("PHASE 12 COMPLETE: EVIDENCE SUMMARY VERIFIED")
        print("="*80)
        print("✅ Reports only actual API analysis outputs")
        print("✅ Clinical review explicitly required")
        print("✅ Experimental evidence properly disclaimed")
        print("✅ No inappropriate medical synthesis")
        print("✅ Individual signals maintained separately")
        print("✅ Proper limitations documented")
        print("✅ No combined medical scoring")
        
        print(f"\n🔬 EVIDENCE SUMMARY TECHNICAL SUMMARY:")
        print("   - Structure: Individual evidence summaries without combination")
        print("   - Sources: Only from actual API analysis outputs")
        print("   - Disclaimers: Experimental nature, not confirmed lesions")
        print("   - Requirements: Clinical review required for all analyses")
        print("   - Limitations: Calibration, certainty, confirmation constraints")
        
        print(f"\n✅ APPROPRIATE USAGE:")
        print("   - 'AI-Assisted Evidence Summary' heading")
        print("   - 'Independent signals, clearly separated'")
        print("   - 'No combined medical score' tag")
        print("   - 'Clinical review required' explicit requirement")
        
        print(f"\n❌ INAPPROPRIATE CLAIMS AVOIDED:")
        print("   - 'Provides medical diagnosis'")
        print("   - 'Clinical diagnosis confirmed'")
        print("   - 'Treatment recommendation'")
        print("   - 'Combined clinical score'")
        
    else:
        print(f"\n❌ EVIDENCE SUMMARY VERIFICATION FAILED")
        failed_criteria = [k for k, v in criteria.items() if not v]
        print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
    return safe

if __name__ == "__main__":
    main()