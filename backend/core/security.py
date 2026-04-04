"""API key authentication dependency."""
import os
import secrets

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str = Security(API_KEY_HEADER)) -> None:
    """Validate the X-API-Key header.

    If COMPLIANCE_API_KEY is not set in the environment the check is skipped
    (dev mode). In production, set COMPLIANCE_API_KEY to a strong random value.
    """
    expected = os.environ.get("COMPLIANCE_API_KEY", "")
    if not expected:
        return  # dev mode: no key configured — open access
    if not secrets.compare_digest(api_key or "", expected):
        raise HTTPException(status_code=403, detail="Invalid API key")
