#!/bin/bash
set -e

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/backup_${TIMESTAMP}.sql.gz"

echo "Creating backup: $BACKUP_FILE"
docker-compose exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB | gzip > $BACKUP_FILE
echo "Backup complete: $BACKUP_FILE"