"""API v1 router."""
from fastapi import APIRouter, Depends

from backend.api.v1 import monitoring, reporting, validation, risk, sanctions, audit
from backend.core.security import require_api_key

_auth = [Depends(require_api_key)]

router = APIRouter()

router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"], dependencies=_auth)
router.include_router(reporting.router, prefix="/reporting", tags=["reporting"], dependencies=_auth)
router.include_router(validation.router, prefix="/validation", tags=["validation"], dependencies=_auth)
router.include_router(risk.router, prefix="/risk", tags=["risk"], dependencies=_auth)
router.include_router(sanctions.router, prefix="/sanctions", tags=["sanctions"], dependencies=_auth)
router.include_router(audit.router, prefix="/audit", tags=["audit"], dependencies=_auth)
