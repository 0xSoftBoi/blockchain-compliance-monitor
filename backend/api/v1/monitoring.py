"""Transaction monitoring API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from backend.services.monitoring import (
    monitoring_service,
    Transaction,
    AlertSeverity,
    AlertType,
)

router = APIRouter()


class TransactionSubmit(BaseModel):
    """Transaction submission request."""
    tx_hash: str = Field(..., description="Transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    value_usd: float = Field(..., description="Transaction value in USD")
    blockchain: str = Field(..., description="Blockchain network")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    token_symbol: Optional[str] = None
    contract_address: Optional[str] = None
    metadata: Optional[dict] = None


class TransactionResponse(BaseModel):
    """Transaction submission response."""
    monitoring_id: str
    tx_hash: str
    status: str
    message: str


@router.post("/transaction", response_model=TransactionResponse)
async def submit_transaction(transaction: TransactionSubmit):
    """Submit a transaction for compliance monitoring.
    
    This endpoint accepts transaction data and queues it for:
    - Sanctions screening
    - Risk scoring
    - Pattern detection
    - Threshold checking
    - Behavioral analysis
    """
    try:
        tx = Transaction(
            tx_hash=transaction.tx_hash,
            from_address=transaction.from_address,
            to_address=transaction.to_address,
            value_usd=transaction.value_usd,
            blockchain=transaction.blockchain,
            timestamp=transaction.timestamp,
            token_symbol=transaction.token_symbol,
            contract_address=transaction.contract_address,
            metadata=transaction.metadata,
        )
        
        monitoring_id = await monitoring_service.submit_transaction(tx)
        
        return TransactionResponse(
            monitoring_id=monitoring_id,
            tx_hash=transaction.tx_hash,
            status="queued",
            message="Transaction submitted for compliance monitoring",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts(
    severity: Optional[AlertSeverity] = Query(None),
    alert_type: Optional[AlertType] = Query(None),
    limit: int = Query(100, le=1000),
):
    """Retrieve compliance alerts.
    
    Filter by severity and/or alert type to focus on specific issues.
    """
    try:
        alerts = await monitoring_service.get_alerts(
            severity=severity,
            alert_type=alert_type,
            limit=limit,
        )
        
        return {
            "count": len(alerts),
            "alerts": [
                {
                    "id": alert.id,
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "tx_hash": alert.transaction.tx_hash,
                    "description": alert.description,
                    "risk_score": alert.risk_score,
                    "recommended_action": alert.recommended_action,
                    "created_at": alert.created_at.isoformat(),
                }
                for alert in alerts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_monitoring_stats():
    """Get monitoring service statistics."""
    try:
        return {
            "active_alerts": len(monitoring_service.active_alerts),
            "queue_size": monitoring_service.transaction_queue.qsize(),
            "monitoring_active": monitoring_service.monitoring_active,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
