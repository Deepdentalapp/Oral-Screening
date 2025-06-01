import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Input
patient_name = st.text_input("Enter Patient Name")

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

# Mark simulated diagnosis
def annotate_image(img, annotations):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    for x, y, label, color in annotations:
        draw.ellipse((x, y, x+40, y+40), outline=color, width=3)
        draw.text((x, y+45), label, fill="white", font=font)
    return img

# PDF Generator
def generate_pdf(name, annotated_data):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8,
        f"Patient Name: {name or 'N/A'}\n"
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102\n"
    )

    # Diagnosis
    pdf.ln(3)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    findings = [
        ("Tooth 16", "Carious", "Restore with composite or GIC"),
        ("Tooth 21", "Broken", "Crown or extraction"),
        ("Tooth 11", "Missing", "Implant or bridge"),
        ("Area near Tooth 13", "Oral Ulcer", "Consult for biopsy if persistent"),
        ("Area near Tooth 34", "Oral Lesion", "Requires clinical evaluation")
    ]
    for f in findings:
        pdf.cell(0, 10, f"{f[0]}: {f[1]} → Treatment: {f[2]}", ln=True)

    # Images
    for label, path in annotated_data:
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

    out_path = os.path.join(UPLOAD_DIR, "affodent_report.pdf")
    pdf.output(out_path)
    return out_path

if all(uploaded_images):
    st.success("All 7 images uploaded.")
    if st.button("Generate Report"):
        results = []
        for i, uploaded_file in enumerate(uploaded_images):
            img = Image.open(uploaded_file).convert("RGB")
            label = image_labels[i]

            # Only annotate first image for now
            if i == 0:
                annotations = [
                    (100, 100, "Tooth 16", "red"),
                    (200, 150, "Tooth 21", "blue"),
                    (300, 120, "Tooth 11", "black"),
                    (400, 160, "Ulcer", "red"),
                    (120, 300, "Lesion", "green")
                ]
                img = annotate_image(img, annotations)

            path = os.path.join(UPLOAD_DIR, f"image_{i+1}.jpg")
            img.save(path)
            results.append((label, path))
            st.image(img, caption=label, use_column_width=True)

        pdf_path = generate_pdf(patient_name, results)
        with open(pdf_path, "rb") as f:
            st.download_button("📄 Download Full Report", f, file_name="AffoDent_Report.pdf")
else:
    st.warning("Please upload all 7 required images.")
