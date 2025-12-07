import streamlit as st
import logging
from Agents.ingestion import IngestionAgent
from Agents.imaging import ImagingAgent
from Agents.therapy import TherapyAgent
from Agents.pharmacy_match import PharmacyAgent

# Configure logging to display in terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to terminal/console
    ]
)

st.set_page_config(page_title="Multi AI Agent Health Assistant", page_icon="🩺")

st.title("🩺 Multi AI Agent Health Assistant")

# Customer Information
st.header("Personal Details")
name = st.text_input("Name")
age = st.number_input("Age", min_value=0, max_value=100)
phone = st.text_input("Phone Number")
gender = st.selectbox("Gender", ["Male", "Female", "Other"])
allergies = st.text_input("Any Known Allergies (Optional)", placeholder="e.g., penicillin, aspirin, ibuprofen")

# Inputs: Symptoms / PDF / Image 
st.header("Input Your Symptoms or Upload Report/Image")
symptoms = st.text_area("Describe your symptoms (e.g., cold, fever, headache)", placeholder="Type your symptoms here...")
uploaded_pdf = st.file_uploader("Upload PDF (Optional)", type=["pdf"])
uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"])

# Process Button
if st.button("Process"):

    # MANDATORY PERSONAL DETAILS 
    if not name:
        st.error("Name is required!")
        st.stop()

    if not phone:
        st.error("Phone number is required!")
        st.stop()

    # AT LEAST ONE CLINICAL INPUT
    if not (symptoms or uploaded_pdf or uploaded_image):
        st.error("Provide at least one: Symptoms, PDF, or Image!")
        st.stop()

    # RUN INGESTION AGENT
    agent = IngestionAgent()

    try:
        result = agent.process(
            image_file=uploaded_image,
            name=name,
            phone=phone,
            age=age,
            notes=symptoms,
            pdf_file=uploaded_pdf,
            allergies=allergies
        )
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()

    st.success("Processing complete!")

    # RUN IMAGING AGENT ONLY IF XRAY IS PROVIDED
    if result.get("xray_path"):
        imaging = ImagingAgent()
        imaging_result = imaging.analyze(result["xray_path"])
    else:
        imaging_result = {"message": "No X-ray provided to Imaging Agent"}


    # Therapy Agent
    therapy = TherapyAgent()
    therapy_result = therapy.recommend(
        notes=result["notes"],
        age=result["patient"]["age"],
        allergies=result["patient"]["allergies"],
        severity_hint=imaging_result.get("severity_hint","mild")
    )
    # st.json(therapy_result)

    # PHARMACY FOUND AGENT BASED ON OTC LIST FROM THERAPY AGENT
    pharmacy_match = PharmacyAgent()
    medicine_skus = [opt["sku"] for opt in therapy_result["otc_options"]]
    pharmacy_result = pharmacy_match.find_matches(medicine_skus)


    # PERSONAL DETAILS (MASKED) 
    with st.expander("📋 Personal Details (Masked)", expanded=True):
        st.write(f"**Name:** {agent.mask_name(name)}")
        st.write(f"**Phone:** {agent.mask_phone(phone)}")
        st.write(f"**Age:** {age}")
        st.write(f"**Gender:** {gender}")
        if allergies:
            st.write(f"**Allergies:** {allergies}")

    # INPUT PROVIDED 
    with st.expander("📥 Input Provided", expanded=True):
        if symptoms:
            st.write(f"**Symptoms:** {symptoms}")
        if uploaded_pdf:
            st.write(f"**Uploaded PDF:** {uploaded_pdf.name}")
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    # INGESTION AGENT OUTPUT 
    with st.expander("🤖 Ingestion Agent Output (JSON)", expanded=False):
        st.json(result)

    # IMAGING AGENT OUTPUT 
    with st.expander("🔬 Imaging Agent Output (JSON)", expanded=False):
        st.json(imaging_result)

    with st.expander(" Therapy Agent Output (JSON)", expanded=False):
        st.json(therapy_result)
    
    with st.expander(" Pharmacy Agent Output (JSON)",expanded=True):
        st.json(pharmacy_result)