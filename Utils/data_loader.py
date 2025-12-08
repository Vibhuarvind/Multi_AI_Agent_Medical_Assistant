"""Data loading utilities with caching for CSV/JSON files."""

import json
import csv
from functools import lru_cache
from typing import List, Dict, Any, Tuple
import pandas as pd


@lru_cache(maxsize=1)
def load_medicines() -> pd.DataFrame:
    """
    Load medicines CSV with caching.
    
    Returns:
        DataFrame with columns: sku, drug_name, indication, age_min, contra_allergy_keywords
    """
    return pd.read_csv("Data/medicines.csv")


@lru_cache(maxsize=1)
def load_interactions() -> pd.DataFrame:
    """
    Load drug interactions CSV with caching.
    
    Returns:
        DataFrame with columns: drug_a, drug_b, level, note
    """
    return pd.read_csv("Data/interactions.csv")


@lru_cache(maxsize=1)
def load_inventory() -> pd.DataFrame:
    """
    Load pharmacy inventory CSV with caching.
    
    Returns:
        DataFrame with columns: pharmacy_id, sku, qty, etc.
    """
    return pd.read_csv("Data/inventory.csv")


@lru_cache(maxsize=1)
def load_pharmacies() -> List[Dict[str, Any]]:
    """
    Load pharmacies JSON with caching.
    
    Returns:
        List of pharmacy dictionaries with id, Name, lat, lon, services, delivery_km
    """
    with open("Data/pharmacies.json", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_zipcodes() -> pd.DataFrame:
    """
    Load zipcodes CSV with caching.
    
    Returns:
        DataFrame with columns: zipcode, lat, lon, city, etc.
    """
    return pd.read_csv("Data/zipcodes.csv")


@lru_cache(maxsize=1)
def load_pincode_map() -> Dict[str, Tuple[float, float]]:
    """
    Builds a lookup from pincode → (lat, lon).
    """
    df = load_zipcodes()
    mapping: Dict[str, Tuple[float, float]] = {}
    for _, row in df.iterrows():
        pincode = str(row["pincode"]).strip()
        if not pincode:
            continue
        mapping[pincode] = (float(row["lat"]), float(row["lon"]))
    return mapping


@lru_cache(maxsize=1)
def load_doctors() -> List[Dict[str, Any]]:
    """
    Load doctors CSV and parse tele-consult slots.
    
    Returns:
        List of doctor dictionaries with doctor_id, name, specialty, tele_slots
    """
    roster = []
    with open("Data/doctors.csv", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            slots = [
                slot.strip() 
                for slot in row["tele_slot_iso8601"].split(",") 
                if slot.strip()
            ]
            roster.append({
                "doctor_id": row["doctor_id"],
                "name": row["name"],
                "specialty": row["specialty"],
                "tele_slots": slots
            })
    return roster

