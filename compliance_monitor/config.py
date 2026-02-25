"""Configuration for compliance monitoring."""

from dataclasses import dataclass
from typing import List


@dataclass
class ComplianceConfig:
    """Compliance monitoring configuration."""
    
    # Jurisdictions to monitor
    jurisdictions: List[str] = None
    
    # Risk thresholds
    risk_threshold: float = 0.7
    
    # Sanctions screening
    enable_sanctions_screening: bool = True
    sanctions_lists: List[str] = None
    
    # KYC settings
    kyc_required: bool = True
    kyc_refresh_days: int = 365
    
    # Reporting
    auto_file_sar: bool = False
    sar_threshold: float = 0.85
    ctr_threshold_usd: int = 10000
    
    # Institution details
    institution_name: str = "Global Settlement"
    
    def __post_init__(self):
        if self.jurisdictions is None:
            self.jurisdictions = ['US', 'EU']
        
        if self.sanctions_lists is None:
            self.sanctions_lists = ['OFAC_SDN', 'EU_SANCTIONS', 'UN_SANCTIONS']