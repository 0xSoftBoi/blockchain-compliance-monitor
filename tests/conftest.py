"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_transaction():
    """Sample transaction for testing."""
    from datetime import datetime
    from backend.services.monitoring import Transaction
    
    return Transaction(
        tx_hash="0x742d35cc6634c0532925a3b844bc9e7fbbdd98e3b7c007e836c8ebcf5df9ae25",
        from_address="0x123456789abcdef123456789abcdef1234567890",
        to_address="0xabcdef123456789abcdef123456789abcdef1234",
        value_usd=15000.00,
        blockchain="ethereum",
        timestamp=datetime.utcnow(),
        token_symbol="USDC",
    )
