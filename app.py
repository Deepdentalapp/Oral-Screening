import streamlit as st
import requests
from PIL import Image, ImageDraw
from datetime import datetime
from fpdf import FPDF
import io

# ----------------------
# Configuration
# ----------------------
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")
ROBOFLOW_API_KEY = "yxVUJt7Trbkn6neMYEyB"
ROBOFLOW_MODEL_ID = "yolov5-obj-ddt-czai4/1"
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"

# ----------------------
# Treatment Suggestions
# ----------------------
TREATMENTS = {
    "caries": "Dental filling or root canal treatment",
    "broken": "Restoration or extraction",
    "missing": "Dental bridge, implant, or denture",
    "stain": "Scaling and polishing",
    "calculus": "Professional dental cleaning (scaling)",
    "ulcer": "Topical medication, monitor for healing",
    "lesion": "Referral for biopsy or specialist opinion",
}

# ----------------------
# Tooth Number Simulator
# ----------------------
def simulate_tooth_number(x, y, img_width, img_height):
    thirds_x = img_width // 3
    if y < img_height // 2:
        return 11 if x < thirds_x else 21 if x < 2 * thirds_x else 22
    else:
        return 31 if x < thirds_x else 41 if x < 2 * thirds_x else 42

# ----------------------
# AI Inference
# ----------------------
def run_inference(image_bytes):
    response = requests.post(
        ROBOFLOW_URL,
        files={"file": image_bytes},
        data={"confidence": 0.3, "overlap": 0.3},
    )
    return response.json()

# ----------------------
# Annotate Image
# ----------------------
def draw_boxes(image, predictions):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    for pred in predictions:
        label = pred["class"]
        x = pred["x"]
        y = pred["y"]
        w = pred["width"]
        h = pred["height"]
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        color = "red" if label == "ulcer" else "green" if label == "lesion" else "blue"
        draw.rectangle([left, top, right, bottom], outline=color, width=2)
        tooth_num = simulate_tooth_number(x, y, width, height)
        draw.text((left, top - 10), f"{label} (T{tooth_num})", fill=color)
    return image

# ----------------------
# PDF Report Generator
# ----------------------
def generate_pdf(name, age, sex, complaint, history, result_json, image):
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

    # Findings Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Findings", ln=True)
    pdf.set_font("Arial", "", 11)
    findings_summary = []
    if "predictions" in result_json and result_json["predictions"]:
        for pred in result_json["predictions"]:
            label = pred["class"]
            x = int(pred["x"])
            y = int(pred["y"])
            tooth_num = simulate_tooth_number(x, y, image.width, image.height)
            treatment = TREATMENTS.get(label, "Clinical evaluation advised")
            findings_summary.append((tooth_num, label, treatment))
            pdf.cell(200, 7, txt=f"- Tooth {tooth_num}: {label.title()} → {treatment}", ln=True)
    else:
        pdf.cell(200, 6, txt="No visible dental issues detected by AI.", ln=True)

    # Image
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Screening Image", ln=True)
    img_path = "/tmp/marked.png"
    image.save(img_path)
    pdf.image(img_path, x=30, w=150)

    # Disclaimer
    pdf.set_font("Arial", "I", 9)
    pdf.ln(10)
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment.")

    return pdf.output(dest="S").encode("latin1")

# ----------------------
# Streamlit UI
# ----------------------
st.title("AffoDent Oral Screening App")
st.markdown("##### By Dr. Deep Sharma, MDS - Panbazar, Guwahati")

with st.form("form"):
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    chief_complaint = st.text_area("Chief Complaint")
    medical_history = st.text_area("Medical History")
    uploaded_image = st.file_uploader("Upload Intraoral Photo (JPG/PNG)", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("Analyze & Generate Report")

if submit:
    if not name or not uploaded_image:
        st.error("Please enter patient name and upload an image.")
    else:
        with st.spinner("Analyzing..."):
            image_bytes = uploaded_image.read()
            result = run_inference(image_bytes)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            marked_image = draw_boxes(image.copy(), result["predictions"])

        st.success("Analysis complete!")

        # Show annotated image
        st.image(marked_image, caption="Annotated Findings", use_column_width=True)

        # Show detected findings
        st.subheader("Detected Findings")
        if result["predictions"]:
            for pred in result["predictions"]:
                label = pred["class"]
                x, y = int(pred["x"]), int(pred["y"])
                tooth = simulate_tooth_number(x, y, image.width, image.height)
                st.write(f"• Tooth {tooth}: {label.title()} → {TREATMENTS.get(label, 'Refer to dentist')}")
        else:
            st.write("No visible issues detected.")

        # Generate and download PDF
        pdf_bytes = generate_pdf(name, age, sex, chief_complaint, medical_history, result, marked_image)
        st.download_button("Download PDF Report", pdf_bytes, file_name=f"{name}_AffoDent_Report.pdf")
        
