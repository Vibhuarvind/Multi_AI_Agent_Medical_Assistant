from Agents.pharmacy_match import PharmacyAgent
from Agents.therapy import TherapyAgent


def test_therapy_supplies_skus_to_pharmacy():
    therapy = TherapyAgent()
    pharmacy = PharmacyAgent()

    therapy_result = therapy.recommend(
        notes="Fever and pain after a long flight",
        age=28,
        allergies=[],
        severity_hint="moderate",
        condition_probs={"pneumonia": 0.8}
    )

    skus = [option["sku"] for option in therapy_result["otc_options"]]
    match = pharmacy.find_matches(skus)

    assert "pharmacy_id" in match
    assert match["items"][0]["sku"] in skus

