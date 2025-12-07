"""Coordinator/Orchestrator agent that routes tasks and consolidates the final plan."""

from Agents.ingestion import IngestionAgent
from Agents.imaging import ImagingAgent
from Agents.therapy import TherapyAgent
from Agents.pharmacy_match import PharmacyAgent
from Utils.logger import get_logger
from Utils.data_loader import load_doctors

logger = get_logger(__name__)

class Orchestrator:
    """Central orchestrator that coordinates all agents and consolidates final plan."""

    def __init__(self):
        self.ingestion = IngestionAgent()
        self.imaging = ImagingAgent()
        self.therapy = TherapyAgent()
        self.pharmacy = PharmacyAgent()
        self.doctors = load_doctors()

    def run_flow(self, image_file=None, name=None, phone=None, age=None,
                 notes=None, allergies=None, pdf_file=None,
                 user_lat=19.12, user_lon=72.84):
        """
        Execute the master pipeline through all agents.

        Returns:
            Consolidated plan with ingestion, diagnosis, therapy, pharmacy,
            and escalation
        """

        # INGESTION
        ingestion_output = self.ingestion.process(
            image_file=image_file, 
            name=name, 
            phone=phone,
            age=age, 
            notes=notes, 
            allergies=allergies, 
            pdf_file=pdf_file
        )
        data = ingestion_output

        timeline = [
            "ingestion_completed"
        ]

        condition_probs = {}
        # IMAGING (Only if x-ray exists)
        if data["xray_path"]:
            img_result = self.imaging.analyze(data["xray_path"])
            condition_probs = img_result.get("condition_probs", {}) or {}
            condition = max(condition_probs, key=condition_probs.get) if condition_probs else "unknown"
            severity = img_result["severity_hint"]
            timeline.append("imaging_completed")
        else:
            img_result = {"condition_probs":None,"severity_hint":"not_assessed"}
            condition = "symptom_based"
            severity = "mild"
            timeline.append("imaging_skipped")

        # THERAPY
        therapy = self.therapy.recommend(
            notes=data["notes"],
            age=data["patient"]["age"],
            allergies=data["patient"]["allergies"],
            severity_hint=severity,
            condition_probs=condition_probs
        )
        timeline.append("therapy_completed")

        # check for escalation risk
        red_flags = therapy.get("red_flags", [])
        max_confidence = (
            max(condition_probs.values()) if condition_probs else 0.0
        )
        escalate = any(
            flag for flag in red_flags
            if "High severity" in flag or "SpO2" in flag
        ) or severity == "severe" or max_confidence < 0.5

        # PHARMACY MATCH
        skus = [m["sku"] for m in therapy["otc_options"]]
        pharmacy_match = (
            self.pharmacy.find_matches(skus, user_lat=user_lat, user_lon=user_lon)
            if skus
            else {"message": "No OTC medicines selected"}
        )
        timeline.append("pharmacy_match_completed")

        escalation_suggestions = []
        if escalate:
            escalation_suggestions = [
                {
                    "doctor": doc["name"],
                    "specialty": doc["specialty"],
                    "tele_slots": doc["tele_slots"],
                    "reason": "Severe findings or red flags detected"
                }
                for doc in self.doctors
            ]

        # FINAL RESPONSE ON THE BASIS OF ALL AGENTS
        return {
            "ingestion_output": ingestion_output,
            "patient": data["patient"],
            "diagnosis": {
                "condition": condition,
                "severity": severity,
                "confidence_source": "xray" if data["xray_path"] else "symptoms"
            },
            "therapy_plan": therapy,
            "pharmacy_match": pharmacy_match,
            "doctor_escalation_needed": escalate,
            "escalation_suggestions": escalation_suggestions,
            "timeline": timeline,
            "disclaimer": (
                "This is not medical advice. Consult a doctor for diagnosis, "
                "emergencies, or worsening symptoms."
            )
        }
