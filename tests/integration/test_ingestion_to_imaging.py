import io

from Agents.ingestion import IngestionAgent
from Agents.imaging import ImagingAgent


def _fake_image(name: str = "demo_pneumonia.jpg"):
    buffer = io.BytesIO(b"xray-bytes")
    buffer.name = name
    buffer.seek(0)
    return buffer


def test_ingestion_produces_file_for_imaging(tmp_path):
    agent = IngestionAgent(upload_dir=str(tmp_path / "integration_ingest"))
    payload = agent.process(
        image_file=_fake_image(),
        name="Test Patient",
        phone="1112223333",
        age=40,
        notes="Persistent cough"
    )

    assert payload["xray_path"]

    imaging = ImagingAgent()
    diagnosis = imaging.analyze(payload["xray_path"])
    assert diagnosis["condition_probs"]["pneumonia"] > 0

