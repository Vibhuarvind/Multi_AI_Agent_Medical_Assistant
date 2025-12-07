"""Lookup dictionaries for user-friendly name mappings."""

from functools import lru_cache
from typing import Dict
from .data_loader import load_medicines, load_pharmacies


@lru_cache(maxsize=1)
def get_sku_to_drug_name_map() -> Dict[str, str]:
    """
    Get mapping from SKU codes to drug names.
    
    Returns:
        Dictionary mapping SKU (e.g., "SKU001") to drug name (e.g., "Paracetamol")
    """
    meds = load_medicines()
    return dict(zip(meds['sku'], meds['drug_name']))


@lru_cache(maxsize=1)
def get_pharmacy_id_to_name_map() -> Dict[str, str]:
    """
    Get mapping from pharmacy IDs to pharmacy names.
    
    Returns:
        Dictionary mapping pharmacy_id (e.g., "ph001") to name (e.g., "MedQuick Andheri")
    """
    pharmacies = load_pharmacies()
    return {ph["id"]: ph["Name"] for ph in pharmacies}

