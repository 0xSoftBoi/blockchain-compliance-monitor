"""Application configuration management."""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "BlockchainComplianceMonitor"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    
    # Database
    DATABASE_URL: str = "postgresql://compliance_user:password@localhost:5432/compliance_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Encryption
    ENCRYPTION_KEY: str = "32-byte-key-change-in-production"
    DATA_ENCRYPTION_ENABLED: bool = True
    
    # Regulatory Configuration
    ENABLED_JURISDICTIONS: List[str] = Field(default=["US", "EU", "APAC"])
    DEFAULT_JURISDICTION: str = "US"
    
    # US Regulations
    BSA_REPORTING_ENABLED: bool = True
    FINCEN_API_KEY: str = ""
    FINCEN_INSTITUTION_ID: str = ""
    OFAC_SCREENING_ENABLED: bool = True
    OFAC_API_KEY: str = ""
    OFAC_REFRESH_INTERVAL_HOURS: int = 24
    
    # EU Regulations
    MICA_COMPLIANCE_ENABLED: bool = True
    EU_SANCTIONS_ENABLED: bool = True
    EU_SANCTIONS_REFRESH_INTERVAL_HOURS: int = 24
    GDPR_COMPLIANCE_MODE: str = "strict"
    
    # Risk Engine
    RISK_SCORING_ENABLED: bool = True
    DEFAULT_RISK_THRESHOLD: int = 70
    HIGH_RISK_THRESHOLD: int = 85
    ML_MODEL_ENABLED: bool = False
    ML_MODEL_PATH: str = "models/risk_scorer_v1.pkl"
    
    # Transaction Monitoring
    MONITORING_ENABLED: bool = True
    TRANSACTION_QUEUE_SIZE: int = 10000
    ALERT_THRESHOLD_USD: float = 10000.0
    SUSPICIOUS_PATTERN_DETECTION: bool = True
    BEHAVIORAL_ANALYSIS_ENABLED: bool = True
    
    # Blockchain Connections
    ETH_RPC_URL: str = "https://eth-mainnet.alchemyapi.io/v2/your-api-key"
    BSC_RPC_URL: str = "https://bsc-dataseed.binance.org/"
    POLYGON_RPC_URL: str = "https://polygon-rpc.com/"
    ARBITRUM_RPC_URL: str = "https://arb1.arbitrum.io/rpc"
    OPTIMISM_RPC_URL: str = "https://mainnet.optimism.io"
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    
    # External APIs
    CHAINALYSIS_API_KEY: str = ""
    CHAINALYSIS_API_URL: str = "https://api.chainalysis.com"
    ELLIPTIC_API_KEY: str = ""
    ELLIPTIC_API_URL: str = "https://api.elliptic.co"
    TRM_LABS_API_KEY: str = ""
    TRM_LABS_API_URL: str = "https://api.trmlabs.com"
    
    # SWIFT Integration
    SWIFT_INTEGRATION_ENABLED: bool = False
    SWIFT_API_URL: str = "https://api.swift.com"
    SWIFT_INSTITUTION_BIC: str = ""
    SWIFT_API_KEY: str = ""
    
    # Reporting
    AUTO_REPORTING_ENABLED: bool = True
    REPORT_RETENTION_DAYS: int = 2555
    REPORT_EXPORT_FORMATS: List[str] = Field(default=["PDF", "XML", "JSON"])
    
    # Audit Trail
    AUDIT_TRAIL_ENABLED: bool = True
    AUDIT_IMMUTABILITY_CHECK: bool = True
    
    # Feature Flags
    FEATURE_ML_RISK_SCORING: bool = False
    FEATURE_STABLECOIN_MONITORING: bool = True
    FEATURE_DEFI_MONITORING: bool = False
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("ENABLED_JURISDICTIONS", mode="before")
    @classmethod
    def parse_jurisdictions(cls, v):
        if isinstance(v, str):
            return [j.strip() for j in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
