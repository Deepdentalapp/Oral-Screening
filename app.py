import streamlit as st
import requests
import io
from PIL import Image
from fpdf import FPDF
import datetime

# Roboflow API configuration
API_KEY = "yxVUJt7Trbkn6neMYEyB"
MODEL_URL = "https://detect.roboflow.com/dental-lesion-detection-rf-4vstt/1"

# App title
st.set_page_config(page_title="AffoDent Oral Screening", layout="centered")
st.title("AffoDent Oral Screening App")
st.markdown("House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001  \n📞 +91 9864272102  \n📧 deep0701@gmail.com")

# Patient details
st.subheader("Patient Details")
patient_name = st.text_input("Patient Name")
patient_age = st.text_input("Age")
patient_sex = st.selectbox("Sex", ["Male", "Female", "Other"])
chief_complaint = st.text_area("Chief Complaint")
medical_history = st.text_area("Medical History")

st.subheader("Upload Minimum 2, Maximum 6 Dental Images")
uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Generate AI Screening Report") and len(uploaded_images) >= 2:
    findings = []

    st.subheader("AI Analysis Results")

    for image_file in uploaded_images:
        image = Image.open(image_file).convert("RGB")

        # Send image to Roboflow
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        upload_url = f"{MODEL_URL}?api_key={API_KEY}"
response = requests.post(
    upload_url,
    files={"file": ("image.jpg", img_bytes, "image/jpeg")},
)

        if response.status_code == 200:
            result = response.json()
            image_findings = []

            for prediction in result["predictions"]:
                label = prediction["class"]
                x = int(prediction["x"])
                y = int(prediction["y"])
                tooth_info = f"Tooth (approx @ {x},{y})"
                image_findings.append(f"{label.capitalize()} detected at {tooth_info}")

            if image_findings:
                findings.extend(image_findings)
                st.success(f"Findings in {image_file.name}:")
                st.write(image_findings)
            else:
                st.warning(f"No findings detected in {image_file.name}.")
        else:
            st.error(f"Error processing {image_file.name}: {response.status_code}")

    # Generate PDF Report
    st.subheader("Download AI Report")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AffoDent Oral Screening Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {patient_age}    Sex: {patient_sex}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Chief Complaint: {chief_complaint}")
    pdf.multi_cell(0, 10, txt=f"Medical History: {medical_history}")
    pdf.ln(10)

    if findings:
        pdf.multi_cell(0, 10, txt="AI Findings:")
        for line in findings:
            pdf.multi_cell(0, 10, txt=f"- {line}")
    else:
        pdf.multi_cell(0, 10, txt="No visible lesions, ulcers, calculus, or caries detected.")

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt="Disclaimer: This AI-generated report is for screening purposes only. Please consult a licensed dentist for confirmation.")

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    st.download_button(
        label="Download Report PDF",
        data=pdf_buffer,
        file_name="AffoDent_Dental_Report.pdf",
        mime="application/pdf"
    )
else:
    st.info("Please upload at least 2 dental images to proceed.")
        
