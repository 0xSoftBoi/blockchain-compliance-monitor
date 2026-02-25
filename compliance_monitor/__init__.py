"""Blockchain Compliance Monitor - Main module."""

from .monitor import ComplianceMonitor
from .config import ComplianceConfig
from .kyc import KYCVerifier
from .sanctions import SanctionsScreener
from .risk import RiskEngine

__version__ = "1.0.0"
__all__ = [
    "ComplianceMonitor",
    "ComplianceConfig",
    "KYCVerifier",
    "SanctionsScreener",
    "RiskEngine"
]