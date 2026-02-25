"""Sanctions screening module."""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


@dataclass
class SanctionsScreeningResult:
    """Result of sanctions screening."""
    entity: str
    is_sanctioned: bool
    matching_lists: List[str]
    confidence: float
    details: Optional[Dict] = None


class SanctionsScreener:
    """Sanctions list screening system."""
    
    def __init__(self):
        # In production, these would be loaded from official sources
        self.ofac_list = self._load_ofac_list()
        self.eu_sanctions = self._load_eu_sanctions()
        self.un_sanctions = self._load_un_sanctions()
        
        logger.info("Sanctions Screener initialized")
    
    def screen_entity(
        self,
        name: str,
        address: Optional[str] = None,
        country: Optional[str] = None,
        entity_type: str = "individual"
    ) -> SanctionsScreeningResult:
        """Screen an entity against sanctions lists.
        
        Args:
            name: Entity name
            address: Physical address
            country: Country code
            entity_type: Type of entity (individual, corporation, etc)
            
        Returns:
            SanctionsScreeningResult
        """
        logger.info(f"Screening entity: {name}")
        
        matching_lists = []
        
        # Check OFAC list
        if self._check_ofac(name, country):
            matching_lists.append("OFAC_SDN")
        
        # Check EU sanctions
        if self._check_eu(name, country):
            matching_lists.append("EU_SANCTIONS")
        
        # Check UN sanctions
        if self._check_un(name, country):
            matching_lists.append("UN_SANCTIONS")
        
        is_sanctioned = len(matching_lists) > 0
        confidence = 1.0 if is_sanctioned else 0.0
        
        if is_sanctioned:
            logger.warning(f"SANCTIONS MATCH: {name} on lists: {matching_lists}")
        
        return SanctionsScreeningResult(
            entity=name,
            is_sanctioned=is_sanctioned,
            matching_lists=matching_lists,
            confidence=confidence,
            details={
                'country': country,
                'entity_type': entity_type,
                'screened_at': datetime.now().isoformat()
            }
        )
    
    def screen_address(self, blockchain_address: str) -> SanctionsScreeningResult:
        """Screen a blockchain address.
        
        Args:
            blockchain_address: Blockchain address to screen
            
        Returns:
            SanctionsScreeningResult
        """
        # In production, would check against known sanctioned addresses
        # For now, check if address is in our known sanctioned list
        
        is_sanctioned = blockchain_address.lower() in self.ofac_list.get('addresses', [])
        
        return SanctionsScreeningResult(
            entity=blockchain_address,
            is_sanctioned=is_sanctioned,
            matching_lists=["OFAC_CRYPTO"] if is_sanctioned else [],
            confidence=1.0 if is_sanctioned else 0.0
        )
    
    def _check_ofac(self, name: str, country: Optional[str]) -> bool:
        """Check against OFAC SDN list."""
        # Simplified check - in production would use fuzzy matching
        name_normalized = name.lower()
        
        for sanctioned_name in self.ofac_list.get('names', []):
            if sanctioned_name.lower() in name_normalized:
                return True
        
        # Check country
        if country and country in self.ofac_list.get('countries', []):
            return True
        
        return False
    
    def _check_eu(self, name: str, country: Optional[str]) -> bool:
        """Check against EU sanctions list."""
        name_normalized = name.lower()
        
        for sanctioned_name in self.eu_sanctions.get('names', []):
            if sanctioned_name.lower() in name_normalized:
                return True
        
        return False
    
    def _check_un(self, name: str, country: Optional[str]) -> bool:
        """Check against UN sanctions list."""
        name_normalized = name.lower()
        
        for sanctioned_name in self.un_sanctions.get('names', []):
            if sanctioned_name.lower() in name_normalized:
                return True
        
        return False
    
    def _load_ofac_list(self) -> Dict:
        """Load OFAC SDN list."""
        # In production, would fetch from official OFAC API
        return {
            'names': [
                'Specially Designated National',
                # More sanctioned entities
            ],
            'countries': ['KP', 'IR', 'SY'],  # North Korea, Iran, Syria
            'addresses': [
                '0x1234567890abcdef1234567890abcdef12345678',  # Example
            ]
        }
    
    def _load_eu_sanctions(self) -> Dict:
        """Load EU sanctions list."""
        return {
            'names': [
                # Sanctioned entities
            ],
            'countries': []
        }
    
    def _load_un_sanctions(self) -> Dict:
        """Load UN sanctions list."""
        return {
            'names': [
                # Sanctioned entities
            ],
            'countries': []
        }