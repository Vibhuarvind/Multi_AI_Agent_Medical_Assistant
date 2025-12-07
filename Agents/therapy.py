"""Therapy Agent: Recommends OTC options based on symptoms and conditions."""

from Utils.logger import get_logger
from Utils.data_loader import load_medicines, load_interactions

logger = get_logger(__name__)

class TherapyAgent:
    """Recommends OTC medications with age/allergy checks and interaction screening."""

    def __init__(self):
        self.meds = load_medicines()
        self.interactions = load_interactions()
        
        self.dosage_map = {
            "Paracetamol": {"dose": "500 mg", "freq": "q6h"},
            "Ibuprofen": {"dose": "400 mg", "freq": "q8h"},
            "Cetirizine": {"dose": "10 mg", "freq": "q24h"},
            "Antacid Tablets": {"dose": "2 tablets", "freq": "q4h"},
            "Loperamide": {"dose": "2 mg", "freq": "q6h"},
            "Saline Nasal Spray": {"dose": "2 sprays", "freq": "q4h"},
            "Hydrocortisone Cream": {"dose": "apply thin layer", "freq": "q12h"},
            "Oral Rehydration Salt (ORS)": {"dose": "1 sachet", "freq": "q4h"}
        }
        self.condition_keywords = {
            "pneumonia": ["fever", "pain", "inflammation", "cough", "chest", "shortness"],
            "covid_suspect": ["fever", "cough", "fatigue", "breath", "loss", "taste"],
            "normal": []
        }

    def recommend(self, notes:str, age:int, allergies:list, severity_hint:str, condition_probs:dict=None):

        red_flags = []
        otc_list = []

        if severity_hint == "severe":
            red_flags.append("High severity detected — Medical consultation needed")
            red_flags.append("SpO2 likely < 92% — Immediate medical attention required")

        top_condition = None
        top_prob = 0.0
        if condition_probs:
            top_condition = max(condition_probs, key=condition_probs.get)
            top_prob = condition_probs.get(top_condition, 0.0)

        if not notes:
            return {"otc_options":[], "red_flags":["No symptoms provided"]}

        notes_lower = notes.lower()
        if top_condition and top_prob >= 0.5:
            keywords = self.condition_keywords.get(top_condition, [])
            if keywords:
                notes_lower = " ".join([notes_lower] + keywords)

        matched = []
        for _, row in self.meds.iterrows():
            # match tokens in indication field
            tokens = row['indication'].lower().replace("&"," ").split()
            if any(t in notes_lower for t in tokens):
                matched.append(row)

        if not matched:
            return {"otc_options":[], "red_flags":["No OTC matched for symptoms"]}

        for row in matched:
            if age < row['age_min']:
                red_flags.append(f"{row['drug_name']} not suitable for age < {row['age_min']}")
                logger.info("Rejected %s (SKU: %s) - age restriction", row['drug_name'], row['sku'])
                continue

            warn=[]
            if allergies and any(a.lower() in row['contra_allergy_keywords'].lower() for a in allergies):
                red_flags.append(f"Avoid {row['drug_name']} — patient allergic")
                logger.info("Rejected %s (SKU: %s) - allergy contraindication", row['drug_name'], row['sku'])
                continue

            if row['contra_allergy_keywords']!="None":
                warn.append(f"contains {row['contra_allergy_keywords']}")

            d = self.dosage_map.get(row['drug_name'],{"dose":"as directed","freq":"as needed"})

            # Log recommended medicine details
            logger.info("Recommending: %s (SKU: %s) - %s %s", row['drug_name'], row['sku'], d['dose'], d['freq'])

            otc_list.append({
                "sku": row['sku'],
                "dose": d['dose'],
                "freq": d['freq'],
                "warnings": warn
            })

        # drug interaction warnings
        if len(otc_list)>1:
            red_flags += self._check_interactions(otc_list)

        logger.info("TherapyAgent: %d OTC options, %d red flags", len(otc_list), len(red_flags))
        
        return {"otc_options": otc_list, "red_flags": red_flags}


    def _check_interactions(self, otc_list):
        warnings=[]
        # Extract SKUs for logging purposes
        skus = [m['sku'] for m in otc_list]
        
        for i in range(len(otc_list)):
            for j in range(i+1, len(otc_list)):
                sku_a, sku_b = skus[i], skus[j]
                
                # Get drug names from original data for interaction check
                drug_a = self.meds[self.meds['sku'] == sku_a].iloc[0]['drug_name']
                drug_b = self.meds[self.meds['sku'] == sku_b].iloc[0]['drug_name']
                
                match=self.interactions[((self.interactions.drug_a==drug_a)&(self.interactions.drug_b==drug_b))|
                                       ((self.interactions.drug_a==drug_b)&(self.interactions.drug_b==drug_a))]
                
                if not match.empty:
                    level = match.iloc[0]["level"]
                    note = match.iloc[0]['note']
                    logger.info("Interaction detected (%s): %s (%s) + %s (%s) - %s", level, drug_a, sku_a, drug_b, sku_b, note)
                    
                    # Show High and Moderate interactions to customers (Low is too minor to surface)
                    if level in ["High", "Moderate"]:
                        warnings.append(f"Drug interaction ({level}): {drug_a} & {drug_b} — {note}")
        
        return warnings
