import streamlit as st
from PIL import Image
from fpdf import FPDF
import os

# Setup
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Input: Patient name
patient_name = st.text_input("Enter Patient Name")

st.markdown("### Upload at least 6 oral photographs (palate, tongue, lips, etc)")
st.info("Upload JPG/PNG images. File size should be less than 2 MB each.")

uploaded_images = []
for i in range(1, 9):  # Allow up to 8 images
    file = st.file_uploader(f"Upload Oral Photograph {i}", type=["jpg", "jpeg", "png"], key=f"img_{i}")
    if file is not None:
        try:
            image = Image.open(file).convert("RGB")
            label = f"Image {i}"
            img_path = os.path.join(UPLOAD_DIR, f"{label.replace(' ', '_')}.jpg")
            image.save(img_path)
            uploaded_images.append((label, img_path))
            st.image(image, caption=label, use_column_width=True)
        except Exception as e:
            st.error(f"Could not upload {label}: {e}")

# Function to generate PDF
def generate_pdf(patient_name, results):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

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

    # Diagnosis Summary (Simulated)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)

    diagnosis_data = [
        ("Tooth 16", "Caries", "Restore with composite or GIC"),
        ("Tooth 21", "Broken", "Crown or extraction"),
        ("Tooth 11", "Missing", "Implant or bridge"),
        ("Palate", "Oral Ulcer", "Topical gel + biopsy if persistent"),
        ("Lower left region", "Oral Lesion", "Needs clinical evaluation")
    ]
    pdf.set_font("Arial", "", 12)
    for tooth, issue, plan in diagnosis_data:
        pdf.cell(0, 10, f"{tooth}: {issue} - Treatment: {plan}", ln=True)

    # Add uploaded photos
    for label, img_path in results:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, label, ln=True)
        try:
            pdf.image(img_path, w=180)
        except RuntimeError:
            pdf.cell(0, 10, f"Could not load image: {label}", ln=True)

    # Legend (No emojis)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Legend:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        "Red Area: Oral Ulcer\n"
        "Green Area: Oral Lesion\n"
        "Blue: Broken Tooth\n"
        "X mark: Missing Tooth\n"
        "Tooth Number: For reference"
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

# Generate report
if len(uploaded_images) >= 6:
    st.success("Sufficient images uploaded.")
    if st.button("Generate Report"):
        pdf_path = generate_pdf(patient_name, uploaded_images)
        with open(pdf_path, "rb") as f:
            st.download_button("Download AffoDent Report", f, file_name="AffoDent_Oral_Report.pdf")
else:
    st.warning("Please upload at least 6 oral cavity photos to proceed.")
