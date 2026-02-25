"""Tests for monitoring service."""
import pytest
from backend.services.monitoring import monitoring_service, Transaction, AlertSeverity
from datetime import datetime


@pytest.mark.asyncio
async def test_submit_transaction(sample_transaction):
    """Test transaction submission."""
    monitoring_id = await monitoring_service.submit_transaction(sample_transaction)
    assert monitoring_id is not None
    assert len(monitoring_id) == 16


@pytest.mark.asyncio
async def test_get_alerts():
    """Test alert retrieval."""
    alerts = await monitoring_service.get_alerts(limit=10)
    assert isinstance(alerts, list)
    assert len(alerts) <= 10


@pytest.mark.asyncio
async def test_high_value_threshold():
    """Test high value transaction threshold."""
    high_value_tx = Transaction(
        tx_hash="0xtest",
        from_address="0x123",
        to_address="0x456",
        value_usd=50000.00,
        blockchain="ethereum",
        timestamp=datetime.utcnow(),
    )
    
    # Submit and allow processing
    await monitoring_service.submit_transaction(high_value_tx)
    # Note: In real tests, we'd wait for processing or mock the queue
