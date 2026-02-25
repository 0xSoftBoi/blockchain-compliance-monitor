"""Risk scoring engine."""

from typing import Dict, Optional
import logging

from .config import ComplianceConfig

logger = logging.getLogger(__name__)


class RiskEngine:
    """Risk assessment engine for transactions and entities."""
    
    def __init__(self, config: ComplianceConfig):
        self.config = config
        self.address_risk_cache = {}
        logger.info("Risk Engine initialized")
    
    def calculate_transaction_risk(
        self,
        amount: int,
        currency: str,
        sender_address: str,
        recipient_address: str,
        sender_country: Optional[str] = None,
        recipient_country: Optional[str] = None
    ) -> float:
        """Calculate risk score for a transaction.
        
        Args:
            amount: Transaction amount in smallest units
            currency: Currency code
            sender_address: Sender blockchain address
            recipient_address: Recipient blockchain address
            sender_country: Sender country code
            recipient_country: Recipient country code
            
        Returns:
            Risk score between 0.0 (low risk) and 1.0 (high risk)
        """
        risk_factors = []
        
        # 1. Amount risk (0-0.3)
        amount_risk = self._calculate_amount_risk(amount, currency)
        risk_factors.append(('amount', amount_risk, 0.3))
        
        # 2. Geographic risk (0-0.3)
        geo_risk = self._calculate_geographic_risk(sender_country, recipient_country)
        risk_factors.append(('geographic', geo_risk, 0.3))
        
        # 3. Counterparty risk (0-0.2)
        sender_risk = self.get_address_risk(sender_address)
        recipient_risk = self.get_address_risk(recipient_address)
        counterparty_risk = max(sender_risk, recipient_risk)
        risk_factors.append(('counterparty', counterparty_risk, 0.2))
        
        # 4. Behavioral risk (0-0.2)
        behavioral_risk = self._calculate_behavioral_risk(sender_address)
        risk_factors.append(('behavioral', behavioral_risk, 0.2))
        
        # Calculate weighted score
        total_risk = sum(score * weight for _, score, weight in risk_factors)
        
        logger.debug(f"Transaction risk calculated: {total_risk:.3f}")
        return min(total_risk, 1.0)
    
    def _calculate_amount_risk(self, amount: int, currency: str) -> float:
        """Calculate risk based on transaction amount."""
        # Convert to USD equivalent (simplified)
        amount_usd = amount / 100  # Assuming amount is in cents
        
        if currency != "USD":
            # In production, would use real exchange rates
            amount_usd = amount / 100
        
        # Risk tiers
        if amount_usd >= 100_000:
            return 1.0
        elif amount_usd >= 50_000:
            return 0.7
        elif amount_usd >= 10_000:
            return 0.4
        elif amount_usd >= 5_000:
            return 0.2
        else:
            return 0.1
    
    def _calculate_geographic_risk(self, sender_country: Optional[str], recipient_country: Optional[str]) -> float:
        """Calculate risk based on geographic factors."""
        high_risk_countries = ['KP', 'IR', 'SY', 'CU', 'VE']
        medium_risk_countries = ['RU', 'BY']
        
        risk = 0.0
        
        for country in [sender_country, recipient_country]:
            if not country or country == 'Unknown':
                risk = max(risk, 0.5)  # Unknown origin is risky
            elif country in high_risk_countries:
                risk = max(risk, 1.0)
            elif country in medium_risk_countries:
                risk = max(risk, 0.6)
        
        return risk
    
    def _calculate_behavioral_risk(self, address: str) -> float:
        """Calculate risk based on behavioral patterns."""
        # In production, would analyze:
        # - Transaction frequency
        # - Transaction timing patterns
        # - Relationship to known entities
        # - Historical compliance issues
        
        # Simplified version
        if address in self.address_risk_cache:
            return self.address_risk_cache[address].get('behavioral_risk', 0.1)
        
        return 0.1  # Default low risk
    
    def get_address_risk(self, address: str) -> float:
        """Get cached risk score for an address."""
        if address in self.address_risk_cache:
            return self.address_risk_cache[address].get('risk_score', 0.0)
        
        # Default risk for new addresses
        return 0.2
    
    def get_address_risk_profile(self, address: str) -> Dict:
        """Get detailed risk profile for an address."""
        if address in self.address_risk_cache:
            return self.address_risk_cache[address]
        
        return {
            'address': address,
            'risk_score': 0.2,
            'risk_level': 'low',
            'transaction_count': 0,
            'first_seen': None,
            'last_seen': None
        }
    
    def update_address_risk(self, address: str, risk_data: Dict):
        """Update risk profile for an address."""
        self.address_risk_cache[address] = risk_data
        logger.info(f"Updated risk profile for {address}")