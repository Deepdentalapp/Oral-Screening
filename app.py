import streamlit as st
import requests
from PIL import Image
import io
import base64
from fpdf import FPDF
from datetime import datetime

# Roboflow model info
API_KEY = "yxVUJt7Trbkn6neMYEyB"
MODEL_URL = "https://detect.roboflow.com/dental-lesion-detection-rf-4vstt/1"

st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")

# Title
st.title("AffoDent Oral Screening App")

# Patient info
st.subheader("Patient Information")
name = st.text_input("Name")
age = st.text_input("Age")
sex = st.selectbox("Sex", ["Male", "Female", "Other"])
complaint = st.text_area("Chief Complaint")
history = st.text_area("Medical History")

# Upload images
st.subheader("Upload Dental Photographs")
st.markdown("Upload at least 2 (ideally 6):")
uploaded_images = st.file_uploader("Upload images (JPG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Minimum 2 images required
if uploaded_images and len(uploaded_images) >= 2:
    if st.button("Analyze"):
        results = []
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="AffoDent Panbazar Dental Clinic", ln=True, align='C')
        pdf.cell(200, 10, txt="House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align='C')
        pdf.cell(200, 10, txt="WhatsApp: 9864272102 | Email: deep0701@gmail.com", ln=True, align='C')
        pdf.ln(10)

        # Patient summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Patient Summary", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"Name: {name}\nAge: {age}\nSex: {sex}\nChief Complaint: {complaint}\nMedical History: {history}\nDate: {datetime.now().strftime('%Y-%m-%d')}")
        pdf.ln(5)

        all_findings = []

        for i, file in enumerate(uploaded_images):
            image = Image.open(file).convert("RGB")
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Send to Roboflow
            response = requests.post(
                MODEL_URL,
                params={"api_key": API_KEY},
                files={"file": buffered},
                data={"confidence": 40, "overlap": 30}
            )

            detections = response.json().get("predictions", [])
            findings = []
            for pred in detections:
                cls = pred['class']
                x = int(pred['x'])
                y = int(pred['y'])
                findings.append(f"Detected: {cls} at approx tooth region near x={x}, y={y}")
                all_findings.append(cls)

            st.image(image, caption=f"Processed Image {i+1}")
            st.write("Findings:")
            for f in findings:
                st.write("-", f)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt=f"Image {i+1} Findings", ln=True)
            pdf.set_font("Arial", size=12)
            for f in findings:
                pdf.cell(200, 10, txt=f"- {f}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Summary of Findings:", ln=True)
        pdf.set_font("Arial", size=12)
        for f in set(all_findings):
            pdf.cell(200, 10, txt=f"- {f}", ln=True)

        pdf.ln(10)
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 10, "Disclaimer: This is an AI-generated preliminary screening report. Clinical confirmation by a dentist is advised.")

        pdf_output = f"/mnt/data/{name.replace(' ', '_')}_oral_report.pdf"
        pdf.output(pdf_output)

        st.success("Analysis complete.")
        with open(pdf_output, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{name}_oral_report.pdf">📄 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)

else:
    st.warning("Please upload at least 2 images.")
        
