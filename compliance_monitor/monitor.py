"""Main compliance monitoring engine."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from .config import ComplianceConfig
from .kyc import KYCVerifier
from .sanctions import SanctionsScreener
from .risk import RiskEngine

logger = logging.getLogger(__name__)


@dataclass
class TransactionScreeningResult:
    """Result of transaction screening."""
    transaction_hash: str
    timestamp: datetime
    risk_score: float
    risk_level: str  # low, medium, high, critical
    risk_factors: List[str]
    sanctions_match: bool
    requires_review: bool
    approved: bool
    notes: str


class ComplianceMonitor:
    """Main compliance monitoring system."""
    
    def __init__(self, config: ComplianceConfig):
        self.config = config
        self.kyc_verifier = KYCVerifier()
        self.sanctions_screener = SanctionsScreener()
        self.risk_engine = RiskEngine(config)
        
        logger.info(f"Compliance Monitor initialized for jurisdictions: {config.jurisdictions}")
    
    def screen_transaction(
        self,
        transaction_hash: str,
        from_address: str,
        to_address: str,
        amount: int,  # Amount in smallest units (e.g., cents, wei)
        currency: str,
        metadata: Optional[Dict] = None
    ) -> TransactionScreeningResult:
        """Screen a blockchain transaction for compliance.
        
        Args:
            transaction_hash: Transaction hash
            from_address: Sender address
            to_address: Recipient address
            amount: Amount in smallest units
            currency: Currency code
            metadata: Additional transaction metadata
            
        Returns:
            TransactionScreeningResult with compliance decision
        """
        logger.info(f"Screening transaction {transaction_hash}")
        
        metadata = metadata or {}
        risk_factors = []
        
        # 1. Sanctions Screening
        sender_sanctions = self.sanctions_screener.screen_address(from_address)
        recipient_sanctions = self.sanctions_screener.screen_address(to_address)
        
        sanctions_match = sender_sanctions.is_sanctioned or recipient_sanctions.is_sanctioned
        
        if sanctions_match:
            risk_factors.append("SANCTIONED_ENTITY")
            logger.warning(f"Sanctions match for transaction {transaction_hash}")
        
        # 2. Risk Scoring
        risk_score = self.risk_engine.calculate_transaction_risk(
            amount=amount,
            currency=currency,
            sender_address=from_address,
            recipient_address=to_address,
            sender_country=metadata.get('sender_country'),
            recipient_country=metadata.get('recipient_country')
        )
        
        # 3. Determine risk level
        if risk_score >= 0.8 or sanctions_match:
            risk_level = "critical"
        elif risk_score >= 0.6:
            risk_level = "high"
        elif risk_score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # 4. Add risk factors
        if amount > 10000_00:  # $10,000 in cents
            risk_factors.append("LARGE_TRANSACTION")
        
        if metadata.get('sender_country') in ['XX', 'Unknown']:
            risk_factors.append("UNKNOWN_JURISDICTION")
        
        # 5. Compliance decision
        requires_review = risk_score >= self.config.risk_threshold or sanctions_match
        approved = not requires_review
        
        result = TransactionScreeningResult(
            transaction_hash=transaction_hash,
            timestamp=datetime.now(),
            risk_score=risk_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            sanctions_match=sanctions_match,
            requires_review=requires_review,
            approved=approved,
            notes=f"Screened against {len(self.config.jurisdictions)} jurisdictions"
        )
        
        # 6. Log if high risk
        if requires_review:
            logger.warning(
                f"Transaction {transaction_hash} requires review: "
                f"Risk={risk_score:.2f}, Factors={risk_factors}"
            )
        
        return result
    
    def generate_sar(
        self,
        transaction_ids: List[str],
        suspicious_activity: List[str],
        narrative: str
    ) -> Dict:
        """Generate Suspicious Activity Report (SAR).
        
        Args:
            transaction_ids: List of suspicious transaction IDs
            suspicious_activity: List of activity types
            narrative: Detailed narrative description
            
        Returns:
            SAR data structure
        """
        sar = {
            "report_id": f"SAR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "filing_date": datetime.now().isoformat(),
            "transactions": transaction_ids,
            "suspicious_activities": suspicious_activity,
            "narrative": narrative,
            "filing_institution": self.config.institution_name,
            "jurisdiction": "US",
            "status": "pending_review"
        }
        
        logger.info(f"Generated SAR: {sar['report_id']}")
        return sar
    
    def get_compliance_status(self, address: str) -> Dict:
        """Get overall compliance status for an address.
        
        Args:
            address: Blockchain address
            
        Returns:
            Compliance status dictionary
        """
        sanctions_result = self.sanctions_screener.screen_address(address)
        risk_profile = self.risk_engine.get_address_risk_profile(address)
        
        return {
            "address": address,
            "sanctioned": sanctions_result.is_sanctioned,
            "risk_level": risk_profile.get('risk_level', 'unknown'),
            "kyc_status": "pending",  # Would check KYC database
            "cleared_for_trading": not sanctions_result.is_sanctioned
        }