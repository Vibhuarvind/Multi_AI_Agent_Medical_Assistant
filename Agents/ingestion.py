import os
import uuid
import re
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

        # Handle optional image
        if image_file:
            allowed_ext = (".png", ".jpg", ".jpeg")
            if not image_file.name.lower().endswith(allowed_ext):
                raise Exception("Invalid image file type")

            # Save image
            unique_name = f"{name}_{uuid.uuid4().hex[:6]}_{image_file.name}"
            save_path = os.path.join(self.images_dir, unique_name)
            with open(save_path, "wb") as f:
                f.write(image_file.read())
            xray_path = save_path.replace("\\", "/")
            logger.info("Stored X-Ray at: %s", xray_path)

        # Handle optional PDF
        if pdf_file:
            if not pdf_file.name.lower().endswith(".pdf"):
                raise Exception("Invalid PDF file type")
            
            # Save PDF
            unique_pdf_name = f"{name}_{uuid.uuid4().hex[:6]}_{pdf_file.name}"
            pdf_save_path = os.path.join(self.pdfs_dir, unique_pdf_name)
            with open(pdf_save_path, "wb") as f:
                f.write(pdf_file.read())
            pdf_path = pdf_save_path.replace("\\", "/")
            pdf_text = self.extract_pdf_text(pdf_path) 
            logger.info("Stored PDF at: %s with text: %s", pdf_path, pdf_text)

        # Mask sensitive data internally (not included in output)
        masked_name = self.mask_name(name)
        masked_phone = self.mask_phone(phone)

        logger.info("Masked Name: %s", masked_name)
        logger.info("Masked Phone: %s", masked_phone)
        logger.info("Age: %d", age)
        logger.info("Notes: %s", notes)

        # Extract allergies (mock)
        # Use provided allergies or extract from notes
        if allergies:
            allergies_list = [a.strip() for a in allergies.split(",")]
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
            "notes": notes
        }
