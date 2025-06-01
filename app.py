import streamlit as st
from PIL import Image
from fpdf import FPDF
import os

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Patient name input
patient_name = st.text_input("Enter Patient Name")

# Upload images (at least 6)
uploaded_images = []
for i in range(1, 9):
    file = st.file_uploader(f"Upload Oral Photograph {i} (Less than 200 MB)", type=["jpg", "jpeg", "png"], key=f"image_{i}")
    if file:
        uploaded_images.append((f"Image {i}", file))

# Simulated diagnosis data
diagnosis_data = [
    ("Tooth 16", "Carious", "Restore with composite or GIC"),
    ("Tooth 21", "Broken", "Crown or extraction"),
    ("Tooth 11", "Missing", "Implant or bridge"),
    ("Near Tooth 13", "Oral Ulcer", "Consult if persists"),
    ("Near Tooth 34", "Oral Lesion", "Clinical evaluation required"),
    ("Tooth 36", "Stains", "Scaling and polishing"),
    ("Tooth 41", "Calculus", "Oral prophylaxis")
]

# Function to generate PDF
def generate_pdf(patient_name, saved_images):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")

    # Clinic and patient info
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        f"Patient Name: {patient_name or 'N/A'}\n"
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102"
    )

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    for tooth, issue, plan in diagnosis_data:
        pdf.cell(0, 10, f"{tooth}: {issue} -> Treatment: {plan}", ln=True)

    # Add photos
    for label, path in saved_images:
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, label, ln=True)
        pdf.image(path, w=180)

    # Legend
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Legend:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8,
        "Red Circle: Oral Ulcer\n"
        "Green Circle: Oral Lesion\n"
        "Blue Box: Broken Tooth\n"
        "X: Missing Tooth\n"
        "Tooth #: Affected Tooth Number"
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

# When ready
if len(uploaded_images) >= 6:
    st.success("Sufficient images uploaded. Ready to generate report.")
    if st.button("Generate Report"):
        saved_paths = []
        for label, file in uploaded_images:
            image = Image.open(file).convert("RGB")
            img_path = os.path.join(UPLOAD_DIR, f"{label.replace(' ', '_')}.jpg")
            image.save(img_path)
            saved_paths.append((label, img_path))
            st.image(image, caption=label, use_column_width=True)

        pdf_path = generate_pdf(patient_name, saved_paths)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download Full Report", f, file_name="AffoDent_Report.pdf")
else:
    st.warning("Please upload at least 6 oral photographs including palate, tongue, and lips.")
