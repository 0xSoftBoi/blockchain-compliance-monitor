# Quick Start Guide

## Get Up and Running in 5 Minutes

### Prerequisites

- Docker & Docker Compose installed
- Git installed
- 8GB RAM minimum

### Step 1: Clone & Configure

```bash
# Clone repository
git clone https://github.com/0xSoftBoi/blockchain-compliance-monitor.git
cd blockchain-compliance-monitor

# Copy environment file
cp .env.example .env
```

### Step 2: Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service health
docker-compose ps
```

### Step 3: Initialize Database

```bash
# Initialize database (creates tables and loads seed data)
docker-compose exec api python scripts/init_db.py
```

### Step 4: Access the System

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Frontend Dashboard**: http://localhost:3000 (if frontend is running)
- **Metrics**: http://localhost:8000/metrics

## Quick API Test

### 1. Submit a Transaction for Monitoring

```bash
curl -X POST "http://localhost:8000/api/v1/monitoring/transaction" \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0x742d35cc6634c0532925a3b844bc9e7fbbdd98e3b7c007e836c8ebcf5df9ae25",
    "from_address": "0x123456789abcdef123456789abcdef1234567890",
    "to_address": "0xabcdef123456789abcdef123456789abcdef1234",
    "value_usd": 15000.00,
    "blockchain": "ethereum"
  }'
```

### 2. Screen an Address for Sanctions

```bash
curl -X POST "http://localhost:8000/api/v1/sanctions/screen" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x123456789abcdef123456789abcdef1234567890"
  }'
```

### 3. Get Risk Score

```bash
curl -X POST "http://localhost:8000/api/v1/risk/score" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x123456789abcdef123456789abcdef1234567890"
  }'
```

### 4. Get Active Alerts

```bash
curl "http://localhost:8000/api/v1/monitoring/alerts?limit=10"
```

## Common Operations

### View Logs

```bash
# API logs
docker-compose logs -f api

# All services
docker-compose logs -f

# Specific number of lines
docker-compose logs --tail=100 api
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs for errors
docker-compose logs api

# Verify environment variables
cat .env

# Check port conflicts
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker-compose exec postgres psql -U compliance_user -d compliance_db -c "SELECT 1"

# Test Redis connection
docker-compose exec redis redis-cli ping
```

### Reset Everything

```bash
# Stop services and remove all data
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
python scripts/init_db.py
```

## Next Steps

1. **Read the Documentation**
   - [Configuration Guide](docs/CONFIGURATION.md)
   - [API Reference](docs/API_REFERENCE.md)
   - [Deployment Guide](docs/DEPLOYMENT.md)

2. **Configure Integrations**
   - Set up blockchain RPC endpoints
   - Configure compliance API keys (Chainalysis, Elliptic)
   - Enable SWIFT integration (if needed)

3. **Customize Settings**
   - Adjust risk thresholds
   - Configure alert rules
   - Set up notifications

4. **Production Deployment**
   - Follow [Deployment Guide](docs/DEPLOYMENT.md)
   - Set up monitoring and alerting
   - Configure backups

## Getting Help

- **Documentation**: Check the `/docs` directory
- **Issues**: https://github.com/0xSoftBoi/blockchain-compliance-monitor/issues
- **API Docs**: http://localhost:8000/docs (interactive)

## Security Notice

⚠️ **IMPORTANT**: 
- Change all default passwords in `.env`
- Never commit `.env` file to version control
- Use strong, unique keys for production
- Enable HTTPS/TLS for production deployments
