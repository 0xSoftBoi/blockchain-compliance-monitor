"""Banking systems integration adapter."""
import logging
from typing import Dict, List, Optional
import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)


class BankingIntegration:
    """Integration adapter for traditional banking systems.
    
    Supports:
    - Account verification
    - Balance checks
    - Payment initiation
    - Transaction history
    - Compliance data exchange
    """
    
    def __init__(self):
        self.api_url = settings.BANKING_API_URL if hasattr(settings, 'BANKING_API_URL') else ""
        self.api_key = settings.BANKING_API_KEY if hasattr(settings, 'BANKING_API_KEY') else ""
        self.enabled = settings.BANKING_API_ENABLED if hasattr(settings, 'BANKING_API_ENABLED') else False
    
    async def verify_account(
        self,
        account_number: str,
        routing_number: str,
        account_holder: str,
    ) -> Dict:
        """Verify bank account details.
        
        Args:
            account_number: Bank account number
            routing_number: Bank routing number
            account_holder: Account holder name
            
        Returns:
            Verification result
        """
        if not self.enabled:
            logger.warning("Banking integration disabled")
            return {"verified": False, "error": "Integration disabled"}
        
        logger.info(f"Verifying bank account: {account_number[-4:]}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/verify/account",
                    json={
                        "account_number": account_number,
                        "routing_number": routing_number,
                        "account_holder": account_holder,
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Banking API error: {e}", exc_info=True)
            return {"verified": False, "error": str(e)}
    
    async def initiate_payment(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        currency: str,
        reference: str,
    ) -> Dict:
        """Initiate bank payment."""
        if not self.enabled:
            return {"success": False, "error": "Integration disabled"}
        
        logger.info(f"Initiating payment: {amount} {currency}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/payments/initiate",
                    json={
                        "from_account": from_account,
                        "to_account": to_account,
                        "amount": amount,
                        "currency": currency,
                        "reference": reference,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Payment initiation error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def get_transaction_history(
        self,
        account_number: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict]:
        """Get transaction history for an account."""
        if not self.enabled:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/accounts/{account_number}/transactions",
                    params={
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=15.0,
                )
                response.raise_for_status()
                return response.json().get("transactions", [])
        except Exception as e:
            logger.error(f"Transaction history error: {e}", exc_info=True)
            return []


# Global banking integration instance
banking_integration = BankingIntegration()
