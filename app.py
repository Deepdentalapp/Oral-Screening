import streamlit as st
import requests
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import io

# ----------------------
# Configuration
# ----------------------
ROBOFLOW_API_KEY = "yxVUJt7Trbkn6neMYEyB"
MODEL_ID = "dental-lesion-detection-rf-4vstt"
MODEL_VERSION = "1"
INFERENCE_URL = f"https://detect.roboflow.com/{MODEL_ID}/{MODEL_VERSION}?api_key={ROBOFLOW_API_KEY}"

# ----------------------
# App Setup
# ----------------------
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")
st.markdown("##### By Dr. Deep Sharma, MDS — Panbazar, Guwahati")

# ----------------------
# Inference Function
# ----------------------
def run_inference(image_bytes):
    try:
        response = requests.post(
            INFERENCE_URL,
            files={"file": image_bytes},
            data={"confidence": 0.4, "overlap": 0.3},
        )
        return response.json()
    except Exception as e:
        st.error(f"Inference error: {e}")
        return {"predictions": []}

# ----------------------
# PDF Generator
# ----------------------
def generate_pdf(name, age, sex, complaint, history, result_json, input_image, logo_image=None):
    pdf = FPDF()
    pdf.add_page()

    # Logo
    if logo_image:
        try:
            logo_path = "/tmp/logo.png"
            logo_image.save(logo_path)
            pdf.image(logo_path, x=10, y=8, w=33)
        except:
            pass

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="AffoDent Panbazar Dental Clinic", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt="House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align="C")
    pdf.cell(200, 7, txt="📞 WhatsApp: 9864272102 | 📧 deep0701@gmail.com", ln=True, align="C")
    pdf.ln(10)

    # Patient Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Patient Information", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 7, txt=f"Age: {age}    Sex: {sex}", ln=True)
    pdf.cell(200, 7, txt=f"Chief Complaint: {complaint}", ln=True)
    pdf.multi_cell(200, 7, txt=f"Medical History: {history}")
    pdf.cell(200, 7, txt=f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
    pdf.ln(5)

    # Findings
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Findings", ln=True)
    pdf.set_font("Arial", "", 11)
    if "predictions" in result_json and result_json["predictions"]:
        for pred in result_json["predictions"]:
            label = pred["class"]
            x = int(pred["x"])
            y = int(pred["y"])
            pdf.cell(200, 6, txt=f"- {label.title()} detected at approx. position ({x}, {y})", ln=True)
    else:
        pdf.cell(200, 6, txt="No visible dental issues detected by AI.", ln=True)

    # Image
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Uploaded Image", ln=True)
    img_path = "/tmp/input.jpg"
    input_image.save(img_path)
    pdf.image(img_path, x=30, w=150)

    # Disclaimer
    pdf.set_font("Arial", "I", 9)
    pdf.ln(10)
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment.")

    return pdf.output(dest="S").encode("latin1")

# ----------------------
# Form UI
# ----------------------
with st.form("patient_form"):
    st.subheader("📋 Patient Information")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Patient Name", max_chars=100)
        age = st.text_input("Age")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    with col2:
        chief_complaint = st.text_area("Chief Complaint")
        medical_history = st.text_area("Medical History")

    st.markdown("📷 **Upload Files**")
    uploaded_image = st.file_uploader("Intraoral Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    logo_file = st.file_uploader("Clinic Logo (optional)", type=["png", "jpg"])

    submit_btn = st.form_submit_button("🩺 Analyze and Generate Report")

# ----------------------
# Main Logic
# ----------------------
if submit_btn:
    if not name or not uploaded_image:
        st.error("Please fill all required fields and upload an image.")
    else:
        st.info("🔄 Processing image. Please wait...")
        img_bytes = uploaded_image.read()
        image = Image.open(io.BytesIO(img_bytes))
        result = run_inference(img_bytes)

        st.success("✅ AI Analysis Complete!")

        st.subheader("🖼️ Uploaded Image")
        st.image(image, caption="Uploaded Intraoral Image", use_column_width=True)

        st.subheader("🔍 AI Detected Issues")
        if "predictions" in result and result["predictions"]:
            for pred in result["predictions"]:
                st.markdown(f"- **{pred['class'].title()}** at approx. position ({pred['x']}, {pred['y']})")
        else:
            st.markdown("✅ No dental issues detected by AI.")

        # PDF Section
        st.subheader("📄 Download Report")
        try:
            logo = Image.open(logo_file) if logo_file else None
        except Exception:
            st.warning("⚠️ Logo file could not be processed. Proceeding without logo.")
            logo = None

        try:
            pdf_bytes = generate_pdf(name, age, sex, chief_complaint, medical_history, result, image, logo)
            st.download_button("📥 Download PDF Report", pdf_bytes, file_name=f"{name}_AffoDent_Report.pdf")
        except Exception as e:
            st.error(f"❌ Error generating PDF: {e}")
