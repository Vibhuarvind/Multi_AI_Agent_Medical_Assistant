from Agents.imaging import ImagingAgent
from Agents.therapy import TherapyAgent


def test_imaging_informs_therapy():
    imaging = ImagingAgent()
    therapy = TherapyAgent()

    imaging_result = imaging.analyze("patient_pneumonia_severe.jpg")
    therapy_result = therapy.recommend(
        notes="Chest discomfort and fever",
        age=35,
        allergies=[],
        severity_hint=imaging_result["severity_hint"],
        condition_probs=imaging_result["condition_probs"]
    )

    assert therapy_result["otc_options"]
    assert therapy_result["red_flags"]

