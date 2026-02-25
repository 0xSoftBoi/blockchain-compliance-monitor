"""Sanctions screening API endpoints."""
from fastapi import APIRouter, HTTPException, Body
from typing import List
from pydantic import BaseModel, Field

from backend.services.sanctions import sanctions_service

router = APIRouter()


class SanctionsScreenRequest(BaseModel):
    """Sanctions screening request."""
    address: str = Field(..., description="Blockchain address to screen")


class BatchSanctionsScreenRequest(BaseModel):
    """Batch sanctions screening request."""
    addresses: List[str] = Field(..., description="List of addresses to screen")


@router.post("/screen")
async def screen_address(request: SanctionsScreenRequest):
    """Screen a single address against sanctions lists.
    
    Checks:
    - OFAC SDN list
    - EU sanctions
    - UN sanctions
    """
    try:
        is_sanctioned = await sanctions_service.is_sanctioned(request.address)
        
        return {
            "address": request.address,
            "sanctioned": is_sanctioned,
            "risk_level": "critical" if is_sanctioned else "low",
            "action": "BLOCK transaction immediately" if is_sanctioned else "Proceed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/screen/batch")
async def screen_addresses_batch(request: BatchSanctionsScreenRequest):
    """Screen multiple addresses in batch.
    
    More efficient for screening multiple addresses at once.
    """
    try:
        results = await sanctions_service.batch_screen(request.addresses)
        
        return {
            "total_screened": len(results),
            "sanctioned_count": sum(1 for v in results.values() if v),
            "results": [
                {
                    "address": addr,
                    "sanctioned": is_sanctioned,
                }
                for addr, is_sanctioned in results.items()
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_sanctions_info():
    """Get information about sanctions lists."""
    try:
        info = await sanctions_service.get_list_info()
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
