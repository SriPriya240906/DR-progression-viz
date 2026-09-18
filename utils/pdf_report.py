try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True

except Exception:
    HAS_REPORTLAB = False

from datetime import datetime


def _safe_value(data, key, default="Not available"):
    value = data.get(key, default)

    if value is None or value == "":
        return default

    return value


def _format_percent(value):
    try:
        value = float(value)

        # Convert 0-1 values to percentage.
        if 0 <= value <= 1:
            value *= 100

        return f"{value:.1f}%"

    except Exception:
        return "Not available"


def _extract_progression(data):
    """Extract only doctor-relevant progression information."""

    prediction = data.get("progression_prediction")

    if not isinstance(prediction, dict):
        return None

    current_grade = prediction.get("current_grade")
    next_stage = prediction.get("next_likely_stage")
    probabilities = prediction.get("probabilities")

    return {
        "current_grade": current_grade,
        "next_likely_stage": next_stage,
        "probabilities": probabilities,
    }


def _stage_name(grade):
    names = {
        0: "No Diabetic Retinopathy",
        1: "Mild NPDR",
        2: "Moderate NPDR",
        3: "Severe NPDR",
        4: "Proliferative DR",
    }

    try:
        return names.get(int(grade), "Unknown")
    except Exception:
        return "Unknown"


