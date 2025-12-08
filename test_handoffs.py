
import pytest
import os
import sys

# Ensure proper path for imports
sys.path.append(os.getcwd())

from Agents.coordinator import Orchestrator
from Agents.therapy import TherapyAgent
from Agents.pharmacy_match import PharmacyAgent

def test_full_chain_smoke():
    """
    Test 1: Does the whole pipeline run end-to-end without crashing?
    """
    orch = Orchestrator()
    res = orch.run_flow(
        image_file=None, # Mocking no image for speed
        name="Test Patient",
        phone="5550100234",
        age=30,
        notes="cough and fever",
        allergies=[],
        pdf_file=None
    )
    
    # Assertions
    assert res is not None
    assert "diagnosis" in res
    assert "therapy_plan" in res
    assert "pharmacy_match" in res
    assert "order_preview" in res
    assert isinstance(res["timeline"], list)
    assert "doctor_escalation_needed" in res
    
    # Check if we got a condition (defaults to symptom_based if no image)
    assert res["diagnosis"]["condition"] in ["symptom_based", "unknown"] or isinstance(res["diagnosis"]["condition"], str)

def test_imaging_to_therapy_handoff():
    """
    Test 2: Can TherapyAgent handle the output structure from ImagingAgent?
    """
    t = TherapyAgent()
    
    # Mock data coming from Imaging Agent
    mock_condition_probs = {"pneumonia": 0.85, "normal": 0.15}
    mock_severity = "moderate"
    
    # Updated to match medicines.csv (SKU001 = Paracetamol -> Fever)
    res = t.recommend(
        notes="high fever and pain", 
        age=45, 
        allergies=[], 
        severity_hint=mock_severity,
        condition_probs=mock_condition_probs
    )
    
    assert "otc_options" in res
    assert len(res["otc_options"]) > 0
    # Should recommend Paracetamol (SKU001) for Fever
    assert any("Paracetamol" in m["sku"] or "SKU001" in m["sku"] for m in res["otc_options"])

def test_therapy_to_pharmacy_handoff():
    """
    Test 3: Can PharmacyAgent handle the SKUs from TherapyAgent?
    """
    p = PharmacyAgent()
    
    # Mock output from Therapy (Updated to match inventory.csv SKUs)
    mock_skus = ["SKU001", "SKU002"] # Paracetamol, Ibuprofen
    
    res = p.find_matches(mock_skus, user_lat=19.12, user_lon=72.84)
    
    assert "pharmacy_id" in res
    assert "items" in res
    assert len(res["items"]) > 0
    assert "price" in res["items"][0]
    assert "drug_name" in res["items"][0]
