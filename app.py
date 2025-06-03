import streamlit as st
import requests
from PIL import Image, ImageDraw
from datetime import datetime
from fpdf import FPDF
import io

# ----------------------
# Configuration
# ----------------------
st.set_page_config(page_title="AffoDent Oral Screening App")

ROBOFLOW_API_KEY = "yxVUJt7Trbkn6neMYEyB"
ROBOFLOW_MODEL_ID = "yolov5-obj-ddt-czai4/1"
ROBOFLOW_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}?api_key={ROBOFLOW_API_KEY}"

# ----------------------
# Helper: Tooth Number Simulation
# ----------------------
def simulate_tooth_number(x, y, img_width, img_height):
    if y < img_height / 2:
        # Maxillary
        if x < img_width / 3:
            return "Tooth #18–14"
        elif x < 2 * img_width / 3:
            return "Tooth #13–23"
        else:
            return "Tooth #24–28"
    else:
        # Mandibular
        if x < img_width / 3:
            return "Tooth #38–34"
        elif x < 2 * img_width / 3:
            return "Tooth #33–43"
        else:
            return "Tooth #44–48"

# ----------------------
# AI Inference
# ----------------------
def run_inference(image_bytes):
    response = requests.post(
        ROBOFLOW_URL,
        files={"file": image_bytes},
        data={"confidence": 0.4, "overlap": 0.3},
    )
    return response.json()

# ----------------------
# PDF Generator
# ----------------------
def generate_pdf(name, age, sex, complaint, history, result_json, input_image):
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
    pdf.cell(200, 10, txt="Findings", ln=True)
    pdf.set_font("Arial", "", 11)
    if "predictions" in result_json and result_json["predictions"]:
        for pred in result_json["predictions"]:
            label = pred["class"]
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
    pdf.multi_cell(200, 5, txt="Disclaimer: This is an AI-assisted screening report. It is not a substitute for a clinical diagnosis. Please consult a qualified dental professional for confirmation and treatment.")

    return pdf.output(dest="S").encode("latin1")

# ----------------------
# App UI
# ----------------------
st.title("AffoDent Oral Screening App")
st.markdown("#### By Dr. Deep Sharma, MDS - Panbazar, Guwahati")

with st.form("patient_form"):
    st.subheader("Patient Information")
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    chief_complaint = st.text_area("Chief Complaint")
    medical_history = st.text_area("Medical History")

    uploaded_image = st.file_uploader("Upload Intraoral Image", type=["jpg", "jpeg", "png"])
    submit_btn = st.form_submit_button("Analyze and Generate Report")

# ----------------------
# Run When Submitted
# ----------------------
if submit_btn:
    if not name or not uploaded_image:
        st.error("Please fill all required fields and upload an image.")
    else:
        with st.spinner("Analyzing image with AI..."):
            image_bytes = uploaded_image.read()
            result = run_inference(image_bytes)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Annotate image
            draw = ImageDraw.Draw(image)
            if "predictions" in result:
                for pred in result["predictions"]:
                    x = int(pred["x"])
                    y = int(pred["y"])
                    w = int(pred["width"])
                    h = int(pred["height"])
                    label = pred["class"]
                    draw.rectangle([(x - w//2, y - h//2), (x + w//2, y + h//2)], outline="red", width=2)
                    draw.text((x - w//2, y - h//2 - 10), label, fill="red")

        st.success("Analysis Complete!")

        if result["predictions"]:
            st.subheader("Detected Findings")
            for pred in result["predictions"]:
                x = int(pred["x"])
                y = int(pred["y"])
                label = pred["class"]
                tooth = simulate_tooth_number(x, y, image.width, image.height)
                st.markdown(f"- **{label.title()}** at {tooth}")
        else:
            st.markdown("No visible issues detected.")

        # PDF Download
        st.subheader("Download Report")
        pdf_bytes = generate_pdf(name, age, sex, chief_complaint, medical_history, result, image)
        st.download_button("Download PDF Report", pdf_bytes, file_name=f"{name}_AffoDent_Report.pdf")
