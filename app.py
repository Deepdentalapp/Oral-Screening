import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Input: Patient name
patient_name = st.text_input("Enter Patient Name")

# Image inputs
image_labels = [
    "1. Front tooth view (Frontal)",
    "2. Right side (Right lateral)",
    "3. Left side (Left lateral)",
    "4. Upper tooth (Occlusal)",
    "5. Lower tooth (Occlusal)",
    "6. Tongue",
    "7. Oral cavity including Palate"
]

uploaded_images = []
for label in image_labels:
    uploaded_images.append(st.file_uploader(f"Upload image - {label}", type=["jpg", "jpeg", "png"], key=label))

def annotate_image(image, label_texts):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for item in label_texts:
        x, y, label, color = item
        draw.ellipse((x, y, x+40, y+40), outline=color, width=3)
        draw.text((x, y+45), label, fill="white", font=font)
    return image

def generate_pdf(patient_name, results):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")

    # Clinic info
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, 
        f"Patient Name: {patient_name or 'N/A'}\n"
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102"
    )

    # Diagnosis summary (simulated)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)

    diagnosis_data = [
        ("Tooth 16", "Carious", "Restore with composite or GIC"),
        ("Tooth 21", "Broken", "Crown or extraction"),
        ("Tooth 11", "Missing", "Implant or bridge"),
        ("Area near Tooth 13", "Oral Ulcer", "Consult for biopsy if persistent"),
        ("Area near Tooth 34", "Oral Lesion", "Requires clinical evaluation")
    ]
    pdf.set_font("Arial", "", 12)
    for tooth, issue, plan in diagnosis_data:
        pdf.cell(0, 10, f"{tooth}: {issue} → Treatment: {plan}", ln=True)

    # Annotated images
    for idx, (label, image_path) in enumerate(results):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, label, ln=True)
        pdf.image(image_path, w=180)

    # Legend
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Legend:", ln=True)
    pdf.set_font("Arial", "", 12)
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

if all(uploaded_images):
    st.success("All images uploaded. Ready to generate report.")
    if st.button("Generate Report"):
        image_outputs = []
        for i, uploaded_file in enumerate(uploaded_images):
            image = Image.open(uploaded_file).convert("RGB")
            label = image_labels[i]

            # Simulated markups only on first image
            if i == 0:
                markups = [
                    (100, 100, "Tooth 16", "red"),
                    (200, 200, "Tooth 21", "blue"),
                    (300, 300, "Tooth 11", "black"),
                    (400, 100, "Ulcer", "red"),
                    (100, 300, "Lesion", "green")
                ]
                annotated = annotate_image(image, markups)
            else:
                annotated = image

            img_path = os.path.join(UPLOAD_DIR, f"image_{i+1}.jpg")
            annotated.save(img_path)
            image_outputs.append((label, img_path))
            st.image(annotated, caption=label, use_column_width=True)

        report_path = generate_pdf(patient_name, image_outputs)
        with open(report_path, "rb") as f:
            st.download_button("📄 Download Full Report", f, file_name="AffoDent_Report.pdf")
else:
    st.warning("Please upload all 7 required images to proceed.")
