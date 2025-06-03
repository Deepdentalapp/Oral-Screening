import streamlit as st
import requests
import os
import json
from PIL import Image
from fpdf import FPDF
import datetime

# Roboflow model config
API_KEY = "yxVUJt7Trbkn6neMYEyB"
MODEL_URL = "https://detect.roboflow.com/dental-lesion-detection-rf-4vstt/1"

# Classes to recognize
CLASSES = [
    "Caries", "Missing Tooth", "Broken Crown", "Root Stamp",
    "Ulcer", "Lesion", "Stain", "Calculus"
]

# PDF Report Class
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AffoDent Panbazar Dental Clinic", ln=True, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, "House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align="C")
        self.cell(0, 10, "Contact: 9864272102 | Email: deep0701@gmail.com", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.multi_cell(0, 10, "Disclaimer: This is an AI-generated screening report. Final diagnosis must be confirmed by a dental professional.", 0, 'C')

# Analyze image with Roboflow API
def analyze_image(image_path):
    try:
        with open(image_path, "rb") as f:
            response = requests.post(
                f"{MODEL_URL}?api_key={API_KEY}",
                files={"file": f},
                data={"confidence": 0.4}
            )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": str(e)}

# Generate PDF
def generate_pdf(patient_info, findings, annotated_images):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, f"Patient Name: {patient_info['name']}", ln=True)
    pdf.cell(0, 10, f"Age: {patient_info['age']}    Sex: {patient_info['sex']}", ln=True)
    pdf.cell(0, 10, f"Chief Complaint: {patient_info['complaint']}", ln=True)
    pdf.cell(0, 10, f"Medical History: {patient_info['history']}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%d-%m-%Y')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "AI Findings Summary", ln=True)
    pdf.set_font("Arial", "", 12)

    if findings:
        for item in findings:
            pdf.cell(0, 10, f"{item['label']} - Tooth No: {item['tooth']}", ln=True)
    else:
        pdf.cell(0, 10, "No significant findings detected.", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Marked Images", ln=True)

    for img_path in annotated_images:
        pdf.image(img_path, w=150)
        pdf.ln(10)

    output_path = "dental_report.pdf"
    pdf.output(output_path)
    return output_path

# Streamlit UI
st.title("AffoDent Oral Screening App")
st.markdown("Please upload at least 2 dental photographs (up to 6).")

uploaded_files = st.file_uploader("Upload dental images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if len(uploaded_files) < 2:
    st.warning("Please upload at least 2 images to proceed.")

else:
    st.subheader("Enter Patient Information")
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    complaint = st.text_area("Chief Complaint")
    history = st.text_area("Medical History")

    if st.button("Analyze"):
        if not name or not age:
            st.warning("Please fill in patient details.")
        else:
            patient_info = {
                "name": name,
                "age": age,
                "sex": sex,
                "complaint": complaint,
                "history": history
            }

            all_findings = []
            annotated_paths = []

            for file in uploaded_files:
                img = Image.open(file).convert("RGB")
                img_path = f"temp_{file.name}"
                img.save(img_path)

                result = analyze_image(img_path)
                if "error" in result:
                    st.error(result["error"])
                    continue

                detections = result.get("predictions", [])
                annotated = img.copy()
                draw = ImageDraw.Draw(annotated)

                for det in detections:
                    label = det["class"]
                    if label not in CLASSES:
                        continue
                    x, y, w, h = det["x"], det["y"], det["width"], det["height"]
                    left = x - w / 2
                    top = y - h / 2
                    right = x + w / 2
                    bottom = y + h / 2
                    draw.rectangle([left, top, right, bottom], outline="red", width=2)
                    draw.text((left, top - 10), label, fill="red")

                    # Simulated tooth number based on x-position
                    tooth_number = int((x / img.width) * 32) + 1
                    all_findings.append({"label": label, "tooth": tooth_number})

                out_path = f"annotated_{file.name}"
                annotated.save(out_path)
                annotated_paths.append(out_path)

            report_path = generate_pdf(patient_info, all_findings, annotated_paths)
            with open(report_path, "rb") as f:
                st.download_button("Download Report", f, file_name="Dental_Report.pdf", mime="application/pdf")
        
