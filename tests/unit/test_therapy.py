from Agents.therapy import TherapyAgent


def test_recommend_matches_symptoms_and_condition():
    agent = TherapyAgent()
    result = agent.recommend(
        notes="Fever and chest pain after mild activity",
        age=30,
        allergies=[],
        severity_hint="moderate",
        condition_probs={"pneumonia": 0.85, "normal": 0.1}
    )

    assert result["otc_options"], "Therapy should recommend at least one OTC for pneumonia keywords"
    assert all("sku" in option for option in result["otc_options"])
    assert "red_flags" in result


def test_recommend_flags_allergy():
    agent = TherapyAgent()
    result = agent.recommend(
        notes="Pain and inflammation",
        age=30,
        allergies=["ibuprofen"],
        severity_hint="mild"
    )

    assert any("Avoid Ibuprofen" in flag for flag in result["red_flags"])

