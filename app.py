def generate_pdf(name, age, sex, complaint, history, result_json, input_image):
    from fpdf import FPDF
    from datetime import datetime

    def estimate_tooth_number(x, y):
        # Simplified estimation; adjust based on actual clinical orientation
        if y < 150:
            if x < 100: return "11"
            elif x < 200: return "12"
            elif x < 300: return "13"
            else: return "14"
        else:
            if x < 100: return "31"
            elif x < 200: return "32"
            elif x < 300: return "33"
            else: return "34"

    def get_treatment(label):
        label = label.lower()
        if "caries" in label:
            return "Restoration / RCT"
        elif "calculus" in label:
            return "Scaling"
        elif "stain" in label:
            return "Polishing"
        elif "ulcer" in label:
            return "Topical medication"
        elif "lesion" in label:
            return "Biopsy advised"
        elif "missing" in label:
            return "Prosthetic replacement"
        else:
            return "Clinical evaluation"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, txt="AffoDent Panbazar Dental Clinic", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt="House no 4, College Hostel Road, Panbazar, Guwahati, Assam 781001", ln=True, align="C")
    pdf.cell(200, 7, txt="WhatsApp: 9864272102 | Email: deep0701@gmail.com", ln=True, align="C")
    pdf.ln(10)

    # Patient Info
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Patient Information", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(200, 7, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 7, txt=f"Age: {age}    Sex: {sex}", ln=True)
    pdf.cell(200, 7, txt=f"Chief Complaint: {complaint}", ln=True)
    pdf.multi_cell(200, 7, txt=f"Medical History: {history}")
    pdf.cell(200, 7, txt=f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True)
    pdf.ln(5)

    # Findings Summary Table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Findings Summary", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 8, txt="Tooth No.", border=1)
    pdf.cell(70, 8, txt="Diagnosis", border=1)
    pdf.cell(70, 8, txt="Treatment Plan", border=1)
    pdf.ln()

    pdf.set_font("Arial", "", 11)
    if "predictions" in result_json and result_json["predictions"]:
        for pred in result_json["predictions"]:
            label = pred["class"].replace("_", " ").title()
            x, y = int(pred["x"]), int(pred["y"])
            tooth = estimate_tooth_number(x, y)
            treatment = get_treatment(label)
            pdf.cell(50, 8, txt=tooth, border=1)
            pdf.cell(70, 8, txt=label, border=1)
            pdf.cell(70, 8, txt=treatment, border=1)
            pdf.ln()
    else:
        pdf.cell(190, 8, txt="No visible dental issues detected.", border=1)

    # Uploaded Image
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Uploaded Image", ln=True)
    img_path = "/tmp/input.jpg"
    input_image.save(img_path)
    pdf.image(img_path, x=30, w=150)

    # Disclaimer
    pdf.set_font("Arial", "I", 9)
    pdf.ln(10)
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. Not a substitute for clinical judgment. Please consult a dental professional for final diagnosis and treatment.")

    return pdf.output(dest="S").encode("latin1")
        
