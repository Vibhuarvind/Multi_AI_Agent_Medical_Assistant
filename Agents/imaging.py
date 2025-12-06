import random
import logging

class ImagingAgent:

    def __init__(self):
        self.labels = ["pneumonia","normal","covid_suspect"]

    def analyze(self, xray_path):
        """
        Lightweight mock classifier (Phase-2)
        Uses filename hints for demo predictability, falls back to random.
        """

        if not xray_path:
            return {"condition_probs": None, "severity_hint": "no-image"}   # safe fallback

        filename_lower = xray_path.lower()

        # DEMO CHEAT CODE: Check filename for keywords
        if "pneumonia" in filename_lower:
            probs = {"pneumonia": 0.85, "normal": 0.10, "covid_suspect": 0.05}
            sev = "severe" if "severe" in filename_lower else "moderate"
        elif "covid" in filename_lower:
            probs = {"pneumonia": 0.15, "normal": 0.20, "covid_suspect": 0.65}
            sev = "moderate" if "moderate" in filename_lower else "mild"
        elif "normal" in filename_lower:
            probs = {"pneumonia": 0.05, "normal": 0.90, "covid_suspect": 0.05}
            sev = "mild"
        else:
            # Fallback: random stub predictions for unknown filenames
            vals = [random.random() for _ in range(3)]
            total = sum(vals)
            probs = {lbl: round(v/total, 2) for lbl, v in zip(self.labels, vals)}
            
            pneu = probs["pneumonia"]
            if pneu > 0.65: sev = "severe"
            elif pneu > 0.35: sev = "moderate"
            else: sev = "mild"

        logging.info(f"Imaging output {probs} severity={sev}")

        return {
            "condition_probs": probs,
            "severity_hint": sev
        }
