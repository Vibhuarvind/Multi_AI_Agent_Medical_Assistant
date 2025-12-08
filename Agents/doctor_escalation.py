from typing import List, Dict

from Utils.constants import SEVERITY_SEVERE
from Utils.logger import get_logger

logger = get_logger(__name__)


class DoctorEscalationAgent:
    """Evaluates red flags, confidence, and severity to recommend tele-consult options."""

    def __init__(self, doctors: List[Dict[str, str]], confidence_threshold: float = 0.5):
        self.doctors = doctors
        self.confidence_threshold = confidence_threshold

    def assess(self, red_flags: List[str], severity: str, condition_probs: Dict[str, float]):
        max_confidence = max(condition_probs.values()) if condition_probs else 0.0
        severity_warning = severity == SEVERITY_SEVERE
        red_flag_issue = any(
            "High severity" in flag or "SpO2" in flag for flag in red_flags
        )
        needs_escalation = (
            severity_warning or red_flag_issue or max_confidence < self.confidence_threshold
        )

        suggestions = []
        if needs_escalation:
            suggestions = [
                {
                    "doctor": doc["name"],
                    "specialty": doc["specialty"],
                    "tele_slots": doc.get("tele_slots", []),
                    "reason": "Severe findings or red flags detected",
                }
                for doc in self.doctors
            ]

        logger.info(
            "Doctor escalation evaluated: %s | confidence=%0.2f",
            "needed" if needs_escalation else "not needed",
            max_confidence,
        )

        return {
            "doctor_escalation_needed": needs_escalation,
            "escalation_suggestions": suggestions,
            "max_confidence": max_confidence,
        }

