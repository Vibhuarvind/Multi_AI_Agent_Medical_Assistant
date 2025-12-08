from Agents.pharmacy_match import PharmacyAgent


def test_find_matches_returns_pharmacy():
    agent = PharmacyAgent()
    result = agent.find_matches(["SKU001"])

    assert "pharmacy_id" in result
    assert result["items"][0]["sku"] == "SKU001"
    assert "price" in result["items"][0]
    assert "drug_name" in result["items"][0]

