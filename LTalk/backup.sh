#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Check if variables are set
if [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ]; then
  echo "Error: POSTGRES_USER or POSTGRES_DB environment variables not set"
  exit 1
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/backup_${TIMESTAMP}.sql.gz"

# Make sure backups directory exists
mkdir -p backups

echo "Creating backup: $BACKUP_FILE"
echo "Using database: $POSTGRES_DB with user: $POSTGRES_USER"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
  echo "Backup complete: $BACKUP_FILE"
else
  echo "Backup failed: $BACKUP_FILE is empty or not created"
  exit 1
fi