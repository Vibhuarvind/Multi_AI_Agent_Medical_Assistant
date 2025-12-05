# app.py
import streamlit as st

st.set_page_config(page_title="Customer Intake Form", page_icon="💊")

st.title("🩺 Multi AI Agent Health Assistant")

# --- Customer Info ---
st.header("Personal Details")
name = st.text_input("Name")
age = st.number_input("Age", min_value=0, max_value=120)
phone = st.text_input("Phone Number")
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

# --- Inputs: Symptoms / PDF / Image ---
st.header("Input Your Symptoms or Upload Report/Image")
symptoms = st.text_area("Describe your symptoms (e.g., cold, fever, headache)", placeholder="Type your symptoms here...")
uploaded_pdf = st.file_uploader("Upload PDF (Optional)", type=["pdf"])
uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg"])

# --- Process Button ---
if st.button("Process"):
    # Check at least one input is provided
    if not symptoms and not uploaded_pdf and not uploaded_image:
        st.error("Please provide at least one input: Symptoms, PDF, or Image!")
    else:
        st.success("Processing your input...")
        st.write("### Personal Details")
        st.write(f"**Name:** {name}")
        st.write(f"**Age:** {age}")
        st.write(f"**Phone:** {phone}")
        st.write(f"**Gender:** {gender}")

        st.write("### Input Provided")
        if symptoms:
            st.write(f"**Symptoms:** {symptoms}")
        if uploaded_pdf:
            st.write(f"**Uploaded PDF:** {uploaded_pdf.name}")
        if uploaded_image:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
