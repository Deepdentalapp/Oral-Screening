import io
from fpdf import FPDF
import streamlit as st

# After you've built your FPDF report
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Example content (replace with your real report)
pdf.cell(200, 10, txt="AffoDent Oral Screening Report", ln=True, align='C')
pdf.cell(200, 10, txt=f"Patient Name: {patient_name}", ln=True)
pdf.cell(200, 10, txt=f"Age: {patient_age}    Sex: {patient_sex}", ln=True)
pdf.multi_cell(0, 10, txt=f"Chief Complaint: {chief_complaint}")
pdf.multi_cell(0, 10, txt=f"Medical History: {medical_history}")
pdf.ln(10)
pdf.multi_cell(0, 10, txt=f"AI Findings:\n{summary_text}")
pdf.ln(10)
pdf.set_font("Arial", size=10)
pdf.multi_cell(0, 10, txt="Disclaimer: This is an AI-generated preliminary report. Please consult a licensed dentist for clinical evaluation.")

# Output to memory buffer
pdf_buffer = io.BytesIO()
pdf.output(pdf_buffer)
pdf_buffer.seek(0)

# Display download button
st.download_button(
    label="Download Dental Report PDF",
    data=pdf_buffer,
    file_name="dental_report.pdf",
    mime="application/pdf"
)
        
