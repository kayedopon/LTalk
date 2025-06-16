// filepath: c:\studies\vgtu\1_year\oop\LTalk\LTalk\LTalk\cleanup.sh
#!/bin/bash
set -e

# Keep backups for 30 days
KEEP_DAYS=30

echo "Cleaning up backups older than $KEEP_DAYS days..."
find backups/ -name "backup_*.sql.gz" -type f -mtime +$KEEP_DAYS -delete
echo "Cleanup complete"