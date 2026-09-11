#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/doctor-platform}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
TIMESTAMP="$(date +%Y-%m-%d_%H-%M-%S)"
DB_BACKUP_FILE="${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"
MEDIA_BACKUP_FILE="${BACKUP_DIR}/media_${TIMESTAMP}.tar.gz"
DB_TEMP_FILE="${DB_BACKUP_FILE}.tmp"
MEDIA_TEMP_FILE="${MEDIA_BACKUP_FILE}.tmp"

umask 077
mkdir -p "$BACKUP_DIR"
trap 'rm -f "$DB_TEMP_FILE" "$MEDIA_TEMP_FILE"' EXIT

cd "$PROJECT_DIR"
docker compose exec -T db sh -c \
    'pg_dump --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
    | gzip > "$DB_TEMP_FILE"

docker compose exec -T web tar -czf - -C /app/media . > "$MEDIA_TEMP_FILE"

mv "$DB_TEMP_FILE" "$DB_BACKUP_FILE"
mv "$MEDIA_TEMP_FILE" "$MEDIA_BACKUP_FILE"
find "$BACKUP_DIR" -type f \( -name 'postgres_*.sql.gz' -o -name 'media_*.tar.gz' \) -mtime "+${RETENTION_DAYS}" -delete

echo "Database backup created: $DB_BACKUP_FILE"
echo "Media backup created: $MEDIA_BACKUP_FILE"