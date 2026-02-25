# API Reference

## Base URL

```
https://api.globalsettlement.com/api/v1
```

## Authentication

All API requests require authentication using JWT tokens.

```bash
Authorization: Bearer <your-jwt-token>
```

## Monitoring Endpoints

### Submit Transaction for Monitoring

**POST** `/monitoring/transaction`

Submit a blockchain transaction for compliance monitoring.

#### Request Body

```json
{
  "tx_hash": "0x742d...",
  "from_address": "0x123...",
  "to_address": "0x456...",
  "value_usd": 15000.00,
  "blockchain": "ethereum",
  "timestamp": "2024-02-25T14:30:00Z",
  "token_symbol": "USDC",
  "contract_address": "0xa0b8..."
}
```

#### Response

```json
{
  "monitoring_id": "mon_a1b2c3d4",
  "tx_hash": "0x742d...",
  "status": "queued",
  "message": "Transaction submitted for compliance monitoring"
}
```

### Get Compliance Alerts

**GET** `/monitoring/alerts?severity=high&limit=100`

#### Query Parameters

- `severity` (optional): Filter by severity (low, medium, high, critical)
- `alert_type` (optional): Filter by type
- `limit` (optional): Maximum results (default: 100)

#### Response

```json
{
  "count": 12,
  "alerts": [
    {
      "id": "alert_xyz",
      "type": "sanctions_hit",
      "severity": "critical",
      "tx_hash": "0x742d...",
      "description": "Sender address is on OFAC sanctions list",
      "risk_score": 100,
      "recommended_action": "BLOCK transaction immediately",
      "created_at": "2024-02-25T14:35:00Z"
    }
  ]
}
```

## Sanctions Screening

### Screen Single Address

**POST** `/sanctions/screen`

#### Request Body

```json
{
  "address": "0x123..."
}
```

#### Response

```json
{
  "address": "0x123...",
  "sanctioned": false,
  "risk_level": "low",
  "action": "Proceed"
}
```

### Batch Screening

**POST** `/sanctions/screen/batch`

#### Request Body

```json
{
  "addresses": ["0x123...", "0x456...", "0x789..."]
}
```

#### Response

```json
{
  "total_screened": 3,
  "sanctioned_count": 0,
  "results": [
    {"address": "0x123...", "sanctioned": false},
    {"address": "0x456...", "sanctioned": false},
    {"address": "0x789...", "sanctioned": false}
  ]
}
```

## Risk Scoring

### Score Address

**POST** `/risk/score`

#### Request Body

```json
{
  "address": "0x123..."
}
```

#### Response

```json
{
  "address": "0x123...",
  "risk_score": 45,
  "risk_level": "medium",
  "recommendation": "Enhanced monitoring recommended"
}
```

### Score Transaction

**POST** `/risk/transaction`

#### Request Body

```json
{
  "from_address": "0x123...",
  "to_address": "0x456...",
  "value_usd": 25000.00,
  "blockchain": "ethereum"
}
```

#### Response

```json
{
  "transaction": {...},
  "risk_assessment": {
    "overall_score": 55,
    "sender_risk": 45,
    "receiver_risk": 60,
    "amount_risk": 12,
    "risk_level": "medium"
  },
  "recommendation": "Enhanced monitoring recommended"
}
```

## Smart Contract Validation

### Validate Contract

**POST** `/validation/contract`

#### Request Body

```json
{
  "source_code": "pragma solidity ^0.8.0; contract MyContract {...}",
  "frameworks": ["mica", "bsa"],
  "contract_address": "0xabc..."
}
```

#### Response

```json
{
  "validation_result": {
    "passed": false,
    "compliance_score": 75,
    "contract_address": "0xabc...",
    "source_code_hash": "sha256...",
    "timestamp": "2024-02-25T14:40:00Z",
    "frameworks_checked": ["mica", "bsa"]
  },
  "issues": [
    {
      "severity": "error",
      "framework": "mica",
      "rule_id": "kyc_requirement",
      "description": "KYC verification required for participants",
      "recommendation": "Implement kyc verification",
      "regulation_reference": "MiCA Article 16-20"
    }
  ],
  "summary": {
    "total_issues": 5,
    "critical": 0,
    "errors": 2,
    "warnings": 3
  }
}
```

## Regulatory Reporting

### Generate Report

**POST** `/reporting/generate`

#### Request Body

```json
{
  "report_type": "sar",
  "period_start": "2024-01-01T00:00:00Z",
  "period_end": "2024-01-31T23:59:59Z",
  "jurisdiction": "US",
  "format": "json"
}
```

#### Response

```json
{
  "report_id": "SAR-20240125-abc123",
  "report_type": "sar",
  "status": "draft",
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "created_at": "2024-02-25T14:45:00Z",
  "data": {...}
}
```

### List Reports

**GET** `/reporting/submissions?report_type=sar&status=submitted&limit=50`

#### Response

```json
{
  "count": 3,
  "reports": [
    {
      "report_id": "SAR-20240125-abc123",
      "type": "sar",
      "status": "submitted",
      "jurisdiction": "US",
      "period_start": "2024-01-01T00:00:00Z",
      "period_end": "2024-01-31T23:59:59Z",
      "created_at": "2024-02-25T14:45:00Z",
      "submitted_at": "2024-02-26T10:00:00Z"
    }
  ]
}
```

## Rate Limiting

- **Standard**: 60 requests per minute
- **Burst**: 1000 requests per hour

### Rate Limit Headers

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1614264000
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {"field": "value_usd", "message": "Must be a positive number"}
  ]
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid or expired token"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 30
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "type": "DatabaseConnectionError"
}
```
