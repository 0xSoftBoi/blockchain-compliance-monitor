"""SWIFT network integration adapter."""
import logging
from typing import Dict, Optional
from datetime import datetime
import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)


class SWIFTIntegration:
    """Integration with SWIFT messaging network.
    
    Supports:
    - ISO 20022 message formatting
    - SWIFT API connectivity
    - Payment status tracking
    - Compliance data exchange
    """
    
    def __init__(self):
        self.api_url = settings.SWIFT_API_URL
        self.bic = settings.SWIFT_INSTITUTION_BIC
        self.api_key = settings.SWIFT_API_KEY
        self.enabled = settings.SWIFT_INTEGRATION_ENABLED
        
    async def send_payment_message(
        self,
        message_type: str,
        debtor: Dict,
        creditor: Dict,
        amount: float,
        currency: str,
        remittance_info: Optional[str] = None,
    ) -> Dict:
        """Send SWIFT payment message.
        
        Args:
            message_type: SWIFT message type (e.g., 'MT103', 'pacs.008')
            debtor: Debtor information
            creditor: Creditor information
            amount: Payment amount
            currency: Currency code (ISO 4217)
            remittance_info: Remittance information
            
        Returns:
            SWIFT message response
        """
        if not self.enabled:
            logger.warning("SWIFT integration disabled")
            return {"error": "SWIFT integration disabled"}
        
        logger.info(f"Sending SWIFT {message_type} message")
        
        # Format message according to ISO 20022
        message = self._format_iso20022_message(
            message_type, debtor, creditor, amount, currency, remittance_info
        )
        
        # Send via SWIFT API
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/messages",
                    json=message,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-SWIFT-BIC": self.bic,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"SWIFT API error: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _format_iso20022_message(
        self,
        message_type: str,
        debtor: Dict,
        creditor: Dict,
        amount: float,
        currency: str,
        remittance_info: Optional[str],
    ) -> Dict:
        """Format message according to ISO 20022 standard."""
        return {
            "message_type": message_type,
            "group_header": {
                "message_id": f"MSG{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "creation_date_time": datetime.utcnow().isoformat(),
                "initiating_party": {
                    "name": "Global Settlement",
                    "bic": self.bic,
                },
            },
            "payment_information": {
                "payment_id": f"PMT{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "payment_method": "TRF",
                "debtor": debtor,
                "debtor_account": debtor.get("account"),
                "creditor": creditor,
                "creditor_account": creditor.get("account"),
                "instructed_amount": {
                    "amount": amount,
                    "currency": currency,
                },
                "remittance_information": remittance_info,
            },
        }
    
    async def get_payment_status(self, message_id: str) -> Dict:
        """Get payment status from SWIFT network."""
        if not self.enabled:
            return {"error": "SWIFT integration disabled"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/messages/{message_id}/status",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-SWIFT-BIC": self.bic,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"SWIFT status check error: {e}", exc_info=True)
            return {"error": str(e)}


# Global SWIFT integration instance
swift_integration = SWIFTIntegration()
