# File: app.py

import streamlit as st
from PIL import Image, ImageDraw
import os
import uuid
import shutil
from fpdf import FPDF

# Must be first Streamlit command
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")

# Constants
CLINIC_NAME = "AffoDent"
APP_NAME = "AffoDent Oral Screening App"
DOCTOR_NAME = "Dr. Deep Sharma MDS"
ADDRESS = "House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001"
WHATSAPP_LINK = "https://wa.me/919864272102"
DISCLAIMER = "Disclaimer: This is an AI-generated report. Please consult your family oral and dental surgeon for a clinical diagnosis."

# Folder for uploads
UPLOAD_DIR = "uploads"
if os.path.exists(UPLOAD_DIR):
    shutil.rmtree(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Dummy analysis: simulate annotation
def analyze_image(image: Image.Image):
    draw = ImageDraw.Draw(image)
    w, h = image.size

    # Simulated annotations
    draw.rectangle([(w*0.1, h*0.1), (w*0.2, h*0.2)], outline="blue", width=4)     # Stain
    draw.rectangle([(w*0.3, h*0.3), (w*0.4, h*0.4)], outline="orange", width=4)   # Calculus
    draw.ellipse([(w*0.6, h*0.1), (w*0.65, h*0.15)], outline="red", width=4)      # Ulcer
    draw.ellipse([(w*0.7, h*0.2), (w*0.75, h*0.25)], outline="green", width=4)    # Lesion
    return image

# Treatment plans
def get_treatment_findings():
    return [
        ("Stains", "Scaling and polishing"),
        ("Calculus", "Professional oral prophylaxis"),
        ("Carious tooth", "Restoration or root canal treatment"),
        ("Broken tooth", "Restoration or crown"),
        ("Root stamp", "Extraction if necessary"),
        ("Missing tooth", "Dental bridge or implant"),
        ("Oral ulcer", "Topical medication, monitor healing"),
        ("Oral lesion", "Referral for specialist evaluation")
    ]

# PDF generator
def generate_pdf(patient_name, images):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"{CLINIC_NAME} - Oral Screening Report", ln=True, align='C')

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, f"Doctor: {DOCTOR_NAME}", ln=True)
    pdf.cell(200, 10, f"Address: {ADDRESS}", ln=True)
    pdf.cell(200, 10, f"WhatsApp: {WHATSAPP_LINK}", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Findings and Suggested Treatments", ln=True)

    pdf.set_font("Arial", '', 12)
    for finding, plan in get_treatment_findings():
        pdf.cell(200, 8, f"{finding}: {plan}", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Marked Photographs", ln=True)

    for img_path in images:
        pdf.image(img_path, w=170)
        pdf.ln(5)

    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 8, DISCLAIMER)

    pdf_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex}_report.pdf")
    pdf.output(pdf_path)
    return pdf_path

# Streamlit UI
st.title(APP_NAME)
st.markdown(f"**Clinic:** {CLINIC_NAME}")
st.markdown(f"**Doctor:** {DOCTOR_NAME}")
st.markdown(f"**Address:** {ADDRESS}")
st.markdown(f"[📱 Contact on WhatsApp]({WHATSAPP_LINK})")

st.markdown("### Step 1: Enter Patient Name")
patient_name = st.text_input("Patient Name")

st.markdown("### Step 2: Upload Dental Images")
uploaded_files = st.file_uploader("Upload JPG/PNG images (e.g., upper arch, lateral, etc.)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files and patient_name:
    st.markdown("### Step 3: Annotated Images")
    saved_paths = []
    for file in uploaded_files:
        image = Image.open(file).convert("RGB")
        annotated = analyze_image(image.copy())
        unique_name = f"{uuid.uuid4().hex}.jpg"
        save_path = os.path.join(UPLOAD_DIR, unique_name)
        annotated.save(save_path)
        saved_paths.append(save_path)
        st.image(annotated, caption=f"Marked: {file.name}", use_column_width=True)

    if st.button("Generate PDF Report"):
        pdf_path = generate_pdf(patient_name, saved_paths)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download Report", f, file_name="AffoDent_Oral_Screening_Report.pdf", mime="application/pdf")
else:
    st.info("Please enter the patient's name and upload at least one image to continue.")
