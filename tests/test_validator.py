"""Tests for smart contract validator."""
import pytest
from backend.services.validator import contract_validator, ComplianceFramework


@pytest.mark.asyncio
async def test_validate_simple_contract():
    """Test validation of simple contract."""
    source_code = """
    pragma solidity ^0.8.0;
    
    contract SimpleTransfer {
        function transfer() public {}
    }
    """
    
    result = await contract_validator.validate_contract(
        source_code=source_code,
        frameworks=[ComplianceFramework.BSA],
    )
    
    assert result is not None
    assert hasattr(result, 'passed')
    assert hasattr(result, 'compliance_score')
    assert 0 <= result.compliance_score <= 100


@pytest.mark.asyncio
async def test_validate_compliant_contract():
    """Test validation of more compliant contract."""
    source_code = """
    pragma solidity ^0.8.0;
    
    contract CompliantTransfer {
        mapping(address => bool) public kyc;
        uint256 public dailyLimit;
        
        modifier onlyOwner() { _; }
        modifier nonReentrant() { _; }
        
        function transfer() public nonReentrant {
            require(kyc[msg.sender], "KYC required");
        }
        
        function pause() public onlyOwner {}
    }
    """
    
    result = await contract_validator.validate_contract(
        source_code=source_code,
        frameworks=[ComplianceFramework.BSA, ComplianceFramework.MICA],
    )
    
    # Should have higher compliance score
    assert result.compliance_score > 50
