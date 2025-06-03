import streamlit as st
import requests
from PIL import Image, ImageDraw
from datetime import datetime
from fpdf import FPDF
import io
import base64

# ----------------------
# Configuration
# ----------------------
st.set_page_config(page_title="AffoDent Oral Screening App")

ROBOFLOW_API_KEY = "yxVUJt7Trbkn6neMYEyB"
ROBOFLOW_MODEL_ID = "yolov5-obj-ddt-czai4/1"
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"

TOOTH_ZONES = [
    (0, 80, "Tooth #11-13"),
    (81, 160, "Tooth #14-16"),
    (161, 240, "Tooth #21-23"),
    (241, 320, "Tooth #24-26"),
    (321, 400, "Tooth #31-33"),
    (401, 480, "Tooth #34-36"),
    (481, 560, "Tooth #41-43"),
    (561, 640, "Tooth #44-46")
]

# ----------------------
# Inference
# ----------------------
def run_inference(image_bytes):
    response = requests.post(
        ROBOFLOW_URL,
        files={"file": image_bytes},
        data={"confidence": 0.4, "overlap": 0.3}
    )
    return response.json()

def annotate_image(image, predictions):
    draw = ImageDraw.Draw(image)
    for pred in predictions:
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        left = x - w / 2
        top = y - h / 2
        right = x + w / 2
        bottom = y + h / 2
        label = pred["class"]
        draw.rectangle([left, top, right, bottom], outline="red", width=2)
        draw.text((left, top - 10), label, fill="red")
    return image

def get_tooth_number(x_pos):
    for left, right, tooth_label in TOOTH_ZONES:
        if left <= x_pos <= right:
            return tooth_label
    return "Unknown Tooth"

# ----------------------
# PDF Generator
# ----------------------
def generate_pdf(name, age, sex, complaint, history, predictions, annotated_img):
    pdf = FPDF()
    pdf.add_page()

    # Header
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

    # Findings
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="AI Findings", ln=True)
    pdf.set_font("Arial", "", 11)
    if predictions:
        for pred in predictions:
            label = pred["class"]
            x = int(pred["x"])
            y = int(pred["y"])
            tooth = get_tooth_number(x)
            pdf.cell(200, 6, txt=f"- {label.title()} at {tooth} (X: {x}, Y: {y})", ln=True)
    else:
        pdf.cell(200, 6, txt="No visible dental issues detected by AI.", ln=True)

    # Annotated Image
    annotated_path = "/tmp/annotated.jpg"
    annotated_img.save(annotated_path)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Annotated Image", ln=True)
    pdf.image(annotated_path, x=30, w=150)

    # Disclaimer
    pdf.set_font("Arial", "I", 9)
    pdf.ln(10)
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment.")

    return pdf.output(dest="S").encode("latin1")

# ----------------------
# Streamlit UI
# ----------------------
st.title("AffoDent Oral Screening App")
st.markdown("#### By Dr. Deep Sharma, MDS - Panbazar, Guwahati")

with st.form("screening_form"):
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    chief_complaint = st.text_area("Chief Complaint")
    medical_history = st.text_area("Medical History")
    uploaded_image = st.file_uploader("Upload Intraoral Photograph", type=["jpg", "jpeg", "png"])
    submit = st.form_submit_button("Analyze and Generate Report")

if submit:
    if not name or not uploaded_image:
        st.error("Please fill all required fields and upload a photo.")
    else:
        with st.spinner("Processing..."):
            img_bytes = uploaded_image.read()
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            result = run_inference(img_bytes)
            predictions = result.get("predictions", [])
            annotated_img = annotate_image(image.copy(), predictions)
            pdf_bytes = generate_pdf(name, age, sex, chief_complaint, medical_history, predictions, annotated_img)

        st.success("Analysis Complete!")

        if predictions:
            st.subheader("Findings:")
            for pred in predictions:
                tooth = get_tooth_number(pred["x"])
                st.markdown(f"- **{pred['class'].title()}** at {tooth}")
        else:
            st.markdown("No dental issues detected by AI.")

        st.subheader("Download Report:")
        st.download_button("Download PDF Report", data=pdf_bytes, file_name=f"{name}_AffoDent_Report.pdf", mime="application/pdf")
        
