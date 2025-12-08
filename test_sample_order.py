"""
Test script to validate sample order JSON and simulate order placement.

This script demonstrates how to:
1. Load a sample order JSON
2. Validate its structure against the expected schema
3. Simulate the order finalization process
4. Display human-readable output

Usage:
    python test_sample_order.py
"""

import json
from datetime import datetime
from pathlib import Path


def validate_order_schema(order: dict) -> tuple[bool, list[str]]:
    """
    Validate order JSON against expected schema.
    
    Returns:
        (is_valid, errors): Tuple of validation status and list of error messages
    """
    errors = []
    
    # Required top-level fields
    required_fields = [
        "pharmacy_id", "items", "eta_min", "delivery_fee", 
        "subtotal", "order_id", "placed_at", "total_cost"
    ]
    
    for field in required_fields:
        if field not in order:
            errors.append(f"Missing required field: {field}")
    
    # Validate items structure
    if "items" in order:
        if not isinstance(order["items"], list):
            errors.append("'items' must be a list")
        elif len(order["items"]) == 0:
            errors.append("'items' list cannot be empty")
        else:
            for idx, item in enumerate(order["items"]):
                required_item_fields = ["sku", "drug_name", "qty", "unit_price", "subtotal"]
                for field in required_item_fields:
                    if field not in item:
                        errors.append(f"Item {idx}: Missing field '{field}'")
    
    # Validate numeric fields
    numeric_fields = ["eta_min", "delivery_fee", "subtotal", "total_cost"]
    for field in numeric_fields:
        if field in order and not isinstance(order[field], (int, float)):
            errors.append(f"Field '{field}' must be numeric")
    
    # Validate timestamp format
    if "placed_at" in order:
        try:
            datetime.fromisoformat(order["placed_at"].replace("Z", "+00:00"))
        except ValueError:
            errors.append("'placed_at' must be valid ISO 8601 timestamp")
    
    # Validate total calculation
    if all(f in order for f in ["subtotal", "delivery_fee", "total_cost"]):
        expected_total = order["subtotal"] + order["delivery_fee"]
        if abs(order["total_cost"] - expected_total) > 0.01:
            errors.append(
                f"Total cost mismatch: {order['total_cost']} != "
                f"{order['subtotal']} + {order['delivery_fee']}"
            )
    
    return len(errors) == 0, errors


def humanize_timestamp(timestamp: str) -> str:
    """Convert ISO timestamp to human-readable format."""
    try:
        normalized = timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        return dt.strftime("%B %d, %Y at %I:%M:%S %p")
    except Exception:
        return timestamp


def display_order(order: dict):
    """Display order in human-readable format."""
    print("\n" + "="*60)
    print("           ORDER CONFIRMATION")
    print("="*60)
    
    print(f"\n📋 Order ID: {order.get('order_id', 'N/A')}")
    print(f"📅 Placed: {humanize_timestamp(order.get('placed_at', ''))}")
    print(f"🏥 Pharmacy: {order.get('pharmacy_id', 'N/A')}")
    print(f"⏱️  Estimated Delivery: {order.get('eta_min', 'N/A')} minutes")
    
    print("\n💊 Items Ordered:")
    print("-" * 60)
    for idx, item in enumerate(order.get("items", []), 1):
        print(f"{idx}. {item.get('drug_name', 'Unknown')} (SKU: {item.get('sku', 'N/A')})")
        print(f"   Quantity: {item.get('qty', 0)} | "
              f"Unit Price: ₹{item.get('unit_price', 0)} | "
              f"Subtotal: ₹{item.get('subtotal', 0)}")
    
    print("\n" + "-" * 60)
    print(f"Subtotal:        ₹{order.get('subtotal', 0):>10.2f}")
    print(f"Delivery Fee:    ₹{order.get('delivery_fee', 0):>10.2f}")
    print(f"{'='*46}")
    print(f"TOTAL:           ₹{order.get('total_cost', 0):>10.2f}")
    print("="*60 + "\n")


def main():
    """Main test function."""
    sample_file = Path("sample_order.json")
    
    # Check if sample file exists
    if not sample_file.exists():
        print(f"❌ Error: {sample_file} not found!")
        print("Please ensure sample_order.json is in the current directory.")
        return 1
    
    # Load sample order
    print(f"📂 Loading sample order from: {sample_file}")
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            order = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {sample_file}")
        print(f"   {e}")
        return 1
    
    # Validate schema
    print("\n🔍 Validating order schema...")
    is_valid, errors = validate_order_schema(order)
    
    if not is_valid:
        print("\n❌ Validation FAILED:")
        for error in errors:
            print(f"   • {error}")
        return 1
    
    print("✅ Schema validation PASSED")
    
    # Display order
    display_order(order)
    
    # Summary
    print("✅ Sample order test completed successfully!")
    print(f"   - Order ID: {order['order_id']}")
    print(f"   - Total items: {len(order['items'])}")
    print(f"   - Total cost: ₹{order['total_cost']}")
    
    return 0


if __name__ == "__main__":
    exit(main())

