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


def humanize_timestamp(timestamp: str) -> str:
    try:
        normalized = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        return dt.strftime("%b %d, %I:%M:%S %p")
    except Exception:
        return timestamp

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
    pincode = st.text_input(
        "Pincode (Optional)",
        placeholder="e.g., 400053"
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
            pincode=pincode,
        )
        st.session_state["latest_result"] = final_result
        st.session_state["order_confirmation"] = None
        st.success("✅ Analysis Complete")
        st.info(final_result["disclaimer"])
        logger.info("Final coordinator payload:\n%s", json.dumps(final_result, indent=2))
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

result = st.session_state.get("latest_result")
if not result:
    st.info("Complete the form and click 'Get Recommendations' to start the workflow.")
else:
    ingestion_output = result["ingestion_output"]
    diagnosis = result["diagnosis"]
    therapy_result = result["therapy_plan"]
    pharmacy_result = result["pharmacy_match"]
    order_preview = result.get("order_preview")
    doctor_assessment = result.get("doctor_assessment")
    order_confirmation = st.session_state.get("order_confirmation")

    tab_customer, tab_observability = st.tabs(
        ["👤 Customer Summary", "🔍 System Observability"]
    )

    with tab_customer:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Condition", diagnosis["condition"].replace("_", " ").title())
        with col2:
            st.metric("Severity", diagnosis["severity"].title())
        with col3:
            if result["doctor_escalation_needed"]:
                st.metric("Action", "⚠️ See Doctor", delta="Urgent")
            else:
                st.metric("Action", "✓ Self Care")

        st.markdown("#### 💊 Recommended Medicines")
        if therapy_result["otc_options"]:
            for option in therapy_result["otc_options"]:
                drug_name = sku_to_name.get(option["sku"], option["sku"])
                warnings_text = (
                    f" ⚠️ {', '.join(option['warnings'])}"
                    if option["warnings"] else ""
                )
                st.write(
                    f"• **{drug_name}** — Take {option['dose']}, "
                    f"{option['freq']}{warnings_text}"
                )
        else:
            st.write("No over-the-counter medicines recommended at this time.")

        if therapy_result["red_flags"]:
            st.markdown("#### ⚠️ Important Safety Information")
            for flag in therapy_result["red_flags"]:
                st.warning(flag)

        st.markdown("#### 🏥 Pharmacy & Delivery")
        if "pharmacy_id" in pharmacy_result:
            pharmacy_name = pharmacy_id_to_name.get(
                pharmacy_result["pharmacy_id"],
                pharmacy_result["pharmacy_id"]
            )
            st.write(f"**Pharmacy:** {pharmacy_name}")
            st.write(f"**Estimated Delivery:** {pharmacy_result['eta_min']} minutes")
            st.write(f"**Delivery Fee:** ₹{pharmacy_result['delivery_fee']}")
            if order_preview:
                st.markdown("##### Order Preview")
                subtotal = order_preview.get("subtotal", 0)
                delivery_fee = order_preview.get("delivery_fee", 0)
                st.write(f"• Subtotal: ₹{subtotal:.2f}")
                st.write(f"• Delivery fee: ₹{delivery_fee:.2f}")
                st.write(f"• Estimated total: ₹{subtotal + delivery_fee:.2f}")
                if st.button("Place mock order", key="place_mock_order"):
                    st.session_state["order_confirmation"] = coordinator.finalize_order(order_preview)
                order_confirmation = st.session_state.get("order_confirmation")
                if order_confirmation:
                    st.markdown("#### 🧾 Order Confirmation")
                    conf = order_confirmation
                    conf_pharmacy_name = pharmacy_id_to_name.get(
                        conf.get("pharmacy_id", ""),
                        conf.get("pharmacy_id", ""),
                    )

                    st.write(f"**Order ID:** {conf.get('order_id', '-')}")
                    if conf.get("placed_at"):
                        st.write(f"**Placed at:** {humanize_timestamp(conf['placed_at'])}")
                    if conf_pharmacy_name:
                        st.write(f"**Pharmacy:** {conf_pharmacy_name}")

                    st.write(f"**Estimated Delivery:** {conf.get('eta_min', '?')} minutes")
                    st.write(f"**Delivery Fee:** ₹{conf.get('delivery_fee', 0):.2f}")
                    st.write(f"**Subtotal:** ₹{conf.get('subtotal', 0):.2f}")
                    st.write(f"**Total Paid:** ₹{conf.get('total_cost', 0):.2f}")

                    st.markdown("**Items:**")
                    for item in conf.get("items", []):
                        item_name = item.get("drug_name") or sku_to_name.get(
                            item.get("sku"),
                            item.get("sku"),
                        )
                        qty = item.get("qty", 0)
                        unit_price = float(item.get("unit_price", 0) or 0)
                        line_total = float(item.get("subtotal", 0) or 0)
                        st.write(
                            f"- {item_name} — {qty} × ₹{unit_price:.2f} = ₹{line_total:.2f}"
                        )
        else:
            st.write(
                pharmacy_result.get(
                    "message", "No pharmacy available for delivery."
                )
            )

        if result["doctor_escalation_needed"] and result["escalation_suggestions"]:
            st.markdown("#### 👨‍⚕️ Available Doctors for Consultation")
            for doc in result["escalation_suggestions"]:
                with st.expander(f"{doc['doctor']} — {doc['specialty']}"):
                    st.write(f"**Specialty:** {doc['specialty']}")
                    st.write("**Available Slots:**")
                    for slot in doc.get("tele_slots", []):
                        st.write(f"  • {humanize_slot(slot)}")
                    st.caption(f"Reason: {doc['reason']}")

    with tab_observability:
        st.markdown("### 🔍 System Observability (Event Log)")
        timeline_labels = {
            "ingestion_completed": "Ingestion completed (inputs validated & saved temporarily)",
            "imaging_completed": "Imaging completed (X-ray analyzed)",
            "imaging_skipped": "Imaging skipped (no X-ray provided)",
            "therapy_completed": "Therapy planning completed",
            "doctor_escalation_evaluated": "Doctor escalation evaluated",
            "pharmacy_match_completed": "Pharmacy matching completed",
            "order_preview_ready": "Order preview ready",
        }

        with st.expander("📌 Pipeline Timeline", expanded=True):
            for entry in result.get("timeline", []):
                label = timeline_labels.get(entry["step"], entry["step"])
                st.write(f"• {humanize_timestamp(entry['at'])} — {label}")

        st.markdown("#### 🧪 Agent Outputs & Debug JSON")
        agent_tab_ing, agent_tab_img, agent_tab_ther, agent_tab_pharm, agent_tab_doc, agent_tab_full, order_place = st.tabs(
            ["Ingestion", "Imaging", "Therapy", "Pharmacy", "Doctor Escalation", "Full Coordinator","Order Placement"]
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

        with agent_tab_doc:
            st.caption("Doctor Escalation Agent Output")
            if doctor_assessment:
                st.json(doctor_assessment)
            else:
                st.info("Doctor escalation assessment not available for this run.")

        with agent_tab_full:
            st.caption("Full Coordinator Payload")
            st.json(result)

        with order_place:
            st.caption("Mock Order Confirmation")
            if order_confirmation:
                st.json(order_confirmation)
            else:
                st.caption("No mock order has been placed in this session.")