import unicodedata

# Clean text for PDF (remove unsupported characters like emojis)
def clean_text(text):
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf(name, age, sex, complaint, history, result_json, input_image):
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt=clean_text("AffoDent Panbazar Dental Clinic"), ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt=clean_text("House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001"), ln=True, align="C")
    pdf.cell(200, 7, txt=clean_text("WhatsApp: 9864272102 | Email: deep0701@gmail.com"), ln=True, align="C")
    pdf.ln(10)

    # Patient Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Patient Information", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt=clean_text(f"Name: {name}"), ln=True)
    pdf.cell(200, 7, txt=clean_text(f"Age: {age}    Sex: {sex}"), ln=True)
    pdf.cell(200, 7, txt=clean_text(f"Chief Complaint: {complaint}"), ln=True)
    pdf.multi_cell(200, 7, txt=clean_text(f"Medical History: {history}"))
    pdf.cell(200, 7, txt=f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
    pdf.ln(5)

    # Findings
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Findings", ln=True)
    pdf.set_font("Arial", "", 11)
    if "predictions" in result_json and result_json["predictions"]:
        for pred in result_json["predictions"]:
            label = clean_text(pred["class"])
            x = int(pred["x"])
            y = int(pred["y"])
            img_w, img_h = input_image.size
            tooth = simulate_tooth_number(x, y, img_w, img_h)
            pdf.cell(200, 6, txt=f"- {label.title()} at {tooth} (approx. x={x}, y={y})", ln=True)
    else:
        pdf.cell(200, 6, txt="No visible dental issues detected by AI.", ln=True)

    # Annotated Image
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Marked Image", ln=True)
    annotated_path = "/tmp/marked.jpg"
    input_image.save(annotated_path)
    pdf.image(annotated_path, x=30, w=150)

    # Disclaimer
    pdf.set_font("Arial", "I", 9)
    pdf.ln(10)
    pdf.multi_cell(200, 5, txt=clean_text("Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment."))

    return pdf.output(dest="S").encode("latin1")
