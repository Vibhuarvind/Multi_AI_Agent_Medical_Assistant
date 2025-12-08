import os
import uuid
import re
from pathlib import Path
"""Ingestion Agent: Handles file validation, PII masking, and file saving."""

from Utils.constants import UPLOADS_DIR
from Utils.logger import get_logger

logger = get_logger(__name__)

class IngestionAgent:

    def __init__(self, upload_dir=UPLOADS_DIR):
        self.upload_dir = upload_dir
        self.images_dir = os.path.join(upload_dir, "images")
        self.pdfs_dir = os.path.join(upload_dir, "pdfs")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.pdfs_dir, exist_ok=True)

    def _save_upload(self, upload_file, target_dir):
        """
        Save an uploaded file under a unique, *non-identifying* name.

        To stay aligned with the POC brief (no PHI/PII storage; see
        `Multi‑Agent Healthcare POC.pdf`), we must not persist raw
        filenames that might contain patient names/IDs.

        However, for demo predictability we _do_ want ImagingAgent's
        filename-based heuristics (e.g. 'pneumonia', 'covid', 'normal')
        to still work when tests deliberately pass such names.

        Compromise:
        - Inspect the original stem for known, *non-identifying*
          condition keywords.
        - If any are present, keep only that keyword as a prefix.
        - Otherwise, use a generic 'xray' prefix.
        - Always append a short random suffix so filenames are unique.
        """
        suffix = Path(upload_file.name).suffix or ""
        stem = Path(upload_file.name).stem.lower()

        keywords = ["pneumonia", "covid", "normal"]
        keyword_prefix = None
        for kw in keywords:
            if kw in stem:
                keyword_prefix = kw
                break

        base_prefix = keyword_prefix or "xray"
        unique_name = f"{base_prefix}_{uuid.uuid4().hex[:6]}{suffix}"
        save_path = os.path.join(target_dir, unique_name)
        with open(save_path, "wb") as f:
            f.write(upload_file.read())
        return save_path.replace("\\", "/")

    def _normalize_allergies(self, allergies):
        if not allergies:
            return []
        if isinstance(allergies, (list, tuple)):
            return [str(a).strip() for a in allergies if str(a).strip()]
        if isinstance(allergies, str):
            return [a.strip() for a in allergies.split(",") if a.strip()]
        raise ValueError("Allergies must be a string or list of strings")

    def _log_notes_snippet(self, notes):
        snippet = (notes or "").strip().replace("\n", " ")
        if len(snippet) > 80:
            snippet = f"{snippet[:80]}..."
        logger.info("Clinical notes snippet: %s", snippet or "<no text provided>")

    # PII Masking
    def mask_name(self, name):
        if not name:
            raise Exception("Name is required")

        if len(name) < 3:
            return "*" * len(name)

        middle = "*" * (len(name) - 2)
        return name[0] + middle + name[-1]

    def mask_phone(self, phone):
        if not phone:
            raise Exception("Phone number is required")

        digits = re.sub(r"\D", "", phone)

        if len(digits) != 10:
            raise Exception("Phone number must be 10 digits")

        return "#" * 8 + digits[-2:]

    # Mock Allergy Detection
    def extract_allergies(self, notes):
        # allergy to any medicines
        allergies_db = ["ibuprofen", "penicillin", "aspirin", "paracetamol"]
        if not notes:
            return []
        lowercased_notes = notes.lower()
        return [a for a in allergies_db if a in lowercased_notes]

    def extract_pdf_text(self, pdf_path):
        """Mock OCR - returns dummy extracted text"""
        if not pdf_path:
            return None
        # In real system, use pytesseract/pdfplumber here
        return "Mock extracted text: Patient complains of persistent cough and fever for 3 days. Temperature 101F."

    # MAIN PROCESS METHOD
    def process(self, image_file=None, name=None, phone=None, age=None, notes=None, pdf_file=None, allergies=None):
        """ Returns details of patient with xray and health problem (notes) """
        # At least one clinical input required
        if not (image_file or notes or pdf_file):
            raise Exception("At least one clinical input (Image, PDF, or Symptoms) is required")

        xray_path = None
        pdf_path = None
        pdf_text = None

        # Handle optional image
        if image_file:
            allowed_ext = (".png", ".jpg", ".jpeg")
            if not image_file.name.lower().endswith(allowed_ext):
                raise Exception("Invalid image file type")

            # Save image
            xray_path = self._save_upload(image_file, self.images_dir)
            logger.info("Stored X-Ray at: %s", xray_path)

        # Handle optional PDF
        if pdf_file:
            if not pdf_file.name.lower().endswith(".pdf"):
                raise Exception("Invalid PDF file type")
            
            # Save PDF
            pdf_path = self._save_upload(pdf_file, self.pdfs_dir)
            pdf_text = self.extract_pdf_text(pdf_path)
            logger.info("Stored PDF at: %s with text: %s", pdf_path, pdf_text)

        # Mask sensitive data internally (not included in output)
        masked_name = self.mask_name(name)
        masked_phone = self.mask_phone(phone)

        logger.info("Masked Name: %s", masked_name)
        logger.info("Masked Phone: %s", masked_phone)
        logger.info("Age: %d", age)
        self._log_notes_snippet(notes)

        # Extract allergies (mock)
        # Use provided allergies or extract from notes
        if allergies:
            allergies_list = self._normalize_allergies(allergies)
        else:
            allergies_list = self.extract_allergies(notes)
        logger.info("Detected Allergies: %s", allergies_list)

        # Ingestion Agent Response
        return {
            "patient": {
                "age": age,
                "allergies": allergies_list
            },
            "xray_path": xray_path,
            "notes": notes or "",
            "pdf_text": pdf_text
        }
