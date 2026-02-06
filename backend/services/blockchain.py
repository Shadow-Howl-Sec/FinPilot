import json
import hashlib
from datetime import datetime
from typing import Optional

class BlockchainVerifier:
    """Blockchain verification for transactions"""

    @staticmethod
    def generate_hash(transaction_id: int, user_id: int, amount: float, 
                     description: str, timestamp: datetime, previous_hash: Optional[str] = None) -> str:
        """Generate SHA256 hash of transaction"""
        transaction_data = {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "amount": amount,
            "description": description,
            "timestamp": timestamp.isoformat(),
            "previous_hash": previous_hash or "genesis"
        }
        json_data = json.dumps(transaction_data, sort_keys=True)
        hash_object = hashlib.sha256(json_data.encode())
        return hash_object.hexdigest()

    @staticmethod
    def verify_transaction(blockchain_hash: str, transaction_id: int, user_id: int,
                          amount: float, description: str, timestamp: datetime,
                          previous_hash: Optional[str] = None) -> bool:
        """Verify transaction integrity"""
        calculated_hash = BlockchainVerifier.generate_hash(
            transaction_id, user_id, amount, description, timestamp, previous_hash
        )
        return calculated_hash == blockchain_hash
