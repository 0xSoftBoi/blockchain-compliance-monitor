"""Tests for sanctions screening."""
import pytest
from backend.services.sanctions import sanctions_service


@pytest.mark.asyncio
async def test_screen_clean_address():
    """Test screening of clean address."""
    address = "0x000000000000000000000000000000000000dead"
    is_sanctioned = await sanctions_service.is_sanctioned(address)
    
    assert isinstance(is_sanctioned, bool)


@pytest.mark.asyncio
async def test_batch_screen():
    """Test batch sanctions screening."""
    addresses = [
        "0x111",
        "0x222",
        "0x333",
    ]
    
    results = await sanctions_service.batch_screen(addresses)
    
    assert len(results) == 3
    assert all(isinstance(v, bool) for v in results.values())


@pytest.mark.asyncio
async def test_sanctions_info():
    """Test sanctions list info retrieval."""
    info = await sanctions_service.get_list_info()
    
    assert "ofac_entries" in info
    assert "eu_entries" in info
    assert "un_entries" in info
    assert "total_entries" in info