def generate_pdf_report(output_path, data):
    """Generate a concise doctor-facing DR ProgressionViz report."""

    if not HAS_REPORTLAB:
        raise RuntimeError(
            "reportlab is not installed in the active Python environment. "
            "Install it with `pip install reportlab`."
        )

    doc = SimpleDocTemplate(
        output_path,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()
    content = []

    # =========================================================
    # TITLE
    # =========================================================

    content.append(
        Paragraph(
            "DR ProgressionViz – AI-Assisted Retinal Assessment",
            styles["Title"],
        )
    )

    content.append(Spacer(1, 8))

    content.append(
        Paragraph(
            f"Report date: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            styles["Normal"],
        )
    )

    content.append(Spacer(1, 18))

    # =========================================================
    # AI ASSESSMENT
    # =========================================================

    content.append(
        Paragraph(
            "1. AI-Assessed Diabetic Retinopathy",
            styles["Heading2"],
        )
    )

    grade = _safe_value(data, "grade")
    label = _safe_value(data, "label")
    confidence = _safe_value(data, "confidence")
    risk = _safe_value(data, "risk")

    # If label is missing, derive it from grade.
    if label == "Not available":
        label = _stage_name(grade)

    content.append(
        Paragraph(
            f"<b>Predicted stage:</b> {label}",
            styles["Normal"],
        )
    )

    content.append(
        Paragraph(
            f"<b>DR grade:</b> {grade}",
            styles["Normal"],
        )
    )

    content.append(
        Paragraph(
            f"<b>Model probability:</b> {_format_percent(confidence)}",
            styles["Normal"],
        )
    )

    content.append(
        Paragraph(
            f"<b>Risk category:</b> {risk}",
            styles["Normal"],
        )
    )

    content.append(Spacer(1, 6))

    content.append(
        Paragraph(
            "<i>Model probability represents the model's output and "
            "should not be interpreted as clinical certainty.</i>",
            styles["Normal"],
        )
    )

    content.append(Spacer(1, 16))

    # =========================================================
    # IMAGE QUALITY
    # =========================================================

    evidence = data.get("evidence_summary", {})

    if isinstance(evidence, dict):

        image_quality = evidence.get("image_quality", {})

        if isinstance(image_quality, dict):

            quality_status = image_quality.get(
                "status",
                "Not available"
            )

            content.append(
                Paragraph(
                    "2. Image Quality",
                    styles["Heading2"],
                )
            )

            content.append(
                Paragraph(
                    f"<b>Overall quality:</b> {quality_status}",
                    styles["Normal"],
                )
            )

            quality_summary = image_quality.get("summary")

            if quality_summary:
                content.append(
                    Paragraph(
                        str(quality_summary),
                        styles["Normal"],
                    )
                )

            warnings = image_quality.get("warnings", [])

            if warnings:
                content.append(
                    Paragraph(
                        "<b>Quality warnings:</b> "
                        + "; ".join(str(w) for w in warnings),
                        styles["Normal"],
                    )
                )

            content.append(Spacer(1, 16))

    # =========================================================
    # SUPPORTING EVIDENCE
    # =========================================================

    content.append(
        Paragraph(
            "3. Supporting AI Evidence",
            styles["Heading2"],
        )
    )

    model_explanation = None
    retinal_structure = None
    lesion_evidence = None

    if isinstance(evidence, dict):
        model_explanation = evidence.get("model_explanation")
        retinal_structure = evidence.get("retinal_structure")
        lesion_evidence = evidence.get("lesion_evidence")

    # Grad-CAM
    if isinstance(model_explanation, dict):

        gradcam_available = model_explanation.get(
            "gradcam_available",
            False
        )

        if gradcam_available:
            content.append(
                Paragraph(
                    "<b>Model attention:</b> Grad-CAM available.",
                    styles["Normal"],
                )
            )

            content.append(
                Paragraph(
                    "Grad-CAM highlights image regions contributing "
                    "to the model prediction. These regions are not "
                    "confirmed lesions.",
                    styles["Normal"],
                )
            )

            content.append(Spacer(1, 6))

    # Retinal structure
    if isinstance(retinal_structure, dict):

        if retinal_structure.get("available"):

            content.append(
                Paragraph(
                    "<b>Retinal structure:</b> "
                    "Experimental structure analysis available.",
                    styles["Normal"],
                )
            )

            content.append(
                Paragraph(
                    "Structure estimates are experimental supporting "
                    "evidence and are not a validated vessel or "
                    "optic-disc segmentation result.",
                    styles["Normal"],
                )
            )

            content.append(Spacer(1, 6))

    # Lesion candidates
    if isinstance(lesion_evidence, dict):

        if lesion_evidence.get("available"):

            content.append(
                Paragraph(
                    "<b>Lesion candidate evidence:</b> "
                    "Dark/bright candidate regions detected.",
                    styles["Normal"],
                )
            )

            content.append(
                Paragraph(
                    "These are image-processing candidates only and "
                    "are not confirmed clinical lesions.",
                    styles["Normal"],
                )
            )

    content.append(Spacer(1, 16))

    # =========================================================
    # PROGRESSION
    # =========================================================

    progression = _extract_progression(data)

    if progression:

        content.append(
            Paragraph(
                "4. Progression Model Output",
                styles["Heading2"],
            )
        )

        current_grade = progression["current_grade"]
        next_stage = progression["next_likely_stage"]

        if current_grade is not None:
            content.append(
                Paragraph(
                    f"<b>Current model-assessed stage:</b> "
                    f"{_stage_name(current_grade)} "
                    f"(Grade {current_grade})",
                    styles["Normal"],
                )
            )

        if next_stage is not None:
            content.append(
                Paragraph(
                    f"<b>Next model-estimated stage:</b> "
                    f"{_stage_name(next_stage)} "
                    f"(Grade {next_stage})",
                    styles["Normal"],
                )
            )

        probabilities = progression.get("probabilities")

        if isinstance(probabilities, dict):

            content.append(
                Paragraph(
                    "<b>Model-estimated stage distribution:</b>",
                    styles["Normal"],
                )
            )

            for stage in ["0", "1", "2", "3", "4"]:

                if stage in probabilities:

                    content.append(
                        Paragraph(
                            f"Grade {stage} – "
                            f"{_stage_name(stage)}: "
                            f"{_format_percent(probabilities[stage])}",
                            styles["Normal"],
                        )
                    )

            content.append(Spacer(1, 6))

            content.append(
                Paragraph(
                    "<i>Progression estimates are model outputs and "
                    "do not represent an established individual "
                    "clinical prognosis.</i>",
                    styles["Normal"],
                )
            )

        content.append(Spacer(1, 16))

    # =========================================================
    # CLINICAL REVIEW
    # =========================================================

    content.append(
        Paragraph(
            "5. Clinical Review",
            styles["Heading2"],
        )
    )

    recommendation = data.get("recommendation")

    if recommendation:
        content.append(
            Paragraph(
                str(recommendation),
                styles["Normal"],
            )
        )
    else:
        content.append(
            Paragraph(
                "Review this AI-assisted assessment with a "
                "qualified ophthalmologist.",
                styles["Normal"],
            )
        )

    content.append(Spacer(1, 16))

    # =========================================================
    # LIMITATIONS
    # =========================================================

    content.append(
        Paragraph(
            "6. Important Limitations",
            styles["Heading2"],
        )
    )

    limitations = [
        "The AI model output is not a standalone clinical diagnosis.",
        "Model probability should not be interpreted as clinical certainty.",
        "Calibration has not been established where a defensible held-out calibration set is unavailable.",
        "Grad-CAM indicates model-contributing regions and does not confirm disease lesions.",
        "Retinal structure and lesion-candidate analysis are experimental supporting evidence.",
        "Progression estimates are model outputs and are not established individual clinical prognosis.",
    ]

    for limitation in limitations:
        content.append(
            Paragraph(
                f"• {limitation}",
                styles["Normal"],
            )
        )

    content.append(Spacer(1, 16))

    # =========================================================
    # DISCLAIMER
    # =========================================================

    content.append(
        Paragraph(
            "Disclaimer",
            styles["Heading2"],
        )
    )

    content.append(
        Paragraph(
            "This report is generated by an experimental AI research "
            "system for decision-support purposes. It does not replace "
            "a comprehensive ophthalmic examination, diagnostic testing, "
            "or clinical judgment by a qualified healthcare professional.",
            styles["Normal"],
        )
    )

    # =========================================================
    # BUILD
    # =========================================================

    doc.build(content)

    return output_path