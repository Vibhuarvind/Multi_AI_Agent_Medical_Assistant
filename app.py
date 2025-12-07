"""Multi-Agent Medical Assistant Streamlit UI"""

import json
from datetime import datetime
import streamlit as st

from Agents.coordinator import Orchestrator
from Utils.logger import get_logger
from Utils.lookups import get_sku_to_drug_name_map, get_pharmacy_id_to_name_map

logger = get_logger(__name__)


def humanize_slot(slot_str: str) -> str:
    """Convert ISO 8601 timestamp to human-readable format."""
    try:
        dt = datetime.fromisoformat(slot_str)
        # Format: Dec 06, 09:00 AM (friendly format, no timezone clutter)
        return dt.strftime("%b %d, %I:%M %p").strip()
    except ValueError:
        return slot_str



st.set_page_config(
    page_title="Healthcare Assistant",
    page_icon="🏥",
    layout="wide"
)

st.markdown("### 🩺 Healthcare Assistant")

# Safety disclaimer
st.warning("⚠️ **This is an educational demo, NOT medical advice. Always consult a healthcare professional for medical concerns.**")


coordinator = Orchestrator()
sku_to_name = get_sku_to_drug_name_map()
pharmacy_id_to_name = get_pharmacy_id_to_name_map()

with st.sidebar:
    st.markdown("#### Patient Information")
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=100, value=30)
    phone = st.text_input("Phone Number")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    allergies = st.text_input(
        "Known Allergies (Optional)",
        placeholder="e.g., penicillin, aspirin"
    )

    st.markdown("#### Symptoms & Reports")
    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="e.g., fever, cough, headache"
    )
    uploaded_pdf = st.file_uploader("Medical Report (PDF)", type=["pdf"])
    uploaded_image = st.file_uploader(
        "X-Ray or Scan Image",
        type=["png", "jpg", "jpeg"]
    )

    st.caption("🔒 All information is kept confidential and anonymous.")
    st.info(
        "⚠️ For emergencies, call your local emergency services immediately."
    )

if st.button("Get Recommendations", type="primary"):
    if not name or not phone:
        st.error("Name and phone are required.")
        st.stop()
    if not (symptoms or uploaded_pdf or uploaded_image):
        st.error("Provide at least one clinical input.")
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
        logger.info("Final coordinator payload:\n%s", json.dumps(final_result, indent=2))
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    st.success("✅ Analysis Complete")
    st.info(final_result["disclaimer"])

    ingestion_output = final_result["ingestion_output"]
    diagnosis = final_result["diagnosis"]
    therapy_result = final_result["therapy_plan"]
    pharmacy_result = final_result["pharmacy_match"]

    # Two main views: Customer summary vs. System observability
    tab_customer, tab_observability = st.tabs(
        ["👤 Customer Summary", "🔍 System Observability"]
    )

    # ---------------- Customer-facing view ----------------
    with tab_customer:
        # Compact metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Condition", diagnosis["condition"].replace("_", " ").title())
        with col2:
            st.metric("Severity", diagnosis["severity"].title())
        with col3:
            if final_result["doctor_escalation_needed"]:
                st.metric("Action", "⚠️ See Doctor", delta="Urgent")
            else:
                st.metric("Action", "✓ Self Care")

        # Recommended Medicines
        st.markdown("#### 💊 Recommended Medicines")
        if therapy_result["otc_options"]:
            for option in therapy_result["otc_options"]:
                drug_name = sku_to_name.get(option['sku'], option['sku'])
                warnings_text = (
                    f" ⚠️ {', '.join(option['warnings'])}"
                    if option['warnings'] else ""
                )
                st.write(
                    f"• **{drug_name}** — Take {option['dose']}, "
                    f"{option['freq']}{warnings_text}"
                )
        else:
            st.write("No over-the-counter medicines recommended at this time.")

        # Safety Alerts
        if therapy_result["red_flags"]:
            st.markdown("#### ⚠️ Important Safety Information")
            for flag in therapy_result["red_flags"]:
                st.warning(flag)

        # Pharmacy Delivery
        st.markdown("#### 🏥 Pharmacy & Delivery")
        if "pharmacy_id" in pharmacy_result:
            pharmacy_name = pharmacy_id_to_name.get(
                pharmacy_result['pharmacy_id'],
                pharmacy_result['pharmacy_id']
            )
            st.write(f"**Pharmacy:** {pharmacy_name}")
            st.write(f"**Estimated Delivery:** {pharmacy_result['eta_min']} minutes")
            st.write(f"**Delivery Fee:** ₹{pharmacy_result['delivery_fee']}")
        else:
            st.write(
                pharmacy_result.get(
                    "message", "No pharmacy available for delivery."
                )
            )

        # Doctor Consultations (only if escalation needed)
        if final_result["doctor_escalation_needed"] and final_result["escalation_suggestions"]:
            st.markdown("#### 👨‍⚕️ Available Doctors for Consultation")
            for doc in final_result["escalation_suggestions"]:
                with st.expander(f"{doc['doctor']} — {doc['specialty']}"):
                    st.write(f"**Specialty:** {doc['specialty']}")
                    st.write("**Available Slots:**")
                    for slot in doc.get("tele_slots", []):
                        st.write(f"  • {humanize_slot(slot)}")
                    st.caption(f"Reason: {doc['reason']}")

    # ---------------- System observability view ----------------
    with tab_observability:
        st.markdown("### 🔍 System Observability (Event Log)")

        # Human-readable pipeline timeline
        timeline_labels = {
            "ingestion_completed": "Ingestion completed (inputs validated & saved)",
            "imaging_completed": "Imaging completed (X-ray analyzed)",
            "imaging_skipped": "Imaging skipped (no X-ray provided)",
            "therapy_completed": "Therapy planning completed",
            "pharmacy_match_completed": "Pharmacy matching completed",
        }

        with st.expander("📌 Pipeline Timeline", expanded=True):
            for step in final_result.get("timeline", []):
                st.write(f"• {timeline_labels.get(step, step)}")

        # Detailed agent outputs (for observability / debugging)
        st.markdown("#### 🧪 Agent Outputs & Debug JSON")
        agent_tab_ing, agent_tab_img, agent_tab_ther, agent_tab_pharm, agent_tab_full = st.tabs(
            ["Ingestion", "Imaging", "Therapy", "Pharmacy", "Full Coordinator"]
        )

        with agent_tab_ing:
            st.caption("Ingestion Agent Output")
            st.json(ingestion_output)

        with agent_tab_img:
            st.caption("Imaging Agent Output")
            st.json(diagnosis)

        with agent_tab_ther:
            st.caption("Therapy Agent Output")
            st.json(therapy_result)

        with agent_tab_pharm:
            st.caption("Pharmacy Match Output")
            st.json(pharmacy_result)

        with agent_tab_full:
            st.caption("Full Coordinator Payload")
            st.json(final_result)