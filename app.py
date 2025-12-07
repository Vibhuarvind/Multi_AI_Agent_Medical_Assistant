import streamlit as st
import logging
import json
from Agents.coordinator import Orchestrator
from Agents.ingestion import IngestionAgent

# Configure logging to display in terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

st.set_page_config(page_title="🩺 Multi AI Agent Health Assistant", page_icon="🩺")

st.title("🩺 Multi AI Agent Health Assistant")
coordinator = Orchestrator()
mask_agent = IngestionAgent()

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

    if not name:
        st.error("Name is required!")
        st.stop()

    if not phone:
        st.error("Phone number is required!")
        st.stop()

    if not (symptoms or uploaded_pdf or uploaded_image):
        st.error("Provide at least one: Symptoms, PDF, or Image!")
        st.stop()

    try:
        final_result = coordinator.run_flow(
            image_file=uploaded_image,
            name=name,
            phone=phone,
            age=age,
            notes=symptoms,
            pdf_file=uploaded_pdf,
            allergies=allergies,
        )

        logging.info("Final coordinator payload:\n" + json.dumps(final_result, indent=2))
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()

    st.success("Processing complete!")
    st.info(final_result["disclaimer"])

    ingestion_output = final_result["ingestion_output"]
    diagnosis = final_result["diagnosis"]
    therapy_result = final_result["therapy_plan"]
    pharmacy_result = final_result["pharmacy_match"]

    with st.expander("📋 Personal Details (Masked)", expanded=True):
        st.write(f"**Name:** {mask_agent.mask_name(name)}")
        st.write(f"**Phone:** {mask_agent.mask_phone(phone)}")
        st.write(f"**Age:** {age}")
        st.write(f"**Gender:** {gender}")
        if allergies:
            st.write(f"**Allergies:** {allergies}")

    with st.expander("📥 Input Provided", expanded=True):
        if symptoms:
            st.write(f"**Symptoms:** {symptoms}")
        if uploaded_pdf:
            st.write(f"**Uploaded PDF:** {uploaded_pdf.name}")
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

    with st.expander("🤖 Ingestion Agent Output (JSON)", expanded=False):
        st.json(ingestion_output)

    with st.expander("🔬 Imaging Agent Output (JSON)", expanded=False):
        st.json(diagnosis)

    with st.expander("💊 Therapy Agent Output (JSON)", expanded=False):
        st.json(therapy_result)

    with st.expander("🏥 Pharmacy Agent Output (JSON)", expanded=True):
        st.json(pharmacy_result)

    with st.expander("📜 Coordinator Timeline", expanded=False):
        st.write(final_result["timeline"])

    with st.expander("👨‍⚕️ Doctor Escalation Suggestions", expanded=False):
        st.write(f"Escalation needed: {final_result['doctor_escalation_needed']}")
        st.json(final_result["escalation_suggestions"])

