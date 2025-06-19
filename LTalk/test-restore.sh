#!/bin/bash
set -e

# Load environment variables from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$1" ]; then
  echo "Usage: ./test-restore.sh backup_filename.sql.gz"
  exit 1
fi

BACKUP_FILE="backups/$1"
TEST_DB="test_restore_db"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Creating test database: $TEST_DB"
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP DATABASE IF EXISTS $TEST_DB;"
docker compose exec db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE $TEST_DB;"

echo "Restoring backup to test database..."
gunzip -c "$BACKUP_FILE" | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$TEST_DB"

echo "Checking restored database..."
docker compose exec db psql -U "$POSTGRES_USER" -d "$TEST_DB" -c "\dt"
echo "Restore test complete!"