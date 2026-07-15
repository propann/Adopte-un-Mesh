#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${ROOT_DIR:-/srv/adopte-un-mesh}"
BACKUP_DIR="${BACKUP_DIR:-${ROOT_DIR}/backups}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$BACKUP_DIR"

if [ -f "$ROOT_DIR/data/adoptmesh.sqlite3" ]; then
  sqlite3 "$ROOT_DIR/data/adoptmesh.sqlite3" ".backup '$BACKUP_DIR/adoptmesh-$STAMP.sqlite3'"
  gzip -f "$BACKUP_DIR/adoptmesh-$STAMP.sqlite3"
  echo "Backup DB: $BACKUP_DIR/adoptmesh-$STAMP.sqlite3.gz"
else
  echo "No database found at $ROOT_DIR/data/adoptmesh.sqlite3"
fi
