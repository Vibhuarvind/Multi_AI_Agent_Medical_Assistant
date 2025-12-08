import io
from pathlib import Path

import pytest

from Agents.ingestion import IngestionAgent


def _fake_upload(name: str, content: bytes = b"data"):
    buffer = io.BytesIO(content)
    buffer.name = name
    buffer.seek(0)
    return buffer


def test_mask_methods_raise_for_missing_values(tmp_path):
    agent = IngestionAgent(upload_dir=str(tmp_path / "ingestion"))
    with pytest.raises(Exception):
        agent.mask_name("")
    with pytest.raises(Exception):
        agent.mask_phone("")


def test_process_saves_image_and_pdf(tmp_path):
    agent = IngestionAgent(upload_dir=str(tmp_path / "ingestion"))
    image = _fake_upload("scan.png", b"xraybytes")
    pdf = _fake_upload("report.pdf", b"pdfcontent")

    payload = agent.process(
        image_file=image,
        pdf_file=pdf,
        name="Vibhu",
        phone="9999999999",
        age=30,
        notes="fever and cough"
    )

    assert payload["patient"]["age"] == 30
    assert payload["notes"] == "fever and cough"
    assert payload["xray_path"]
    assert Path(payload["xray_path"]).exists()
    assert payload["pdf_text"]


def test_process_rejects_invalid_image_extension(tmp_path):
    agent = IngestionAgent(upload_dir=str(tmp_path / "ingestion"))
    bad_image = _fake_upload("scan.bmp", b"xray")

    with pytest.raises(Exception):
        agent.process(
            image_file=bad_image,
            name="Vibhu",
            phone="9999999999",
            age=30,
            notes="fever"
        )


def test_process_requires_clinical_input(tmp_path):
    agent = IngestionAgent(upload_dir=str(tmp_path / "ingestion"))
    with pytest.raises(Exception):
        agent.process(
            name="Vibhu",
            phone="9999999999",
            age=30,
            notes=None
        )

