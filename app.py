from fpdf import FPDF
from io import BytesIO

def safe_latin1(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_pdf(name, age, sex, chief_complaint, medical_history, result, marked_image):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="AffoDent Oral Screening Report", ln=True, align='C')

    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    # Patient Info
    pdf.cell(200, 10, txt="Patient Information", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Name: {safe_latin1(name)}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {safe_latin1(age)}", ln=True)
    pdf.cell(200, 10, txt=f"Sex: {safe_latin1(sex)}", ln=True)
    pdf.cell(200, 10, txt=f"Chief Complaint: {safe_latin1(chief_complaint)}", ln=True)
    pdf.multi_cell(0, 10, txt=f"Medical History: {safe_latin1(medical_history)}")

    pdf.ln(5)

    # Results
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Findings:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=safe_latin1(result))

    pdf.ln(5)

    # Image
    if marked_image:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            marked_image.save(tmpfile.name)
            pdf.image(tmpfile.name, x=10, y=None, w=180)

    # Disclaimer
    pdf.ln(10)
    pdf.set_font("Arial", size=8)
    pdf.multi_cell(0, 8, txt=safe_latin1("This is an AI-generated screening report. Please consult a licensed dentist for clinical diagnosis and treatment."))

    # Return as bytes
    return pdf.output(dest="S").encode("latin1", "replace")
        
