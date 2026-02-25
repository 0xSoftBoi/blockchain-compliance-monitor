#!/bin/bash
# Database backup script

set -e

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="compliance_db"
DB_USER="compliance_user"
DB_HOST="localhost"

echo "Starting database backup: $DATE"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz

echo "Backup completed: ${DB_NAME}_${DATE}.sql.gz"

# Clean up old backups (keep last 30 days)
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +30 -delete

echo "Old backups cleaned up"

# Upload to S3 (if configured)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    aws s3 cp $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz s3://$AWS_S3_BUCKET/backups/
    echo "Backup uploaded to S3"
fi

echo "Backup process complete"
