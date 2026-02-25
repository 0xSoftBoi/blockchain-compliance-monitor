# Deployment Guide

## Production Deployment

### Prerequisites

- Linux server (Ubuntu 22.04 LTS recommended)
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 6+
- SSL/TLS certificates
- Domain name configured

### Docker Deployment

#### 1. Clone Repository

```bash
git clone https://github.com/0xSoftBoi/blockchain-compliance-monitor.git
cd blockchain-compliance-monitor
```

#### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with production values
nano .env
```

#### 3. Build and Start Services

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### 4. Initialize Database

```bash
docker-compose exec api python scripts/init_db.py
```

#### 5. Verify Deployment

```bash
curl http://localhost:8000/health
```

### Kubernetes Deployment

#### 1. Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### 2. Deploy with Helm

```bash
helm install compliance ./k8s/helm/compliance \
  --namespace compliance \
  --create-namespace \
  --values ./k8s/helm/compliance/values-prod.yaml
```

#### 3. Configure Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: compliance-ingress
spec:
  tls:
    - hosts:
        - compliance.globalsettlement.com
      secretName: compliance-tls
  rules:
    - host: compliance.globalsettlement.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: compliance-api
                port:
                  number: 8000
```

### AWS Deployment

#### Using ECS

```bash
# Install AWS CLI and configure
aws configure

# Create ECR repository
aws ecr create-repository --repository-name compliance-monitor

# Build and push image
docker build -t compliance-monitor .
aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker tag compliance-monitor:latest <account-id>.dkr.ecr.<region>.amazonaws.com/compliance-monitor:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/compliance-monitor:latest

# Deploy to ECS
aws ecs create-service --service-name compliance-api --cluster compliance --desired-count 2
```

### Azure Deployment

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name compliance-rg --location eastus

# Create container instance
az container create \
  --resource-group compliance-rg \
  --name compliance-api \
  --image compliance-monitor:latest \
  --cpu 2 --memory 4 \
  --ports 8000
```

### GCP Deployment

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Deploy to Cloud Run
gcloud run deploy compliance-api \
  --image gcr.io/project-id/compliance-monitor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## SSL/TLS Configuration

### Using Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d compliance.globalsettlement.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring Setup

### Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'compliance-api'
    static_configs:
      - targets: ['api:8000']
```

### Grafana Dashboards

1. Import dashboard: `grafana/compliance-dashboard.json`
2. Configure Prometheus data source
3. Set up alerts for critical metrics

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U compliance_user compliance_db | gzip > /backups/compliance_db_$DATE.sql.gz

# Retention: 30 days
find /backups -name "compliance_db_*.sql.gz" -mtime +30 -delete
```

### Backup to S3

```bash
aws s3 sync /backups s3://compliance-backups/ --storage-class STANDARD_IA
```

## High Availability

### Load Balancer Configuration

```nginx
upstream compliance_api {
    least_conn;
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 443 ssl http2;
    server_name compliance.globalsettlement.com;

    ssl_certificate /etc/ssl/certs/compliance.crt;
    ssl_certificate_key /etc/ssl/private/compliance.key;

    location / {
        proxy_pass http://compliance_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Replication

```bash
# Primary server
postgresql.conf:
  wal_level = replica
  max_wal_senders = 3
  wal_keep_size = 64

# Standby server
standby.signal:
  primary_conninfo = 'host=primary-db port=5432 user=replicator'
```

## Security Hardening

1. **Firewall Rules**

```bash
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from trusted-ip to any port 5432
```

2. **Fail2Ban**

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

3. **SELinux/AppArmor**

```bash
sudo apt install apparmor apparmor-utils
sudo aa-enforce /etc/apparmor.d/*
```

## Performance Tuning

### PostgreSQL

```sql
-- postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
work_mem = 64MB
max_connections = 200
```

### Redis

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### API Server

```bash
# Increase worker count
uvicorn backend.main:app --workers 8 --host 0.0.0.0 --port 8000
```

## Rollback Procedure

```bash
# Tag current version
git tag v1.0.1

# Rollback to previous version
docker-compose down
git checkout v1.0.0
docker-compose -f docker-compose.prod.yml up -d
```

## Health Checks

```bash
# API health
curl https://compliance.globalsettlement.com/health

# Database health
psql -h localhost -U compliance_user -c "SELECT 1"

# Redis health
redis-cli ping
```
