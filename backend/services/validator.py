"""Smart contract compliance validation service."""
import logging
import re
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from backend.core.config import settings

logger = logging.getLogger(__name__)


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    MICA = "mica"  # EU Markets in Crypto-Assets
    BSA = "bsa"  # Bank Secrecy Act
    ISO20022 = "iso20022"  # Financial messaging standard
    WOLFSBERG = "wolfsberg"  # Wolfsberg AML principles
    FATF = "fatf"  # Financial Action Task Force
    GDPR = "gdpr"  # General Data Protection Regulation


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Smart contract validation issue."""
    severity: ValidationSeverity
    framework: ComplianceFramework
    rule_id: str
    description: str
    line_number: Optional[int] = None
    recommendation: Optional[str] = None
    regulation_reference: Optional[str] = None


@dataclass
class ValidationResult:
    """Complete validation result."""
    contract_address: Optional[str]
    source_code_hash: str
    timestamp: datetime
    frameworks_checked: List[ComplianceFramework]
    passed: bool
    issues: List[ValidationIssue]
    compliance_score: int  # 0-100
    metadata: Optional[Dict] = None


class SmartContractValidator:
    """Smart contract compliance validation service.
    
    Validates smart contracts against institutional compliance frameworks:
    - MiCA (EU)
    - Bank Secrecy Act (US)
    - ISO 20022 standards
    - Wolfsberg Group guidelines
    - FATF recommendations
    """
    
    def __init__(self):
        self._mica_rules = self._load_mica_rules()
        self._bsa_rules = self._load_bsa_rules()
        self._iso20022_rules = self._load_iso20022_rules()
        self._wolfsberg_rules = self._load_wolfsberg_rules()
    
    def _load_mica_rules(self) -> Dict:
        """Load MiCA compliance rules."""
        return {
            "transfer_limits": {
                "description": "Stablecoin transfers must have daily limits",
                "check": lambda code: "transferLimit" in code or "dailyLimit" in code,
            },
            "kyc_requirement": {
                "description": "KYC verification required for participants",
                "check": lambda code: "kyc" in code.lower() or "verified" in code.lower(),
            },
            "travel_rule": {
                "description": "Must implement Travel Rule for transfers > 1000 EUR",
                "check": lambda code: "travelRule" in code or "beneficiaryInfo" in code,
            },
            "reserve_backing": {
                "description": "Stablecoins must maintain reserve backing",
                "check": lambda code: "reserve" in code.lower() and "backing" in code.lower(),
            },
        }
    
    def _load_bsa_rules(self) -> Dict:
        """Load Bank Secrecy Act compliance rules."""
        return {
            "ctr_monitoring": {
                "description": "Monitor for Currency Transaction Report thresholds",
                "check": lambda code: "threshold" in code.lower() or "limit" in code.lower(),
            },
            "sar_flags": {
                "description": "Flag suspicious activity for SAR filing",
                "check": lambda code: "suspicious" in code.lower() or "flag" in code.lower(),
            },
            "recordkeeping": {
                "description": "Maintain transaction records",
                "check": lambda code: "record" in code.lower() or "log" in code.lower(),
            },
        }
    
    def _load_iso20022_rules(self) -> Dict:
        """Load ISO 20022 messaging standard rules."""
        return {
            "structured_data": {
                "description": "Use structured remittance information",
                "check": lambda code: "remittanceInformation" in code or "structuredData" in code,
            },
            "party_identification": {
                "description": "Include proper party identification",
                "check": lambda code: "debtor" in code.lower() and "creditor" in code.lower(),
            },
        }
    
    def _load_wolfsberg_rules(self) -> Dict:
        """Load Wolfsberg Group AML/CTF guidelines."""
        return {
            "customer_due_diligence": {
                "description": "Implement CDD procedures",
                "check": lambda code: "dueDiligence" in code or "cdd" in code.lower(),
            },
            "pep_screening": {
                "description": "Screen for Politically Exposed Persons",
                "check": lambda code: "pep" in code.lower() or "politicallyExposed" in code,
            },
        }
    
    async def validate_contract(
        self,
        source_code: str,
        frameworks: List[ComplianceFramework],
        contract_address: Optional[str] = None,
    ) -> ValidationResult:
        """Validate smart contract against compliance frameworks.
        
        Args:
            source_code: Smart contract source code
            frameworks: List of frameworks to validate against
            contract_address: Optional deployed contract address
            
        Returns:
            ValidationResult with all issues found
        """
        logger.info(f"Validating contract against frameworks: {frameworks}")
        
        issues: List[ValidationIssue] = []
        
        # Run framework-specific validations
        if ComplianceFramework.MICA in frameworks:
            issues.extend(await self._validate_mica(source_code))
        
        if ComplianceFramework.BSA in frameworks:
            issues.extend(await self._validate_bsa(source_code))
        
        if ComplianceFramework.ISO20022 in frameworks:
            issues.extend(await self._validate_iso20022(source_code))
        
        if ComplianceFramework.WOLFSBERG in frameworks:
            issues.extend(await self._validate_wolfsberg(source_code))
        
        # Common security checks
        issues.extend(await self._validate_security(source_code))
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(issues)
        
        # Determine if validation passed
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        passed = len(critical_issues) == 0 and compliance_score >= 70
        
        result = ValidationResult(
            contract_address=contract_address,
            source_code_hash=self._hash_source(source_code),
            timestamp=datetime.utcnow(),
            frameworks_checked=frameworks,
            passed=passed,
            issues=issues,
            compliance_score=compliance_score,
            metadata={
                "critical_issues": len(critical_issues),
                "error_issues": len([i for i in issues if i.severity == ValidationSeverity.ERROR]),
                "warning_issues": len([i for i in issues if i.severity == ValidationSeverity.WARNING]),
            }
        )
        
        logger.info(
            f"Validation complete: {'PASSED' if passed else 'FAILED'} - "
            f"Score: {compliance_score}/100 - Issues: {len(issues)}"
        )
        
        return result
    
    async def _validate_mica(self, source_code: str) -> List[ValidationIssue]:
        """Validate against MiCA requirements."""
        issues = []
        
        for rule_id, rule in self._mica_rules.items():
            if not rule["check"](source_code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    framework=ComplianceFramework.MICA,
                    rule_id=rule_id,
                    description=rule["description"],
                    recommendation=f"Implement {rule['description'].lower()}",
                    regulation_reference="MiCA Article 16-20",
                ))
        
        return issues
    
    async def _validate_bsa(self, source_code: str) -> List[ValidationIssue]:
        """Validate against BSA requirements."""
        issues = []
        
        for rule_id, rule in self._bsa_rules.items():
            if not rule["check"](source_code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    framework=ComplianceFramework.BSA,
                    rule_id=rule_id,
                    description=rule["description"],
                    recommendation=f"Add {rule['description'].lower()}",
                    regulation_reference="31 CFR 103",
                ))
        
        return issues
    
    async def _validate_iso20022(self, source_code: str) -> List[ValidationIssue]:
        """Validate against ISO 20022 standards."""
        issues = []
        
        for rule_id, rule in self._iso20022_rules.items():
            if not rule["check"](source_code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    framework=ComplianceFramework.ISO20022,
                    rule_id=rule_id,
                    description=rule["description"],
                    recommendation=f"Consider implementing {rule['description'].lower()}",
                    regulation_reference="ISO 20022 Message Standards",
                ))
        
        return issues
    
    async def _validate_wolfsberg(self, source_code: str) -> List[ValidationIssue]:
        """Validate against Wolfsberg principles."""
        issues = []
        
        for rule_id, rule in self._wolfsberg_rules.items():
            if not rule["check"](source_code):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    framework=ComplianceFramework.WOLFSBERG,
                    rule_id=rule_id,
                    description=rule["description"],
                    recommendation=f"Implement {rule['description'].lower()}",
                    regulation_reference="Wolfsberg AML Principles",
                ))
        
        return issues
    
    async def _validate_security(self, source_code: str) -> List[ValidationIssue]:
        """Common security validations."""
        issues = []
        
        # Check for reentrancy protection
        if "nonReentrant" not in source_code and "ReentrancyGuard" not in source_code:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.CRITICAL,
                framework=ComplianceFramework.BSA,  # General security
                rule_id="reentrancy_protection",
                description="Missing reentrancy protection",
                recommendation="Add nonReentrant modifier or ReentrancyGuard",
            ))
        
        # Check for access controls
        if "onlyOwner" not in source_code and "AccessControl" not in source_code:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                framework=ComplianceFramework.BSA,
                rule_id="access_control",
                description="Missing access control mechanisms",
                recommendation="Implement role-based access control",
            ))
        
        # Check for pause functionality
        if "pause" not in source_code.lower() and "emergency" not in source_code.lower():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                framework=ComplianceFramework.MICA,
                rule_id="emergency_stop",
                description="Missing emergency stop functionality",
                recommendation="Add pausable functionality for compliance emergencies",
            ))
        
        return issues
    
    def _calculate_compliance_score(self, issues: List[ValidationIssue]) -> int:
        """Calculate overall compliance score."""
        if not issues:
            return 100
        
        # Deduct points based on severity
        deductions = {
            ValidationSeverity.INFO: 0,
            ValidationSeverity.WARNING: 5,
            ValidationSeverity.ERROR: 15,
            ValidationSeverity.CRITICAL: 30,
        }
        
        total_deduction = sum(deductions[issue.severity] for issue in issues)
        score = max(0, 100 - total_deduction)
        
        return score
    
    def _hash_source(self, source_code: str) -> str:
        """Generate hash of source code."""
        import hashlib
        return hashlib.sha256(source_code.encode()).hexdigest()


# Global validator instance
contract_validator = SmartContractValidator()
