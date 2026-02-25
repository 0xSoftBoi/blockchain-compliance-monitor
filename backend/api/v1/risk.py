"""Risk scoring API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.services.risk_engine import risk_engine

router = APIRouter()


class RiskScoreRequest(BaseModel):
    """Risk score request."""
    address: str = Field(..., description="Address to score")


class TransactionRiskRequest(BaseModel):
    """Transaction risk scoring request."""
    from_address: str
    to_address: str
    value_usd: float
    blockchain: str = "ethereum"


@router.post("/score")
async def score_address(request: RiskScoreRequest):
    """Get risk score for a blockchain address.
    
    Returns a score from 0-100 where:
    - 0-30: Low risk
    - 30-60: Medium risk
    - 60-85: High risk
    - 85-100: Critical risk
    """
    try:
        score = await risk_engine.score_address(request.address)
        
        if score < 30:
            risk_level = "low"
        elif score < 60:
            risk_level = "medium"
        elif score < 85:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return {
            "address": request.address,
            "risk_score": score,
            "risk_level": risk_level,
            "recommendation": get_recommendation(risk_level),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transaction")
async def score_transaction(request: TransactionRiskRequest):
    """Score a complete transaction including both parties."""
    try:
        tx_data = {
            "from_address": request.from_address,
            "to_address": request.to_address,
            "value_usd": request.value_usd,
            "blockchain": request.blockchain,
        }
        
        result = await risk_engine.score_transaction(tx_data)
        
        return {
            "transaction": tx_data,
            "risk_assessment": result,
            "recommendation": get_recommendation(result["risk_level"]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network/{address}")
async def get_network_analysis(address: str, depth: int = 2):
    """Analyze counterparty network for an address."""
    try:
        network = await risk_engine.get_counterparty_network(address, depth)
        return network
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_recommendation(risk_level: str) -> str:
    """Get recommendation based on risk level."""
    recommendations = {
        "low": "Transaction may proceed with standard monitoring",
        "medium": "Enhanced monitoring recommended",
        "high": "Enhanced due diligence required before proceeding",
        "critical": "Transaction should be blocked pending investigation",
    }
    return recommendations.get(risk_level, "Unknown risk level")
