"""Real-time transaction monitoring service."""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
import hashlib

from backend.core.config import settings
from backend.services.sanctions import sanctions_service
from backend.services.risk_engine import risk_engine

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Types of compliance alerts."""
    SANCTIONS_HIT = "sanctions_hit"
    HIGH_RISK_ENTITY = "high_risk_entity"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    STRUCTURING_DETECTED = "structuring_detected"
    RAPID_MOVEMENT = "rapid_movement"
    LAYERING_DETECTED = "layering_detected"
    UNUSUAL_BEHAVIOR = "unusual_behavior"


@dataclass
class Transaction:
    """Transaction data model."""
    tx_hash: str
    from_address: str
    to_address: str
    value_usd: float
    blockchain: str
    timestamp: datetime
    token_symbol: Optional[str] = None
    contract_address: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class ComplianceAlert:
    """Compliance alert data model."""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    transaction: Transaction
    description: str
    risk_score: int
    recommended_action: str
    created_at: datetime
    metadata: Optional[Dict] = None


class MonitoringService:
    """Real-time blockchain transaction monitoring service."""
    
    def __init__(self):
        self.active_alerts: List[ComplianceAlert] = []
        self.monitoring_active = False
        self.transaction_queue: asyncio.Queue = asyncio.Queue(
            maxsize=settings.TRANSACTION_QUEUE_SIZE
        )
        self._monitor_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the monitoring service."""
        if not settings.MONITORING_ENABLED:
            logger.info("Monitoring service disabled by configuration")
            return
            
        self.monitoring_active = True
        self._monitor_task = asyncio.create_task(self._process_queue())
        logger.info("Transaction monitoring service started")
    
    async def stop(self):
        """Stop the monitoring service."""
        self.monitoring_active = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Transaction monitoring service stopped")
    
    async def submit_transaction(self, transaction: Transaction) -> str:
        """Submit a transaction for compliance monitoring.
        
        Args:
            transaction: Transaction data to monitor
            
        Returns:
            Monitoring ID for tracking
        """
        monitoring_id = hashlib.sha256(
            f"{transaction.tx_hash}{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        await self.transaction_queue.put((monitoring_id, transaction))
        logger.info(f"Transaction {transaction.tx_hash} queued for monitoring (ID: {monitoring_id})")
        
        return monitoring_id
    
    async def _process_queue(self):
        """Process transaction queue continuously."""
        logger.info("Transaction queue processor started")
        
        while self.monitoring_active:
            try:
                # Get transaction from queue with timeout
                try:
                    monitoring_id, transaction = await asyncio.wait_for(
                        self.transaction_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Process transaction
                await self._analyze_transaction(monitoring_id, transaction)
                
            except Exception as e:
                logger.error(f"Error processing transaction queue: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _analyze_transaction(self, monitoring_id: str, transaction: Transaction):
        """Analyze transaction for compliance issues.
        
        Args:
            monitoring_id: Unique monitoring identifier
            transaction: Transaction to analyze
        """
        logger.debug(f"Analyzing transaction {transaction.tx_hash}")
        
        alerts = []
        
        # 1. Sanctions screening
        if settings.OFAC_SCREENING_ENABLED:
            sanctions_results = await self._check_sanctions(transaction)
            alerts.extend(sanctions_results)
        
        # 2. Risk scoring
        if settings.RISK_SCORING_ENABLED:
            risk_alerts = await self._check_risk(transaction)
            alerts.extend(risk_alerts)
        
        # 3. Threshold checking
        threshold_alerts = self._check_thresholds(transaction)
        alerts.extend(threshold_alerts)
        
        # 4. Pattern detection
        if settings.SUSPICIOUS_PATTERN_DETECTION:
            pattern_alerts = await self._detect_patterns(transaction)
            alerts.extend(pattern_alerts)
        
        # 5. Behavioral analysis
        if settings.BEHAVIORAL_ANALYSIS_ENABLED:
            behavior_alerts = await self._analyze_behavior(transaction)
            alerts.extend(behavior_alerts)
        
        # Store alerts
        for alert in alerts:
            self.active_alerts.append(alert)
            logger.warning(
                f"Alert generated: {alert.alert_type.value} - "
                f"{alert.severity.value} - {transaction.tx_hash}"
            )
        
        if not alerts:
            logger.debug(f"Transaction {transaction.tx_hash} passed all checks")
    
    async def _check_sanctions(self, transaction: Transaction) -> List[ComplianceAlert]:
        """Check transaction addresses against sanctions lists."""
        alerts = []
        
        # Check sender
        if await sanctions_service.is_sanctioned(transaction.from_address):
            alerts.append(ComplianceAlert(
                id=self._generate_alert_id(),
                alert_type=AlertType.SANCTIONS_HIT,
                severity=AlertSeverity.CRITICAL,
                transaction=transaction,
                description=f"Sender address {transaction.from_address} is on sanctions list",
                risk_score=100,
                recommended_action="BLOCK transaction and file SAR immediately",
                created_at=datetime.utcnow(),
                metadata={"sanctioned_party": transaction.from_address}
            ))
        
        # Check receiver
        if await sanctions_service.is_sanctioned(transaction.to_address):
            alerts.append(ComplianceAlert(
                id=self._generate_alert_id(),
                alert_type=AlertType.SANCTIONS_HIT,
                severity=AlertSeverity.CRITICAL,
                transaction=transaction,
                description=f"Recipient address {transaction.to_address} is on sanctions list",
                risk_score=100,
                recommended_action="BLOCK transaction and file SAR immediately",
                created_at=datetime.utcnow(),
                metadata={"sanctioned_party": transaction.to_address}
            ))
        
        return alerts
    
    async def _check_risk(self, transaction: Transaction) -> List[ComplianceAlert]:
        """Check risk scores for transaction parties."""
        alerts = []
        
        # Score sender
        sender_risk = await risk_engine.score_address(transaction.from_address)
        if sender_risk >= settings.HIGH_RISK_THRESHOLD:
            alerts.append(ComplianceAlert(
                id=self._generate_alert_id(),
                alert_type=AlertType.HIGH_RISK_ENTITY,
                severity=AlertSeverity.HIGH,
                transaction=transaction,
                description=f"High-risk sender (score: {sender_risk})",
                risk_score=sender_risk,
                recommended_action="Enhanced due diligence required",
                created_at=datetime.utcnow(),
                metadata={"address": transaction.from_address, "score": sender_risk}
            ))
        
        # Score receiver
        receiver_risk = await risk_engine.score_address(transaction.to_address)
        if receiver_risk >= settings.HIGH_RISK_THRESHOLD:
            alerts.append(ComplianceAlert(
                id=self._generate_alert_id(),
                alert_type=AlertType.HIGH_RISK_ENTITY,
                severity=AlertSeverity.HIGH,
                transaction=transaction,
                description=f"High-risk receiver (score: {receiver_risk})",
                risk_score=receiver_risk,
                recommended_action="Enhanced due diligence required",
                created_at=datetime.utcnow(),
                metadata={"address": transaction.to_address, "score": receiver_risk}
            ))
        
        return alerts
    
    def _check_thresholds(self, transaction: Transaction) -> List[ComplianceAlert]:
        """Check transaction against reporting thresholds."""
        alerts = []
        
        # BSA CTR threshold ($10,000)
        if transaction.value_usd >= settings.ALERT_THRESHOLD_USD:
            severity = AlertSeverity.MEDIUM
            if transaction.value_usd >= 50000:
                severity = AlertSeverity.HIGH
            
            alerts.append(ComplianceAlert(
                id=self._generate_alert_id(),
                alert_type=AlertType.THRESHOLD_EXCEEDED,
                severity=severity,
                transaction=transaction,
                description=f"Transaction exceeds reporting threshold: ${transaction.value_usd:,.2f}",
                risk_score=min(50 + int(transaction.value_usd / 10000), 90),
                recommended_action="File CTR if within 24-hour period aggregate",
                created_at=datetime.utcnow(),
                metadata={"threshold": settings.ALERT_THRESHOLD_USD}
            ))
        
        return alerts
    
    async def _detect_patterns(self, transaction: Transaction) -> List[ComplianceAlert]:
        """Detect suspicious transaction patterns."""
        alerts = []
        
        # Structuring detection (multiple transactions just under threshold)
        # Rapid movement detection
        # Layering detection
        # This would require historical transaction analysis
        
        # Placeholder for pattern detection logic
        # In production, this would query historical data and use ML models
        
        return alerts
    
    async def _analyze_behavior(self, transaction: Transaction) -> List[ComplianceAlert]:
        """Analyze behavioral patterns."""
        alerts = []
        
        # Behavioral analysis would include:
        # - Unusual transaction times
        # - Geographic anomalies
        # - Velocity checks
        # - Network analysis
        
        # Placeholder for behavioral analysis
        # In production, this would use ML models and historical baselines
        
        return alerts
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{len(self.active_alerts)}".encode()
        ).hexdigest()[:12]
    
    async def get_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        limit: int = 100
    ) -> List[ComplianceAlert]:
        """Retrieve compliance alerts.
        
        Args:
            severity: Filter by severity level
            alert_type: Filter by alert type
            limit: Maximum number of alerts to return
            
        Returns:
            List of compliance alerts
        """
        alerts = self.active_alerts[-limit:]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        
        return alerts


# Global monitoring service instance
monitoring_service = MonitoringService()
