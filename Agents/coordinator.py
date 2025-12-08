"""Coordinator/Orchestrator agent that routes tasks and consolidates the final plan."""

from copy import deepcopy
from datetime import datetime
from uuid import uuid4

from Agents.ingestion import IngestionAgent
from Agents.imaging import ImagingAgent
from Agents.therapy import TherapyAgent
from Agents.pharmacy_match import PharmacyAgent
from Agents.doctor_escalation import DoctorEscalationAgent
from Utils.logger import get_logger
from Utils.data_loader import load_doctors
from Utils.lookups import get_coords_for_pincode
from Utils.constants import SEVERITY_MILD

logger = get_logger(__name__)

class Orchestrator:
    """Central orchestrator that coordinates all agents and consolidates the final plan."""

    DEFAULT_LAT = 19.12
    DEFAULT_LON = 72.84

    #initializing the agents
    def __init__(self):
        self.ingestion = IngestionAgent()
        self.imaging = ImagingAgent()
        self.therapy = TherapyAgent()
        self.pharmacy = PharmacyAgent()
        self.doctors = load_doctors()
        self.doctor_escalation = DoctorEscalationAgent(self.doctors)

    #function to get the timestamp
    def _timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"

    #function to add a timeline entry
    def _timeline_entry(self, step: str) -> dict:
        return {"step": step, "at": self._timestamp()}

    #function to combine the notes from the ingestion agent
    def _combine_notes(self, notes: str, pdf_text: str) -> str:
        return " ".join(filter(None, [notes, pdf_text])).strip()

    #function to build the order preview
    def _build_order_preview(self, pharmacy_match: dict) -> dict | None:
        if "pharmacy_id" not in pharmacy_match:
            return None

        items = []
        subtotal = 0.0
        for item in pharmacy_match.get("items", []):
            qty = item.get("qty", 0)
            price = float(item.get("price") or 0)
            line_total = qty * price
            subtotal += line_total
            items.append({
                "sku": item["sku"],
                "drug_name": item.get("drug_name"),
                "qty": qty,
                "unit_price": price,
                "subtotal": line_total,
            })

        return {
            "pharmacy_id": pharmacy_match["pharmacy_id"],
            "items": items,
            "eta_min": pharmacy_match.get("eta_min"),
            "delivery_fee": pharmacy_match.get("delivery_fee", 0),
            "subtotal": subtotal,
        }

    #function to finalize the order
    def finalize_order(self, order_preview: dict | None) -> dict | None:
        if not order_preview:
            return None
        order = deepcopy(order_preview)
        order["order_id"] = f"ORDER-{uuid4().hex[:6].upper()}"
        order["placed_at"] = datetime.utcnow().isoformat() + "Z"
        order["total_cost"] = round(
            order_preview["subtotal"] + order_preview.get("delivery_fee", 0), 2
        )
        return order

    #main function that orchestrates the flow of the pipeline
    def run_flow(
        self,
        image_file=None,
        name=None,
        phone=None,
        age=None,
        notes=None,
        allergies=None,
        pdf_file=None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        pincode: str | None = None,
    ):
        """
        Execute the master pipeline through all agents.

        Returns:
            Consolidated plan with ingestion, diagnosis, therapy, pharmacy,
            and escalation
        """

        coords = get_coords_for_pincode(pincode)
        if coords:
            user_lat, user_lon = coords
        if user_lat is None or user_lon is None:
            user_lat = self.DEFAULT_LAT
            user_lon = self.DEFAULT_LON

        #calling ingestion agent
        ingestion_output = self.ingestion.process(
            image_file=image_file,
            name=name,
            phone=phone,
            age=age,
            notes=notes,
            allergies=allergies,
            pdf_file=pdf_file,
        )
        data = ingestion_output

        timeline = [self._timeline_entry("ingestion_completed")]
        
        #calling imaging agent
        condition_probs = {}
        if data["xray_path"]:
            img_result = self.imaging.analyze(data["xray_path"])
            condition_probs = img_result.get("condition_probs", {}) or {}
            condition = (
                max(condition_probs, key=condition_probs.get)
                if condition_probs
                else "unknown"
            )
            severity = img_result["severity_hint"]
            timeline.append(self._timeline_entry("imaging_completed"))
        else:
            img_result = {"condition_probs": None, "severity_hint": "not_assessed"}
            condition = "symptom_based"
            severity = SEVERITY_MILD
            timeline.append(self._timeline_entry("imaging_skipped"))

        #calling therapy agent
        notes_for_therapy = self._combine_notes(data.get("notes"), data.get("pdf_text"))
        therapy = self.therapy.recommend(
            notes=notes_for_therapy,
            age=data["patient"]["age"],
            allergies=data["patient"]["allergies"],
            severity_hint=severity,
            condition_probs=condition_probs,
        )
        timeline.append(self._timeline_entry("therapy_completed"))

        #calling doctor escalation agent
        red_flags = therapy.get("red_flags", [])
        doctor_assessment = self.doctor_escalation.assess(
            red_flags, severity, condition_probs
        )
        timeline.append(self._timeline_entry("doctor_escalation_evaluated"))


        #calling pharmacy agent
        skus = [m["sku"] for m in therapy["otc_options"]]
        if skus:
            pharmacy_match = self.pharmacy.find_matches(
                skus, user_lat=user_lat, user_lon=user_lon
            )
        else:
            pharmacy_match = {"message": "No OTC medicines selected"}
        timeline.append(self._timeline_entry("pharmacy_match_completed"))

        #building medicine order preview
        order_preview = self._build_order_preview(pharmacy_match)
        if order_preview:
            timeline.append(self._timeline_entry("order_preview_ready"))

        #returning the final response from all the agents
        return {
            "ingestion_output": ingestion_output,
            "patient": data["patient"],
            "diagnosis": {
                "condition": condition,
                "severity": severity,
                "confidence_source": "xray" if data["xray_path"] else "symptoms",
            },
            "therapy_plan": therapy,
            "pharmacy_match": pharmacy_match,
            "doctor_escalation_needed": doctor_assessment["doctor_escalation_needed"],
            "escalation_suggestions": doctor_assessment["escalation_suggestions"],
            "doctor_assessment": doctor_assessment,
            "timeline": timeline,
            "order_preview": order_preview,
            "disclaimer": (
                "This is not medical advice. Consult a doctor for diagnosis, "
                "emergencies, or worsening symptoms."
            ),
        }
