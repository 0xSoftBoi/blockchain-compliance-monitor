"""Blockchain network integration adapter."""
import logging
from typing import Dict, List, Optional
from web3 import Web3
from web3.exceptions import TransactionNotFound

from backend.core.config import settings

logger = logging.getLogger(__name__)


class BlockchainIntegration:
    """Integration with multiple blockchain networks.
    
    Supports:
    - Ethereum and EVM chains
    - Transaction monitoring
    - Balance queries
    - Smart contract interaction
    """
    
    def __init__(self):
        self.networks = {
            "ethereum": Web3(Web3.HTTPProvider(settings.ETH_RPC_URL)),
            "bsc": Web3(Web3.HTTPProvider(settings.BSC_RPC_URL)),
            "polygon": Web3(Web3.HTTPProvider(settings.POLYGON_RPC_URL)),
            "arbitrum": Web3(Web3.HTTPProvider(settings.ARBITRUM_RPC_URL)),
            "optimism": Web3(Web3.HTTPProvider(settings.OPTIMISM_RPC_URL)),
        }
    
    async def get_transaction(self, tx_hash: str, network: str = "ethereum") -> Optional[Dict]:
        """Get transaction details from blockchain.
        
        Args:
            tx_hash: Transaction hash
            network: Blockchain network name
            
        Returns:
            Transaction details or None
        """
        try:
            w3 = self.networks.get(network)
            if not w3:
                logger.error(f"Unsupported network: {network}")
                return None
            
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                "hash": tx_hash,
                "from": tx["from"],
                "to": tx["to"],
                "value": float(w3.from_wei(tx["value"], "ether")),
                "gas_used": receipt["gasUsed"],
                "status": receipt["status"],
                "block_number": tx["blockNumber"],
                "timestamp": w3.eth.get_block(tx["blockNumber"])["timestamp"],
            }
        except TransactionNotFound:
            logger.warning(f"Transaction not found: {tx_hash}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transaction: {e}", exc_info=True)
            return None
    
    async def get_address_balance(self, address: str, network: str = "ethereum") -> float:
        """Get balance for an address."""
        try:
            w3 = self.networks.get(network)
            if not w3:
                return 0.0
            
            balance_wei = w3.eth.get_balance(address)
            return float(w3.from_wei(balance_wei, "ether"))
        except Exception as e:
            logger.error(f"Error fetching balance: {e}", exc_info=True)
            return 0.0
    
    async def monitor_address(
        self,
        address: str,
        network: str = "ethereum",
        from_block: int = "latest",
    ) -> List[Dict]:
        """Monitor transactions for an address."""
        try:
            w3 = self.networks.get(network)
            if not w3:
                return []
            
            # Get recent blocks
            if from_block == "latest":
                from_block = w3.eth.block_number - 100
            
            transactions = []
            for block_num in range(from_block, w3.eth.block_number + 1):
                block = w3.eth.get_block(block_num, full_transactions=True)
                for tx in block["transactions"]:
                    if tx["from"].lower() == address.lower() or (
                        tx["to"] and tx["to"].lower() == address.lower()
                    ):
                        transactions.append({
                            "hash": tx["hash"].hex(),
                            "from": tx["from"],
                            "to": tx["to"],
                            "value": float(w3.from_wei(tx["value"], "ether")),
                            "block_number": block_num,
                        })
            
            return transactions
        except Exception as e:
            logger.error(f"Error monitoring address: {e}", exc_info=True)
            return []


# Global blockchain integration instance
blockchain_integration = BlockchainIntegration()
