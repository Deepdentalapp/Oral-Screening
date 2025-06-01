import streamlit as st
from PIL import Image
from fpdf import FPDF
import os

# Page setup
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Patient Name
patient_name = st.text_input("Enter Patient Name")

# Upload images one by one
image_labels = [
    "1. Frontal View (Front Teeth)",
    "2. Right Lateral View",
    "3. Left Lateral View",
    "4. Upper Occlusal View",
    "5. Lower Occlusal View",
    "6. Tongue",
    "7. Oral Cavity Including Palate"
]

uploaded_images = []
for label in image_labels:
    uploaded = st.file_uploader(f"Upload: {label} (Max 200MB)", type=["jpg", "jpeg", "png"], key=label)
    if uploaded:
        uploaded_images.append((label, uploaded))

# Generate PDF
def generate_pdf(patient_name, image_infos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")

    # Clinic Info
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        f"Patient Name: {patient_name or 'N/A'}\n"
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102"
    )

    # Diagnosis Summary
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    diagnosis_data = [
        ("Tooth 16", "Carious", "Restore with composite or GIC"),
        ("Tooth 21", "Broken", "Crown or extraction"),
        ("Tooth 11", "Missing", "Implant or bridge"),
        ("Area near Tooth 13", "Oral Ulcer", "Consult if persists"),
        ("Area near Tooth 34", "Oral Lesion", "Clinical evaluation required")
    ]
    for tooth, issue, plan in diagnosis_data:
        pdf.cell(0, 10, f"{tooth}: {issue} → Treatment: {plan}", ln=True)

    # Add images
    for idx, (label, file) in enumerate(image_infos):
        image = Image.open(file).convert("RGB")
        img_path = os.path.join(UPLOAD_DIR, f"img_{idx+1}.jpg")
        image.save(img_path)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, label, ln=True)
        pdf.image(img_path, w=180)

    # Legend
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Legend:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8,
        "🔴 Red Circle: Oral Ulcer\n"
        "🟢 Green Circle: Oral Lesion\n"
        "🔵 Blue Box: Broken Tooth\n"
        "❌ X: Missing Tooth"
    )

    # Disclaimer
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8,
        "Disclaimer: This is an AI-generated simulated report. "
        "Please consult your family oral and dental surgeon for confirmation and treatment."
    )

    output_path = os.path.join(UPLOAD_DIR, "affodent_report.pdf")
    pdf.output(output_path)
    return output_path

# Button to generate
if len(uploaded_images) >= 6:
    st.success("Minimum 6 images uploaded. Ready to generate report.")
    if st.button("Generate Report"):
        pdf_path = generate_pdf(patient_name, uploaded_images)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download AffoDent Report", f, file_name="AffoDent_Report.pdf")
else:
    st.warning("Please upload at least 6 images to proceed.")
