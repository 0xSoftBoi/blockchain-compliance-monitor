"""Logging configuration."""
import logging
import sys
from typing import Any
from backend.core.config import settings


def setup_logging() -> None:
    """Configure application logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Root logger configuration
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/compliance.log", mode="a"),
        ],
    )
    
    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {settings.LOG_LEVEL} level")


class ComplianceLogger:
    """Compliance-specific logger with structured logging."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_transaction(self, tx_hash: str, action: str, metadata: dict[str, Any]) -> None:
        """Log transaction-related events."""
        self.logger.info(
            f"Transaction {action}: {tx_hash}",
            extra={"tx_hash": tx_hash, "action": action, **metadata}
        )
    
    def log_alert(self, alert_type: str, severity: str, details: dict[str, Any]) -> None:
        """Log compliance alerts."""
        log_func = getattr(self.logger, severity.lower(), self.logger.info)
        log_func(
            f"Compliance Alert [{alert_type}]",
            extra={"alert_type": alert_type, "severity": severity, **details}
        )
    
    def log_audit(self, action: str, user: str, resource: str, metadata: dict[str, Any]) -> None:
        """Log audit trail events."""
        self.logger.info(
            f"Audit: {action} by {user} on {resource}",
            extra={"action": action, "user": user, "resource": resource, **metadata}
        )
