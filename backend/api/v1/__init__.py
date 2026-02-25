"""API v1 router."""
from fastapi import APIRouter

from backend.api.v1 import monitoring, reporting, validation, risk, sanctions, audit

router = APIRouter()

router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
router.include_router(reporting.router, prefix="/reporting", tags=["reporting"])
router.include_router(validation.router, prefix="/validation", tags=["validation"])
router.include_router(risk.router, prefix="/risk", tags=["risk"])
router.include_router(sanctions.router, prefix="/sanctions", tags=["sanctions"])
router.include_router(audit.router, prefix="/audit", tags=["audit"])
