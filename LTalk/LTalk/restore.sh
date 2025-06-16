#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "Usage: ./restore.sh backup_filename.sql.gz"
  exit 1
fi

BACKUP_FILE="backups/$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring from backup: $BACKUP_FILE"
gzip -dc $BACKUP_FILE | docker-compose exec -T db psql -U $POSTGRES_USER $POSTGRES_DB
echo "Restore complete"