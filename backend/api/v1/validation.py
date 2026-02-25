"""Smart contract validation API endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.services.validator import (
    contract_validator,
    ComplianceFramework,
)

router = APIRouter()


class ValidationRequest(BaseModel):
    """Contract validation request."""
    source_code: str = Field(..., description="Smart contract source code")
    frameworks: List[ComplianceFramework] = Field(
        default=[ComplianceFramework.BSA, ComplianceFramework.MICA],
        description="Compliance frameworks to validate against"
    )
    contract_address: Optional[str] = Field(None, description="Deployed contract address")


@router.post("/contract")
async def validate_contract(request: ValidationRequest):
    """Validate smart contract against compliance frameworks.
    
    Supported frameworks:
    - MiCA (EU Markets in Crypto-Assets)
    - BSA (US Bank Secrecy Act)
    - ISO 20022 (Financial messaging)
    - Wolfsberg (AML principles)
    - FATF (International standards)
    """
    try:
        result = await contract_validator.validate_contract(
            source_code=request.source_code,
            frameworks=request.frameworks,
            contract_address=request.contract_address,
        )
        
        return {
            "validation_result": {
                "passed": result.passed,
                "compliance_score": result.compliance_score,
                "contract_address": result.contract_address,
                "source_code_hash": result.source_code_hash,
                "timestamp": result.timestamp.isoformat(),
                "frameworks_checked": [f.value for f in result.frameworks_checked],
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "framework": issue.framework.value,
                    "rule_id": issue.rule_id,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "line_number": issue.line_number,
                    "regulation_reference": issue.regulation_reference,
                }
                for issue in result.issues
            ],
            "summary": {
                "total_issues": len(result.issues),
                "critical": result.metadata.get("critical_issues", 0),
                "errors": result.metadata.get("error_issues", 0),
                "warnings": result.metadata.get("warning_issues", 0),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contract/upload")
async def validate_contract_file(file: UploadFile = File(...)):
    """Validate smart contract from uploaded file."""
    try:
        source_code = await file.read()
        source_code = source_code.decode("utf-8")
        
        result = await contract_validator.validate_contract(
            source_code=source_code,
            frameworks=[ComplianceFramework.BSA, ComplianceFramework.MICA],
        )
        
        return {
            "filename": file.filename,
            "passed": result.passed,
            "compliance_score": result.compliance_score,
            "issues_count": len(result.issues),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
