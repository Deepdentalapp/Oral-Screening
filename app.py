import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from fpdf import FPDF

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
st.title("🦷 AffoDent Oral Screening App")
st.caption("AI-based simulated dental diagnosis with annotated report.")

uploaded_file = st.file_uploader("Upload an intraoral image", type=["jpg", "jpeg", "png"])

def simulate_diagnosis(image):
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    findings = []

    # Simulated detections
    # Carious tooth - Tooth 16
    draw.ellipse((100, 100, 140, 140), outline="red", width=3)
    draw.text((100, 145), "Tooth 16", fill="white", font=font)
    findings.append(("Tooth 16", "Carious", "Restore with composite or GIC"))

    # Broken tooth - Tooth 21
    draw.rectangle((200, 200, 240, 240), outline="blue", width=3)
    draw.text((200, 245), "Tooth 21", fill="white", font=font)
    findings.append(("Tooth 21", "Broken", "Crown or extraction"))

    # Missing tooth - Tooth 11
    draw.line((300, 300, 340, 340), fill="black", width=4)
    draw.line((340, 300, 300, 340), fill="black", width=4)
    draw.text((300, 345), "Tooth 11", fill="white", font=font)
    findings.append(("Tooth 11", "Missing", "Implant or bridge"))

    # Oral ulcer
    draw.ellipse((400, 100, 440, 140), outline="red", width=3)
    draw.text((400, 145), "Ulcer", fill="white", font=font)
    findings.append(("Area near Tooth 13", "Oral Ulcer", "Consult for biopsy if persistent"))

    # Oral lesion
    draw.ellipse((100, 300, 140, 340), outline="green", width=3)
    draw.text((100, 345), "Lesion", fill="white", font=font)
    findings.append(("Area near Tooth 34", "Oral Lesion", "Requires clinical evaluation"))

    return image, findings

def generate_pdf_report(image, findings):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Oral Screening Report", ln=True, align="C")

    # Clinic info
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, 
        "Clinic: AffoDent\n"
        "Address: House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001\n"
        "Doctor: Dr. Deep Sharma, MDS\n"
        "WhatsApp: https://wa.me/919864272102"
    )

    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Diagnosis Summary", ln=True)

    for tooth, issue, treatment in findings:
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"{tooth}: {issue} → Treatment: {treatment}", ln=True)

    # Save annotated image
    annotated_path = os.path.join(UPLOAD_DIR, "annotated.jpg")
    image.save(annotated_path)

    # Insert image
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Annotated Image", ln=True)
    pdf.image(annotated_path, w=160)

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

    # Save PDF
    pdf_path = os.path.join(UPLOAD_DIR, "report.pdf")
    pdf.output(pdf_path)
    return pdf_path

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_column_width=True)

    annotated_image, findings = simulate_diagnosis(image)
    st.image(annotated_image, caption="Annotated Image", use_column_width=True)

    if st.button("Generate Report"):
        report_path = generate_pdf_report(annotated_image, findings)
        with open(report_path, "rb") as f:
            st.download_button("📄 Download Report PDF", f, file_name="AffoDent_Report.pdf")
