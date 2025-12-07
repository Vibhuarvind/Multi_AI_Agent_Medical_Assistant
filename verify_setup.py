import sys
import os

# Ensure we can import from local
sys.path.append(os.getcwd())

def main():
    print("=== Medical Assistant Setup Verification ===")
    
    # 1. Check Directory Structure
    req_dirs = ["Agents", "Data", "Utils"]
    for d in req_dirs:
        if os.path.exists(d):
            print(f"[PASS] Directory found: {d}")
        else:
            print(f"[FAIL] Missing directory: {d}")

    # 2. Check Data Files
    req_files_actual = [
        "Data/medicines.csv", 
        "Data/inventory.csv", 
        "Data/zipcodes.csv", 
        "Data/pharmacies.json",
        "Data/doctors.csv",
        "Data/interactions.csv"
    ]

    for f in req_files_actual:
        if os.path.exists(f):
            print(f"[PASS] Data file found: {f}")
        else:
            print(f"[FAIL] Missing data file: {f}")

    # 3. Check Imports
    try:
        from Agents.ingestion import IngestionAgent
        print("[PASS] Imported IngestionAgent")
    except ImportError as e:
        print(f"[FAIL] IngestionAgent import failed: {e}")

    try:
        from Agents.imaging import ImagingAgent
        print("[PASS] Imported ImagingAgent")
    except ImportError as e:
        print(f"[FAIL] ImagingAgent import failed: {e}")

    try:
        from Agents.therapy import TherapyAgent
        print("[PASS] Imported TherapyAgent")
    except ImportError as e:
        print(f"[FAIL] TherapyAgent import failed: {e}")

    try:
        from Agents.pharmacy_match import PharmacyAgent
        print("[PASS] Imported PharmacyAgent")
    except ImportError as e:
        print(f"[FAIL] PharmacyAgent import failed: {e}")

    try:
        from Agents.coordinator import Orchestrator
        print("[PASS] Imported Orchestrator")
    except ImportError as e:
        print(f"[FAIL] Orchestrator import failed: {e}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    main()
