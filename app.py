import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Patient info input
patient_name = st.text_input("Enter Patient Name")

# File uploader
st.subheader("Upload at least 6 images of the oral cavity (including palate, tongue, lips, teeth)")
uploaded_images = st.file_uploader(
    "Upload Oral Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

# Annotate simulated findings
def annotate_image(img, marks):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    for x, y, label, color in marks:
        draw.ellipse((x, y, x+40, y+40), outline=color, width=3)
        draw.text((x, y+45), label, fill="white", font=font)
    return img

# Generate PDF Report
def generate_pdf(patient_name, image_infos):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        f"Patient Name: {patient_name or 'N/A'}\n"
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102\n"
    )

    pdf.ln(3)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    findings = [
        ("Tooth 16", "Carious", "Restore with composite or GIC"),
        ("Tooth 21", "Broken", "Crown or extraction"),
        ("Tooth 11", "Missing", "Implant or bridge"),
        ("Area near Tooth 13", "Oral Ulcer", "Consult if persists"),
        ("Area near Tooth 34", "Oral Lesion", "Clinical evaluation required")
    ]
    for f in findings:
        pdf.cell(0, 10, f"{f[0]}: {f[1]} → Treatment: {f[2]}", ln=True)

    # Add image pages
    for idx, (label, path) in enumerate(image_infos):
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Image {idx+1}: {label}", ln=True)
        pdf.image(path, w=180)

    # Legend
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Legend:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8,
        "🔴 Red Circle: Oral Ulcer\n"
        "🟢 Green Circle: Oral Lesion\n"
        "🔵 Blue Box: Broken Tooth\n"
        "❌ X: Missing Tooth\n"
        "🦷 Label: Tooth Number"
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

if uploaded_images and len(uploaded_images) >= 6:
    st.success(f"{len(uploaded_images)} image(s) uploaded. Click below to generate report.")
    if st.button("Generate Report"):
        annotated_paths = []
        for i, uploaded_file in enumerate(uploaded_images):
            label = uploaded_file.name
            img = Image.open(uploaded_file).convert("RGB")

            # Simulated annotations on first image
            if i == 0:
                marks = [
                    (100, 100, "Tooth 16", "red"),
                    (200, 150, "Tooth 21", "blue"),
                    (300, 120, "Tooth 11", "black"),
                    (400, 160, "Ulcer", "red"),
                    (120, 300, "Lesion", "green")
                ]
                img = annotate_image(img, marks)

            img_path = os.path.join(UPLOAD_DIR, f"img_{i+1}.jpg")
            img.save(img_path)
            annotated_paths.append((label, img_path))
            st.image(img, caption=label, use_column_width=True)

        report_path = generate_pdf(patient_name, annotated_paths)
        with open(report_path, "rb") as f:
            st.download_button("📄 Download AffoDent Report", f, file_name="AffoDent_Report.pdf")
else:
    st.info("Please upload at least 6 images of the oral cavity to proceed.")
