from Agents.imaging import ImagingAgent


def test_demo_cheat_code_for_pneumonia():
    agent = ImagingAgent()
    result = agent.analyze("patient_pneumonia_severe.jpg")
    assert result["condition_probs"]["pneumonia"] > 0.8
    assert result["severity_hint"] == "severe"


def test_no_image_returns_safe_output():
    agent = ImagingAgent()
    result = agent.analyze(None)
    assert result["severity_hint"] == "no-image"
    assert result["condition_probs"] is None

