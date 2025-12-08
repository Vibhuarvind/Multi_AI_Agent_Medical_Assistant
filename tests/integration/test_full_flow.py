import io

from Agents.coordinator import Orchestrator
from Agents.ingestion import IngestionAgent


def _fake_image(name: str = "demo_pneumonia.jpg"):
    buffer = io.BytesIO(b"xray-bytes")
    buffer.name = name
    buffer.seek(0)
    return buffer


def test_orchestrator_runs_end_to_end(tmp_path):
    orchestrator = Orchestrator()
    orchestrator.ingestion = IngestionAgent(upload_dir=str(tmp_path / ".coordinator_ingest"))

    final = orchestrator.run_flow(
        image_file=_fake_image(),
        name="Panel Patient",
        phone="9998887776",
        age=34,
        notes="Worsening cough and chest tightness",
        allergies="aspirin"
    )

    assert final["therapy_plan"]["otc_options"]
    assert "pharmacy_id" in final["pharmacy_match"]
    assert final["timeline"]
    assert isinstance(final["timeline"][0], dict)
    assert final["order_preview"]
    assert "subtotal" in final["order_preview"]

