"""Tests for risk engine."""
import pytest
from backend.services.risk_engine import risk_engine


@pytest.mark.asyncio
async def test_score_address():
    """Test address risk scoring."""
    address = "0x123456789abcdef123456789abcdef1234567890"
    score = await risk_engine.score_address(address)
    
    assert isinstance(score, int)
    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_score_transaction():
    """Test transaction risk scoring."""
    tx_data = {
        "from_address": "0x123",
        "to_address": "0x456",
        "value_usd": 10000.00,
        "blockchain": "ethereum",
    }
    
    result = await risk_engine.score_transaction(tx_data)
    
    assert "overall_score" in result
    assert "sender_risk" in result
    assert "receiver_risk" in result
    assert "risk_level" in result
    assert result["risk_level"] in ["low", "medium", "high", "critical"]
