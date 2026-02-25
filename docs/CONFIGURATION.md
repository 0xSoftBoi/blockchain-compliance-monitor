# Configuration Guide

## Environment Variables

### Required Configuration

```bash
# Application
APP_NAME=BlockchainComplianceMonitor
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/compliance_db

# Security
SECRET_KEY=your-secret-key-min-32-characters
JWT_SECRET_KEY=your-jwt-secret-key-min-32-characters
ENCRYPTION_KEY=your-encryption-key-exactly-32-bytes
```

### Regulatory Configuration

#### United States (BSA/FinCEN)

```bash
BSA_REPORTING_ENABLED=true
FINCEN_API_KEY=your-fincen-api-key
FINCEN_INSTITUTION_ID=your-institution-id
OFAC_SCREENING_ENABLED=true
OFAC_API_KEY=your-ofac-api-key
```

#### European Union (MiCA)

```bash
MICA_COMPLIANCE_ENABLED=true
EU_SANCTIONS_ENABLED=true
GDPR_COMPLIANCE_MODE=strict
```

### Blockchain Connections

```bash
ETH_RPC_URL=https://eth-mainnet.alchemyapi.io/v2/your-api-key
BSC_RPC_URL=https://bsc-dataseed.binance.org/
POLYGON_RPC_URL=https://polygon-rpc.com/
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
OPTIMISM_RPC_URL=https://mainnet.optimism.io
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### External Compliance APIs

```bash
CHAINALYSIS_API_KEY=your-chainalysis-api-key
CHAINALYSIS_API_URL=https://api.chainalysis.com

ELLIPTIC_API_KEY=your-elliptic-api-key
ELLIPTIC_API_URL=https://api.elliptic.co

TRM_LABS_API_KEY=your-trm-labs-api-key
TRM_LABS_API_URL=https://api.trmlabs.com
```

### SWIFT Integration

```bash
SWIFT_INTEGRATION_ENABLED=true
SWIFT_API_URL=https://api.swift.com
SWIFT_INSTITUTION_BIC=YOURBICODE
SWIFT_API_KEY=your-swift-api-key
SWIFT_CERTIFICATE_PATH=/path/to/swift/cert.pem
```

## Risk Thresholds

```bash
DEFAULT_RISK_THRESHOLD=70
HIGH_RISK_THRESHOLD=85
ALERT_THRESHOLD_USD=10000
```

## Feature Flags

```bash
FEATURE_ML_RISK_SCORING=true
FEATURE_STABLECOIN_MONITORING=true
FEATURE_DEFI_MONITORING=true
FEATURE_CROSS_CHAIN_TRACKING=true
```

## Database Configuration

### PostgreSQL Setup

```sql
CREATE DATABASE compliance_db;
CREATE USER compliance_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE compliance_db TO compliance_user;
```

### Redis Configuration

```bash
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600
```

## Monitoring & Observability

```bash
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=production
```

## Notifications

```bash
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password
SMTP_FROM=compliance@globalsettlement.com

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_API_KEY=your-pagerduty-api-key
```

## Best Practices

1. **Never commit secrets** to version control
2. **Use secrets management** (HashiCorp Vault, AWS Secrets Manager)
3. **Rotate credentials** regularly
4. **Use different keys** for development and production
5. **Enable audit logging** for all configuration changes
6. **Encrypt sensitive data** at rest and in transit

## Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Configure proper `DATABASE_URL` with strong password
- [ ] Set unique `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure `ENCRYPTION_KEY` (exactly 32 bytes)
- [ ] Set up proper logging and monitoring
- [ ] Configure backup strategy
- [ ] Enable HTTPS/TLS
- [ ] Set up firewall rules
- [ ] Configure rate limiting
- [ ] Enable audit trail
- [ ] Test failover procedures
