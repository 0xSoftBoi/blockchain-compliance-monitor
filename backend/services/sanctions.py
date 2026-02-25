"""Sanctions screening service."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import hashlib

from backend.core.config import settings

logger = logging.getLogger(__name__)


class SanctionsService:
    """Sanctions list screening service.
    
    Integrates with multiple sanctions lists:
    - OFAC (US Treasury)
    - EU Sanctions
    - UN Sanctions
    - National sanctions lists
    """
    
    def __init__(self):
        self._ofac_list: Set[str] = set()
        self._eu_list: Set[str] = set()
        self._un_list: Set[str] = set()
        self._last_update: Optional[datetime] = None
        self._cache: Dict[str, bool] = {}  # Address -> sanctioned status
        self._update_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize sanctions lists."""
        logger.info("Initializing sanctions screening service")
        
        # Initial load
        await self._refresh_lists()
        
        # Start periodic refresh task
        self._update_task = asyncio.create_task(self._periodic_refresh())
        
        logger.info(
            f"Sanctions lists initialized: "
            f"OFAC={len(self._ofac_list)}, EU={len(self._eu_list)}, UN={len(self._un_list)}"
        )
    
    async def _periodic_refresh(self):
        """Periodically refresh sanctions lists."""
        while True:
            try:
                await asyncio.sleep(settings.OFAC_REFRESH_INTERVAL_HOURS * 3600)
                await self._refresh_lists()
            except Exception as e:
                logger.error(f"Error in periodic sanctions refresh: {e}", exc_info=True)
    
    async def _refresh_lists(self):
        """Refresh all sanctions lists from sources."""
        logger.info("Refreshing sanctions lists...")
        
        try:
            # In production, these would make actual API calls
            # to OFAC, EU, UN sanctions databases
            
            if settings.OFAC_SCREENING_ENABLED:
                await self._refresh_ofac()
            
            if settings.EU_SANCTIONS_ENABLED:
                await self._refresh_eu()
            
            await self._refresh_un()
            
            self._last_update = datetime.utcnow()
            self._cache.clear()  # Clear cache after update
            
            logger.info("Sanctions lists refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing sanctions lists: {e}", exc_info=True)
    
    async def _refresh_ofac(self):
        """Refresh OFAC sanctions list."""
        # Placeholder - in production, this would:
        # 1. Download SDN list from OFAC
        # 2. Parse XML/CSV data
        # 3. Extract cryptocurrency addresses
        # 4. Update internal list
        
        # Example sanctioned addresses (for demonstration)
        example_sanctioned = {
            "0x7Db418b5D567A4e0E8c59Ad71BE1FcE48f3E6107",  # Example North Korea linked
            "0x19Aa5Fe80D33a56D56c78e82eA5E50E5d80b4Dff",  # Example ransomware
        }
        
        self._ofac_list.update(example_sanctioned)
        logger.debug(f"OFAC list updated: {len(self._ofac_list)} entries")
    
    async def _refresh_eu(self):
        """Refresh EU sanctions list."""
        # Placeholder - in production, connect to EU sanctions API
        example_sanctioned = set()
        self._eu_list.update(example_sanctioned)
        logger.debug(f"EU list updated: {len(self._eu_list)} entries")
    
    async def _refresh_un(self):
        """Refresh UN sanctions list."""
        # Placeholder - in production, connect to UN sanctions API
        example_sanctioned = set()
        self._un_list.update(example_sanctioned)
        logger.debug(f"UN list updated: {len(self._un_list)} entries")
    
    async def is_sanctioned(self, address: str) -> bool:
        """Check if an address is on any sanctions list.
        
        Args:
            address: Blockchain address to check
            
        Returns:
            True if address is sanctioned, False otherwise
        """
        # Normalize address
        address = address.lower()
        
        # Check cache first
        if address in self._cache:
            return self._cache[address]
        
        # Check all lists
        is_sanctioned = (
            address in self._ofac_list or
            address in self._eu_list or
            address in self._un_list
        )
        
        # Cache result
        self._cache[address] = is_sanctioned
        
        if is_sanctioned:
            logger.warning(f"SANCTIONS HIT: Address {address} is on sanctions list")
        
        return is_sanctioned
    
    async def batch_screen(self, addresses: List[str]) -> Dict[str, bool]:
        """Screen multiple addresses at once.
        
        Args:
            addresses: List of addresses to screen
            
        Returns:
            Dictionary mapping address to sanctioned status
        """
        results = {}
        for address in addresses:
            results[address] = await self.is_sanctioned(address)
        return results
    
    async def get_list_info(self) -> Dict:
        """Get information about sanctions lists.
        
        Returns:
            Dictionary with list sizes and last update time
        """
        return {
            "ofac_entries": len(self._ofac_list),
            "eu_entries": len(self._eu_list),
            "un_entries": len(self._un_list),
            "total_entries": len(self._ofac_list) + len(self._eu_list) + len(self._un_list),
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "cache_size": len(self._cache),
        }


# Global sanctions service instance
sanctions_service = SanctionsService()
