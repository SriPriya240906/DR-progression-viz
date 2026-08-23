try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False

from datetime import datetime


def generate_pdf_report(output_path, data):
    """Generate a PDF report using reportlab.

    If reportlab is not installed the function raises a clear RuntimeError
    instead of causing an import-time crash so the app can handle the
    missing optional dependency more gracefully.
    """
    if not HAS_REPORTLAB:
        raise RuntimeError(
            "reportlab is not installed in the active Python environment. "
            "Install it with `pip install reportlab` or run the app with the project venv."
        )

    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph("DR ProgressionViz - AI Medical Report", styles["Title"]))
    content.append(Spacer(1, 12))

    # Timestamp
    content.append(Paragraph(f"Date: {datetime.now()}", styles["Normal"]))
    content.append(Spacer(1, 12))

    # Diagnosis
    content.append(Paragraph(f"Predicted Grade: {data['grade']}", styles["Normal"]))
    content.append(Paragraph(f"Confidence: {data['confidence']}%", styles["Normal"]))
    content.append(Paragraph(f"Risk Level: {data['risk']}", styles["Normal"]))
    content.append(Spacer(1, 12))

    # Progression
    content.append(Paragraph("Progression Prediction:", styles["Heading2"]))
    content.append(Paragraph(str(data['progression']), styles["Normal"]))
    content.append(Spacer(1, 12))

    # Recommendation
    content.append(Paragraph("Clinical Recommendation:", styles["Heading2"]))
    content.append(Paragraph(data['recommendation'], styles["Normal"]))

    doc.build(content)

    return output_path