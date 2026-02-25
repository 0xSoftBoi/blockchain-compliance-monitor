"""Regulatory reporting API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from backend.services.reporting import (
    reporting_service,
    ReportType,
    ReportFormat,
    ReportStatus,
)

router = APIRouter()


class ReportGenerationRequest(BaseModel):
    """Report generation request."""
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    jurisdiction: str = "US"
    format: ReportFormat = ReportFormat.JSON


@router.post("/generate")
async def generate_report(request: ReportGenerationRequest):
    """Generate a regulatory report.
    
    Supported report types:
    - SAR: Suspicious Activity Report (FinCEN)
    - CTR: Currency Transaction Report (FinCEN)
    - MICA_QUARTERLY: MiCA Quarterly Report (EU)
    - MICA_ANNUAL: MiCA Annual Report (EU)
    - TRAVEL_RULE: Travel Rule Compliance Report
    """
    try:
        report = await reporting_service.generate_report(
            report_type=request.report_type,
            period_start=request.period_start,
            period_end=request.period_end,
            jurisdiction=request.jurisdiction,
            format=request.format,
        )
        
        return {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "status": report.status.value,
            "period": {
                "start": report.period_start.isoformat(),
                "end": report.period_end.isoformat(),
            },
            "created_at": report.created_at.isoformat(),
            "data": report.data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submissions")
async def list_reports(
    report_type: Optional[ReportType] = Query(None),
    status: Optional[ReportStatus] = Query(None),
    limit: int = Query(100, le=1000),
):
    """List regulatory reports."""
    try:
        reports = await reporting_service.list_reports(
            report_type=report_type,
            status=status,
            limit=limit,
        )
        
        return {
            "count": len(reports),
            "reports": [
                {
                    "report_id": r.report_id,
                    "type": r.report_type.value,
                    "status": r.status.value,
                    "jurisdiction": r.jurisdiction,
                    "period_start": r.period_start.isoformat(),
                    "period_end": r.period_end.isoformat(),
                    "created_at": r.created_at.isoformat(),
                    "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
                }
                for r in reports
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit/{report_id}")
async def submit_report(report_id: str):
    """Submit a report to regulatory authority.
    
    Report must be in 'approved' status before submission.
    """
    try:
        success = await reporting_service.submit_report(report_id)
        
        return {
            "report_id": report_id,
            "submitted": success,
            "message": "Report submitted successfully" if success else "Submission failed",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
