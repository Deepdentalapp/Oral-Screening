import streamlit as st
import requests
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import io

# ----------------------
# Configuration
# ----------------------
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")

ROBOFLOW_API_KEY = "yxVUJt7Trbkn6neMYEyB"
MODEL_ID = "dental-lesion-detection-rf-4vstt"
MODEL_VERSION = "1"
INFERENCE_URL = f"https://detect.roboflow.com/{MODEL_ID}/{MODEL_VERSION}?api_key={ROBOFLOW_API_KEY}"

# ----------------------
# Title
# ----------------------
st.title("AffoDent Oral Screening App")
st.markdown("**By Dr. Deep Sharma, MDS – Panbazar, Guwahati**")

# ----------------------
# Form Input
# ----------------------
with st.form("patient_form"):
    st.subheader("Patient Information")
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    chief_complaint = st.text_area("Chief Complaint")
    medical_history = st.text_area("Medical History")

    uploaded_image = st.file_uploader("Upload Intraoral Image (JPG/PNG)", type=["jpg", "jpeg", "png"])
    logo_file = st.file_uploader("Upload Clinic Logo (optional)", type=["jpg", "png"])

    submit_btn = st.form_submit_button("Analyze and Generate Report")

# ----------------------
# Inference Function
# ----------------------
def run_inference(image_bytes):
    response = requests.post(
        INFERENCE_URL,
        files={"file": image_bytes},
        data={"confidence": 0.4, "overlap": 0.3},
    )
    return response.json()

# ----------------------
# PDF Generator
# ----------------------
def generate_pdf(name, age, sex, complaint, history, result_json, input_image, logo_image=None):
    pdf = FPDF()
    pdf.add_page()

    # Logo
    if logo_image:
        logo_path = "/tmp/logo.png"
        logo_image.save(logo_path)
        pdf.image(logo_path, x=10, y=8, w=33)

    # Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="AffoDent Panbazar Dental Clinic", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt="House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align="C")
    pdf.cell(200, 7, txt="WhatsApp: 9864272102 | Email: deep0701@gmail.com", ln=True, align="C")
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
            pdf.cell(200, 6, txt=f"- {label.title()} at approx. position ({x}, {y})", ln=True)
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
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional.")

    return pdf.output(dest="S").encode("latin1")

# ----------------------
# Main Execution
# ----------------------
if submit_btn:
    if not name or not uploaded_image:
        st.error("Please fill all required fields and upload an image.")
    else:
        with st.spinner("Processing image..."):
            img_bytes = uploaded_image.read()
            result = run_inference(img_bytes)
            image = Image.open(io.BytesIO(img_bytes))

        st.success("Analysis Complete!")

        # Show predictions
        if "predictions" in result and result["predictions"]:
            st.subheader("Detected Issues")
            for pred in result["predictions"]:
                st.markdown(f"- **{pred['class'].title()}** at position ({pred['x']}, {pred['y']})")
        else:
            st.markdown("No issues detected.")

        # Generate PDF
        st.subheader("Download Report")
        logo = Image.open(logo_file) if logo_file else None
        try:
            pdf_bytes = generate_pdf(name, age, sex, chief_complaint, medical_history, result, image, logo)
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"{name.replace(' ', '_')}_AffoDent_Report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
