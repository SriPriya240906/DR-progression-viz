import streamlit as st
from PIL import Image
import tempfile

from model import predict_details
from retrieval_engine.similarity_search import search_similar_images
from retrieval_engine.progression_search import get_progression_map
from retrieval_engine.progression_simulator import simulate_progression
from utils.pdf_report import generate_pdf_report

# -----------------------------
# OPTIONAL IMPORTS (SAFE)
# -----------------------------
try:
    from retrieval_engine.progression_model import predict_progression
except Exception:
    predict_progression = None

try:
    from progression_engine.gradcam import generate_gradcam
    GRADCAM_AVAILABLE = True
except Exception:
    GRADCAM_AVAILABLE = False


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="DR ProgressionViz",
    page_icon="👁️",
    layout="wide"
)

st.title("👁️ DR ProgressionViz")
st.markdown("AI Diagnosis + Retrieval + Progression Intelligence + Report")

# -----------------------------
# LABELS
# -----------------------------
grade_names = {
    0: "No Diabetic Retinopathy",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative DR"
}

risk_levels = {
    0: "Low",
    1: "Moderate",
    2: "High",
    3: "Very High",
    4: "Critical"
}

# -----------------------------
# UPLOAD
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Retinal Image",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        image.save(tmp.name)
        image_path = tmp.name

    # -----------------------------
    # AI PREDICTION
    # -----------------------------
    details = predict_details(image_path)

    grade = details.get("grade", 0)
    confidence = details.get("confidence", 0.0)
    probabilities = details.get("probabilities", {})

    # -----------------------------
    # ENGINE OUTPUTS (SAFE)
    # -----------------------------
    try:
        similar_images = search_similar_images(image_path)
    except Exception:
        similar_images = []

    try:
        progression_map = get_progression_map(image_path)
    except Exception:
        progression_map = {}

    try:
        progression_sim = simulate_progression(image_path)
    except Exception:
        progression_sim = []

    try:
        progression_pred = predict_progression(image_path) if predict_progression else None
    except Exception:
        progression_pred = None

    # -----------------------------
    # LAYOUT
    # -----------------------------
    col1, col2 = st.columns([1.2, 1])

    # =========================
    # LEFT PANEL
    # =========================
    with col1:

        st.subheader("Uploaded Image")
        st.image(image, use_container_width=True)

        st.markdown("---")

        # Grad-CAM
        st.subheader("Grad-CAM Explanation")

        if GRADCAM_AVAILABLE:
            try:
                cam = generate_gradcam(image_path)
                st.image(cam, use_container_width=True)
            except Exception as e:
                st.warning("Grad-CAM failed")
        else:
            st.info("Grad-CAM not available")

        # Similar cases
        st.markdown("---")
        st.subheader("Similar Cases")

        if similar_images:
            for score, p in similar_images:
                st.image(p, width=150)
                st.caption(f"Similarity: {score:.4f}")
        else:
            st.info("No similar cases found")

        # Simulation
        st.markdown("---")
        st.subheader("Progression Simulation")

        if progression_sim:
            for step in progression_sim:
                st.write(f"Stage {step.get('grade')}")
                st.image(step.get("image"), width=160)
        else:
            st.info("No simulation available")

    # =========================
    # RIGHT PANEL
    # =========================
    with col2:

        st.subheader("Prediction Result")

        st.success(f"Grade: {grade}")
        st.info(grade_names.get(grade, "Unknown"))

        st.metric("Confidence", f"{confidence:.2f}%")

        st.markdown("---")

        st.subheader("Risk Level")
        st.progress((grade + 1) / 5)
        st.write(risk_levels.get(grade, "Unknown"))

        # -------------------------
        # Progression Prediction
        # -------------------------
        st.markdown("---")
        st.subheader("AI Progression Prediction")

        if progression_pred:
            st.write(f"Current Grade: {progression_pred.get('current_grade')}")
            st.write(f"Next Stage: {progression_pred.get('next_likely_stage')}")

            probs = progression_pred.get("probabilities", {})
            if isinstance(probs, dict):
                for k, v in probs.items():
                    st.write(f"Stage {k}: {v:.3f}")
        else:
            st.info("Progression model not available (train model first)")

        # -------------------------
        # Progression Map
        # -------------------------
        st.markdown("---")
        st.subheader("Case-Based Progression Map")

        if progression_map:
            for g in range(5):
                st.write(f"### Stage {g} - {grade_names[g]}")

                for score, img in progression_map.get(g, []):
                    st.image(img, width=120)
                    st.caption(f"{score:.4f}")
        else:
            st.info("No progression map data")

        # -------------------------
        # PDF REPORT (FIXED)
        # -------------------------
        st.markdown("---")
        st.subheader("Generate PDF Report")

        if st.button("Generate Report"):

            report_data = {
                "grade": grade,
                "confidence": confidence,
                "risk": risk_levels.get(grade),
                "progression": progression_pred,
                "recommendation": (
                    "Maintain blood sugar control, "
                    "regular eye screening, and follow ophthalmologist advice."
                )
            }

            file_path = "dr_report.pdf"
            generate_pdf_report(file_path, report_data)

            with open(file_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    f,
                    file_name="DR_Report.pdf"
                )

    # -----------------------------
    # SYSTEM STATUS
    # -----------------------------
    st.markdown("---")
    st.subheader("System Status")

    st.success("AI Classification Active")
    st.success("Retrieval Engine Active")
    st.success("Progression Simulation Active")

    if predict_progression:
        st.success("AI Progression Model Loaded")
    else:
        st.warning("AI Progression Model Missing")

    if GRADCAM_AVAILABLE:
        st.success("Grad-CAM Active")
    else:
        st.warning("Grad-CAM Not Available")