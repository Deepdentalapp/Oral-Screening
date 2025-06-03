import streamlit as st
from fpdf import FPDF
from datetime import datetime
import io

st.set_page_config(page_title="AffoDent Oral Screening App", page_icon="🦷")

st.title("AffoDent Oral Screening App")

# Patient info input with required validation
name = st.text_input("Patient Name *")
age = st.number_input("Age *", min_value=0, max_value=120, step=1)
sex = st.selectbox("Sex *", options=["Male", "Female", "Other"])
complaint = st.text_area("Chief Complaint *")
history = st.text_area("Medical History")

uploaded_image = st.file_uploader("Upload Oral Image *", type=["jpg", "jpeg", "png"])

if st.button("Generate PDF Report"):
    # Validation
    if not name.strip():
        st.error("Please enter the patient's name.")
    elif age <= 0:
        st.error("Please enter a valid age.")
    elif not complaint.strip():
        st.error("Please enter the chief complaint.")
    elif uploaded_image is None:
        st.error("Please upload an oral image.")
    else:
        st.info("Generating PDF report...")
        try:
            # Simulated AI result JSON for demo purposes
            # In practice, replace with your actual model prediction result
            result_json = {
                "predictions": [
                    {"class": "carious tooth", "x": 120, "y": 80, "tooth_number": 16},
                    {"class": "missing tooth", "x": 300, "y": 150, "tooth_number": 24},
                    {"class": "oral lesion", "x": 200, "y": 200},
                    {"class": "stain", "x": 250, "y": 120},
                    {"class": "calculus", "x": 280, "y": 100},
                    {"class": "oral ulcer", "x": 350, "y": 180}
                ]
            }

            # Read image bytes
            input_image = uploaded_image.read()

            # PDF generation
            pdf = FPDF()
            pdf.add_page()

            # Clinic Header
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "AffoDent Panbazar Dental Clinic", ln=True, align="C")
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 7, "House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align="C")
            pdf.cell(0, 7, "WhatsApp: 9864272102 | Email: deep0701@gmail.com", ln=True, align="C")
            pdf.ln(10)

            # Patient Info
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Patient Information", ln=True)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 7, f"Name: {name}", ln=True)
            pdf.cell(0, 7, f"Age: {age}    Sex: {sex}", ln=True)
            pdf.cell(0, 7, f"Chief Complaint: {complaint}", ln=True)
            pdf.multi_cell(0, 7, f"Medical History: {history}")
            pdf.cell(0, 7, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
            pdf.ln(5)

            # Findings Section
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Findings", ln=True)
            pdf.set_font("Arial", "", 11)
            if result_json.get("predictions"):
                for pred in result_json["predictions"]:
                    label = pred["class"].title()
                    x = pred.get("x")
                    y = pred.get("y")
                    tooth_num = pred.get("tooth_number")
                    if tooth_num:
                        pdf.cell(0, 6, txt=f"- {label} (Tooth #{tooth_num}) detected at approx. position ({x}, {y})", ln=True)
                    else:
                        pdf.cell(0, 6, txt=f"- {label} detected at approx. position ({x}, {y})", ln=True)
            else:
                pdf.cell(0, 6, "No visible dental issues detected by AI.", ln=True)

            pdf.ln(5)

            # Add uploaded image to PDF (fit width 150)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Uploaded Image", ln=True)

            # Save image temporarily
            from PIL import Image
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(input_image)
                tmp_image_path = tmp_file.name

            pdf.image(tmp_image_path, x=30, w=150)

            pdf.ln(10)

            # Disclaimer
            pdf.set_font("Arial", "I", 9)
            pdf.multi_cell(0, 5, "Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment.")

            # Output PDF as bytes
            pdf_bytes = pdf.output(dest="S").encode("latin1")

            st.success("PDF report generated successfully!")

            # Provide PDF download button
            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=f"AffoDent_Report_{name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )

        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            st.error("Ensure you do not include emojis or special characters in text inputs.")
